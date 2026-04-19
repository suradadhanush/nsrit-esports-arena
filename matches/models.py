"""
Matches App - Tournament Bracket System
"""
from django.db import models
from tournaments.models import Tournament
from teams.models import Team
from players.models import Player


class Match(models.Model):
    ROUND_CHOICES = [
        ('ROUND_64', 'Round of 64'),
        ('ROUND_32', 'Round of 32'),
        ('ROUND_16', 'Round of 16'),
        ('QUARTER', 'Quarter Final'),
        ('SEMI', 'Semi Final'),
        ('THIRD_PLACE', 'Third Place Match'),
        ('FINAL', 'Grand Final'),
    ]
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    round_name = models.CharField(max_length=15, choices=ROUND_CHOICES)
    match_number = models.IntegerField()
    bracket_position = models.IntegerField(default=0)

    # For team-based tournaments
    team1 = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_team1'
    )
    team2 = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_team2'
    )

    # For solo tournaments
    player1 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_player1'
    )
    player2 = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_player2'
    )

    # Result
    winner_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_won'
    )
    winner_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_won'
    )

    # Scores
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)

    # Schedule
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    server_details = models.CharField(max_length=200, blank=True)
    room_id = models.CharField(max_length=50, blank=True)
    room_password = models.CharField(max_length=50, blank=True)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)

    # Link to next match (bracket progression)
    next_match = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_matches'
    )

    class Meta:
        db_table = 'matches'
        ordering = ['round_name', 'match_number']
        unique_together = [('tournament', 'round_name', 'match_number')]
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f"{self.tournament.title} | {self.get_round_name_display()} | M{self.match_number}"

    @property
    def is_bye(self):
        """Returns True if one participant is missing (bye round)."""
        return (self.team1 is None or self.team2 is None) if self.tournament.mode != 'SOLO' else (
            self.player1 is None or self.player2 is None
        )


class TournamentResult(models.Model):
    """Final results and prize distribution."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='results')
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.IntegerField()
    prize_won = models.IntegerField(default=0)
    kills = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    rank_points_awarded = models.IntegerField(default=0)

    class Meta:
        db_table = 'results'
        ordering = ['tournament', 'position']
        unique_together = [('tournament', 'position')]

    def __str__(self):
        name = self.team.name if self.team else self.player.ign
        return f"#{self.position} {name} — {self.tournament.title}"
