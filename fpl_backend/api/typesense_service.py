# api/typesense_service.py
import typesense
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TypesenseService:
    def __init__(self):
        self.client = typesense.Client(settings.TYPESENSE_CONFIG)
        self.collection_name = 'fpl_users'
        
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
            # Create collection if it doesn't exist
            self.create_collection_if_not_exists()
            
            # Search for the player
            search_parameters = {
                'q': f'{player_name} {team_name}',
                'query_by': 'player_name,team_name,full_name',
                'filter_by': f'team_name:={team_name}',
                'per_page': 1
            }
            
            search_result = self.client.collections[self.collection_name].documents.search(search_parameters)
            
            if search_result['hits']:
                player_data = search_result['hits'][0]['document']
                logger.info(f"Found player in Typesense: {player_data}")
                return player_data.get('player_id')
            else:
                logger.info(f"No player found for {player_name} in {team_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching player in Typesense: {e}")
            return None
    

# Global instance
typesense_service = TypesenseService()
