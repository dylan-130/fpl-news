# api/ml_models.py
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BetGenerator:
    def __init__(self):
        self.player_profiles = self._load_player_profiles()
        self.user_betting_history = self._load_user_history()
        self.bet_types = {
            'goal_scorer': {'base_odds': 2.0, 'multiplier': 1.2},  # Evens
            'assist': {'base_odds': 2.5, 'multiplier': 1.3},       # 3/2 shot
            'clean_sheet': {'base_odds': 1.8, 'multiplier': 1.1},  # 4/5 shot
            'shots_on_target': {'base_odds': 1.5, 'multiplier': 1.1}, # 1/2 shot
            'multiple_goals': {'base_odds': 4.0, 'multiplier': 1.4}, # 3/1 shot
            'man_of_match': {'base_odds': 3.5, 'multiplier': 1.3},  # 5/2 shot
            'yellow_card': {'base_odds': 2.2, 'multiplier': 1.2},   # 6/5 shot
            'over_goals': {'base_odds': 1.6, 'multiplier': 1.1}     # 3/5 shot
        }
        
    def _load_player_profiles(self) -> Dict[str, Dict]:
        """Load player performance profiles from FPL data"""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll use a simplified profile system
            return {
                'high_profile': {
                    'goal_probability': 0.25,
                    'assist_probability': 0.20,
                    'bonus_probability': 0.30,
                    'form_multiplier': 1.5
                },
                'mid_profile': {
                    'goal_probability': 0.15,
                    'assist_probability': 0.15,
                    'bonus_probability': 0.20,
                    'form_multiplier': 1.2
                },
                'low_profile': {
                    'goal_probability': 0.08,
                    'assist_probability': 0.10,
                    'bonus_probability': 0.12,
                    'form_multiplier': 1.0
                }
            }
        except Exception as e:
            logger.error(f"Error loading player profiles: {e}")
            return {}

    def _load_user_history(self) -> Dict[str, List]:
        """Load user betting history for personalization"""
        try:
            # Use absolute path to ensure file is saved in the correct location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            history_file = os.path.join(current_dir, 'user_betting_history.json')
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded user history from {history_file}: {len(data)} users")
                    return data
            else:
                logger.info(f"No existing user history file found at {history_file}")
            return {}
        except Exception as e:
            logger.error(f"Error loading user history: {e}")
            return {}

    def _save_user_history(self):
        """Save user betting history"""
        try:
            # Use absolute path to ensure file is saved in the correct location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            history_file = os.path.join(current_dir, 'user_betting_history.json')
            
            with open(history_file, 'w') as f:
                json.dump(self.user_betting_history, f, indent=2)
            
            logger.info(f"Saved user history to {history_file}: {len(self.user_betting_history)} users")
        except Exception as e:
            logger.error(f"Error saving user history: {e}")

    def analyze_team_composition(self, team_data: List[Dict]) -> Dict[str, Any]:
        """Analyze team composition to determine betting strategy"""
        analysis = {
            'captain': None,
            'vice_captain': None,
            'high_profile_players': [],
            'defensive_players': [],
            'attacking_players': [],
            'team_strength': 0
        }
        
        for player in team_data:
            # Identify captain and vice captain
            if player.get('is_captain'):
                analysis['captain'] = player
            elif player.get('is_vice_captain'):
                analysis['vice_captain'] = player
            
            # Categorize players by position and profile
            element_type = player.get('element_type', 1)
            player_name = player.get('name', '').lower()
            
            # Determine player profile based on name and position
            profile = self._determine_player_profile(player_name, element_type)
            
            if profile == 'high_profile':
                analysis['high_profile_players'].append(player)
            elif element_type == 2:  # Defenders
                analysis['defensive_players'].append(player)
            elif element_type in [3, 4]:  # Midfielders and Forwards
                analysis['attacking_players'].append(player)
        
        # Calculate team strength
        analysis['team_strength'] = len(analysis['high_profile_players']) * 2 + \
                                   len(analysis['attacking_players']) + \
                                   len(analysis['defensive_players']) * 0.5
        
        return analysis

    def _determine_player_profile(self, player_name: str, position: int) -> str:
        """Determine player profile based on name recognition and position"""
        high_profile_names = [
            'salah', 'haaland', 'kane', 'de bruyne', 'bruno', 'son', 'rashford',
            'saka', 'martinelli', 'odegaard', 'palmer', 'foden', 'grealish',
            'van dijk', 'dias', 'stones', 'walker', 'alisson', 'ederson'
        ]
        
        if any(name in player_name for name in high_profile_names):
            return 'high_profile'
        elif position == 1:  # Goalkeepers
            return 'mid_profile'
        else:
            return 'low_profile'

    def generate_bet_suggestions(self, team_data: List[Dict], player_id: str, luck_level: int = 0) -> Dict[str, Any]:
        """Generate personalized bet suggestions based on team analysis"""
        analysis = self.analyze_team_composition(team_data)
        user_history = self.user_betting_history.get(player_id, [])
        
        # Determine baseline odds based on user history
        baseline_odds = self._calculate_baseline_odds(user_history)
        
        # Generate bet legs with luck-based player selection
        bet_legs = []
        total_odds = 1.0
        
        # Select players based on luck level
        selected_players = self._select_players_by_luck(team_data, analysis, luck_level)
        
        # Captain bet (highest confidence)
        if selected_players.get('captain'):
            captain_leg = self._create_captain_bet(selected_players['captain'], luck_level, baseline_odds)
            bet_legs.append(captain_leg)
            total_odds *= captain_leg['odds']
        
        # Vice captain bet
        if selected_players.get('vice_captain'):
            vc_leg = self._create_vice_captain_bet(selected_players['vice_captain'], luck_level, baseline_odds)
            bet_legs.append(vc_leg)
            total_odds *= vc_leg['odds']
        
        # High profile player bets
        for player in selected_players.get('high_profile', [])[:2]:  # Limit to 2 high profile bets
            if player not in [selected_players.get('captain'), selected_players.get('vice_captain')]:
                high_profile_leg = self._create_high_profile_bet(player, luck_level, baseline_odds)
                bet_legs.append(high_profile_leg)
                total_odds *= high_profile_leg['odds']
        
        # Defensive bet (yellow card)
        if selected_players.get('defensive'):
            defensive_leg = self._create_defensive_bet([selected_players['defensive']], luck_level, baseline_odds)
            bet_legs.append(defensive_leg)
            total_odds *= defensive_leg['odds']
        
        # Attacking bet
        if selected_players.get('attacking'):
            attacking_leg = self._create_attacking_bet([selected_players['attacking']], luck_level, baseline_odds)
            bet_legs.append(attacking_leg)
            total_odds *= attacking_leg['odds']
        
        # Ensure we have 4-6 legs
        while len(bet_legs) < 4 and len(selected_players.get('extra', [])) > 0:
            extra_player = selected_players['extra'].pop(0)
            extra_leg = self._create_extra_bet(extra_player, luck_level, baseline_odds)
            bet_legs.append(extra_leg)
            total_odds *= extra_leg['odds']
        
        return {
            'bet_legs': bet_legs,
            'total_odds': total_odds,
            'team_analysis': analysis,
            'luck_level': luck_level
        }

    def _select_players_by_luck(self, team_data: List[Dict], analysis: Dict, luck_level: int) -> Dict[str, Any]:
        """Select different players based on luck level"""
        selected = {}
        
        # Sort players by risk level (higher luck = riskier players)
        all_players = team_data.copy()
        
        # For higher luck levels, prioritize players with higher odds potential
        if luck_level > 0:
            # Sort by potential for higher odds (lower profile players, attacking positions)
            all_players.sort(key=lambda x: (
                self._determine_player_profile(x['name'].lower(), x.get('element_type', 1)) != 'high_profile',
                x.get('element_type', 1) in [3, 4],  # Midfielders and forwards first
                x.get('total_points', 0)  # Lower points = higher odds
            ))
            
            # For each luck level, shift the player selection to get different players
            # This ensures every click of "I'm Feeling Lucky!" gives different players
            shift_amount = luck_level * 2  # Shift by 2 positions per luck level
            if shift_amount > 0:
                # Rotate the player list to get different selections
                all_players = all_players[shift_amount:] + all_players[:shift_amount]
        else:
            # For lower luck levels, prioritize safer players
            all_players.sort(key=lambda x: (
                self._determine_player_profile(x['name'].lower(), x.get('element_type', 1)) == 'high_profile',
                x.get('total_points', 0),  # Higher points = safer
                x.get('element_type', 1)  # Goalkeepers and defenders first
            ))
            
            # For negative luck levels, also shift to get different safe players
            shift_amount = abs(luck_level) * 2
            if shift_amount > 0:
                all_players = all_players[shift_amount:] + all_players[:shift_amount]
        
        # Select captain based on luck level
        if analysis['captain']:
            if luck_level > 0:
                # For higher luck, choose a riskier captain from the shifted list
                riskier_captains = [p for p in all_players if p.get('element_type', 1) in [3, 4]]
                selected['captain'] = riskier_captains[0] if riskier_captains else all_players[0]
            else:
                # For lower luck, choose from the shifted safe players
                safe_captains = [p for p in all_players if self._determine_player_profile(p['name'].lower(), p.get('element_type', 1)) == 'high_profile']
                selected['captain'] = safe_captains[0] if safe_captains else all_players[0]
        
        # Select vice captain
        if analysis['vice_captain']:
            if luck_level > 0:
                # For higher luck, choose a different riskier player
                available_players = [p for p in all_players if p != selected.get('captain')]
                selected['vice_captain'] = available_players[0] if available_players else all_players[1] if len(all_players) > 1 else selected.get('captain')
            else:
                # For lower luck, choose a different safe player
                available_players = [p for p in all_players if p != selected.get('captain')]
                selected['vice_captain'] = available_players[0] if available_players else all_players[1] if len(all_players) > 1 else selected.get('captain')
        
        # Select high profile players
        high_profile_available = [p for p in all_players 
                                if p not in [selected.get('captain'), selected.get('vice_captain')]
                                and self._determine_player_profile(p['name'].lower(), p.get('element_type', 1)) == 'high_profile']
        selected['high_profile'] = high_profile_available[:2]
        
        # Select defensive player
        defensive_available = [p for p in all_players 
                             if p not in [selected.get('captain'), selected.get('vice_captain')] + selected.get('high_profile', [])
                             and p.get('element_type', 1) == 2]
        if defensive_available:
            selected['defensive'] = defensive_available[0]
        
        # Select attacking player
        attacking_available = [p for p in all_players 
                             if p not in [selected.get('captain'), selected.get('vice_captain')] + selected.get('high_profile', [])
                             and p.get('element_type', 1) in [3, 4]]
        if attacking_available:
            selected['attacking'] = attacking_available[0]
        
        # Extra players for filling up the bet
        used_players = [selected.get('captain'), selected.get('vice_captain')] + selected.get('high_profile', []) + [selected.get('defensive'), selected.get('attacking')]
        extra_players = [p for p in all_players if p not in used_players and p is not None]
        selected['extra'] = extra_players
        
        return selected

    def _calculate_baseline_odds(self, user_history: List[Dict]) -> float:
        """Calculate baseline odds based on user's betting history"""
        if not user_history:
            return 1.2  # Very low odds for new users - 1/5 shot
        
        # Calculate average luck level from recent bets to understand user preference
        recent_bets = user_history[-10:]  # Last 10 bets
        if recent_bets:
            avg_luck_level = float(np.mean([bet.get('luck_level', 0) for bet in recent_bets]))
            
            # Adjust baseline based on user's luck preference
            if avg_luck_level > 0:
                # User prefers higher odds - start with higher baseline
                baseline = 1.2 + (avg_luck_level * 0.3)
            elif avg_luck_level < 0:
                # User prefers lower odds - start with lower baseline
                baseline = 1.2 + (avg_luck_level * 0.2)
            else:
                # User stays neutral - moderate baseline
                baseline = 1.5
            
            return max(1.1, min(6.0, baseline))
        
        return 1.2

    def _create_captain_bet(self, player: Dict, luck_level: int, baseline_odds: float) -> Dict:
        """Create a bet for the captain"""
        profile = self._determine_player_profile(player['name'].lower(), player.get('element_type', 1))
        position = player.get('element_type', 1)
        
        # Choose appropriate bet type based on position
        if position == 1:  # Goalkeeper
            bet_type = 'Clean Sheet'
            base_odds = 1.5  # 1/2 shot
        elif position == 2:  # Defender
            bet_type = 'Yellow Card'
            base_odds = 2.0  # Evens
        else:  # Midfielder or Forward
            bet_type = 'Goal Scorer (Captain)'
            base_odds = 1.8  # 4/5 shot
        
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"captain_{player['id']}",
            'player': player['name'],
            'team': player.get('team_name', 'Unknown'),
            'betType': bet_type,
            'odds': adjusted_odds,
            'confidence': 'High'
        }

    def _create_vice_captain_bet(self, player: Dict, luck_level: int, baseline_odds: float) -> Dict:
        """Create a bet for the vice captain"""
        profile = self._determine_player_profile(player['name'].lower(), player.get('element_type', 1))
        position = player.get('element_type', 1)
        
        # Choose appropriate bet type based on position
        if position == 1:  # Goalkeeper
            bet_type = 'Clean Sheet'
            base_odds = 1.6  # 3/5 shot
        elif position == 2:  # Defender
            bet_type = 'Yellow Card'
            base_odds = 2.2  # 6/5 shot
        else:  # Midfielder or Forward
            bet_type = 'Assist (Vice Captain)'
            base_odds = 2.0  # Evens
        
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"vc_{player['id']}",
            'player': player['name'],
            'team': player.get('team_name', 'Unknown'),
            'betType': bet_type,
            'odds': adjusted_odds,
            'confidence': 'Medium-High'
        }

    def _create_high_profile_bet(self, player: Dict, luck_level: int, baseline_odds: float) -> Dict:
        """Create a bet for high profile players"""
        profile = self._determine_player_profile(player['name'].lower(), player.get('element_type', 1))
        position = player.get('element_type', 1)
        
        # Choose appropriate bet type based on position
        if position == 1:  # Goalkeeper
            bet_type = 'Clean Sheet'
            base_odds = 1.7  # 7/10 shot
        elif position == 2:  # Defender
            bet_type = 'Yellow Card'
            base_odds = 2.5  # 3/2 shot
        else:  # Midfielder or Forward
            bet_type = 'Goal Scorer'
            base_odds = 2.2  # 6/5 shot
        
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"high_{player['id']}",
            'player': player['name'],
            'team': player.get('team_name', 'Unknown'),
            'betType': bet_type,
            'odds': adjusted_odds,
            'confidence': 'Medium'
        }

    def _create_defensive_bet(self, defenders: List[Dict], luck_level: int, baseline_odds: float) -> Dict:
        """Create a defensive bet (yellow card)"""
        # Use the highest profile defender
        best_defender = max(defenders, key=lambda x: self._determine_player_profile(x['name'].lower(), x.get('element_type', 1)) == 'high_profile')
        
        base_odds = self.bet_types['yellow_card']['base_odds']
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"def_{best_defender['id']}",
            'player': best_defender['name'],
            'team': best_defender.get('team_name', 'Unknown'),
            'betType': 'Yellow Card',
            'odds': adjusted_odds,
            'confidence': 'Medium'
        }

    def _create_attacking_bet(self, attackers: List[Dict], luck_level: int, baseline_odds: float) -> Dict:
        """Create an attacking bet"""
        # Use the highest profile attacker
        best_attacker = max(attackers, key=lambda x: self._determine_player_profile(x['name'].lower(), x.get('element_type', 1)) == 'high_profile')
        
        base_odds = self.bet_types['assist']['base_odds']
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"att_{best_attacker['id']}",
            'player': best_attacker['name'],
            'team': best_attacker.get('team_name', 'Unknown'),
            'betType': 'Assist',
            'odds': adjusted_odds,
            'confidence': 'Medium'
        }

    def _create_extra_bet(self, player: Dict, luck_level: int, baseline_odds: float) -> Dict:
        """Create an extra bet for remaining players"""
        profile = self._determine_player_profile(player['name'].lower(), player.get('element_type', 1))
        position = player.get('element_type', 1)
        
        # Choose bet type based on position and profile
        if position == 1:  # Goalkeeper
            bet_type = 'Clean Sheet'
            base_odds = 1.8  # 4/5 shot
        elif position == 2:  # Defender
            bet_type = 'Yellow Card'
            base_odds = 2.8  # 9/5 shot
        elif position == 3:  # Midfielder
            if profile == 'high_profile':
                bet_type = 'Assist'
                base_odds = 2.5  # 3/2 shot
            else:
                bet_type = 'Shots on Target'
                base_odds = 1.6  # 3/5 shot
        else:  # Forward
            if profile == 'high_profile':
                bet_type = 'Goal Scorer'
                base_odds = 2.5  # 3/2 shot
            else:
                bet_type = 'Shots on Target'
                base_odds = 1.8  # 4/5 shot
        
        adjusted_odds = self._adjust_odds_for_luck(base_odds, luck_level, baseline_odds)
        
        return {
            'id': f"extra_{player['id']}",
            'player': player['name'],
            'team': player.get('team_name', 'Unknown'),
            'betType': bet_type,
            'odds': adjusted_odds,
            'confidence': 'Low-Medium'
        }

    def _adjust_odds_for_luck(self, base_odds: float, luck_level: int, baseline_odds: float) -> float:
        """Adjust odds based on luck level and user history"""
        # Simplified odds adjustment - more predictable and realistic
        if luck_level > 0:
            # Feeling lucky - increase odds by 20% per level
            adjusted_odds = base_odds * (1 + (luck_level * 0.2))
        elif luck_level < 0:
            # Not feeling lucky - decrease odds by 15% per level
            adjusted_odds = base_odds * (1 + (luck_level * 0.15))
        else:
            # Neutral - use base odds
            adjusted_odds = base_odds
        
        # Apply user history baseline adjustment
        # If user prefers higher odds, increase baseline
        # If user prefers lower odds, decrease baseline
        user_history_multiplier = baseline_odds / 1.2  # Normalize to default baseline
        adjusted_odds = adjusted_odds * user_history_multiplier
        
        # Clamp to reasonable range
        min_odds = 1.1
        max_odds = 8.0 if luck_level > 0 else 5.0
        
        return max(min_odds, min(max_odds, adjusted_odds))

    def get_user_history(self, player_id: str) -> List[Dict]:
        """Get betting history for a specific user (for debugging)"""
        return self.user_betting_history.get(player_id, [])
    
    def reload_history(self):
        """Reload user history from file (for debugging)"""
        self.user_betting_history = self._load_user_history()
        logger.info(f"Reloaded user history: {len(self.user_betting_history)} users")

    def record_bet(self, player_id: str, bet_data: Dict):
        """Record a bet in user history for learning"""
        logger.info(f"Recording bet for player {player_id}")
        logger.info(f"Bet data: {bet_data}")
        
        if player_id not in self.user_betting_history:
            self.user_betting_history[player_id] = []
            logger.info(f"Created new history for player {player_id}")
        
        bet_record = {
            'timestamp': datetime.now().isoformat(),
            'total_odds': bet_data.get('total_odds', 1.0),
            'luck_level': bet_data.get('luck_level', 0),
            'stake': bet_data.get('total_stake', 0),
            'potential_win': bet_data.get('potential_win', 0),
            'legs_count': len(bet_data.get('legs', [])),
            'bet_id': bet_data.get('bet_id', 'unknown')
        }
        
        self.user_betting_history[player_id].append(bet_record)
        logger.info(f"Added bet record: {bet_record}")
        
        # Keep only last 50 bets per user
        if len(self.user_betting_history[player_id]) > 50:
            self.user_betting_history[player_id] = self.user_betting_history[player_id][-50:]
            logger.info(f"Trimmed history for player {player_id} to 50 bets")
        
        # Save immediately after recording
        self._save_user_history()
        logger.info(f"Recorded bet for player {player_id}: {bet_record}")
        logger.info(f"Total bets for player {player_id}: {len(self.user_betting_history[player_id])}")

# Global instance
bet_generator = BetGenerator() 