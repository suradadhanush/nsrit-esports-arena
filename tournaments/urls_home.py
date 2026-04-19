"""Home URL - root path"""
from django.urls import path
from tournaments.views import home

urlpatterns = [
    path('', home, name='home'),
]
