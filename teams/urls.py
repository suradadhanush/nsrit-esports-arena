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
    path('<slug:slug>/join/', views.request_join, name='request_join'),
    path('join-request/<int:request_id>/<str:action>/', views.respond_join_request, name='respond_join_request'),
    path('<slug:slug>/edit/', views.edit_team, name='edit'),
    path('<slug:slug>/kick/<int:member_id>/', views.kick_member, name='kick_member'),
    path('<slug:slug>/transfer/<int:member_id>/', views.transfer_captaincy, name='transfer_captaincy'),
]
