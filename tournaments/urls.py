"""Tournaments URLs"""
from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.tournament_list, name='list'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    
    path('approve/<int:reg_id>/', views.approve_registration, name='approve_registration'),
    path('reject/<int:reg_id>/', views.reject_registration, name='reject_registration'),
    
    path('<slug:slug>/', views.tournament_detail, name='detail'),
    path('<slug:slug>/register/', views.register_tournament, name='register'),

]
