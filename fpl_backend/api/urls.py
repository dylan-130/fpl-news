# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('get_player_id/', views.get_player_id, name='get_player_id'),
    path('async_get_team_data/', views.async_get_team_data, name='async_get_team_data'),
]