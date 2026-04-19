"""
Matches Views - Bracket Generation and Display
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone

import math
import random

from .models import Match, TournamentResult
from tournaments.models import Tournament, Registration
from teams.models import Team
from players.models import Player


# ─────────────────────────────────────────────
# BRACKET VIEW
# ─────────────────────────────────────────────
def bracket_view(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)

    matches = Match.objects.filter(
        tournament=tournament
    ).order_by('round_name', 'match_number')

    rounds = {}
    round_order = [
        'ROUND_64', 'ROUND_32', 'ROUND_16',
        'QUARTER', 'SEMI', 'THIRD_PLACE', 'FINAL'
    ]

    for match in matches:
        rounds.setdefault(match.round_name, []).append(match)

    ordered_rounds = [(r, rounds[r]) for r in round_order if r in rounds]

    return render(request, 'matches/bracket.html', {
        'tournament': tournament,
        'rounds': ordered_rounds,
        'all_matches': matches,
    })


# ─────────────────────────────────────────────
# GENERATE BRACKET
# ─────────────────────────────────────────────
@staff_member_required
def generate_bracket(request, slug):

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('matches:bracket', slug=slug)

    tournament = get_object_or_404(Tournament, slug=slug)

    registrations = list(
        Registration.objects.filter(
            tournament=tournament,
            status='CONFIRMED'
        ).select_related('player')
    )

    if len(registrations) < 2:
        messages.error(request, 'Need at least 2 confirmed registrations.')
        return redirect('matches:bracket', slug=slug)

    # Prevent accidental regeneration if matches already exist
    if Match.objects.filter(tournament=tournament).exists():
        messages.warning(request, "Bracket already exists. Delete first if needed.")
        return redirect('matches:bracket', slug=slug)

    random.shuffle(registrations)

    n = len(registrations)
    bracket_size = 2 ** math.ceil(math.log2(n))

    round_map = {
        64: 'ROUND_64',
        32: 'ROUND_32',
        16: 'ROUND_16',
        8: 'QUARTER',
        4: 'SEMI',
        2: 'FINAL'
    }

    first_round = round_map.get(bracket_size, 'ROUND_64')

    participants = registrations + [None] * (bracket_size - n)

    created_matches = []
    match_number = 1

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
            match_data['team1'] = getattr(p1, 'team', None)
            match_data['team2'] = getattr(p2, 'team', None)
        else:
            match_data['player1'] = p1.player if p1 else None
            match_data['player2'] = p2.player if p2 else None

        Match.objects.create(**match_data)

        created_matches.append(match_number)
        match_number += 1

    messages.success(
        request,
        f'✅ Bracket generated! {len(created_matches)} matches created.'
    )

    return redirect('matches:bracket', slug=slug)


# ─────────────────────────────────────────────
# UPDATE MATCH RESULT
# ─────────────────────────────────────────────
@staff_member_required
def update_match_result(request, match_id):

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('matches:bracket')

    match = get_object_or_404(Match, id=match_id)

    winner_id = request.POST.get('winner')

    if not winner_id:
        messages.error(request, "Select a winner.")
        return redirect('matches:bracket', slug=match.tournament.slug)

    score1 = int(request.POST.get('score1', 0))
    score2 = int(request.POST.get('score2', 0))

    match.team1_score = score1
    match.team2_score = score2
    match.status = 'COMPLETED'
    match.completed_at = timezone.now()

    tournament = match.tournament

    # ───── TEAM MODE ─────
    if tournament.mode in ['SQUAD', 'TEAM5']:

        try:
            winner_team = Team.objects.get(id=winner_id)
        except Team.DoesNotExist:
            messages.error(request, "Invalid team selected.")
            return redirect('matches:bracket', slug=tournament.slug)

        match.winner_team = winner_team

        winner_team.total_wins += 1
        winner_team.total_matches += 1
        winner_team.rank_points += 10
        winner_team.save()

        if match.team1 and match.team1 != winner_team:
            match.team1.total_matches += 1
            match.team1.save()

        if match.team2 and match.team2 != winner_team:
            match.team2.total_matches += 1
            match.team2.save()

    # ───── SOLO MODE ─────
    else:

        try:
            winner_player = Player.objects.get(id=winner_id)
        except Player.DoesNotExist:
            messages.error(request, "Invalid player selected.")
            return redirect('matches:bracket', slug=tournament.slug)

        match.winner_player = winner_player

        winner_player.total_wins += 1
        winner_player.total_matches += 1
        winner_player.rank_points += 10
        winner_player.update_tier()
        winner_player.save()

    match.save()

    messages.success(request, 'Match result updated!')

    return redirect('matches:bracket', slug=tournament.slug)