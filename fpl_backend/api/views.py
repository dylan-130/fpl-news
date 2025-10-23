# api/views.py
import logging
import json
import uuid
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import get_player_id_from_api, get_current_event, get_team_data, get_player_leagues, get_league_standings, get_player_transfers, get_player_captain_chips
from .ml_models import bet_generator
from .typesense_service import typesense_service
from .news_generator import NewsGenerator

# Logger to monitor the process
logger = logging.getLogger(__name__)

# Home endpoint for basic checks
def home(request):
    return HttpResponse(content="Welcome to the FPL API!", content_type="text/plain")

# View to get player ID
@csrf_exempt
async def get_player_id(request):
    player_name = request.GET.get('playerName')
    team_name = request.GET.get('teamName')

    if not player_name or not team_name:
        return JsonResponse({'error': 'Missing playerName or teamName'}, status=400)

    player_id = await get_player_id_from_api(player_name, team_name)

    if player_id is None:
        return JsonResponse({'error': 'Player ID not found'}, status=404)

    return JsonResponse({'player_id': player_id})

# View to get team data (player_id is now passed in)
@csrf_exempt
async def async_get_team_data(request):
    player_id = request.GET.get('playerId')

    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)

    # Fetch the current event (gameweek)
    current_event = await get_current_event()

    if not current_event:
        # Return error if current event cannot be fetched
        return JsonResponse({'error': 'Could not fetch current event.'}, status=500)
    
    gameweek = current_event['id']
    logger.info(f"Fetched current event: {current_event}, gameweek: {gameweek}")

    # Fetch the team data based on player ID and gameweek
    team_response = await get_team_data(player_id, gameweek)

    if not team_response:
        # Return error if no team data is found
        return JsonResponse({'error': 'Team data not found.'}, status=404)

    team_data = team_response['team_data']
    active_chip = team_response.get('active_chip')
    automatic_subs = team_response.get('automatic_subs', [])

    # Add gameweek to each player
    for player in team_data:
        player['event'] = gameweek

    # Handle captain/vice-captain logic and point doubling
    captain_playing = False
    vice_captain_playing = False
    
    # First pass: check if captain and vice-captain are playing (have points > 0)
    for player in team_data:
        if player.get('is_captain') and player.get('points', 0) > 0:
            captain_playing = True
        if player.get('is_vice_captain') and player.get('points', 0) > 0:
            vice_captain_playing = True

    # Second pass: apply captain logic
    for player in team_data:
        # If captain is not playing and vice-captain is playing, make vice-captain the captain
        if not captain_playing and vice_captain_playing and player.get('is_vice_captain'):
            player['is_captain'] = True
            player['is_vice_captain'] = False
            player['multiplier'] = 2
            player['points'] = player.get('points', 0) * 2
            logger.info(f"Vice-captain {player['name']} promoted to captain due to captain not playing")
        # If player has multiplier 2 (captain), double their points
        elif player.get('multiplier') == 2:
            current_points = player.get('points', 0)
            player['points'] = current_points * 2
            if not player.get('is_captain'):
                player['is_captain'] = True
                player['is_vice_captain'] = False
            logger.info(f"Captain {player['name']} points doubled from {current_points} to {player['points']}")

    # Calculate total points (excluding bench unless bench boost is active)
    bench_boost_active = active_chip == 'bboost'
    total_points = 0
    
    for player in team_data:
        # Only count points from starting 11 unless bench boost is active
        if player['position'] <= 11 or bench_boost_active:
            total_points += player.get('points', 0)

    logger.info(f"Total points calculated: {total_points} (bench boost active: {bench_boost_active})")

    return JsonResponse({
        'team_data': team_data,
        'total_points': total_points,
        'active_chip': active_chip,
        'bench_boost_active': bench_boost_active,
        'gameweek': gameweek
    })

# View to generate bet suggestions
@csrf_exempt
async def generate_bet_suggestions(request):
    player_id = request.GET.get('playerId')
    luck_level = int(request.GET.get('luckLevel', 0))

    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)

    try:
        # Fetch team data first
        current_event = await get_current_event()
        if not current_event:
            return JsonResponse({'error': 'Could not fetch current event.'}, status=500)
        
        gameweek = current_event['id']
        team_response = await get_team_data(player_id, gameweek)
        
        if not team_response:
            return JsonResponse({'error': 'Team data not found.'}, status=404)

        team_data = team_response['team_data']
        active_chip = team_response.get('active_chip')

        # Apply same captain logic as in async_get_team_data
        captain_playing = False
        vice_captain_playing = False
        
        for player in team_data:
            if player.get('is_captain') and player.get('points', 0) > 0:
                captain_playing = True
            if player.get('is_vice_captain') and player.get('points', 0) > 0:
                vice_captain_playing = True

        for player in team_data:
            if not captain_playing and vice_captain_playing and player.get('is_vice_captain'):
                player['is_captain'] = True
                player['is_vice_captain'] = False
                player['multiplier'] = 2
                player['points'] = player.get('points', 0) * 2
            elif player.get('multiplier') == 2:
                player['points'] = player.get('points', 0) * 2
                if not player.get('is_captain'):
                    player['is_captain'] = True
                    player['is_vice_captain'] = False

        # Generate bet suggestions using ML
        bet_suggestions = bet_generator.generate_bet_suggestions(
            team_data, player_id, luck_level
        )

        logger.info(f"Generated bet suggestions for player {player_id} with luck level {luck_level}")
        
        return JsonResponse({
            'bet_legs': bet_suggestions['bet_legs'],
            'total_odds': bet_suggestions['total_odds'],
            'team_data': team_data,
            'luck_level': luck_level
        })

    except Exception as e:
        logger.error(f"Error generating bet suggestions: {e}")
        return JsonResponse({'error': 'Failed to generate bet suggestions.'}, status=500)

# View to adjust odds based on luck level
@csrf_exempt
async def adjust_odds(request):
    player_id = request.GET.get('playerId')
    luck_level = int(request.GET.get('luckLevel', 0))

    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)

    try:
        # Fetch team data
        current_event = await get_current_event()
        if not current_event:
            return JsonResponse({'error': 'Could not fetch current event.'}, status=500)
        
        gameweek = current_event['id']
        team_response = await get_team_data(player_id, gameweek)
        
        if not team_response:
            return JsonResponse({'error': 'Team data not found.'}, status=404)

        team_data = team_response['team_data']
        active_chip = team_response.get('active_chip')

        # Apply same captain logic as in async_get_team_data
        captain_playing = False
        vice_captain_playing = False
        
        for player in team_data:
            if player.get('is_captain') and player.get('points', 0) > 0:
                captain_playing = True
            if player.get('is_vice_captain') and player.get('points', 0) > 0:
                vice_captain_playing = True

        for player in team_data:
            if not captain_playing and vice_captain_playing and player.get('is_vice_captain'):
                player['is_captain'] = True
                player['is_vice_captain'] = False
                player['multiplier'] = 2
                player['points'] = player.get('points', 0) * 2
            elif player.get('multiplier') == 2:
                player['points'] = player.get('points', 0) * 2
                if not player.get('is_captain'):
                    player['is_captain'] = True
                    player['is_vice_captain'] = False

        # Generate new bet suggestions with adjusted luck level
        bet_suggestions = bet_generator.generate_bet_suggestions(
            team_data, player_id, luck_level
        )

        logger.info(f"Adjusted odds for player {player_id} to luck level {luck_level}")
        
        return JsonResponse({
            'bet_legs': bet_suggestions['bet_legs'],
            'total_odds': bet_suggestions['total_odds'],
            'luck_level': luck_level
        })

    except Exception as e:
        logger.error(f"Error adjusting odds: {e}")
        return JsonResponse({'error': 'Failed to adjust odds.'}, status=500)

# View to place a bet
@csrf_exempt
@require_http_methods(["POST"])
async def place_bet(request):
    try:
        bet_data = json.loads(request.body)
        player_id = bet_data.get('playerId')
        
        if not player_id:
            return JsonResponse({'error': 'Player ID missing.'}, status=400)

        # Generate unique bet ID
        bet_id = str(uuid.uuid4())
        
        # Record the bet in user history for ML learning
        bet_generator.record_bet(player_id, {
            **bet_data,
            'bet_id': bet_id
        })

        # Create receipt data
        receipt_data = {
            'betId': bet_id,
            'legs': bet_data.get('legs', []),
            'totalOdds': bet_data.get('totalOdds', 1.0),
            'totalStake': bet_data.get('totalStake', 0),
            'potentialWin': bet_data.get('potentialWin', 0),
            'luckLevel': bet_data.get('luckLevel', 0),
            'timestamp': bet_data.get('timestamp', '')
        }

        logger.info(f"Bet placed successfully for player {player_id} with bet ID {bet_id}")
        
        return JsonResponse(receipt_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        return JsonResponse({'error': 'Failed to place bet.'}, status=500)

# Debug endpoint to check user history
@csrf_exempt
async def debug_user_history(request):
    player_id = request.GET.get('playerId')
    
    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)
    
    try:
        # Reload history from file to ensure we have latest data
        bet_generator.reload_history()
        
        # Get user history
        user_history = bet_generator.get_user_history(player_id)
        
        return JsonResponse({
            'player_id': player_id,
            'bet_count': len(user_history),
            'history': user_history,
            'total_users': len(bet_generator.user_betting_history)
        })
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        return JsonResponse({'error': 'Failed to get user history.'}, status=500)

# Endpoint to check if user has betting history
@csrf_exempt
async def user_history(request):
    player_id = request.GET.get('playerId')
    
    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)
    
    try:
        # Get user history
        user_history = bet_generator.get_user_history(player_id)
        
        return JsonResponse({
            'player_id': player_id,
            'bet_count': len(user_history),
            'is_returning_user': len(user_history) > 0
        })
        
    except Exception as e:
        logger.error(f"Error checking user history: {e}")
        return JsonResponse({'error': 'Failed to check user history.'}, status=500)

# Debug endpoint to check ML calculations
@csrf_exempt
async def debug_ml_calculations(request):
    player_id = request.GET.get('playerId')
    luck_level = int(request.GET.get('luckLevel', 0))
    
    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)
    
    try:
        # Get user history
        user_history = bet_generator.get_user_history(player_id)
        
        # Calculate baseline odds
        baseline_odds = bet_generator._calculate_baseline_odds(user_history)
        
        # Get sample bet calculation
        sample_bet = {
            'base_odds': 2.0,  # Goal scorer base
            'luck_level': luck_level,
            'baseline_odds': baseline_odds
        }
        
        # Calculate adjusted odds
        adjusted_odds = bet_generator._adjust_odds_for_luck(
            sample_bet['base_odds'], 
            sample_bet['luck_level'], 
            sample_bet['baseline_odds']
        )
        
        return JsonResponse({
            'player_id': player_id,
            'user_history_count': len(user_history),
            'recent_luck_levels': [bet.get('luck_level', 0) for bet in user_history[-5:]],
            'baseline_odds': baseline_odds,
            'sample_calculation': {
                'base_odds': sample_bet['base_odds'],
                'luck_level': sample_bet['luck_level'],
                'baseline_odds': sample_bet['baseline_odds'],
                'adjusted_odds': adjusted_odds
            }
        })
        
    except Exception as e:
        logger.error(f"Error in ML debug: {e}")
        return JsonResponse({'error': 'Failed to debug ML calculations.'}, status=500)

@csrf_exempt
async def get_autocomplete_suggestions(request):
    query = request.GET.get('q', '').strip()
    field = request.GET.get('field', 'both')
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        suggestions = typesense_service.get_autocomplete_suggestions(query, field)
        return JsonResponse({
            'suggestions': suggestions,
            'query': query,
            'field': field
        })
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {e}")
        return JsonResponse({'error': 'Failed to get suggestions.'}, status=500)

@csrf_exempt
async def get_player_leagues_view(request):
    """Get all leagues for a player"""
    player_id = request.GET.get('playerId')
    
    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)
    
    try:
        leagues = await get_player_leagues(player_id)
        if not leagues:
            return JsonResponse({'error': 'No leagues found.'}, status=404)
        
        return JsonResponse({'leagues': leagues})
    except Exception as e:
        logger.error(f"Error fetching player leagues: {e}")
        return JsonResponse({'error': 'Failed to fetch leagues.'}, status=500)

@csrf_exempt
async def generate_league_news(request):
    """Generate news articles for all player's leagues"""
    player_id = request.GET.get('playerId')
    team_name = request.GET.get('teamName', 'Your Team')
    manager_name = request.GET.get('managerName', 'Manager')
    
    if not player_id:
        return JsonResponse({'error': 'Player ID missing.'}, status=400)
    
    try:
        # Get player's leagues
        leagues = await get_player_leagues(player_id)
        if not leagues:
            return JsonResponse({'error': 'No leagues found.'}, status=404)
        
        # Get current gameweek and team data
        current_event = await get_current_event()
        if not current_event:
            return JsonResponse({'error': 'Could not fetch current event.'}, status=500)
        
        gameweek = current_event['id']
        team_response = await get_team_data(player_id, gameweek)
        
        if not team_response:
            return JsonResponse({'error': 'Team data not found.'}, status=404)
        
        # Generate articles for each league
        news_generator = NewsGenerator()
        articles = []
        
        for league in leagues:
            league_standings = await get_league_standings(league['id'], gameweek)
            transfers_data = await get_player_transfers(player_id, gameweek)
            chips_data = await get_player_captain_chips(player_id, gameweek)
            
            if league_standings:
                article = news_generator.generate_article(
                    league, 
                    {
                        'team_name': team_name,
                        'manager_name': manager_name,
                        'team_data': team_response['team_data'],
                        'active_chip': team_response.get('active_chip')
                    },
                    {'gameweek': gameweek},
                    league_standings,
                    int(player_id),
                    transfers_data,
                    chips_data
                )
                articles.append(article)
        
        return JsonResponse({'articles': articles})
    except Exception as e:
        logger.error(f"Error generating league news: {e}")
        return JsonResponse({'error': 'Failed to generate news.'}, status=500)
