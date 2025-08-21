#!/usr/bin/env python3
"""
Ground Scorecard Analyzer for Dream11 Template Generation
Analyzes actual match scorecards from a ground to determine optimal team compositions
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from db import addDreamTeam

class GroundScorecardAnalyzer:
    def __init__(self):
        self.fantasy_points_rules = {
            # Batting points (Dream11 standard)
            'run': 1,
            'boundary': 1,
            'six': 2,
            'fifty': 8,
            'century': 16,
            'duck': -2,
            'strike_rate_bonus': 0,  # Will calculate based on SR
            
            # Bowling points
            'wicket': 25,
            'maiden': 12,
            'lbw_bowled': 8,
            'economy_bonus': 0,  # Will calculate based on economy
            
            # Fielding points
            'catch': 8,
            'stumping': 12,
            'run_out': 12
        }
    
    def analyze_ground_and_generate_templates(self, ground_results_url, match_id, ground_name="Unknown Ground"):
        """Main function to analyze ground and generate templates"""
        print(f"🏟️ Analyzing ground: {ground_name}")
        print(f"📋 Ground results URL: {ground_results_url}")
        
        # Step 1: Extract match scorecard URLs from Twenty20 links
        scorecard_urls = self._extract_scorecard_urls(ground_results_url)
        print(f"🔗 Found {len(scorecard_urls)} scorecard URLs from Twenty20 links")
        
        if not scorecard_urls:
            print("❌ No Twenty20 scorecard URLs found")
            print("💡 This could be because:")
            print("   - No Twenty20 matches at this ground")
            print("   - Website structure has changed")
            print("   - Invalid ground results URL")
            print("   - Network connectivity issues")
            return False
        
        # Convert match URLs to full scorecard URLs if needed
        full_scorecard_urls = []
        for url in scorecard_urls:
            full_url = self._extract_scorecard_from_match_link(url)
            full_scorecard_urls.append(full_url)
        
        scorecard_urls = full_scorecard_urls
        print(f"✅ Converted to {len(scorecard_urls)} full scorecard URLs")
        
        # Step 2: Analyze each scorecard
        match_analyses = []
        for i, url in enumerate(scorecard_urls[:5], 1):  # Limit to 5 matches for testing
            print(f"\n🏏 Analyzing match {i}/5: {url}")
            analysis = self._analyze_scorecard(url)
            if analysis:
                match_analyses.append(analysis)
            time.sleep(2)  # Be respectful
        
        if not match_analyses:
            print("❌ No successful match analyses")
            return False
        
        # Step 3: Generate templates based on successful patterns
        templates = self._generate_templates_from_matches(match_analyses, ground_name)
        
        # Step 4: Save templates to database
        saved_count = 0
        for template in templates:
            success = self._save_template_to_db(template, match_id, ground_name)
            if success:
                saved_count += 1
        
        print(f"✅ Generated and saved {saved_count} templates based on {len(match_analyses)} matches")
        return saved_count > 0
    
    def _extract_scorecard_urls(self, ground_results_url):
        """Extract scorecard URLs from 'Twenty20' links in ground results table"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(ground_results_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            scorecard_urls = []
            
            print("🔍 Looking for 'Twenty20' links in ground results table...")
            
            # Method 1: Look for links with text "Twenty20" or "T20"
            twenty20_links = soup.find_all('a', string=lambda text: text and ('Twenty20' in text or 'T20' in text))
            
            for link in twenty20_links:
                href = link.get('href')
                if href:
                    if not href.startswith('http'):
                        href = 'https://www.espncricinfo.com' + href
                    scorecard_urls.append(href)
                    print(f"   ✅ Found Twenty20 link: {href}")
            
            # Method 2: Look in table rows for Twenty20 links after date columns
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    # Look for date pattern in first few cells, then Twenty20 link in subsequent cells
                    for i, cell in enumerate(cells):
                        # Check if this cell contains a date (various formats)
                        cell_text = cell.get_text().strip()
                        if any(month in cell_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or \
                           any(char.isdigit() for char in cell_text) and len(cell_text) > 4:
                            
                            # Look for Twenty20 links in the next few cells
                            for j in range(i+1, min(i+4, len(cells))):
                                if j < len(cells):
                                    next_cell = cells[j]
                                    twenty20_link = next_cell.find('a', string=lambda text: text and 
                                                                  ('Twenty20' in text or 'T20' in text or 'ODI' in text))
                                    
                                    if twenty20_link:
                                        href = twenty20_link.get('href')
                                        if href:
                                            if not href.startswith('http'):
                                                href = 'https://www.espncricinfo.com' + href
                                            scorecard_urls.append(href)
                                            print(f"   ✅ Found table Twenty20 link: {href}")
            
            # Method 3: Look for any links that might lead to scorecards (fallback)
            if not scorecard_urls:
                print("   ⚠️ No Twenty20 links found, trying fallback method...")
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    link_text = link.get_text().strip().lower()
                    
                    # Look for match-related links
                    if any(keyword in href for keyword in ['scorecard', 'match']) or \
                       any(keyword in link_text for keyword in ['scorecard', 'match', 'vs']):
                        if not href.startswith('http'):
                            href = 'https://www.espncricinfo.com' + href
                        scorecard_urls.append(href)
                        print(f"   ✅ Found fallback link: {href}")
            
            # Remove duplicates and filter valid URLs
            unique_urls = list(set(scorecard_urls))
            
            # Filter for actual scorecard URLs
            valid_urls = []
            for url in unique_urls:
                if any(keyword in url for keyword in ['scorecard', 'match']) and \
                   not any(exclude in url for exclude in ['series', 'team', 'player', 'stats']):
                    valid_urls.append(url)
            
            print(f"🔗 Found {len(valid_urls)} valid scorecard URLs")
            
            return valid_urls[:10]  # Limit to 10 matches
            
        except Exception as e:
            print(f"❌ Error extracting scorecard URLs: {e}")
            return []
    
    def _extract_scorecard_from_match_link(self, match_url):
        """Convert a match URL to its full scorecard URL"""
        try:
            # If it's already a scorecard URL, return as is
            if 'scorecard' in match_url:
                return match_url
            
            # Extract match ID from the URL
            import re
            match_id_pattern = r'/(\d+)\.html'
            match = re.search(match_id_pattern, match_url)
            
            if match:
                match_id = match.group(1)
                # Convert to full scorecard URL
                scorecard_url = f"https://www.espncricinfo.com/series/{match_id}/full-scorecard"
                return scorecard_url
            
            # If we can't extract match ID, try to fetch the page and look for scorecard link
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(match_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for scorecard link on the match page
            scorecard_link = soup.find('a', href=lambda href: href and 'scorecard' in href)
            if scorecard_link:
                href = scorecard_link['href']
                if not href.startswith('http'):
                    href = 'https://www.espncricinfo.com' + href
                return href
            
            return match_url  # Return original if we can't convert
            
        except Exception as e:
            print(f"⚠️ Error converting match URL to scorecard: {e}")
            return match_url
    
    def _analyze_scorecard(self, scorecard_url):
        """Analyze a single scorecard to get top 11 performers and their roles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(scorecard_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract match teams
            teams = self._extract_team_names(soup)
            
            # Extract all player performances
            all_players = self._extract_all_player_data(soup, teams)
            
            if len(all_players) < 11:
                print(f"⚠️ Only found {len(all_players)} players, skipping this match")
                return None
            
            # Calculate fantasy points for each player
            for player in all_players:
                player['fantasy_points'] = self._calculate_fantasy_points(player)
            
            # Get top 11 performers
            top_11 = sorted(all_players, key=lambda x: x['fantasy_points'], reverse=True)[:11]
            
            print(f"🏆 DREAM11 TEAM - Top 11 performers (fantasy points):")
            print("=" * 70)
            
            # Print detailed Dream11 team
            total_points = 0
            role_count = {'TOP': 0, 'MID': 0, 'HIT': 0, 'POW': 0, 'BRE': 0, 'DEA': 0}
            team_count = {'A': 0, 'B': 0}
            
            for i, player in enumerate(top_11, 1):
                captain_mark = "🔥 (C)" if i == 1 else "⭐ (VC)" if i == 2 else ""
                print(f"   {i:2d}. {player['name']:<20} ({player['team']}) - {player['fantasy_points']:3.0f} pts - {player['role']} {captain_mark}")
                
                # Performance breakdown
                if player['runs'] > 0 or player['balls'] > 0:
                    sr = (player['runs'] / player['balls'] * 100) if player['balls'] > 0 else 0
                    print(f"       Batting: {player['runs']} runs ({player['balls']} balls, SR: {sr:.1f}) | {player['fours']}x4, {player['sixes']}x6")
                
                if player['wickets'] > 0 or player['overs'] > 0:
                    economy = (player['runs_conceded'] / player['overs']) if player['overs'] > 0 else 0
                    print(f"       Bowling: {player['wickets']} wickets ({player['overs']} overs, Econ: {economy:.1f}) | {player['maidens']} maidens")
                
                if player['catches'] > 0 or player['stumpings'] > 0 or player['run_outs'] > 0:
                    print(f"       Fielding: {player['catches']} catches, {player['stumpings']} stumpings, {player['run_outs']} run-outs")
                
                print()  # Empty line for readability
                
                # Count statistics
                total_points += player['fantasy_points']
                if player['role'] in role_count:
                    role_count[player['role']] += 1
                else:
                    role_count[player['role']] = 1
                
                if player['team'] in team_count:
                    team_count[player['team']] += 1
                else:
                    team_count[player['team']] = 1
            
            print("=" * 70)
            print(f"📊 DREAM11 TEAM SUMMARY:")
            print(f"   Total Fantasy Points: {total_points:.0f}")
            # Show actual team distribution
            team_names = list(team_count.keys())
            team_dist = " | ".join([f"{team}: {count}" for team, count in team_count.items()])
            print(f"   Team Distribution: {team_dist}")
            
            # Show actual role distribution
            role_dist = " | ".join([f"{role}: {count}" for role, count in role_count.items()])
            print(f"   Role Distribution: {role_dist}")
            
            # Generate composition based on top 11 roles
            composition = self._calculate_composition_from_top11(top_11)
            print(f"   Template Composition: {composition}")
            print("=" * 70)
            
            # Save Dream11 team to JSON file
            try:
                self._save_dream11_team_to_file(top_11, teams, scorecard_url)
            except Exception as e:
                print(f"⚠️ Error saving Dream11 team to file: {e}")
            
            return {
                'teams': teams,
                'top_11': top_11,
                'composition': composition,
                'url': scorecard_url
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Error analyzing scorecard: {e}")
            print(f"📍 Error details: {traceback.format_exc()}")
            return None
    
    def _extract_team_names(self, soup):
        """Extract team names from scorecard"""
        try:
            # Look for team names in various possible locations
            team_elements = soup.find_all(['h2', 'h3', 'span'], class_=re.compile(r'team|title'))
            
            teams = []
            for elem in team_elements:
                text = elem.get_text().strip()
                if len(text) > 2 and len(text) < 20 and not any(x in text.lower() for x in ['scorecard', 'match', 'result']):
                    teams.append(text)
            
            # Return first two unique team names
            unique_teams = []
            for team in teams:
                if team not in unique_teams:
                    unique_teams.append(team)
                if len(unique_teams) == 2:
                    break
            
            return unique_teams if len(unique_teams) == 2 else ['Team A', 'Team B']
            
        except:
            return ['Team A', 'Team B']
    
    def _extract_all_player_data(self, soup, teams):
        """Extract all player data from scorecard"""
        players = []
        
        try:
            # Find all tables (batting and bowling)
            tables = soup.find_all('table')
            
            for table_idx, table in enumerate(tables):
                # Determine if this is batting or bowling table
                headers = [th.get_text().strip().lower() for th in table.find_all(['th', 'td'])[:10]]
                
                # Check if this is a batting table (and not a league table)
                if any(keyword in ' '.join(headers) for keyword in ['batting', 'runs', 'balls', 'r', 'b']) and \
                   not any(keyword in ' '.join(headers) for keyword in ['bowling', 'overs', 'wickets', 'team', 'pt', 'points']) and \
                   len(headers) >= 3:  # Ensure it's a proper scorecard table
                    # This is a batting table
                    print(f"   🏏 Found batting table {table_idx + 1}")
                    batting_players = self._extract_batting_data(table, teams, table_idx)
                    
                    # Filter out duplicate players and non-players
                    valid_players = []
                    seen_names = set()
                    for player in batting_players:
                        # Skip team abbreviations and duplicate names
                        if len(player['name']) > 3 and \
                           player['name'] not in seen_names and \
                           not player['name'].isupper() and \
                           player['name'] not in ['GLO', 'WAR', 'NOR', 'WOR', 'GLA', 'SOM', 'LEI', 'DER', 'YOR', 'LAN', 'NOT', 'DUR', 'SUR', 'SUS', 'KEN', 'MID', 'ESS', 'HAM']:
                            valid_players.append(player)
                            seen_names.add(player['name'])
                    
                    players.extend(valid_players)
                    
                    # Stop after finding 2 batting tables (one for each team)
                    if len([p for p in players if p['runs'] > 0 or p['balls'] > 0]) >= 15:
                        break
                    
                elif any(keyword in ' '.join(headers) for keyword in ['bowling', 'overs', 'wickets', 'o', 'm', 'w']):
                    # This is a bowling table
                    print(f"   🎳 Found bowling table {table_idx + 1}")
                    players.extend(self._extract_bowling_data(table, teams, table_idx))
            
            return players
            
        except Exception as e:
            print(f"❌ Error extracting player data: {e}")
            return []
    
    def _extract_batting_data(self, table, teams, table_idx):
        """Extract batting data from a batting table"""
        players = []
        team = teams[0] if table_idx < 2 else teams[1] if len(teams) > 1 else 'Team A'
        
        try:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for position, row in enumerate(rows, 1):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    # Try different approaches to extract player name
                    name_cell = cells[0]
                    
                    # Method 1: Look for player name in links
                    player_link = name_cell.find('a')
                    if player_link:
                        player_name = player_link.get_text().strip()
                    else:
                        # Method 2: Get text directly
                        player_name = name_cell.get_text().strip()
                    
                    # Skip non-player rows
                    if any(keyword in player_name.lower() for keyword in ['extras', 'total', 'fall', 'did not bat', 'yet to bat']):
                        continue
                    
                    # Skip if it's just position numbers or generic text
                    if player_name.lower() in ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th'] or \
                       player_name.isdigit() or len(player_name) < 2:
                        continue
                    
                    # Clean player name
                    player_name = re.sub(r'[†*‡§]', '', player_name).strip()
                    if not player_name:
                        continue
                    
                    # Extract batting stats - try different cell positions
                    runs = 0
                    balls = 0
                    fours = 0
                    sixes = 0
                    
                    # Look for runs in different cells (ESPN format varies)
                    for i in range(1, min(len(cells), 8)):
                        cell_text = cells[i].get_text().strip()
                        
                        # Look for runs (usually a number)
                        if cell_text.isdigit() and runs == 0:
                            runs = self._safe_int(cell_text)
                        
                        # Look for balls (often in parentheses or after runs)
                        elif '(' in cell_text and ')' in cell_text:
                            balls_match = re.search(r'\((\d+)\)', cell_text)
                            if balls_match:
                                balls = int(balls_match.group(1))
                        
                        # Look for boundaries (4s and 6s)
                        elif 'x4' in cell_text.lower() or cell_text == '4':
                            fours = self._safe_int(re.sub(r'[^\d]', '', cell_text))
                        elif 'x6' in cell_text.lower() or cell_text == '6':
                            sixes = self._safe_int(re.sub(r'[^\d]', '', cell_text))
                    
                    # If we still don't have stats, try standard positions
                    if runs == 0 and len(cells) > 2:
                        runs = self._safe_int(cells[2].get_text())
                    if balls == 0 and len(cells) > 3:
                        balls = self._safe_int(cells[3].get_text())
                    if fours == 0 and len(cells) > 4:
                        fours = self._safe_int(cells[4].get_text())
                    if sixes == 0 and len(cells) > 5:
                        sixes = self._safe_int(cells[5].get_text())
                    
                    # Determine role based on batting position
                    role = self._determine_batting_role(position)
                    
                    player = {
                        'name': player_name,
                        'team': team,
                        'role': role,
                        'batting_position': position,
                        'runs': runs,
                        'balls': balls,
                        'fours': fours,
                        'sixes': sixes,
                        'wickets': 0,
                        'overs': 0,
                        'maidens': 0,
                        'runs_conceded': 0,
                        'catches': 0,
                        'stumpings': 0,
                        'run_outs': 0
                    }
                    
                    players.append(player)
                    print(f"   📝 Extracted: {player_name} ({team}) - {runs} runs, {balls} balls")
                    
                    if len(players) >= 11:  # Limit per team
                        break
            
        except Exception as e:
            print(f"❌ Error extracting batting data: {e}")
        
        return players
    
    def _extract_bowling_data(self, table, teams, table_idx):
        """Extract bowling data and merge with existing players or create new ones"""
        bowling_players = []
        team = teams[0] if table_idx < 2 else teams[1] if len(teams) > 1 else 'Team A'
        
        try:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    # Extract bowler name
                    name_cell = cells[0]
                    
                    # Method 1: Look for player name in links
                    player_link = name_cell.find('a')
                    if player_link:
                        player_name = player_link.get_text().strip()
                    else:
                        # Method 2: Get text directly
                        player_name = name_cell.get_text().strip()
                    
                    # Skip non-player rows
                    if any(keyword in player_name.lower() for keyword in ['extras', 'total', 'fall', 'did not bowl']):
                        continue
                    
                    # Clean player name
                    player_name = re.sub(r'[†*‡§]', '', player_name).strip()
                    if not player_name or len(player_name) < 2:
                        continue
                    
                    # Extract bowling stats
                    overs = 0
                    maidens = 0
                    runs_conceded = 0
                    wickets = 0
                    
                    # Parse bowling figures (O-M-R-W format)
                    try:
                        if len(cells) >= 5:
                            overs = self._safe_float(cells[1].get_text())
                            maidens = self._safe_int(cells[2].get_text())
                            runs_conceded = self._safe_int(cells[3].get_text())
                            wickets = self._safe_int(cells[4].get_text())
                    except:
                        pass
                    
                    # Determine bowling role based on economy and wickets
                    bowling_role = self._determine_bowling_role(overs, wickets, runs_conceded)
                    
                    bowling_player = {
                        'name': player_name,
                        'team': team,
                        'role': bowling_role,
                        'batting_position': 11,  # Default for bowlers
                        'runs': 0,  # Will be updated if batting data exists
                        'balls': 0,
                        'fours': 0,
                        'sixes': 0,
                        'wickets': wickets,
                        'overs': overs,
                        'maidens': maidens,
                        'runs_conceded': runs_conceded,
                        'catches': 0,
                        'stumpings': 0,
                        'run_outs': 0
                    }
                    
                    bowling_players.append(bowling_player)
                    print(f"   🎳 Extracted bowler: {player_name} ({team}) - {wickets} wickets, {overs} overs, {runs_conceded} runs")
            
        except Exception as e:
            print(f"❌ Error extracting bowling data: {e}")
        
        return bowling_players
    
    def _safe_float(self, text):
        """Safely convert text to float (for overs)"""
        try:
            # Handle overs format like "4.0" or "3.2"
            return float(str(text).strip())
        except:
            return 0.0
    
    def _determine_bowling_role(self, overs, wickets, runs_conceded):
        """Determine bowling role based on performance"""
        if overs == 0:
            return 'BRE'  # Didn't bowl
        
        economy = runs_conceded / overs if overs > 0 else 10
        
        # Death bowlers: Usually bowl in pressure situations, may have higher economy but take wickets
        if wickets >= 2 and economy <= 8:
            return 'DEA'  # Death bowler
        # Powerplay bowlers: Good economy, wickets in early overs
        elif wickets >= 1 and economy <= 6:
            return 'POW'  # Powerplay bowler
        # Breakthrough bowlers: Take wickets but may be expensive
        elif wickets >= 2:
            return 'BRE'  # Breakthrough bowler
        # Economic bowlers: Low economy, control the game
        elif economy <= 5:
            return 'BRE'  # Economical bowler
        else:
            return 'BRE'  # General bowler
    
    def _safe_int(self, text):
        """Safely convert text to integer"""
        try:
            # Extract first number from text
            numbers = re.findall(r'\d+', str(text))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _determine_batting_role(self, position):
        """Determine player role based on batting position"""
        if position in [1, 2]:
            return 'TOP'  # Openers
        elif position in [3, 4]:
            return 'MID'  # Middle order
        elif position in [5, 6]:
            return 'HIT'  # Finishers
        elif position == 7:
            return 'POW'  # Power hitter
        else:
            return 'BRE'  # Tail/Breakers
    
    def _calculate_fantasy_points(self, player):
        """Calculate fantasy points based on player performance"""
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
        
        # Strike rate bonus (if SR > 150, +2 points; if SR > 100, +1 point)
        if player['balls'] > 0:
            strike_rate = (player['runs'] / player['balls']) * 100
            if strike_rate > 150:
                points += 2
            elif strike_rate > 100:
                points += 1
        
        # Bowling points
        points += player['wickets'] * self.fantasy_points_rules['wicket']
        points += player['maidens'] * self.fantasy_points_rules['maiden']
        
        # Economy bonus (if economy < 4, +4 points; if < 6, +2 points)
        if player['overs'] > 0:
            economy = player['runs_conceded'] / player['overs']
            if economy < 4:
                points += 4
            elif economy < 6:
                points += 2
        
        # Fielding points
        points += player['catches'] * self.fantasy_points_rules['catch']
        points += player['stumpings'] * self.fantasy_points_rules['stumping']
        points += player['run_outs'] * self.fantasy_points_rules['run_out']
        
        return points
    
    def _calculate_composition_from_top11(self, top_11):
        """Calculate template composition based on top 11 performers' roles"""
        composition = {
            'atop': 0, 'amid': 0, 'ahit': 0, 'apow': 0, 'abre': 0, 'adea': 0,
            'btop': 0, 'bmid': 0, 'bhit': 0, 'bpow': 0, 'bbre': 0, 'bdea': 0
        }
        
        # Get unique team names from top 11
        teams_in_top11 = list(set(player['team'] for player in top_11))
        team_a = teams_in_top11[0] if len(teams_in_top11) > 0 else 'Team A'
        
        for player in top_11:
            team_prefix = 'a' if player['team'] == team_a else 'b'
            role = player['role'].lower()
            
            # Map role to composition key
            if role == 'top':
                key = f'{team_prefix}top'
            elif role == 'mid':
                key = f'{team_prefix}mid'
            elif role == 'hit':
                key = f'{team_prefix}hit'
            elif role == 'pow':
                key = f'{team_prefix}pow'
            elif role == 'bre':
                key = f'{team_prefix}bre'
            elif role == 'dea':  # Death bowlers
                key = f'{team_prefix}dea'
            else:
                key = f'{team_prefix}mid'  # Default to middle order
            
            if key in composition:
                composition[key] += 1
        
        return composition
    
    def _generate_templates_from_matches(self, match_analyses, ground_name):
        """Generate templates based on multiple match analyses"""
        if not match_analyses:
            return []
        
        # Aggregate all compositions
        total_composition = {
            'atop': 0, 'amid': 0, 'ahit': 0, 'apow': 0, 'abre': 0, 'adea': 0,
            'btop': 0, 'bmid': 0, 'bhit': 0, 'bpow': 0, 'bbre': 0, 'bdea': 0
        }
        
        for analysis in match_analyses:
            comp = analysis['composition']
            for key in total_composition:
                total_composition[key] += comp.get(key, 0)
        
        # Calculate average composition
        num_matches = len(match_analyses)
        avg_composition = {}
        for key, total in total_composition.items():
            avg_composition[key] = round(total / num_matches)
        
        # Ensure total equals 11
        total_players = sum(avg_composition.values())
        if total_players != 11:
            # Adjust to make total 11
            diff = 11 - total_players
            sorted_roles = sorted(avg_composition.items(), key=lambda x: x[1], reverse=True)
            
            for role, count in sorted_roles:
                if diff == 0:
                    break
                if diff > 0 and count < 3:  # Don't exceed 3 per role
                    avg_composition[role] += 1
                    diff -= 1
                elif diff < 0 and count > 0:
                    avg_composition[role] -= 1
                    diff += 1
        
        # Create template
        template = {
            'name': f'{ground_name} - Performance Based Strategy',
            'stadium': ground_name,
            'winning': 'Data Driven',
            'composition': avg_composition,
            'matches_analyzed': num_matches,
            'description': f'Based on top performers from {num_matches} actual matches at {ground_name}'
        }
        
        # Print summary of all Dream11 teams analyzed
        self._print_dream11_teams_summary(match_analyses, ground_name)
        
        return [template]
    
    def _print_dream11_teams_summary(self, match_analyses, ground_name):
        """Print summary of all Dream11 teams from analyzed matches"""
        print(f"\n🏆 DREAM11 TEAMS SUMMARY - {ground_name}")
        print("=" * 80)
        
        for i, analysis in enumerate(match_analyses, 1):
            print(f"\n🏏 Match {i}: {analysis['teams'][0]} vs {analysis['teams'][1]}")
            print(f"   URL: {analysis['url']}")
            
            top_11 = analysis['top_11']
            total_points = sum(player['fantasy_points'] for player in top_11)
            
            print(f"   Dream11 Team (Total: {total_points:.0f} points):")
            for j, player in enumerate(top_11[:5], 1):  # Show top 5
                captain_mark = "🔥" if j == 1 else "⭐" if j == 2 else ""
                print(f"     {j}. {player['name']:<15} ({player['team']}) - {player['fantasy_points']:3.0f} pts {captain_mark}")
            
            if len(top_11) > 5:
                print(f"     ... and {len(top_11) - 5} more players")
            
            # Show composition derived from this match
            composition = analysis['composition']
            comp_str = f"atop:{composition.get('atop',0)} amid:{composition.get('amid',0)} ahit:{composition.get('ahit',0)} "
            comp_str += f"btop:{composition.get('btop',0)} bmid:{composition.get('bmid',0)} bhit:{composition.get('bhit',0)}"
            print(f"   Template Contribution: {comp_str}")
        
        print("\n" + "=" * 80)
    
    def _save_template_to_db(self, template, match_id, ground_name):
        """Save template to database"""
        try:
            comp = template['composition']
            
            success = addDreamTeam(
                matchbetween=template['name'],
                stadium=template['stadium'],
                wininning=template['winning'],
                one=str(comp.get('atop', 0)),
                two=str(comp.get('amid', 0)),
                three=str(comp.get('ahit', 0)),
                four=str(comp.get('bpow', 0)),
                five=str(comp.get('bbre', 0)),
                six=str(comp.get('bdea', 0)),
                seven=str(comp.get('btop', 0)),
                eight=str(comp.get('bmid', 0)),
                nine=str(comp.get('bhit', 0)),
                ten=str(comp.get('apow', 0)),
                eleven=str(comp.get('abre', 0)),
                twelve=str(comp.get('adea', 0)),
                cap=0,
                vc=1,
                source_match_id=match_id
            )
            
            if success:
                print(f"✅ Saved template: {template['name']}")
            else:
                print(f"❌ Failed to save template: {template['name']}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error saving template: {e}")
            return False
    
    def _save_dream11_team_to_file(self, top_11, teams, scorecard_url):
        """Save the Dream11 team to a JSON file"""
        try:
            from datetime import datetime
            import json
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dream11_team_{timestamp}.json"
            
            # Prepare Dream11 team data
            dream11_data = {
                "metadata": {
                    "generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "match": f"{teams[0]} vs {teams[1]}" if len(teams) >= 2 else "Unknown Match",
                    "scorecard_url": scorecard_url,
                    "total_fantasy_points": sum(player['fantasy_points'] for player in top_11),
                    "generation_method": "Actual Scorecard Analysis"
                },
                "dream11_team": []
            }
            
            # Add each player with detailed stats
            for i, player in enumerate(top_11, 1):
                player_data = {
                    "position": i,
                    "name": player['name'],
                    "team": player['team'],
                    "role": player['role'],
                    "fantasy_points": player['fantasy_points'],
                    "is_captain": i == 1,
                    "is_vice_captain": i == 2,
                    "batting_stats": {
                        "runs": player['runs'],
                        "balls": player['balls'],
                        "fours": player['fours'],
                        "sixes": player['sixes'],
                        "strike_rate": (player['runs'] / player['balls'] * 100) if player['balls'] > 0 else 0
                    },
                    "bowling_stats": {
                        "wickets": player['wickets'],
                        "overs": player['overs'],
                        "maidens": player['maidens'],
                        "runs_conceded": player['runs_conceded'],
                        "economy": (player['runs_conceded'] / player['overs']) if player['overs'] > 0 else 0
                    },
                    "fielding_stats": {
                        "catches": player['catches'],
                        "stumpings": player['stumpings'],
                        "run_outs": player['run_outs']
                    }
                }
                dream11_data["dream11_team"].append(player_data)
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dream11_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Dream11 team saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving Dream11 team to file: {e}")

def main():
    """Test the ground scorecard analyzer"""
    analyzer = GroundScorecardAnalyzer()
    
    # Example usage
    ground_url = "https://www.espncricinfo.com/series/ipl-2024-1410320/points-table-standings"
    match_id = 39
    ground_name = "Test Ground"
    
    success = analyzer.analyze_ground_and_generate_templates(ground_url, match_id, ground_name)
    
    if success:
        print("🎉 Successfully generated templates from ground analysis!")
    else:
        print("❌ Failed to generate templates")

if __name__ == "__main__":
    main()