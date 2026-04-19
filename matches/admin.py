"""Matches Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Match, TournamentResult


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'round_name', 'status_badge', 'score_display', 'scheduled_at']
    list_filter = ['tournament', 'round_name', 'status']
    search_fields = ['tournament__title']
    ordering = ['tournament', 'round_name', 'match_number']
    # list_editable = ['status']  # Removed - status not in list_display for direct edit

    fieldsets = (
        ('Match Info', {'fields': ('tournament', 'round_name', 'match_number', 'bracket_position')}),
        ('Teams (Squad)', {'fields': ('team1', 'team2', 'winner_team')}),
        ('Players (Solo)', {'fields': ('player1', 'player2', 'winner_player')}),
        ('Scores', {'fields': ('team1_score', 'team2_score')}),
        ('Schedule', {'fields': ('scheduled_at', 'completed_at', 'server_details', 'room_id', 'room_password')}),
        ('Status', {'fields': ('status', 'notes', 'next_match')}),
    )

    def status_badge(self, obj):
        colors = {'SCHEDULED': '#888', 'LIVE': '#00C851', 'COMPLETED': '#00B0FF', 'POSTPONED': '#FFBB33', 'CANCELLED': '#FF4444'}
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:12px;">{}</span>',
                           colors.get(obj.status, '#888'), obj.status)
    status_badge.short_description = 'Status'

    def score_display(self, obj):
        return f"{obj.team1_score} : {obj.team2_score}"
    score_display.short_description = 'Score'

    actions = ['set_live', 'set_completed']

    def set_live(self, request, queryset):
        queryset.update(status='LIVE')
    set_live.short_description = '🔴 Set Live'

    def set_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    set_completed.short_description = '✅ Set Completed'


@admin.register(TournamentResult)
class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'position', 'player', 'team', 'prize_won', 'rank_points_awarded']
    list_filter = ['tournament']
    ordering = ['tournament', 'position']
