# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('get_player_id/', views.get_player_id, name='get_player_id'),
    path('async_get_team_data/', views.async_get_team_data, name='async_get_team_data'),
    path('generate_bet_suggestions/', views.generate_bet_suggestions, name='generate_bet_suggestions'),
    path('adjust_odds/', views.adjust_odds, name='adjust_odds'),
    path('place_bet/', views.place_bet, name='place_bet'),
    path('debug_user_history/', views.debug_user_history, name='debug_user_history'),
    path('user_history/', views.user_history, name='user_history'),
    path('debug_ml_calculations/', views.debug_ml_calculations, name='debug_ml_calculations'),
    path('autocomplete/', views.get_autocomplete_suggestions, name='get_autocomplete_suggestions'),
    path('get_player_leagues/', views.get_player_leagues_view, name='get_player_leagues'),
    path('generate_league_news/', views.generate_league_news, name='generate_league_news'),
]