"""
Matches Views
- bracket_view: show bracket for a tournament
- schedule_view: show matches + time slots
- tournament_leaderboard_view: per-tournament team stats
- results_view: final positions and prizes
- admin_update_match_view: form for admin to set winner
- admin_create_slots_view: form to bulk-create time slots
- admin_assign_slot_view: assign slot to match
- generate_bracket: staff generates bracket
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone

import math
import random

from .models import Match, TournamentResult, TimeSlot, TeamStats
from .services import update_match_result, assign_match_to_slot, create_time_slots, get_tournament_leaderboard
from tournaments.models import Tournament, Registration
from teams.models import Team
from players.models import Player


ROUND_ORDER = ['ROUND_64', 'ROUND_32', 'ROUND_16', 'QUARTER', 'SEMI', 'THIRD_PLACE', 'FINAL']


# ── PUBLIC VIEWS ──────────────────────────────────────────────────────────────

def bracket_view(request, slug):
    """Public: show tournament bracket."""
    tournament = get_object_or_404(Tournament, slug=slug)
    matches = Match.objects.filter(tournament=tournament).order_by('round_name', 'match_number')

    rounds = {}
    for match in matches:
        rounds.setdefault(match.round_name, []).append(match)
    ordered_rounds = [(r, rounds[r]) for r in ROUND_ORDER if r in rounds]

    return render(request, 'matches/bracket.html', {
        'tournament': tournament,
        'rounds': ordered_rounds,
        'all_matches': matches,
    })


def schedule_view(request, slug):
    """Public: show match schedule with times."""
    tournament = get_object_or_404(Tournament, slug=slug)
    matches = Match.objects.filter(
        tournament=tournament
    ).select_related('team1', 'team2', 'player1', 'player2', 'winner_team', 'winner_player').order_by('scheduled_at', 'round_name', 'match_number')

    slots = TimeSlot.objects.filter(tournament=tournament).order_by('start_time')

    return render(request, 'matches/schedule.html', {
        'tournament': tournament,
        'matches': matches,
        'slots': slots,
    })


def tournament_leaderboard_view(request, slug):
    """Public: per-tournament team standings."""
    tournament = get_object_or_404(Tournament, slug=slug)
    standings = get_tournament_leaderboard(tournament)

    return render(request, 'matches/tournament_leaderboard.html', {
        'tournament': tournament,
        'standings': standings,
    })


def results_view(request, slug):
    """Public: final results and prize distribution."""
    tournament = get_object_or_404(Tournament, slug=slug)
    results = TournamentResult.objects.filter(
        tournament=tournament
    ).select_related('team', 'player__user').order_by('position')

    return render(request, 'matches/results.html', {
        'tournament': tournament,
        'results': results,
    })


# ── ADMIN VIEWS ───────────────────────────────────────────────────────────────

@staff_member_required
def admin_update_match_view(request, slug):
    """Admin: form to select a match and update its result."""
    tournament = get_object_or_404(Tournament, slug=slug)
    matches = Match.objects.filter(
        tournament=tournament
    ).exclude(status='COMPLETED').order_by('round_name', 'match_number')

    selected_match = None
    match_id = request.GET.get('match_id') or request.POST.get('match_id')
    if match_id:
        selected_match = get_object_or_404(Match, id=match_id, tournament=tournament)

    if request.method == 'POST' and selected_match:
        winner_id = request.POST.get('winner_id')
        score1 = int(request.POST.get('score1', 0))
        score2 = int(request.POST.get('score2', 0))

        if not winner_id:
            messages.error(request, 'Please select a winner.')
        else:
            is_team = tournament.mode in ['SQUAD', 'TEAM5', 'DUO']
            try:
                update_match_result(
                    match_id=selected_match.id,
                    winner_id=int(winner_id),
                    is_team_mode=is_team,
                    score1=score1,
                    score2=score2,
                )
                messages.success(request, f'✅ Match result updated! Winner set.')
                return redirect('matches:admin_update_match', slug=slug)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

    return render(request, 'matches/admin_update_match.html', {
        'tournament': tournament,
        'matches': matches,
        'selected_match': selected_match,
    })


@staff_member_required
def admin_create_slots_view(request, slug):
    """Admin: bulk create time slots for a tournament."""
    tournament = get_object_or_404(Tournament, slug=slug)
    slots = TimeSlot.objects.filter(tournament=tournament).order_by('start_time')

    if request.method == 'POST':
        from datetime import datetime
        start_str = request.POST.get('start_time')
        interval = int(request.POST.get('interval_minutes', 30))
        count = int(request.POST.get('count', 4))

        try:
            start_time = timezone.make_aware(
                datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
            )
            create_time_slots(tournament, start_time, interval, count)
            messages.success(request, f'✅ {count} time slots created!')
            return redirect('matches:admin_slots', slug=slug)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'matches/admin_slots.html', {
        'tournament': tournament,
        'slots': slots,
    })


@staff_member_required
def admin_assign_slot_view(request, slug):
    """Admin: assign a time slot to a match."""
    tournament = get_object_or_404(Tournament, slug=slug)

    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        slot_id = request.POST.get('slot_id')
        try:
            assign_match_to_slot(match_id, slot_id)
            messages.success(request, '✅ Slot assigned to match!')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('matches:admin_slots', slug=slug)

    unscheduled = Match.objects.filter(
        tournament=tournament, scheduled_at__isnull=True
    ).order_by('round_name', 'match_number')
    available_slots = TimeSlot.objects.filter(tournament=tournament, is_booked=False)

    return render(request, 'matches/admin_assign_slot.html', {
        'tournament': tournament,
        'unscheduled_matches': unscheduled,
        'available_slots': available_slots,
    })


@staff_member_required
def generate_bracket(request, slug):
    """Admin: generate knockout bracket from confirmed registrations."""
    if request.method != 'POST':
        return redirect('matches:bracket', slug=slug)

    tournament = get_object_or_404(Tournament, slug=slug)
    registrations = list(
        Registration.objects.filter(
            tournament=tournament, status='CONFIRMED'
        ).select_related('player')
    )

    if len(registrations) < 2:
        messages.error(request, 'Need at least 2 confirmed registrations to generate bracket.')
        return redirect('matches:bracket', slug=slug)

    if Match.objects.filter(tournament=tournament).exists():
        messages.warning(request, 'Bracket already exists. Delete existing matches from admin first.')
        return redirect('matches:bracket', slug=slug)

    random.shuffle(registrations)
    n = len(registrations)
    bracket_size = 2 ** math.ceil(math.log2(n))

    round_map = {2: 'FINAL', 4: 'SEMI', 8: 'QUARTER', 16: 'ROUND_16', 32: 'ROUND_32', 64: 'ROUND_64'}
    first_round = round_map.get(bracket_size, 'ROUND_64')

    participants = registrations + [None] * (bracket_size - n)
    match_number = 1
    first_round_matches = []

    for i in range(0, bracket_size, 2):
        p1 = participants[i]
        p2 = participants[i + 1] if i + 1 < bracket_size else None

        match_data = {
            'tournament': tournament,
            'round_name': first_round,
            'match_number': match_number,
            'bracket_position': i // 2,
            'status': 'SCHEDULED',
        }

        if tournament.mode in ['SQUAD', 'TEAM5']:
            try:
                match_data['team1'] = p1.player.team_membership.team if p1 else None
                match_data['team2'] = p2.player.team_membership.team if p2 else None
            except Exception:
                match_data['team1'] = None
                match_data['team2'] = None
        else:
            match_data['player1'] = p1.player if p1 else None
            match_data['player2'] = p2.player if p2 else None

        m = Match.objects.create(**match_data)
        first_round_matches.append(m)
        match_number += 1

    messages.success(request, f'✅ Bracket generated! {len(first_round_matches)} matches created.')
    return redirect('matches:bracket', slug=slug)
