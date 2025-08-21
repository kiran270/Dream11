#!/usr/bin/env python3
"""
Scorecard Analyzer for Dream11 Template Generation
Analyzes actual match scorecards to determine optimal team compositions
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

class ScorecardAnalyzer:
    def __init__(self):
        self.fantasy_points_rules = {
            # Batting points
            'run': 1,
            'boundary': 1,
            'six': 2,
            'fifty': 8,
            'century': 16,
            'duck': -2,
            
            # Bowling points
            'wicket': 25,
            'maiden': 12,
            'lbw_bowled': 8,
            'catch_stumping': 8,
            
            # Fielding points
            'catch': 8,
            'stumping': 12,
            'run_out': 12,
            'direct_hit': 6
        }
        
        self.role_mapping = {
            # Batting positions to roles
            1: 'TOP',  # Opener
            2: 'TOP',  # Opener
            3: 'MID',  # Middle order
            4: 'MID',  # Middle order
            5: 'HIT',  # Finisher
            6: 'HIT',  # Finisher
            7: 'POW',  # Power hitter
            8: 'BRE',  # Tail/Breaker
            9: 'BRE',  # Tail/Breaker
            10: 'BRE', # Tail/Breaker
            11: 'BRE'  # Tail/Breaker
        }
    
    def analyze_ground_scorecards(self, ground_results_url):
        """Analyze all scorecards from a ground to generate templates"""
        print(f"🏟️ Analyzing scorecards from: {ground_results_url}")
        
        # Step 1: Get all match links from ground results
        match_links = self._extract_match_links(ground_results_url)
        print(f"📋 Found {len(match_links)} matches to analyze")
        
        # Step 2: Analyze each match scorecard
        all_templates = []
        for i, match_link in enumerate(match_links[:10], 1):  # Limit to 10 matches for testing
            print(f"\n🏏 Analyzing match {i}/{min(10, len(match_links))}: {match_link}")
            template = self._analyze_single_match(match_link)
            if template:
                all_templates.append(template)
            time.sleep(2)  # Be respectful to the server
        
        # Step 3: Generate final templates based on patterns
        final_templates = self._generate_templates_from_analysis(all_templates)
        
        return final_templates
    
    def _extract_match_links(self, ground_results_url):
        """Extract all match scorecard links from ground results page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(ground_results_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            match_links = []
            # Look for scorecard links (usually contain 'full-scorecard' or similar)
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'full-scorecard' in href or 'scorecard' in href:
                    if not href.startswith('http'):
                        href = 'https://www.espncricinfo.com' + href
                    match_links.append(href)
            
            return list(set(match_links))  # Remove duplicates
            
        except Exception as e:
            print(f"❌ Error extracting match links: {e}")
            return []
    
    def _analyze_single_match(self, scorecard_url):
        """Analyze a single match scorecard to get top 11 performers and their roles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(scorecard_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match info
            match_info = self._extract_match_info(soup)
            
            # Extract player performances
            players = self._extract_player_performances(soup)
            
            # Calculate fantasy points for each player
            for player in players:
                player['fantasy_points'] = self._calculate_fantasy_points(player)
            
            # Get top 11 performers
            top_11 = sorted(players, key=lambda x: x['fantasy_points'], reverse=True)[:11]
            
            # Analyze roles of top 11
            template_composition = self._analyze_top_11_roles(top_11, match_info)
            
            return {
                'match_info': match_info,
                'top_11': top_11,
                'composition': template_composition,
                'scorecard_url': scorecard_url
            }
            
        except Exception as e:
            print(f"❌ Error analyzing scorecard {scorecard_url}: {e}")
            return None
    
    def _extract_match_info(self, soup):
        """Extract basic match information"""
        try:
            # Extract team names
            team_elements = soup.find_all('span', class_='ds-text-title-xs')
            teams = [elem.text.strip() for elem in team_elements[:2]] if team_elements else ['Team A', 'Team B']
            
            # Extract match result
            result_elem = soup.find('div', class_='ds-text-tight-m')
            result = result_elem.text.strip() if result_elem else 'Result not found'
            
            return {
                'team1': teams[0] if len(teams) > 0 else 'Team A',
                'team2': teams[1] if len(teams) > 1 else 'Team B',
                'result': result
            }
        except:
            return {'team1': 'Team A', 'team2': 'Team B', 'result': 'Unknown'}
    
    def _extract_player_performances(self, soup):
        """Extract all player performances from scorecard"""
        players = []
        
        try:
            # Find batting tables
            batting_tables = soup.find_all('table', class_='ds-w-full')
            
            for table_idx, table in enumerate(batting_tables):
                team = 'A' if table_idx == 0 else 'B'
                innings = 1 if table_idx < 2 else 2
                
                rows = table.find_all('tr')
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:
                        player_name = cells[0].text.strip()
                        if player_name and not any(x in player_name.lower() for x in ['extras', 'total', 'fall']):
                            
                            # Extract batting stats
                            runs = self._extract_number(cells[2].text) if len(cells) > 2 else 0
                            balls = self._extract_number(cells[3].text) if len(cells) > 3 else 0
                            fours = self._extract_number(cells[4].text) if len(cells) > 4 else 0
                            sixes = self._extract_number(cells[5].text) if len(cells) > 5 else 0
                            
                            player = {
                                'name': player_name,
                                'team': team,
                                'innings': innings,
                                'batting_position': row_idx,
                                'runs': runs,
                                'balls': balls,
                                'fours': fours,
                                'sixes': sixes,
                                'wickets': 0,
                                'maidens': 0,
                                'catches': 0,
                                'stumpings': 0,
                                'run_outs': 0
                            }
                            
                            players.append(player)
            
            # Extract bowling stats (simplified for now)
            # This would need more complex parsing for full bowling stats
            
        except Exception as e:
            print(f"❌ Error extracting player performances: {e}")
        
        return players
    
    def _extract_number(self, text):
        """Extract number from text"""
        try:
            numbers = re.findall(r'\d+', str(text))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _calculate_fantasy_points(self, player):
        """Calculate fantasy points for a player based on their performance"""
        points = 0
        
        # Batting points
        points += player['runs'] * self.fantasy_points_rules['run']
        points += player['fours'] * self.fantasy_points_rules['boundary']
        points += player['sixes'] * self.fantasy_points_rules['six']
        
        # Milestone bonuses
        if player['runs'] >= 100:
            points += self.fantasy_points_rules['century']
        elif player['runs'] >= 50:
            points += self.fantasy_points_rules['fifty']
        elif player['runs'] == 0 and player['balls'] > 0:
            points += self.fantasy_points_rules['duck']
        
        # Bowling points
        points += player['wickets'] * self.fantasy_points_rules['wicket']
        points += player['maidens'] * self.fantasy_points_rules['maiden']
        
        # Fielding points
        points += player['catches'] * self.fantasy_points_rules['catch']
        points += player['stumpings'] * self.fantasy_points_rules['stumping']
        points += player['run_outs'] * self.fantasy_points_rules['run_out']
        
        return points
    
    def _analyze_top_11_roles(self, top_11, match_info):
        """Analyze roles of top 11 performers to create template composition"""
        composition = {
            'atop': 0, 'amid': 0, 'ahit': 0, 'apow': 0, 'abre': 0, 'adea': 0,
            'btop': 0, 'bmid': 0, 'bhit': 0, 'bpow': 0, 'bbre': 0, 'bdea': 0
        }
        
        for player in top_11:
            team = player['team']
            position = player['batting_position']
            
            # Determine role based on batting position
            if position in [1, 2]:
                role = 'top'
            elif position in [3, 4]:
                role = 'mid'
            elif position in [5, 6]:
                role = 'hit'
            elif position in [7, 8]:
                role = 'pow'
            else:
                role = 'bre'
            
            # For bowling roles, we'd need more analysis of when wickets were taken
            # For now, assume death bowlers if they took wickets in later overs
            
            # Map to composition
            key = f"{team.lower()}{role}"
            if key in composition:
                composition[key] += 1
        
        return composition
    
    def _generate_templates_from_analysis(self, all_templates):
        """Generate final templates based on analysis of all matches"""
        if not all_templates:
            return []
        
        # Aggregate compositions from all matches
        total_composition = {
            'atop': 0, 'amid': 0, 'ahit': 0, 'apow': 0, 'abre': 0, 'adea': 0,
            'btop': 0, 'bmid': 0, 'bhit': 0, 'bpow': 0, 'bbre': 0, 'bdea': 0
        }
        
        for template in all_templates:
            comp = template['composition']
            for key in total_composition:
                total_composition[key] += comp.get(key, 0)
        
        # Calculate average composition
        num_matches = len(all_templates)
        avg_composition = {}
        for key, total in total_composition.items():
            avg_composition[key] = round(total / num_matches)
        
        # Ensure total is 11
        total_players = sum(avg_composition.values())
        if total_players != 11:
            # Adjust the composition to total 11
            diff = 11 - total_players
            # Add/subtract from the most common roles
            sorted_roles = sorted(avg_composition.items(), key=lambda x: x[1], reverse=True)
            for role, count in sorted_roles:
                if diff == 0:
                    break
                if diff > 0:
                    avg_composition[role] += 1
                    diff -= 1
                elif count > 0:
                    avg_composition[role] -= 1
                    diff += 1
        
        # Create final template
        final_template = {
            'name': 'Ground Performance Based Template',
            'description': f'Based on analysis of {num_matches} matches',
            'composition': avg_composition,
            'matches_analyzed': num_matches,
            'source_matches': [t['match_info'] for t in all_templates]
        }
        
        return [final_template]

def main():
    """Test the scorecard analyzer"""
    analyzer = ScorecardAnalyzer()
    
    # Example ground results URL (you would provide the actual URL)
    ground_url = "https://www.espncricinfo.com/series/ipl-2024-1410320/points-table-standings"
    
    templates = analyzer.analyze_ground_scorecards(ground_url)
    
    if templates:
        print(f"\n🎯 Generated {len(templates)} templates:")
        for template in templates:
            print(f"\n📋 {template['name']}")
            print(f"📊 Composition: {template['composition']}")
            print(f"🏏 Based on {template['matches_analyzed']} matches")
    else:
        print("❌ No templates generated")

if __name__ == "__main__":
    main()