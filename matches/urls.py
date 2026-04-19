"""Matches URLs"""
from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('<slug:slug>/bracket/', views.bracket_view, name='bracket'),
    path('<slug:slug>/generate-bracket/', views.generate_bracket, name='generate_bracket'),
    path('result/<int:match_id>/update/', views.update_match_result, name='update_result'),
]
