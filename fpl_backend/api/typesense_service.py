# api/typesense_service.py
import typesense
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TypesenseService:
    def __init__(self):
        self.client = typesense.Client(settings.TYPESENSE_CONFIG)
        self.collection_name = 'fplmanagers'
        
    def get_client(self):
        """Get the Typesense client instance"""
        return self.client
    
    def create_collection_if_not_exists(self):
        """Create the FPL users collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.collections.retrieve()
            collection_names = [col['name'] for col in collections]
            
            if self.collection_name not in collection_names:
                # Create the collection
                schema = {
                    'name': self.collection_name,
                    'fields': [
                        {'name': 'player_name', 'type': 'string'},
                        {'name': 'team_name', 'type': 'string'},
                        {'name': 'player_id', 'type': 'int32'},
                        {'name': 'full_name', 'type': 'string'},
                        {'name': 'created_at', 'type': 'int64'}
                    ]
                }
                self.client.collections.create(schema)
                logger.info(f"Created Typesense collection: {self.collection_name}")
            else:
                logger.info(f"Typesense collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating Typesense collection: {e}")
            raise
    
    def search_player(self, player_name, team_name):
        """Search for a player in Typesense"""
        try:
            self.create_collection_if_not_exists()
            logger.info(f"Searching for player: '{player_name}' in team: '{team_name}'")
            
            # Try multiple search strategies
            search_strategies = [
                {'q': f'{player_name} {team_name}', 'query_by': 'manager_name,squad_name', 'per_page': 10},
                {'q': f'{player_name}', 'query_by': 'manager_name', 'per_page': 10},
                {'q': f'{team_name}', 'query_by': 'squad_name', 'per_page': 10}
            ]
            
            for i, search_parameters in enumerate(search_strategies):
                search_result = self.client.collections[self.collection_name].documents.search(search_parameters)
                
                if search_result['hits']:
                    # Look for exact match first
                    for hit in search_result['hits']:
                        player_data = hit['document']
                        if (player_data.get('manager_name', '').lower() == player_name.lower() and 
                            player_data.get('squad_name', '').lower() == team_name.lower()):
                            logger.info(f"Exact match found for {player_name} in {team_name}")
                            return hit.get('document', {}).get('id') or hit.get('id')
                    
                    # If no exact match on first strategy, return first result
                    if i == 0:
                        logger.info(f"Returning first match for {player_name} in {team_name}")
                        return search_result['hits'][0].get('document', {}).get('id') or search_result['hits'][0].get('id')
            
            logger.info(f"No player found for {player_name} in {team_name}")
            return None
                
        except Exception as e:
            logger.error(f"Error searching player in Typesense: {e}")
            return None
    
    def get_autocomplete_suggestions(self, query, field='both'):
        try:
            self.create_collection_if_not_exists()
            if field == 'team':
                search_parameters = {'q': query, 'query_by': 'squad_name', 'per_page': 20}
            elif field == 'name':
                search_parameters = {'q': query, 'query_by': 'manager_name', 'per_page': 20}
            else:
                search_parameters = {'q': query, 'query_by': 'manager_name,squad_name', 'per_page': 20}

            search_result = self.client.collections[self.collection_name].documents.search(search_parameters)
            suggestions = []
            seen_teams = set()
            seen_names = set()

            for hit in search_result['hits']:
                player_data = hit['document']
                manager_name = player_data.get('manager_name', '')
                squad_name = player_data.get('squad_name', '')

                if field in ['team', 'both'] and squad_name and squad_name not in seen_teams:
                    suggestions.append({'type': 'team', 'value': squad_name, 'display': squad_name})
                    seen_teams.add(squad_name)
                if field in ['name', 'both'] and manager_name and manager_name not in seen_names:
                    suggestions.append({'type': 'name', 'value': manager_name, 'display': manager_name})
                    seen_names.add(manager_name)
            return suggestions[:10]
        except Exception as e:
            logger.error(f"Error getting autocomplete suggestions: {e}")
            return []

# Global instance
typesense_service = TypesenseService()
