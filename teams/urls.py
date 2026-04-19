"""Teams URLs"""
from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='list'),
    path('create/', views.create_team, name='create'),
    path('leave/', views.leave_team, name='leave'),
    path('<slug:slug>/', views.team_detail, name='detail'),
    path('<slug:slug>/invite/', views.invite_player, name='invite'),
    path('invite/<int:invite_id>/<str:action>/', views.respond_invite, name='respond_invite'),
]
