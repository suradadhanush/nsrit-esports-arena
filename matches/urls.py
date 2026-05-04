"""Matches URLs"""
from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    # ── Public ────────────────────────────────────────────────────────────────
    path('<slug:slug>/bracket/', views.bracket_view, name='bracket'),
    path('<slug:slug>/schedule/', views.schedule_view, name='schedule'),
    path('<slug:slug>/leaderboard/', views.tournament_leaderboard_view, name='tournament_leaderboard'),
    path('<slug:slug>/results/', views.results_view, name='results'),

    # ── Admin ─────────────────────────────────────────────────────────────────
    path('<slug:slug>/generate-bracket/', views.generate_bracket, name='generate_bracket'),
    path('<slug:slug>/admin/update-match/', views.admin_update_match_view, name='admin_update_match'),
    path('<slug:slug>/admin/slots/', views.admin_create_slots_view, name='admin_slots'),
    path('<slug:slug>/admin/assign-slot/', views.admin_assign_slot_view, name='admin_assign_slot'),
]
