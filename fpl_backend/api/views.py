# api/views.py
import logging
import json
import uuid
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import get_player_id_from_api, get_current_event, get_team_data
from .ml_models import bet_generator
from .typesense_service import typesense_service

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
    team_data = await get_team_data(player_id, gameweek)

    if not team_data:
        # Return error if no team data is found
        return JsonResponse({'error': 'Team data not found.'}, status=404)

    # Return the fetched team data as a JSON response
    return JsonResponse(team_data, safe=False)

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
        team_data = await get_team_data(player_id, gameweek)
        
        if not team_data:
            return JsonResponse({'error': 'Team data not found.'}, status=404)

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
        team_data = await get_team_data(player_id, gameweek)
        
        if not team_data:
            return JsonResponse({'error': 'Team data not found.'}, status=404)

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
