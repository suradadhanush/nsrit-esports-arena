"""Matches Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Match, TournamentResult, TimeSlot, TeamStats


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'round_name', 'status_badge', 'score_display', 'scheduled_at', 'winner_display']
    list_filter = ['tournament', 'round_name', 'status']
    search_fields = ['tournament__title', 'team1__name', 'team2__name']
    ordering = ['tournament', 'round_name', 'match_number']

    fieldsets = (
        ('Match Info', {'fields': ('tournament', 'round_name', 'match_number', 'bracket_position', 'next_match')}),
        ('Teams (Squad/Team Mode)', {'fields': ('team1', 'team2', 'winner_team')}),
        ('Players (Solo Mode)', {'fields': ('player1', 'player2', 'winner_player')}),
        ('Scores', {'fields': ('team1_score', 'team2_score')}),
        ('Room Details', {'fields': ('room_id', 'room_password', 'server_details')}),
        ('Schedule', {'fields': ('scheduled_at', 'completed_at')}),
        ('Status & Notes', {'fields': ('status', 'notes')}),
    )

    actions = ['set_live', 'set_completed', 'set_scheduled']

    def status_badge(self, obj):
        colors = {
            'SCHEDULED': '#888', 'LIVE': '#00C851',
            'COMPLETED': '#00B0FF', 'POSTPONED': '#FFBB33', 'CANCELLED': '#FF4444'
        }
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;">{}</span>',
            colors.get(obj.status, '#888'), obj.status
        )
    status_badge.short_description = 'Status'

    def score_display(self, obj):
        return f"{obj.team1_score} : {obj.team2_score}"
    score_display.short_description = 'Score'

    def winner_display(self, obj):
        if obj.winner_team:
            return format_html('<span style="color:#00C851;">🏆 {}</span>', obj.winner_team.name)
        if obj.winner_player:
            return format_html('<span style="color:#00C851;">🏆 {}</span>', obj.winner_player.ign)
        return '—'
    winner_display.short_description = 'Winner'

    def set_live(self, request, queryset):
        queryset.update(status='LIVE')
        self.message_user(request, f'{queryset.count()} match(es) set to LIVE.')
    set_live.short_description = '🔴 Set Live'

    def set_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
        self.message_user(request, f'{queryset.count()} match(es) set to COMPLETED.')
    set_completed.short_description = '✅ Set Completed'

    def set_scheduled(self, request, queryset):
        queryset.update(status='SCHEDULED')
    set_scheduled.short_description = '📅 Set Scheduled'


@admin.register(TournamentResult)
class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'position', 'player', 'team', 'prize_won', 'kills', 'rank_points_awarded']
    list_filter = ['tournament']
    ordering = ['tournament', 'position']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'label', 'start_time', 'end_time', 'is_booked']
    list_filter = ['tournament', 'is_booked']
    ordering = ['tournament', 'start_time']
    list_editable = ['is_booked']


@admin.register(TeamStats)
class TeamStatsAdmin(admin.ModelAdmin):
    list_display = ['team', 'tournament', 'matches_played', 'wins', 'losses', 'points']
    list_filter = ['tournament']
    ordering = ['tournament', '-wins']
