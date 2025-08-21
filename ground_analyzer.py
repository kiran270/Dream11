#!/usr/bin/env python3
"""
Ground Analyzer for Dream11 Team Generation
Analyzes ground statistics to provide insights for team selection
"""

import json
import os
import re
from datetime import datetime

class GroundAnalyzer:
    def __init__(self):
        self.ground_data = None
        self.analysis = {}
    
    def load_ground_data(self, json_file_path):
        """Load ground statistics from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.ground_data = json.load(f)
            print(f"✅ Loaded ground data: {self.ground_data.get('ground_name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Error loading ground data: {e}")
            return False
    
    def analyze_ground_conditions(self):
        """Analyze ground conditions for Dream11 strategy"""
        if not self.ground_data:
            return None
        
        analysis = {
            'ground_name': self.ground_data.get('ground_name', 'Unknown'),
            'total_matches': 0,
            'avg_runs_per_over': 0,
            'avg_runs_per_match': 0,
            'batting_friendly': False,
            'bowling_friendly': False,
            'balanced_ground': False,
            'high_scoring': False,
            'low_scoring': False,
            'match_results': {
                'total_completed_matches': 0,
                'wins_batting_first': 0,
                'wins_chasing': 0,
                'wins_by_runs': 0,
                'wins_by_wickets': 0,
                'abandoned_matches': 0,
                'tied_matches': 0,
                'batting_first_success_rate': 0,
                'chasing_success_rate': 0,
                'avg_winning_margin_runs': 0,
                'avg_winning_margin_wickets': 0
            },
            'scorecard_analysis': {
                'high_scores_frequency': 0,
                'low_scores_frequency': 0,
                'avg_first_innings_score': 0,
                'avg_second_innings_score': 0,
                'powerplay_importance': 0,
                'middle_overs_importance': 0,
                'death_overs_importance': 0,
                'top_order_contribution': 0,
                'middle_order_contribution': 0,
                'lower_order_contribution': 0,
                'pace_bowler_effectiveness': 0,
                'spin_bowler_effectiveness': 0,
                'wicket_keeper_batting_avg': 0
            },
            'player_importance': {
                'openers': 0,
                'middle_order_batsmen': 0,
                'finishers': 0,
                'wicket_keeper_batsmen': 0,
                'pace_bowlers': 0,
                'spin_bowlers': 0,
                'death_bowlers': 0,
                'all_rounders': 0
            },
            'recommendations': {
                'batting_strategy': '',
                'bowling_strategy': '',
                'captain_preference': '',
                'team_composition': '',
                'toss_strategy': '',
                'key_player_types': '',
                'powerplay_strategy': '',
                'death_overs_strategy': ''
            }
        }
        
        # Analyze overall figures table
        for table in self.ground_data.get('tables', []):
            if 'overall' in table.get('caption', '').lower() or 'figures' in table.get('caption', '').lower():
                for row in table.get('data', []):
                    if len(row) >= 13:  # Ensure we have enough columns
                        try:
                            matches = int(row[2]) if row[2].isdigit() else 0
                            runs = int(row[8]) if row[8].isdigit() else 0
                            balls = int(row[10]) if row[10].isdigit() else 0
                            rpo = float(row[12]) if row[12].replace('.', '').isdigit() else 0
                            
                            analysis['total_matches'] = matches
                            analysis['avg_runs_per_over'] = rpo
                            
                            if matches > 0:
                                analysis['avg_runs_per_match'] = runs / matches
                            
                            # Determine ground characteristics
                            if rpo >= 8.0:
                                analysis['high_scoring'] = True
                                analysis['batting_friendly'] = True
                            elif rpo <= 6.5:
                                analysis['low_scoring'] = True
                                analysis['bowling_friendly'] = True
                            else:
                                analysis['balanced_ground'] = True
                            
                        except (ValueError, IndexError):
                            continue
        
        # Analyze match results table for detailed insights
        self._analyze_match_results(analysis)
        
        # Analyze scorecards for player type importance
        self._analyze_scorecards(analysis)
        
        # Generate recommendations based on analysis
        self._generate_recommendations(analysis)
        
        self.analysis = analysis
        return analysis
    
    def _analyze_match_results(self, analysis):
        """Analyze detailed match results for batting/chasing insights"""
        match_results = analysis['match_results']
        
        for table in self.ground_data.get('tables', []):
            caption = table.get('caption', '').lower()
            if 'match result' in caption or 'result list' in caption:
                
                run_margins = []
                wicket_margins = []
                
                for row in table.get('data', []):
                    if len(row) >= 3:  # Ensure we have winner, result, margin columns
                        try:
                            winner = row[0].strip()
                            result = row[1].strip().lower()
                            margin = row[2].strip().lower()
                            
                            # Skip abandoned/tied matches for win analysis
                            if result == 'aban' or not winner:
                                match_results['abandoned_matches'] += 1
                                continue
                            elif result == 'tied':
                                match_results['tied_matches'] += 1
                                continue
                            
                            match_results['total_completed_matches'] += 1
                            
                            # Analyze margin type and extract numbers
                            if 'run' in margin:
                                match_results['wins_by_runs'] += 1
                                # Extract run margin
                                run_match = re.search(r'(\d+)\s*run', margin)
                                if run_match:
                                    run_margins.append(int(run_match.group(1)))
                                
                                # Wins by runs typically indicate batting first wins
                                match_results['wins_batting_first'] += 1
                                
                            elif 'wicket' in margin:
                                match_results['wins_by_wickets'] += 1
                                # Extract wicket margin
                                wicket_match = re.search(r'(\d+)\s*wicket', margin)
                                if wicket_match:
                                    wicket_margins.append(int(wicket_match.group(1)))
                                
                                # Wins by wickets indicate chasing wins
                                match_results['wins_chasing'] += 1
                        
                        except (ValueError, IndexError):
                            continue
                
                # Calculate success rates
                total_completed = match_results['total_completed_matches']
                if total_completed > 0:
                    match_results['batting_first_success_rate'] = (match_results['wins_batting_first'] / total_completed) * 100
                    match_results['chasing_success_rate'] = (match_results['wins_chasing'] / total_completed) * 100
                
                # Calculate average margins
                if run_margins:
                    match_results['avg_winning_margin_runs'] = sum(run_margins) / len(run_margins)
                if wicket_margins:
                    match_results['avg_winning_margin_wickets'] = sum(wicket_margins) / len(wicket_margins)
                
                break  # Found the results table, no need to continue
    
    def _analyze_scorecards(self, analysis):
        """Analyze scorecards to determine player type importance"""
        scorecard_analysis = analysis['scorecard_analysis']
        player_importance = analysis['player_importance']
        
        # Look for batting statistics tables
        for table in self.ground_data.get('tables', []):
            caption = table.get('caption', '').lower()
            
            # Analyze batting statistics
            if any(keyword in caption for keyword in ['batting', 'runs', 'innings']):
                self._analyze_batting_patterns(table, scorecard_analysis, player_importance)
            
            # Analyze bowling statistics  
            elif any(keyword in caption for keyword in ['bowling', 'wickets', 'overs']):
                self._analyze_bowling_patterns(table, scorecard_analysis, player_importance)
            
            # Analyze overall match data for scoring patterns
            elif 'overall' in caption or 'aggregate' in caption:
                self._analyze_scoring_patterns(table, scorecard_analysis)
        
        # Calculate player importance scores based on ground characteristics
        self._calculate_player_importance_scores(analysis)
    
    def _analyze_batting_patterns(self, table, scorecard_analysis, player_importance):
        """Analyze batting patterns from scorecard data"""
        try:
            headers = table.get('headers', [])
            data = table.get('data', [])
            
            # Look for batting position or role indicators
            for row in data:
                if len(row) >= len(headers):
                    row_dict = dict(zip(headers, row))
                    
                    # Analyze batting positions if available
                    for header, value in row_dict.items():
                        header_lower = header.lower()
                        
                        # Look for batting order indicators
                        if 'top' in header_lower or 'opener' in header_lower:
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['openers'] += score
                            except:
                                pass
                        
                        elif 'middle' in header_lower:
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['middle_order_batsmen'] += score
                            except:
                                pass
                        
                        elif 'finish' in header_lower or 'lower' in header_lower:
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['finishers'] += score
                            except:
                                pass
        
        except Exception as e:
            print(f"Error analyzing batting patterns: {e}")
    
    def _analyze_bowling_patterns(self, table, scorecard_analysis, player_importance):
        """Analyze bowling patterns from scorecard data"""
        try:
            headers = table.get('headers', [])
            data = table.get('data', [])
            
            for row in data:
                if len(row) >= len(headers):
                    row_dict = dict(zip(headers, row))
                    
                    # Analyze bowling types and effectiveness
                    for header, value in row_dict.items():
                        header_lower = header.lower()
                        
                        # Look for pace bowling indicators
                        if any(keyword in header_lower for keyword in ['pace', 'fast', 'seam']):
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['pace_bowlers'] += score
                            except:
                                pass
                        
                        # Look for spin bowling indicators
                        elif any(keyword in header_lower for keyword in ['spin', 'turn', 'slow']):
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['spin_bowlers'] += score
                            except:
                                pass
                        
                        # Look for death bowling indicators
                        elif any(keyword in header_lower for keyword in ['death', 'final', 'last']):
                            try:
                                score = float(re.sub(r'[^\d.]', '', str(value)))
                                player_importance['death_bowlers'] += score
                            except:
                                pass
        
        except Exception as e:
            print(f"Error analyzing bowling patterns: {e}")
    
    def _analyze_scoring_patterns(self, table, scorecard_analysis):
        """Analyze overall scoring patterns"""
        try:
            data = table.get('data', [])
            
            for row in data:
                if len(row) >= 8:  # Ensure we have runs data
                    try:
                        runs = int(row[8]) if row[8].isdigit() else 0
                        matches = int(row[2]) if row[2].isdigit() else 1
                        
                        if matches > 0:
                            avg_score = runs / matches
                            
                            # Categorize scoring patterns
                            if avg_score >= 180:
                                scorecard_analysis['high_scores_frequency'] += 1
                            elif avg_score <= 140:
                                scorecard_analysis['low_scores_frequency'] += 1
                            
                            # Estimate innings breakdown (simplified)
                            scorecard_analysis['avg_first_innings_score'] = avg_score * 0.52  # Typically slightly higher
                            scorecard_analysis['avg_second_innings_score'] = avg_score * 0.48
                    
                    except (ValueError, IndexError):
                        continue
        
        except Exception as e:
            print(f"Error analyzing scoring patterns: {e}")
    
    def _calculate_player_importance_scores(self, analysis):
        """Calculate player importance scores based on ground characteristics"""
        rpo = analysis['avg_runs_per_over']
        match_results = analysis['match_results']
        player_importance = analysis['player_importance']
        
        # Base importance on ground type and match results
        if analysis['batting_friendly']:
            # High-scoring ground - favor aggressive batsmen
            player_importance['openers'] += 30
            player_importance['middle_order_batsmen'] += 25
            player_importance['finishers'] += 35
            player_importance['wicket_keeper_batsmen'] += 20
            player_importance['all_rounders'] += 25
            player_importance['pace_bowlers'] += 15
            player_importance['spin_bowlers'] += 10
            player_importance['death_bowlers'] += 30
            
        elif analysis['bowling_friendly']:
            # Low-scoring ground - favor bowlers and steady batsmen
            player_importance['openers'] += 25
            player_importance['middle_order_batsmen'] += 30
            player_importance['finishers'] += 20
            player_importance['wicket_keeper_batsmen'] += 15
            player_importance['all_rounders'] += 35
            player_importance['pace_bowlers'] += 30
            player_importance['spin_bowlers'] += 25
            player_importance['death_bowlers'] += 20
            
        else:
            # Balanced ground - equal importance
            base_score = 25
            for key in player_importance:
                player_importance[key] += base_score
        
        # Adjust based on chasing vs batting first success
        chasing_rate = match_results.get('chasing_success_rate', 50)
        batting_first_rate = match_results.get('batting_first_success_rate', 50)
        
        if chasing_rate > batting_first_rate + 10:
            # Chasing friendly - favor finishers and death bowlers
            player_importance['finishers'] += 15
            player_importance['death_bowlers'] += 15
            player_importance['all_rounders'] += 10
        elif batting_first_rate > chasing_rate + 10:
            # Batting first friendly - favor openers and middle order
            player_importance['openers'] += 15
            player_importance['middle_order_batsmen'] += 15
            player_importance['spin_bowlers'] += 10
        
        # Normalize scores to 0-100 scale
        max_score = max(player_importance.values()) if player_importance.values() else 1
        for key in player_importance:
            player_importance[key] = min(100, (player_importance[key] / max_score) * 100)
    
    def _generate_player_type_recommendations(self, analysis):
        """Generate specific player type recommendations"""
        player_importance = analysis['player_importance']
        recommendations = analysis['recommendations']
        
        # Sort player types by importance
        sorted_players = sorted(player_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Top 3 most important player types
        top_players = sorted_players[:3]
        key_players = [player[0].replace('_', ' ').title() for player in top_players]
        
        recommendations['key_player_types'] = f"Prioritize: {', '.join(key_players)}"
        
        # Specific phase strategies
        if player_importance['openers'] >= 80:
            recommendations['powerplay_strategy'] = 'Focus on aggressive openers - powerplay crucial'
        elif player_importance['openers'] >= 60:
            recommendations['powerplay_strategy'] = 'Balanced powerplay approach with steady openers'
        else:
            recommendations['powerplay_strategy'] = 'Conservative powerplay - wickets more important than runs'
        
        if player_importance['death_bowlers'] >= 80:
            recommendations['death_overs_strategy'] = 'Death bowling specialists essential - high-pressure situations'
        elif player_importance['finishers'] >= 80:
            recommendations['death_overs_strategy'] = 'Explosive finishers crucial - expect close finishes'
        else:
            recommendations['death_overs_strategy'] = 'Balanced death overs approach'
    
    def _generate_recommendations(self, analysis):
        """Generate Dream11 strategy recommendations"""
        rpo = analysis['avg_runs_per_over']
        match_results = analysis['match_results']
        
        # Base recommendations on ground type
        if analysis['batting_friendly']:
            analysis['recommendations']['batting_strategy'] = 'Focus on top-order batsmen and aggressive players'
            analysis['recommendations']['bowling_strategy'] = 'Pick wicket-taking bowlers over economical ones'
            analysis['recommendations']['captain_preference'] = 'Batsmen or aggressive all-rounders'
            analysis['recommendations']['team_composition'] = 'Batting heavy: 5-6 batsmen, 2-3 all-rounders, 3-4 bowlers'
            
        elif analysis['bowling_friendly']:
            analysis['recommendations']['batting_strategy'] = 'Pick reliable middle-order batsmen'
            analysis['recommendations']['bowling_strategy'] = 'Focus on economical bowlers and wicket-takers'
            analysis['recommendations']['captain_preference'] = 'Bowlers or bowling all-rounders'
            analysis['recommendations']['team_composition'] = 'Bowling heavy: 3-4 batsmen, 3-4 all-rounders, 4-5 bowlers'
            
        else:  # Balanced ground
            analysis['recommendations']['batting_strategy'] = 'Balanced approach with consistent performers'
            analysis['recommendations']['bowling_strategy'] = 'Mix of wicket-takers and economical bowlers'
            analysis['recommendations']['captain_preference'] = 'Consistent all-rounders or in-form players'
            analysis['recommendations']['team_composition'] = 'Balanced: 4-5 batsmen, 3-4 all-rounders, 3-4 bowlers'
        
        # Add toss strategy based on batting first vs chasing success
        batting_first_rate = match_results['batting_first_success_rate']
        chasing_rate = match_results['chasing_success_rate']
        
        if batting_first_rate > chasing_rate + 10:  # Significant advantage
            analysis['recommendations']['toss_strategy'] = f'Bat first preferred ({batting_first_rate:.1f}% vs {chasing_rate:.1f}% success rate)'
        elif chasing_rate > batting_first_rate + 10:
            analysis['recommendations']['toss_strategy'] = f'Chase preferred ({chasing_rate:.1f}% vs {batting_first_rate:.1f}% success rate)'
        else:
            analysis['recommendations']['toss_strategy'] = f'Balanced toss advantage (Bat: {batting_first_rate:.1f}%, Chase: {chasing_rate:.1f}%)'
        
        # Generate player type recommendations
        self._generate_player_type_recommendations(analysis)
    
    def get_team_strategy_weights(self):
        """Get strategy weights for different player types based on ground analysis"""
        if not self.analysis:
            return None
        
        # Default weights
        weights = {
            'batsmen_weight': 1.0,
            'bowlers_weight': 1.0,
            'all_rounders_weight': 1.0,
            'wicket_keepers_weight': 1.0,
            'aggressive_players_weight': 1.0,
            'economical_bowlers_weight': 1.0
        }
        
        if self.analysis['batting_friendly']:
            weights['batsmen_weight'] = 1.3
            weights['aggressive_players_weight'] = 1.2
            weights['bowlers_weight'] = 0.8
            weights['economical_bowlers_weight'] = 0.7
            
        elif self.analysis['bowling_friendly']:
            weights['bowlers_weight'] = 1.3
            weights['economical_bowlers_weight'] = 1.2
            weights['batsmen_weight'] = 0.8
            weights['aggressive_players_weight'] = 0.7
            
        return weights
    
    def get_ground_insights(self):
        """Get formatted ground insights for display"""
        if not self.analysis:
            return "No ground analysis available"
        
        insights = []
        insights.append(f"🏟️ Ground: {self.analysis['ground_name']}")
        insights.append(f"📊 Matches Analyzed: {self.analysis['total_matches']}")
        insights.append(f"🏃 Average RPO: {self.analysis['avg_runs_per_over']:.2f}")
        
        if self.analysis['avg_runs_per_match'] > 0:
            insights.append(f"🎯 Avg Runs/Match: {self.analysis['avg_runs_per_match']:.0f}")
        
        # Ground type
        if self.analysis['batting_friendly']:
            insights.append("⚡ Ground Type: BATTING FRIENDLY")
        elif self.analysis['bowling_friendly']:
            insights.append("🎳 Ground Type: BOWLING FRIENDLY")
        else:
            insights.append("⚖️ Ground Type: BALANCED")
        
        # Match results analysis
        match_results = self.analysis['match_results']
        if match_results['total_completed_matches'] > 0:
            insights.append(f"\n📈 MATCH RESULTS ANALYSIS:")
            insights.append(f"• Completed Matches: {match_results['total_completed_matches']}")
            insights.append(f"• Wins Batting First: {match_results['wins_batting_first']} ({match_results['batting_first_success_rate']:.1f}%)")
            insights.append(f"• Wins Chasing: {match_results['wins_chasing']} ({match_results['chasing_success_rate']:.1f}%)")
            
            if match_results['wins_by_runs'] > 0:
                insights.append(f"• Wins by Runs: {match_results['wins_by_runs']} (Avg: {match_results['avg_winning_margin_runs']:.1f} runs)")
            
            if match_results['wins_by_wickets'] > 0:
                insights.append(f"• Wins by Wickets: {match_results['wins_by_wickets']} (Avg: {match_results['avg_winning_margin_wickets']:.1f} wickets)")
            
            if match_results['abandoned_matches'] > 0:
                insights.append(f"• Abandoned: {match_results['abandoned_matches']}")
        
        # Player importance analysis
        player_importance = self.analysis.get('player_importance', {})
        if any(player_importance.values()):
            insights.append(f"\n👥 PLAYER TYPE IMPORTANCE:")
            # Sort by importance and show top 5
            sorted_players = sorted(player_importance.items(), key=lambda x: x[1], reverse=True)
            for player_type, importance in sorted_players[:5]:
                if importance > 0:
                    player_name = player_type.replace('_', ' ').title()
                    insights.append(f"• {player_name}: {importance:.0f}% importance")
        
        # Recommendations
        insights.append("\n🎯 DREAM11 STRATEGY:")
        for key, value in self.analysis['recommendations'].items():
            if value:
                insights.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(insights)
    
    def apply_ground_bias_to_players(self, players):
        """Apply ground-based bias to player selection percentages"""
        if not self.analysis or not players:
            return players
        
        weights = self.get_team_strategy_weights()
        if not weights:
            return players
        
        modified_players = []
        
        for player in players:
            if len(player) < 6:  # Ensure player has required fields
                modified_players.append(player)
                continue
            
            # Create a copy of the player data
            modified_player = list(player)
            original_percentage = float(player[5])
            role = player[2].upper()
            
            # Apply role-based weights
            multiplier = 1.0
            
            if role == 'BAT':
                multiplier = weights['batsmen_weight']
            elif role in ['BOWL']:
                multiplier = weights['bowlers_weight']
            elif role in ['ALL', 'AL']:
                multiplier = weights['all_rounders_weight']
            elif role == 'WK':
                multiplier = weights['wicket_keepers_weight']
            
            # Apply ground bias
            new_percentage = original_percentage * multiplier
            
            # Ensure percentage doesn't go below 0 or above 100
            new_percentage = max(0, min(100, new_percentage))
            
            # Update the percentage in the player data
            modified_player[5] = new_percentage
            
            modified_players.append(modified_player)
        
        return modified_players

def load_latest_ground_data():
    """Load the most recent ground statistics file"""
    try:
        # Look for ground stats files
        ground_files = [f for f in os.listdir('.') if f.startswith('ground_stats_') and f.endswith('.json')]
        
        if not ground_files:
            return None
        
        # Get the most recent file
        latest_file = max(ground_files, key=lambda x: os.path.getctime(x))
        
        analyzer = GroundAnalyzer()
        if analyzer.load_ground_data(latest_file):
            analyzer.analyze_ground_conditions()
            return analyzer
        
    except Exception as e:
        print(f"Error loading ground data: {e}")
    
    return None

if __name__ == "__main__":
    # Test the analyzer
    analyzer = GroundAnalyzer()
    if analyzer.load_ground_data('ground_stats_20250820_140711.json'):
        analysis = analyzer.analyze_ground_conditions()
        print(analyzer.get_ground_insights())
        print("\nStrategy Weights:", analyzer.get_team_strategy_weights())