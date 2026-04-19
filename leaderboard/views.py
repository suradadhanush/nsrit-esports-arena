"""Leaderboard Views"""
from django.shortcuts import render
from .models import LeaderboardEntry, TeamLeaderboard
from players.models import Player


def leaderboard(request):
    """Global leaderboard with category filters."""
    category = request.GET.get('category', 'OVERALL')
    season = request.GET.get('season', 'Season 1')

    entries = LeaderboardEntry.objects.filter(
        category=category,
        season=season
    ).select_related('player__user').order_by('rank')[:50]

    team_entries = TeamLeaderboard.objects.filter(
        category=category,
        season=season
    ).select_related('team').order_by('rank')[:20]

    context = {
        'entries': entries,
        'team_entries': team_entries,
        'category': category,
        'season': season,
        'categories': LeaderboardEntry.CATEGORY_CHOICES,
        'top3': entries[:3],
    }
    return render(request, 'leaderboard/leaderboard.html', context)


def rebuild_leaderboard(request):
    """Rebuild leaderboard from player stats."""
    players = Player.objects.all().order_by('-rank_points')
    for rank, player in enumerate(players, 1):
        LeaderboardEntry.objects.update_or_create(
            player=player,
            category='OVERALL',
            season='Season 1',
            defaults={
                'rank': rank,
                'rank_points': player.rank_points,
                'total_wins': player.total_wins,
                'total_kills': player.total_kills,
                'total_matches': player.total_matches,
                'tournament_wins': player.tournament_wins,
            }
        )
    from django.contrib import messages
    from django.shortcuts import redirect
    messages.success(request, '🏆 Leaderboard rebuilt!')
    return redirect('leaderboard:leaderboard')
