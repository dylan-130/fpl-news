# api/services.py
import aiohttp
import logging
from .typesense_service import typesense_service

logger = logging.getLogger(__name__)

async def get_player_id_from_api(player_name, team_name):
    """
    Get player ID from Typesense Cloud instead of AWS API
    """
    try:
        # Search for the player in Typesense
        player_id = typesense_service.search_player(player_name, team_name)
        
        if player_id:
            logger.info(f"Found player ID {player_id} for {player_name} in {team_name}")
            return player_id
        else:
            logger.warning(f"No player found for {player_name} in {team_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching player ID from Typesense: {e}")
        return None

async def get_current_event():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Check if the response is successful
                if not response.ok:
                    logger.error(f"Failed to fetch bootstrap-static data. Status: {response.status}")
                    return None

                data = await response.json()

                # Find the current event
                current_event = next((event for event in data['events'] if event['is_current']), None)
                if not current_event:
                    logger.error("No current event found in bootstrap-static response.")
                    return None

                logger.info(f"Current event found: {current_event['id']}")
                return current_event

    except Exception as e:
        logger.error(f"Error fetching current event: {e}")
        return None
    
async def get_team_data(player_id, gameweek):
    url = f'https://fantasy.premierleague.com/api/entry/{player_id}/event/{gameweek}/picks/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Check if response is successful
                if response.status != 200:
                    logger.error(f"FPL API Error: Status {response.status} for player {player_id}, GW {gameweek}")
                    return None
                data = await response.json()
                logger.info(f"Fetched team data: {data}")
                if 'picks' not in data:
                    logger.error(f"No 'picks' in response for player {player_id}, GW {gameweek}")
                    return None
                
                # Fetch additional player details from bootstrap-static
                bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
                async with session.get(bootstrap_url) as bootstrap_response:
                    if bootstrap_response.status != 200:
                        logger.error(f"Failed to fetch bootstrap data. Status: {bootstrap_response.status}")
                        return None
                    
                    bootstrap_data = await bootstrap_response.json()
                    players = {p['id']: p for p in bootstrap_data['elements']}
                    teams = {t['id']: t for t in bootstrap_data['teams']}

                team_data = []
                for pick in data['picks']:
                    player = players.get(pick['element'], {})
                    team_data.append({
                        'id': pick['element'],
                        'name': player.get('web_name', 'Unknown'),
                        'position': pick['position'],
                        'element_type': player.get('element_type', 1),
                        'points': player.get('event_points', 0),
                        'is_captain': pick['is_captain'],
                        'is_vice_captain': pick['is_vice_captain'],
                        'multiplier': pick['multiplier'],
                        'team_name': teams.get(player.get('team', 0), {}).get('short_name', '')
                    })
                return team_data
    except Exception as e:
        logger.error(f"Error in get_team_data: {e}")
        return None