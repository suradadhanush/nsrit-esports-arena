"""Teams Admin"""
from django.contrib import admin
from .models import Team, TeamMember, TeamInvite


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ['player', 'role', 'jersey_number', 'is_active']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'game', 'captain', 'member_count', 'total_wins', 'rank_points', 'is_recruiting']
    list_filter = ['game', 'is_recruiting']
    search_fields = ['name', 'tag']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TeamMemberInline]
    ordering = ['-rank_points']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['player', 'team', 'role', 'joined_at', 'is_active']
    list_filter = ['role', 'team__game']
    search_fields = ['player__ign', 'team__name']


@admin.register(TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    list_display = ['invited_player', 'team', 'invited_by', 'role', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['invited_player__ign', 'team__name']
