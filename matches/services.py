"""
Match Services
- update_match_result: set winner + auto-progress to next round
- assign_match_to_slot: assign time slot with conflict check
- update_team_stats: increment per-tournament stats
- get_tournament_leaderboard: return ranked teams for a tournament
"""
from django.db import transaction
from django.utils import timezone


def update_match_result(match_id, winner_id, is_team_mode=True, score1=0, score2=0):
    """
    Set match winner, mark completed, auto-progress winner to next match.
    Idempotent — safe to call multiple times.
    """
    from .models import Match, TeamStats
    from teams.models import Team
    from players.models import Player

    with transaction.atomic():
        match = Match.objects.select_for_update().get(id=match_id)

        match.team1_score = score1
        match.team2_score = score2
        match.status = 'COMPLETED'
        match.completed_at = timezone.now()

        if is_team_mode:
            winner = Team.objects.get(id=winner_id)
            loser = match.team1 if match.team2 == winner else match.team2

            match.winner_team = winner

            # Update team global stats
            winner.total_wins += 1
            winner.total_matches += 1
            winner.rank_points += 10
            winner.save(update_fields=['total_wins', 'total_matches', 'rank_points'])

            if loser:
                loser.total_matches += 1
                loser.save(update_fields=['total_matches'])

            # Update per-tournament TeamStats
            _update_team_stats(match.tournament, winner, won=True)
            if loser:
                _update_team_stats(match.tournament, loser, won=False)

            # Auto-progress winner to next match
            if match.next_match:
                next_m = match.next_match
                if next_m.team1 is None:
                    next_m.team1 = winner
                elif next_m.team2 is None:
                    next_m.team2 = winner
                next_m.save(update_fields=['team1', 'team2'])

        else:
            winner = Player.objects.get(id=winner_id)
            match.winner_player = winner

            winner.total_wins += 1
            winner.total_matches += 1
            winner.rank_points += 10
            winner.save(update_fields=['total_wins', 'total_matches', 'rank_points'])

            # Auto-progress to next match
            if match.next_match:
                next_m = match.next_match
                if next_m.player1 is None:
                    next_m.player1 = winner
                elif next_m.player2 is None:
                    next_m.player2 = winner
                next_m.save(update_fields=['player1', 'player2'])

        match.save()
    return match


def _update_team_stats(tournament, team, won=True):
    """Increment per-tournament TeamStats for a team."""
    from .models import TeamStats
    stats, _ = TeamStats.objects.get_or_create(tournament=tournament, team=team)
    stats.matches_played += 1
    if won:
        stats.wins += 1
        stats.points += 3
    else:
        stats.losses += 1
    stats.save(update_fields=['matches_played', 'wins', 'losses', 'points'])


def assign_match_to_slot(match_id, slot_id):
    """
    Assign a time slot to a match.
    Raises ValueError if slot is already booked.
    """
    from .models import Match, TimeSlot

    with transaction.atomic():
        slot = TimeSlot.objects.select_for_update().get(id=slot_id)

        if slot.is_booked:
            raise ValueError(f"Time slot '{slot}' is already booked.")

        match = Match.objects.get(id=match_id)
        match.scheduled_at = slot.start_time
        match.save(update_fields=['scheduled_at'])

        slot.is_booked = True
        slot.save(update_fields=['is_booked'])

    return match


def get_tournament_leaderboard(tournament):
    """Return TeamStats for a tournament sorted by wins then points."""
    from .models import TeamStats
    return TeamStats.objects.filter(
        tournament=tournament
    ).select_related('team').order_by('-wins', '-points', 'losses')


def create_time_slots(tournament, start_time, interval_minutes, count):
    """
    Bulk create time slots for a tournament.
    start_time: datetime object
    interval_minutes: gap between slots in minutes
    count: number of slots to create
    """
    from .models import TimeSlot
    from datetime import timedelta

    slots = []
    for i in range(count):
        slot_start = start_time + timedelta(minutes=interval_minutes * i)
        slot_end = slot_start + timedelta(minutes=interval_minutes)
        slots.append(TimeSlot(
            tournament=tournament,
            start_time=slot_start,
            end_time=slot_end,
            label=f'Match Slot {i + 1}',
        ))

    TimeSlot.objects.bulk_create(slots)
    return slots
