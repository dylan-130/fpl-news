# api/news_generator.py
import random
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self):
        self.templates = {
            'captain_masterstroke': [
                "{team_name} Take Top Spot in {league_name} After {captain_name} Captaincy Masterstroke",
                "{manager_name}'s {captain_name} Gamble Pays Off as {team_name} Climb {league_name}",
                "Captain {captain_name} Delivers as {team_name} Claim {league_name} Lead",
                "{team_name} Soar to Top of {league_name} After {captain_name} Captain Brilliance",
                "{manager_name} Celebrates {captain_name} Masterclass as {team_name} Lead {league_name}"
            ],
            'big_rise': [
                "{team_name} Rocket Up {league_name} After {player_name} Heroics",
                "{manager_name} Celebrates as {team_name} Soar Up {league_name} Standings",
                "Massive Gameweek for {team_name} as They Climb {league_name} Table",
                "{team_name} Make Big Move in {league_name} After {player_name} Stellar Performance",
                "{manager_name}'s {team_name} Climb {league_name} Rankings After {player_name} Magic"
            ],
            'dramatic_fall': [
                "{team_name} Slip Down {league_name} After Disastrous Gameweek",
                "{manager_name} Left Reeling as {team_name} Drop Places in {league_name}",
                "Tough Week for {team_name} as {league_name} Position Slides",
                "{team_name} Struggle in {league_name} as {manager_name} Faces League Drop",
                "Disappointing Gameweek Sees {team_name} Fall Down {league_name} Table"
            ],
            'consistent_performance': [
                "{team_name} Maintain Strong Position in {league_name}",
                "{manager_name}'s {team_name} Hold Steady in {league_name} Race",
                "Solid Gameweek Keeps {team_name} in {league_name} Contention",
                "{team_name} Stay Consistent in {league_name} Battle",
                "{manager_name} Keeps {team_name} Competitive in {league_name}"
            ]
        }
        
        self.article_templates = {
            'captain_masterstroke': [
                "In a masterstroke of tactical genius, {manager_name} made the bold decision to captain {captain_name} this gameweek, and boy did it pay off! {team_name} now sit proudly at the top of {league_name} after {captain_name} delivered a stunning {captain_points} points, proving that sometimes the biggest risks yield the biggest rewards. The fantasy football world is buzzing with this inspired choice, as {manager_name} has shown the tactical nous that separates the great managers from the good ones.",
                
                "The fantasy football world is buzzing after {manager_name}'s inspired captaincy choice. By selecting {captain_name} as captain, {team_name} have rocketed to the summit of {league_name}. {captain_name}'s incredible {captain_points} points this gameweek shows why they're considered one of the game's elite performers. This wasn't just luck - it was a calculated risk that paid dividends, showcasing {manager_name}'s deep understanding of the game and their players' form.",
                
                "What a week for {team_name}! {manager_name}'s decision to captain {captain_name} has been vindicated in spectacular fashion. With {captain_name} racking up an impressive {captain_points} points, {team_name} now lead {league_name} and have sent a clear message to their rivals. The timing couldn't have been better, as this masterclass in captaincy selection has propelled {team_name} to the top of the table. {manager_name} must be feeling like a tactical genius right now.",
                
                "Sometimes in fantasy football, you need to trust your instincts, and {manager_name} did exactly that. The decision to captain {captain_name} was met with some skepticism, but the results speak for themselves. {captain_name}'s {captain_points} points have catapulted {team_name} to the summit of {league_name}, proving that bold moves often lead to the biggest rewards. This is what separates the champions from the also-rans.",
                
                "The art of captaincy selection is one of the most crucial skills in fantasy football, and {manager_name} has mastered it to perfection. By choosing {captain_name} as captain, {team_name} have soared to the top of {league_name} with {captain_name} delivering a magnificent {captain_points} points. This wasn't just a good choice - it was a game-changing decision that has reshaped the entire league table."
            ],
            'big_rise': [
                "What a turnaround for {team_name}! {manager_name} must be absolutely delighted as their team has climbed {position_change} places in {league_name} this gameweek. The standout performance came from {player_name}, who delivered {player_points} points and proved to be the catalyst for this remarkable rise up the table. This kind of momentum shift doesn't happen by accident - it's the result of careful planning, astute transfers, and perfect timing.",
                
                "Fantasy football is all about momentum, and {team_name} have it in spades! {manager_name} has guided their team up {position_change} places in {league_name}, with {player_name} leading the charge with an outstanding {player_points} points. This could be the start of something special for {team_name}, as they've shown they have the quality to compete with the best teams in the league. The rest of the competition will be looking over their shoulders now.",
                
                "The {league_name} table has been shaken up by {team_name}'s incredible gameweek! {manager_name} has seen their team jump {position_change} places, thanks in large part to {player_name}'s magnificent {player_points} points. This kind of performance doesn't come around often, and {team_name} have made the most of it. The league is now wide open, and {team_name} have thrown their hat into the ring as serious contenders.",
                
                "Sometimes a single gameweek can change everything, and that's exactly what happened for {team_name}. {manager_name} has orchestrated a remarkable {position_change}-place climb in {league_name}, with {player_name} delivering a performance for the ages with {player_points} points. This is the kind of week that managers dream about - when everything clicks and your team delivers beyond expectations.",
                
                "The {league_name} has a new force to be reckoned with! {team_name} have stormed up the table with a {position_change}-place climb, and {manager_name} is the architect of this remarkable transformation. {player_name} was the star of the show with {player_points} points, but this was a team effort that showcased the depth and quality of {team_name}'s squad. The league title race just got a lot more interesting."
            ],
            'dramatic_fall': [
                "It's been a week to forget for {team_name} as they've slipped {position_change} places down the {league_name} table. {manager_name} will be hoping this is just a temporary blip, but with their team struggling to find form, they'll need to regroup quickly if they want to climb back up the standings. Every manager knows that fantasy football is a rollercoaster, and this is just one of those dips that every team experiences.",
                
                "The wheels have come off for {team_name} this gameweek as they've dropped {position_change} places in {league_name}. {manager_name} will be scratching their head wondering what went wrong, but in fantasy football, fortunes can change quickly. This is the harsh reality of the game - one bad week can undo weeks of good work. Time to bounce back stronger!",
                
                "A disappointing gameweek for {team_name} sees them fall {position_change} places in {league_name}. {manager_name} will be looking for answers after this setback, but every manager knows that fantasy football is a marathon, not a sprint. The key now is to learn from this experience and come back stronger. There's still plenty of time to turn things around.",
                
                "Sometimes the fantasy football gods are cruel, and this week they've been particularly unkind to {team_name}. A {position_change}-place drop in {league_name} is hard to swallow, but {manager_name} knows that this is part of the game. The best managers are those who can weather the storm and come back fighting. This is just a temporary setback in what promises to be an exciting season.",
                
                "The {league_name} table can be unforgiving, and {team_name} have learned that lesson the hard way this gameweek. A {position_change}-place fall is a bitter pill to swallow, but {manager_name} will be using this as motivation to improve. Every champion has faced adversity, and how you respond to it defines your character. {team_name} will be back stronger."
            ],
            'consistent_performance': [
                "Steady as she goes for {team_name}! {manager_name} has maintained their team's position in {league_name} with another solid gameweek. While they might not have made headlines, consistency is key in fantasy football, and {team_name} are showing they have what it takes to stay competitive. This kind of steady performance often goes unnoticed, but it's the foundation of any successful fantasy campaign.",
                
                "No fireworks this week for {team_name}, but {manager_name} will be pleased with another steady performance that keeps them in the mix in {league_name}. Sometimes the best strategy is to avoid the big mistakes, and {team_name} are doing exactly that. This consistency will serve them well as the season progresses, and they'll be ready to pounce when opportunities arise.",
                
                "Another week, another solid performance from {team_name}. {manager_name} has their team positioned well in {league_name}, and while they might not be grabbing the headlines, they're quietly going about their business and staying in contention. This is the mark of a well-managed team - consistent, reliable, and always in the mix.",
                
                "The {league_name} table shows {team_name} holding their ground, and {manager_name} will be satisfied with another week of steady progress. While other teams are making dramatic moves up and down the table, {team_name} are maintaining their position with the kind of consistency that wins championships. Sometimes the best move is no move at all.",
                
                "Consistency is the name of the game for {team_name}, and {manager_name} has their team performing exactly as they need to in {league_name}. While they haven't made any dramatic moves this gameweek, they've maintained their position and stayed competitive. This kind of steady performance builds confidence and sets the foundation for future success.",
                
                "In a league full of ups and downs, {team_name} are providing the stability that {manager_name} craves. Another week of consistent performance in {league_name} shows that this team has the right formula. While others chase the big scores, {team_name} are building a platform for sustained success. This is smart fantasy football management.",
                
                "The {league_name} table reflects the steady progress that {team_name} have made under {manager_name}'s guidance. While they haven't set the world alight this gameweek, they've done exactly what was needed to maintain their position. This kind of reliability is invaluable in fantasy football, and {team_name} are proving they have what it takes to compete at the highest level."
            ]
        }
    
    def _calculate_position_change(self, league_standings, player_id, current_gameweek):
        """Calculate how many places the player moved in the league"""
        if not league_standings or not league_standings.get('standings'):
            return 0
        
        standings = league_standings['standings']['results']
        
        # Find current position
        current_position = None
        player_entry = None
        for i, entry in enumerate(standings):
            if entry['entry'] == player_id:
                current_position = i + 1  # Position is 1-indexed
                player_entry = entry
                break
        
        if current_position is None or not player_entry:
            return 0
        
        # Get current gameweek points
        current_gameweek_points = player_entry.get('event_total', 0)
        current_total_points = player_entry.get('total', 0)
        
        # Calculate what the total would have been before this gameweek
        previous_total_points = current_total_points - current_gameweek_points
        
        # Create a list of all players with their previous totals for comparison
        previous_standings = []
        for entry in standings:
            other_current_total = entry.get('total', 0)
            other_current_gameweek = entry.get('event_total', 0)
            other_previous_total = other_current_total - other_current_gameweek
            previous_standings.append({
                'entry': entry['entry'],
                'previous_total': other_previous_total,
                'current_total': other_current_total
            })
        
        # Sort by previous total points (descending)
        previous_standings.sort(key=lambda x: x['previous_total'], reverse=True)
        
        # Find where this player would have ranked with previous total points
        previous_position = 1
        for i, standing in enumerate(previous_standings):
            if standing['entry'] == player_id:
                previous_position = i + 1
                break
        
        # Calculate position change (positive = moved up, negative = moved down)
        position_change = previous_position - current_position
        
        logger.info(f"Player {player_id} in GW{current_gameweek}: Previous position {previous_position}, Current position {current_position}, Change: {position_change}")
        
        return position_change
    def _get_position_arrow(self, position_change):
        """Get arrow symbol for position change"""
        if position_change > 0:
            return "↗"  # Up arrow
        elif position_change < 0:
            return "↘"  # Down arrow
        else:
            return "→"  # Level arrow
    
    def _calculate_all_position_changes(self, league_standings, current_gameweek):
        """Calculate position changes for all players in the league"""
        if not league_standings or not league_standings.get('standings'):
            return {}
        
        standings = league_standings['standings']['results']
        position_changes = {}
        
        for entry in standings:
            player_id = entry['entry']
            position_change = self._calculate_position_change(league_standings, player_id, current_gameweek)
            position_changes[player_id] = position_change
        
        return position_changes
    
    def _get_player_position_in_league(self, league_standings, player_id):
        """Get the player's current position in the league"""
        if not league_standings or 'standings' not in league_standings:
            return None
        
        standings = league_standings['standings']['results']
        for i, entry in enumerate(standings):
            if entry['entry'] == player_id:
                return i + 1  # Position is 1-indexed
        return None
    
    def _get_player_total_points(self, league_standings, player_id):
        """Get the player's total points in the league"""
        if not league_standings or 'standings' not in league_standings:
            return 0
        
        standings = league_standings['standings']['results']
        for entry in standings:
            if entry['entry'] == player_id:
                return entry['total']
        return 0
    
    def _analyze_captain_performance(self, team_data):
        """Analyze the captain's performance"""
        captain = None
        for player in team_data:
            if player.get('is_captain'):
                captain = player
                break
        
        if not captain:
            return {'name': 'Unknown', 'points': 0, 'base_points': 0}
        
        # API returns base points, captain gets doubled
        base_points = captain['points']
        captain_points = base_points * 2
        
        return {
            'name': captain['name'],
            'points': captain_points,
            'base_points': base_points
        }
    
    def _get_top_performer(self, team_data):
        """Get the top performing player from the team"""
        if not team_data:
            return 'Unknown Player'
        
        top_player = max(team_data, key=lambda x: x.get('points', 0))
        return top_player['name']
    
    def _analyze_transfers(self, transfers_data, team_data):
        """Analyze transfer activity for the gameweek"""
        if not transfers_data:
            return {
                'transfers_made': 0,
                'transfer_cost': 0,
                'transfers_in': [],
                'transfers_out': [],
                'transfer_summary': 'No transfers made this gameweek.',
                'transfer_analysis': 'The manager decided to stick with their current squad, showing confidence in their selections.'
            }
        
        transfers_in = []
        transfers_out = []
        total_cost = 0
        
        for transfer in transfers_data:
            if transfer.get('element_in'):
                transfers_in.append({
                    'name': transfer.get('element_in_name', 'Unknown'),
                    'cost': transfer.get('element_in_cost', 0)
                })
            if transfer.get('element_out'):
                transfers_out.append({
                    'name': transfer.get('element_out_name', 'Unknown'),
                    'cost': transfer.get('element_out_cost', 0)
                })
            total_cost += transfer.get('cost', 0)
        
        # Find transfer performance by matching names with team data
        transfer_performance = []
        for transfer_in in transfers_in:
            # Find the player in current team data
            for player in team_data:
                if player.get('name') == transfer_in['name']:
                    transfer_performance.append({
                        'name': transfer_in['name'],
                        'points': player.get('points', 0),
                        'cost': transfer_in['cost']
                    })
                    break
        
        # Generate detailed transfer analysis
        if len(transfers_in) == 0:
            transfer_summary = 'No transfers made this gameweek.'
            transfer_analysis = 'The manager decided to stick with their current squad, showing confidence in their selections.'
        elif len(transfers_in) == 1:
            transfer_summary = f"Made 1 transfer: brought in {transfers_in[0]['name']} for {transfers_in[0]['cost']}m."
            if transfer_performance:
                points = transfer_performance[0]['points']
                transfer_analysis = f"Smart move! {transfers_in[0]['name']} delivered {points} points, proving the manager's eye for talent."
            else:
                transfer_analysis = f"Time will tell if {transfers_in[0]['name']} was the right call."
        else:
            transfer_summary = f"Made {len(transfers_in)} transfers, spending {total_cost}m on new players."
            if transfer_performance:
                total_points = sum(tp['points'] for tp in transfer_performance)
                transfer_analysis = f"Bold transfer strategy! The new signings combined for {total_points} points this gameweek."
            else:
                transfer_analysis = f"Ambitious transfer window - let's see how these moves pay off."
        
        return {
            'transfers_made': len(transfers_in),
            'transfer_cost': total_cost,
            'transfers_in': transfers_in,
            'transfers_out': transfers_out,
            'transfer_summary': transfer_summary,
            'transfer_analysis': transfer_analysis,
            'transfer_performance': transfer_performance
        }
    
    def _analyze_chips(self, chips_data):
        """Analyze chips used for the gameweek"""
        if not chips_data:
            return {
                'chips_used': [],
                'chip_summary': 'No chips played this gameweek.'
            }
        
        # Handle different data types safely
        if isinstance(chips_data, dict):
            chips_used = chips_data.get('chips_used', [])
        elif isinstance(chips_data, list):
            chips_used = chips_data
        else:
            # If it's not a dict or list (e.g., int), treat as no chips
            chips_used = []
        
        if chips_used:
            chip_summary = f"Played {', '.join(chips_used)} this gameweek."
        else:
            chip_summary = 'No chips played this gameweek.'
        
        return {
            'chips_used': chips_used,
            'chip_summary': chip_summary
        }
    
    def _analyze_team_performance(self, team_data, active_chip=None):
        """Analyze overall team performance"""
        if not team_data:
            return {
                'total_points': 0,
                'top_scorer': 'Unknown',
                'top_scorer_points': 0,
                'captain_points': 0,
                'vice_captain_points': 0,
                'bench_points': 0,
                'chips_used': []
            }
        
        # Create a copy of team_data to avoid mutating the original
        import copy
        team_data_copy = copy.deepcopy(team_data)
        
        # Apply captain doubling logic (same as team page)
        captain_playing = False
        vice_captain_playing = False
        
        # First pass: check if captain and vice-captain are playing
        for player in team_data_copy:
            if player.get('is_captain') and player.get('points', 0) > 0:
                captain_playing = True
            if player.get('is_vice_captain') and player.get('points', 0) > 0:
                vice_captain_playing = True
        
        # Second pass: apply captain logic
        for player in team_data_copy:
            # If captain is not playing and vice-captain is playing, make vice-captain the captain
            if not captain_playing and vice_captain_playing and player.get('is_vice_captain'):
                player['is_captain'] = True
                player['is_vice_captain'] = False
                player['multiplier'] = 2
                player['points'] = player.get('points', 0) * 2
            # If player has multiplier 2 (captain), double their points
            elif player.get('multiplier') == 2:
                current_points = player.get('points', 0)
                player['points'] = current_points * 2
                if not player.get('is_captain'):
                    player['is_captain'] = True
                    player['is_vice_captain'] = False
        
        # Calculate total points (excluding bench unless bench boost is active)
        bench_boost_active = active_chip == 'bboost'
        total_points = 0
        
        for player in team_data_copy:
            # Only count points from starting 11 unless bench boost is active
            if player['position'] <= 11 or bench_boost_active:
                total_points += player.get('points', 0)
        top_player = max(team_data_copy, key=lambda x: x.get('points', 0))
        captain = next((p for p in team_data_copy if p.get('is_captain')), None)
        vice_captain = next((p for p in team_data_copy if p.get('is_vice_captain')), None)
        
        # Calculate bench points (players with 0 points are likely benched)
        bench_points = sum(player.get('points', 0) for player in team_data_copy if player.get('points', 0) == 0)
        
        return {
            'total_points': total_points,
            'top_scorer': top_player['name'],
            'top_scorer_points': top_player['points'],
            'captain_points': captain['points'] if captain else 0,
            'vice_captain_points': vice_captain['points'] if vice_captain else 0,
            'bench_points': bench_points,
            'chips_used': []  # Would need additional data to determine chips
        }
    
    def _generate_detailed_analysis(self, team_performance, league_data, player_data):
        """Generate detailed analysis section"""
        analysis = []
        
        # Captain analysis
        if team_performance['captain_points'] > 15:
            analysis.append(f"The captaincy choice was spot-on, with {team_performance['captain_points']} points proving to be a masterstroke.")
        elif team_performance['captain_points'] > 10:
            analysis.append(f"The captain delivered a solid {team_performance['captain_points']} points, showing good decision-making.")
        else:
            analysis.append(f"The captaincy didn't quite work out this week with only {team_performance['captain_points']} points, but every manager has these weeks.")
        
        # Top scorer analysis
        if team_performance['top_scorer_points'] > 20:
            analysis.append(f"The standout performer was {team_performance['top_scorer']} with an incredible {team_performance['top_scorer_points']} points, showcasing the depth of quality in this squad.")
        elif team_performance['top_scorer_points'] > 15:
            analysis.append(f"{team_performance['top_scorer']} was the star of the show with {team_performance['top_scorer_points']} points, proving to be a valuable asset.")
        else:
            analysis.append(f"The team performance was balanced, with {team_performance['top_scorer']} leading the way with {team_performance['top_scorer_points']} points.")
        
        # Total points analysis
        if team_performance['total_points'] > 80:
            analysis.append(f"With {team_performance['total_points']} total points, this was a week to remember for {player_data['team_name']}.")
        elif team_performance['total_points'] > 60:
            analysis.append(f"A solid {team_performance['total_points']} points shows the consistency that {player_data['team_name']} are building.")
        else:
            analysis.append(f"While {team_performance['total_points']} points might not be spectacular, it's the kind of steady performance that keeps teams competitive.")
        
    def _generate_league_context(self, league_standings, player_data, current_position, player_id):
        """Generate league context and competitor analysis"""
        if not league_standings or not league_standings.get('standings'):
            return ""
        
        standings = league_standings['standings']['results']
        context = []
        
        # Find teams above and below
        teams_above = []
        teams_below = []
        
        for i, entry in enumerate(standings):
            if entry['entry'] == player_id:
                # Get teams above (lower rank numbers)
                teams_above = standings[max(0, i-3):i]
                # Get teams below (higher rank numbers)
                teams_below = standings[i+1:min(len(standings), i+4)]
                break
        
        # Analyze teams above
        if teams_above:
            context.append(f"Looking at the teams above {player_data['team_name']} in the table, ")
            for team in teams_above:
                context.append(f"{team['entry_name']} ({team['player_name']}) with {team['total']} points, ")
            context.append("are setting the pace in this competitive league.")
        
        # Analyze teams below
        if teams_below:
            context.append(f"Meanwhile, the chasing pack includes ")
            for team in teams_below:
                context.append(f"{team['entry_name']} ({team['player_name']}) on {team['total']} points, ")
            context.append("who will be looking to close the gap in the coming weeks.")
        
        return " ".join(context)
    
    def _generate_future_outlook(self, league_data, player_data, current_position, team_performance):
        """Generate future outlook and predictions"""
        outlook = []
        
        # Based on current performance, provide outlook
        if team_performance['total_points'] > 80:
            outlook.append(f"With this kind of form, {player_data['team_name']} are well-positioned to challenge for the {league_data.get('name', 'league')} title.")
        elif team_performance['total_points'] > 60:
            outlook.append(f"The consistency shown by {player_data['team_name']} suggests they'll be a force to be reckoned with in the coming weeks.")
        else:
            outlook.append(f"There's room for improvement for {player_data['team_name']}, but the foundation is there for a strong finish to the season.")
        
        # Add generic future outlook
        outlook.append("The coming gameweeks will be crucial as teams look to consolidate their positions and make their moves up the table.")
        
    def _analyze_league_competitors(self, league_standings, player_id, gameweek):
        """Analyze what other players in the league have done"""
        if not league_standings or not league_standings.get('standings'):
            return []
        
        standings = league_standings['standings']['results']
        competitor_insights = []
        
        # Get top performers this gameweek (excluding current player)
        sorted_by_gw_points = sorted(standings, key=lambda x: x.get('event_total', 0), reverse=True)
        
        # For now, return basic insights with points data
        # TODO: Add async competitor data fetching in a separate endpoint
        for entry in sorted_by_gw_points[:5]:  # Top 5 performers
            if entry['entry'] != player_id:
                gw_points = entry.get('event_total', 0)
                manager_name = entry.get('player_name', 'Unknown')
                team_name = entry.get('entry_name', 'Unknown')
                total_points = entry.get('total', 0)
                
                # Enhanced insight with more context
                if gw_points > 80:
                    insight_text = f"{manager_name} ({team_name}) had a phenomenal gameweek with {gw_points} points, bringing their total to {total_points}."
                elif gw_points > 60:
                    insight_text = f"{manager_name} ({team_name}) delivered a solid {gw_points} points this gameweek, maintaining their {total_points} total."
                else:
                    insight_text = f"{manager_name} ({team_name}) managed {gw_points} points this gameweek, with {total_points} total points."
                
                competitor_insights.append(insight_text)
        
        return competitor_insights
    def _generate_competitor_insights(self, competitor_insights):
        """Generate natural, varied competitor insights"""
        if not competitor_insights:
            return ""
        
        # Create varied sentence structures
        sentence_starters = [
            "Leading the charge was",
            "Hot on their heels was", 
            "Making their mark was",
            "Delivering a strong performance was",
            "Rounding out the top performers was"
        ]
        
        insights_text = []
        for i, insight in enumerate(competitor_insights[:3]):  # Top 3 insights
            if i < len(sentence_starters):
                # Extract manager name and team from insight
                parts = insight.split(" with ")
                if len(parts) >= 2:
                    manager_info = parts[0]
                    rest = " with " + parts[1]
                    varied_insight = f"{sentence_starters[i]} {manager_info}{rest}"
                else:
                    varied_insight = insight
            else:
                varied_insight = insight
            
            insights_text.append(varied_insight)
        
        return " ".join(insights_text)
    
    def _generate_captain_section(self, captain_performance, player_data):
        """Generate captain analysis section"""
        if captain_performance['points'] > 15:
            return f"Captain Analysis: {player_data['manager_name']} made an inspired choice by captaining {captain_performance['name']}, who delivered {captain_performance['points']} points. This tactical decision proved to be a masterstroke, showcasing the manager's keen eye for form and fixtures."
        elif captain_performance['points'] > 10:
            return f"Captain Analysis: The decision to captain {captain_performance['name']} paid off with {captain_performance['points']} points. While not spectacular, it was a solid choice that contributed to the team's overall performance."
        else:
            return f"Captain Analysis: Unfortunately, the captaincy choice of {captain_performance['name']} didn't quite work out this week with only {captain_performance['points']} points. Every manager has these weeks, and it's all part of the fantasy football experience."
    
    def _generate_transfers_section(self, transfers_analysis, player_data):
        """Generate transfers analysis section"""
        return f"Transfer Activity: {transfers_analysis['transfer_summary']} {player_data['manager_name']} showed their tactical nous in the transfer market this gameweek."
    
    def _generate_chips_section(self, chips_analysis, player_data):
        """Generate chips analysis section"""
        return f"Chip Usage: {chips_analysis['chip_summary']} Strategic chip usage can be the difference between success and failure in fantasy football."
    
    def _generate_captain_section(self, captain_performance, player_data):
        """Generate captain analysis section"""
        if captain_performance['points'] > 15:
            return f"Captain Analysis: {player_data['manager_name']} made an inspired choice by captaining {captain_performance['name']}, who delivered {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points). This tactical decision proved to be a masterstroke, showcasing the manager's keen eye for form and fixtures."
        elif captain_performance['points'] > 10:
            return f"Captain Analysis: The decision to captain {captain_performance['name']} paid off with {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points). While not spectacular, it was a solid choice that contributed to the team's overall performance."
        else:
            return f"Captain Analysis: Unfortunately, the captaincy choice of {captain_performance['name']} didn't quite work out this week with only {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points). Every manager has these weeks, and it's all part of the fantasy football experience."
    
    def _generate_transfers_section(self, transfers_analysis, player_data):
        """Generate transfers analysis section"""
        base_text = f"Transfer Activity: {transfers_analysis['transfer_summary']} {transfers_analysis['transfer_analysis']}"
        
        # Add specific transfer performance details
        if transfers_analysis['transfer_performance']:
            performance_details = []
            for tp in transfers_analysis['transfer_performance']:
                performance_details.append(f"{tp['name']} ({tp['points']} points)")
            
            if performance_details:
                base_text += f" The new signings delivered: {', '.join(performance_details)}."
        
        return base_text
    
    def _generate_chips_section(self, chips_analysis, player_data):
        """Generate chips analysis section"""
        return f"Chip Usage: {chips_analysis['chip_summary']} Strategic chip usage can be the difference between success and failure in fantasy football."
    
    def _generate_standouts_section(self, standouts, player_data):
        """Generate league standouts section"""
        if not standouts:
            return ""
        
        standout_text = "League Standouts: "
        standout_details = []
        
        for standout in standouts[:3]:  # Top 3 standouts
            standout_details.append(f"{standout['manager_name']} ({standout['team_name']}) with {standout['gameweek_points']} points")
        
        if standout_details:
            standout_text += f"Meanwhile, {', '.join(standout_details)} showed why they're serious contenders this season."
        
        return standout_text
        
    def _generate_performance_section(self, team_performance, player_data):
        """Generate team performance section"""
        if team_performance['total_points'] > 80:
            return f"Team Performance: What a week for {player_data['team_name']}! With {team_performance['total_points']} points, this was a performance to remember. {team_performance['top_scorer']} was the standout performer with {team_performance['top_scorer_points']} points, leading the charge for this remarkable gameweek."
        elif team_performance['total_points'] > 60:
            return f"Team Performance: A solid {team_performance['total_points']} points shows the consistency that {player_data['team_name']} are building. {team_performance['top_scorer']} led the way with {team_performance['top_scorer_points']} points, proving to be a valuable asset."
        else:
            return f"Team Performance: While {team_performance['total_points']} points might not be spectacular, it's the kind of steady performance that keeps teams competitive. {team_performance['top_scorer']} was the top performer with {team_performance['top_scorer_points']} points."
    
    def _generate_article_body(self, league_data, player_data, gameweek_results, position_change, league_standings=None, player_id=None, transfers_data=None, chips_data=None, competitor_insights=None):
        """Generate a natural, flowing sports article"""
        captain_performance = self._analyze_captain_performance(player_data['team_data'])
        top_performer = self._get_top_performer(player_data['team_data'])
        team_performance = self._analyze_team_performance(player_data['team_data'], player_data.get('active_chip'))
        transfers_analysis = self._analyze_transfers(transfers_data or [], player_data['team_data'])
        chips_analysis = self._analyze_chips(chips_data or [])
        league_insights = self._analyze_league_competitors(league_standings, player_id, gameweek_results['gameweek'])
        
        # Calculate real position change if not provided
        if position_change == 0 and league_standings and player_id:
            position_change = self._calculate_position_change(league_standings, player_id, gameweek_results['gameweek'])
        
        # Calculate position changes for all players
        all_position_changes = {}
        if league_standings and player_id:
            all_position_changes = self._calculate_all_position_changes(league_standings, gameweek_results['gameweek'])
        
        # Get current position in league
        current_position = None
        if league_standings and player_id:
            current_position = self._get_player_position_in_league(league_standings, player_id)
        
        # Determine article type based on ACTUAL performance and position
        if current_position == 1:  # Player is actually top of league
            article_type = 'captain_masterstroke'
            template = random.choice(self.article_templates[article_type])
            opening = template.format(
                manager_name=player_data['manager_name'],
                captain_name=captain_performance['name'],
                team_name=player_data['team_name'],
                league_name=league_data.get('name', 'the league'),
                captain_points=captain_performance['points']
            )
        elif position_change > 2:  # Big rise
            article_type = 'big_rise'
            template = random.choice(self.article_templates[article_type])
            opening = template.format(
                team_name=player_data['team_name'],
                manager_name=player_data['manager_name'],
                position_change=position_change,
                league_name=league_data.get('name', 'the league'),
                player_name=top_performer,
                player_points=team_performance['top_scorer_points']
            )
        elif position_change < -2:  # Dramatic fall
            article_type = 'dramatic_fall'
            template = random.choice(self.article_templates[article_type])
            opening = template.format(
                team_name=player_data['team_name'],
                manager_name=player_data['manager_name'],
                position_change=abs(position_change),
                league_name=league_data.get('name', 'the league')
            )
        else:  # Consistent performance
            article_type = 'consistent_performance'
            template = random.choice(self.article_templates[article_type])
            opening = template.format(
                team_name=player_data['team_name'],
                manager_name=player_data['manager_name'],
                league_name=league_data.get('name', 'the league')
            )
        
        # Build natural flowing paragraphs
        paragraphs = [opening]
        
        # Captain paragraph
        if captain_performance['points'] > 15:
            captain_text = f"The tactical masterclass continued with {player_data['manager_name']}'s inspired captaincy choice. {captain_performance['name']} delivered {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points), proving once again that great managers trust their instincts when it matters most."
        elif captain_performance['points'] > 10:
            captain_text = f"Captaincy decisions can make or break a gameweek, and {player_data['manager_name']} got it right this time. {captain_performance['name']} rewarded the faith shown in them with {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points), contributing significantly to the team's overall performance."
        else:
            captain_text = f"Sometimes the captaincy choice doesn't quite work out, and that was the case for {player_data['manager_name']} this gameweek. {captain_performance['name']} could only manage {captain_performance['points']} points (doubled from {captain_performance['base_points']} base points), but every manager knows these weeks are part of the fantasy football journey."
        
        paragraphs.append(captain_text)
        
        # Transfer paragraph
        if transfers_analysis['transfers_made'] > 0:
            if transfers_analysis['transfer_performance']:
                transfer_names = [tp['name'] for tp in transfers_analysis['transfer_performance']]
                transfer_points = [tp['points'] for tp in transfers_analysis['transfer_performance']]
                total_transfer_points = sum(transfer_points)
                
                if len(transfer_names) == 1:
                    transfer_text = f"The transfer market proved fruitful for {player_data['manager_name']}, with {transfer_names[0]} delivering {transfer_points[0]} points and justifying the manager's faith in their scouting abilities."
                else:
                    transfer_text = f"Bold transfer moves paid off handsomely for {player_data['team_name']}, with the new signings combining for {total_transfer_points} points. {', '.join(transfer_names)} showed exactly why {player_data['manager_name']} brought them to the club."
            else:
                transfer_text = f"Transfer activity saw {player_data['manager_name']} make {transfers_analysis['transfers_made']} moves, spending {transfers_analysis['transfer_cost']}m in the process. Time will tell if these acquisitions prove to be shrewd investments."
        else:
            transfer_text = f"Sometimes the best transfer is no transfer at all, and {player_data['manager_name']} showed faith in their current squad by keeping their powder dry this gameweek."
        
        paragraphs.append(transfer_text)
        
        # Chips paragraph
        if chips_analysis['chips_used']:
            chips_text = f"Strategic chip usage came into play for {player_data['team_name']}, with {player_data['manager_name']} deploying {', '.join(chips_analysis['chips_used'])} to maximize their gameweek potential. These calculated risks often separate the contenders from the pretenders."
        else:
            chips_text = f"No chips were played this gameweek, suggesting {player_data['manager_name']} is saving their ammunition for the crucial weeks ahead when strategic advantages can make all the difference."
        
        paragraphs.append(chips_text)
        
        # Team performance paragraph
        if team_performance['total_points'] > 80:
            performance_text = f"What a week for {player_data['team_name']}! The squad delivered a magnificent {team_performance['total_points']} points, with {team_performance['top_scorer']} leading the charge with {team_performance['top_scorer_points']} points. This kind of collective performance is what championship dreams are made of."
        elif team_performance['total_points'] > 60:
            performance_text = f"A solid {team_performance['total_points']} points shows the consistency that {player_data['team_name']} are building under {player_data['manager_name']}'s guidance. {team_performance['top_scorer']} was the standout performer with {team_performance['top_scorer_points']} points, but this was truly a team effort."
        else:
            performance_text = f"While {team_performance['total_points']} points might not set the world alight, it's the kind of steady performance that keeps teams competitive. {team_performance['top_scorer']} led by example with {team_performance['top_scorer_points']} points, showing the depth of quality in this squad."
        
        paragraphs.append(performance_text)
        
        # League competition paragraph
        if competitor_insights:
            league_text = f"The {league_data.get('name', 'league')} continues to provide fierce competition, with several managers making their mark this gameweek. "
            league_text += self._generate_competitor_insights(competitor_insights)
            league_text += f" This level of competition keeps everyone on their toes and makes every gameweek crucial in the title race."
            paragraphs.append(league_text)
        
        # Add league table placeholder with position changes
        paragraphs.append(f"\n[LEAGUE_TABLE_PLACEHOLDER]\n")
        
        # Add position change info to the article
        if position_change != 0:
            arrow = self._get_position_arrow(position_change)
            paragraphs.append(f"Position Change: {arrow} {abs(position_change)} places {'up' if position_change > 0 else 'down'} this gameweek.")
        
        # Future outlook paragraph
        if team_performance['total_points'] > 80:
            outlook_text = f"With this kind of form, {player_data['team_name']} are well-positioned to challenge for the {league_data.get('name', 'league')} title. The coming gameweeks will be crucial as teams look to consolidate their positions and make their moves up the table."
        elif team_performance['total_points'] > 60:
            outlook_text = f"The consistency shown by {player_data['team_name']} suggests they'll be a force to be reckoned with in the coming weeks. The foundation is there for a strong finish to the season."
        else:
            outlook_text = f"There's room for improvement for {player_data['team_name']}, but the foundation is there for a strong finish to the season. The coming gameweeks will be crucial as teams look to consolidate their positions and make their moves up the table."
        
        paragraphs.append(outlook_text)
        
        return "\n\n".join(paragraphs)
    
    def generate_article(self, league_data, player_data, gameweek_results, league_standings=None, player_id=None, transfers_data=None, chips_data=None):
        """
        Generate personalized news article for a league
        """
        # Get real league position and points
        current_position = None
        total_points = 0
        
        if league_standings and player_id:
            current_position = self._get_player_position_in_league(league_standings, player_id)
            total_points = self._get_player_total_points(league_standings, player_id)
        
        # Calculate position changes for all players
        all_position_changes = {}
        if league_standings and player_id:
            all_position_changes = self._calculate_all_position_changes(league_standings, gameweek_results['gameweek'])
        
        # Get competitor insights
        competitor_insights = self._analyze_league_competitors(league_standings, player_id, gameweek_results['gameweek'])
        
        # Analyze the player's performance vs league
        position_change = self._calculate_position_change(league_standings, player_id, gameweek_results['gameweek'])
        captain_performance = self._analyze_captain_performance(player_data['team_data'])
        
        # Select appropriate template based on ACTUAL performance and position
        if current_position == 1:  # Player is actually top of league
            template = random.choice(self.templates['captain_masterstroke'])
            headline = template.format(
                team_name=player_data['team_name'],
                captain_name=captain_performance['name'],
                manager_name=player_data['manager_name'],
                league_name=league_data.get('name', 'the league')
            )
        elif position_change > 2:
            template = random.choice(self.templates['big_rise'])
            headline = template.format(
                team_name=player_data['team_name'],
                player_name=self._get_top_performer(player_data['team_data']),
                manager_name=player_data['manager_name'],
                league_name=league_data.get('name', 'the league')
            )
        elif position_change < -2:
            template = random.choice(self.templates['dramatic_fall'])
            headline = template.format(
                team_name=player_data['team_name'],
                manager_name=player_data['manager_name'],
                league_name=league_data.get('name', 'the league')
            )
        else:
            template = random.choice(self.templates['consistent_performance'])
            headline = template.format(
                team_name=player_data['team_name'],
                manager_name=player_data['manager_name'],
                league_name=league_data.get('name', 'the league')
            )
        
        # Generate article body
        article_body = self._generate_article_body(
            league_data, player_data, gameweek_results, position_change, league_standings, player_id, transfers_data, chips_data, competitor_insights
        )
        
        return {
            'headline': headline,
            'body': article_body,
            'league_name': league_data.get('name', 'Unknown League'),
            'league_id': league_data.get('id'),
            'gameweek': gameweek_results['gameweek'],
            'position_change': position_change,
            'current_position': current_position,
            'total_points': total_points,
            'league_standings': league_standings,
            'all_position_changes': all_position_changes,
            'competitor_insights': competitor_insights
        }
