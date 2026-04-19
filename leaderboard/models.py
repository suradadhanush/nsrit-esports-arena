"""
Leaderboard App - Rankings & Statistics
"""
from django.db import models
from players.models import Player
from teams.models import Team
from tournaments.models import Tournament


class LeaderboardEntry(models.Model):
    """Global player leaderboard."""
    CATEGORY_CHOICES = [
        ('OVERALL', 'Overall'),
        ('BGMI', 'BGMI'),
        ('VALORANT', 'Valorant'),
        ('COD', 'Call of Duty Mobile'),
        ('FREE_FIRE', 'Free Fire'),
        ('CS2', 'Counter-Strike 2'),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries'
    )
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='OVERALL')
    rank = models.IntegerField()
    rank_points = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_kills = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    tournament_wins = models.IntegerField(default=0)
    season = models.CharField(max_length=20, default='Season 1')

    class Meta:
        db_table = 'leaderboard'
        ordering = ['rank']
        unique_together = [('player', 'category', 'season')]
        verbose_name = 'Leaderboard Entry'
        verbose_name_plural = 'Leaderboard'

    def __str__(self):
        return f"#{self.rank} {self.player.ign} ({self.category})"

    @property
    def win_rate(self):
        if self.total_matches > 0:
            return round((self.total_wins / self.total_matches) * 100, 1)
        return 0.0


class TeamLeaderboard(models.Model):
    """Team rankings."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='leaderboard_entries')
    category = models.CharField(max_length=15, default='OVERALL')
    rank = models.IntegerField()
    rank_points = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    season = models.CharField(max_length=20, default='Season 1')

    class Meta:
        db_table = 'team_leaderboard'
        ordering = ['rank']
        verbose_name = 'Team Leaderboard Entry'
        verbose_name_plural = 'Team Leaderboard'

    def __str__(self):
        return f"#{self.rank} {self.team.name}"
