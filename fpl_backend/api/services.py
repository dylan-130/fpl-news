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
                
                return {
                    'team_data': team_data,
                    'active_chip': data.get('active_chip'),
                    'automatic_subs': data.get('automatic_subs', [])
                }
    except Exception as e:
        logger.error(f"Error in get_team_data: {e}")
        return None

async def get_player_leagues(player_id):
    """
    Fetch all leagues a player is involved in, excluding unwanted leagues
    """
    url = f'https://fantasy.premierleague.com/api/entry/{player_id}/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch player leagues. Status: {response.status}")
                    return None
                
                data = await response.json()
                # Extract league information from the response
                all_leagues = data.get('leagues', {}).get('classic', [])
                
                # Filter out unwanted leagues
                unwanted_league_names = [
                    'second chance',
                    'overall',
                    'gameweek 1',
                    'country league',
                    'club league',
                    'supporters league'
                ]
                
                # Also filter by common league name patterns
                unwanted_patterns = [
                    'second chance',
                    'overall',
                    'gameweek',
                    'country',
                    'club',
                    'supporters',
                    'global',
                    'worldwide'
                ]
                
                # Premier League club names to filter out
                premier_league_clubs = [
                    'arsenal', 'aston villa', 'brighton', 'burnley', 'chelsea', 'crystal palace',
                    'everton', 'fulham', 'leeds', 'leicester', 'liverpool', 'manchester city',
                    'manchester united', 'man city', 'man united', 'man utd', 'newcastle',
                    'norwich', 'sheffield', 'southampton', 'tottenham', 'tottenham hotspur',
                    'spurs', 'watford', 'west brom', 'west ham', 'wolves', 'wolverhampton'
                ]
                
                # Country names to filter out
                countries = [
                    'ireland', 'england', 'scotland', 'wales', 'northern ireland', 'spain',
                    'france', 'germany', 'italy', 'portugal', 'netherlands', 'belgium',
                    'brazil', 'argentina', 'mexico', 'usa', 'canada', 'australia', 'japan',
                    'south korea', 'china', 'india', 'nigeria', 'south africa', 'egypt',
                    'morocco', 'tunisia', 'algeria', 'ghana', 'senegal', 'ivory coast',
                    'cameroon', 'kenya', 'uganda', 'tanzania', 'ethiopia', 'sudan',
                    'libya', 'angola', 'mozambique', 'zimbabwe', 'zambia', 'botswana',
                    'namibia', 'lesotho', 'swaziland', 'madagascar', 'mauritius',
                    'seychelles', 'comoros', 'malawi', 'zambia', 'malawi', 'zimbabwe'
                ]
                
                filtered_leagues = []
                for league in all_leagues:
                    league_name = league.get('name', '').lower()
                    
                    # Skip if league name contains any unwanted patterns
                    should_exclude = False
                    for pattern in unwanted_patterns:
                        if pattern in league_name:
                            should_exclude = True
                            break
                    
                    # Skip if it's an exact match with unwanted names
                    if league_name in unwanted_league_names:
                        should_exclude = True
                    
                    # Skip if league name contains any Premier League club names
                    for club in premier_league_clubs:
                        if club in league_name:
                            should_exclude = True
                            break
                    
                    # Skip if league name contains any country names
                    for country in countries:
                        if country in league_name:
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        filtered_leagues.append(league)
                
                logger.info(f"Fetched {len(all_leagues)} total leagues, filtered to {len(filtered_leagues)} leagues for player {player_id}")
                return filtered_leagues
    except Exception as e:
        logger.error(f"Error fetching player leagues: {e}")
        return None

async def get_league_standings(league_id, gameweek=None):
    """
    Fetch league standings and recent results
    """
    url = f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch league standings for {league_id}. Status: {response.status}")
                    return None
                
                data = await response.json()
                logger.info(f"Fetched league standings for league {league_id}")
                return data
    except Exception as e:
        logger.error(f"Error fetching league standings: {e}")
        return None

async def get_player_transfers(player_id, gameweek):
    """
    Fetch player's transfers for a specific gameweek
    """
    url = f'https://fantasy.premierleague.com/api/entry/{player_id}/transfers/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch transfers for player {player_id}. Status: {response.status}")
                    return []
                
                data = await response.json()
                # Filter transfers for the specific gameweek
                gameweek_transfers = [transfer for transfer in data if transfer.get('event') == gameweek]
                logger.info(f"Fetched {len(gameweek_transfers)} transfers for player {player_id} in GW{gameweek}")
                return gameweek_transfers
    except Exception as e:
        logger.error(f"Error fetching transfers: {e}")
        return []

async def get_player_captain_chips(player_id, gameweek):
    """
    Fetch player's captain and chips used for a specific gameweek
    """
    url = f'https://fantasy.premierleague.com/api/entry/{player_id}/event/{gameweek}/picks/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch captain/chips for player {player_id}. Status: {response.status}")
                    return None

                data = await response.json()
                
                # Find captain
                captain = None
                for pick in data.get('picks', []):
                    if pick.get('is_captain'):
                        captain = {
                            'name': pick.get('element', {}).get('web_name', 'Unknown'),
                            'points': pick.get('points', 0)
                        }
                        break
                
                # Get chips used
                chips_used = []
                if data.get('active_chip') == 'wildcard':
                    chips_used.append('Wildcard')
                elif data.get('active_chip') == 'freehit':
                    chips_used.append('Free Hit')
                elif data.get('active_chip') == 'triplecaptain':
                    chips_used.append('Triple Captain')
                elif data.get('active_chip') == 'bboost':
                    chips_used.append('Bench Boost')
                
                logger.info(f"Fetched captain/chips for player {player_id} in GW{gameweek}: Captain={captain}, Chips={chips_used}")
                return {
                    'captain': captain,
                    'chips_used': chips_used
                }
    except Exception as e:
        logger.error(f"Error fetching captain/chips: {e}")
        return None