#!/usr/bin/env python3
"""
Dream11 Team Manager
Complete utility for managing Dream11 teams via API
"""

import requests
import json
import sys
import argparse
from datetime import datetime

class Dream11API:
    """Dream11 API Client Class"""
    
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://tg-backend.site/api/fantasy"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
    
    def _make_request(self, endpoint, payload, operation_name):
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            print(f"🚀 {operation_name}...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {operation_name} successful!")
                return data
            else:
                print(f"❌ {operation_name} failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ {operation_name} error: {e}")
            return None
    
    def fetch_teams(self, match_id):
        """Fetch all teams for a match"""
        payload = {
            "fantasyApp": "dream11",
            "matchId": match_id,
            "authToken": self.auth_token
        }
        return self._make_request("list-of-teams", payload, "Fetching teams")
    
    def add_team(self, match_id, captain, vice_captain, players, sport_index=0, team_type="new"):
        """Add a new team"""
        payload = {
            "matchId": match_id,
            "captain": captain,
            "vice_captain": vice_captain,
            "players": players,
            "fantasyApp": "dream11",
            "authToken": self.auth_token,
            "sportIndex": sport_index,
            "type": team_type
        }
        return self._make_request("add-team", payload, "Adding team")
    
    def bulk_add_teams(self, match_id, teams_data):
        """Add multiple teams at once"""
        results = []
        total_teams = len(teams_data)
        
        print(f"🔄 Adding {total_teams} teams...")
        
        for i, team_data in enumerate(teams_data, 1):
            print(f"\n📤 Adding team {i}/{total_teams}")
            
            result = self.add_team(
                match_id=match_id,
                captain=team_data['captain'],
                vice_captain=team_data['vice_captain'],
                players=team_data['players']
            )
            
            if result:
                results.append({
                    'team_number': i,
                    'team_id': result.get('teamId'),
                    'status': result.get('status'),
                    'original_data': team_data
                })
                print(f"✅ Team {i} added successfully (ID: {result.get('teamId')})")
            else:
                print(f"❌ Team {i} failed to add")
                results.append({
                    'team_number': i,
                    'status': 'failed',
                    'original_data': team_data
                })
        
        return results

def save_to_file(data, filename):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def load_from_file(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"📂 Data loaded from: {filename}")
        return data
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def convert_fetched_to_addable(fetched_teams):
    """Convert fetched teams format to addable format"""
    addable_teams = []
    
    for team in fetched_teams.get('teams_list', []):
        addable_team = {
            'captain': team['captain'],
            'vice_captain': team['vice_captain'],
            'players': team['player_list']
        }
        addable_teams.append(addable_team)
    
    return addable_teams

def main():
    parser = argparse.ArgumentParser(description='Dream11 Team Manager')
    parser.add_argument('operation', choices=['fetch', 'add', 'bulk-add', 'convert'], 
                       help='Operation to perform')
    parser.add_argument('--match-id', required=True, help='Match ID')
    parser.add_argument('--auth-token', required=True, help='Authentication token')
    parser.add_argument('--input-file', help='Input file for bulk operations')
    parser.add_argument('--output-file', help='Output file to save results')
    parser.add_argument('--captain', type=int, help='Captain player ID (for add operation)')
    parser.add_argument('--vice-captain', type=int, help='Vice-captain player ID (for add operation)')
    parser.add_argument('--players', help='Comma-separated player IDs (for add operation)')
    
    args = parser.parse_args()
    
    # Initialize API client
    api = Dream11API(args.auth_token)
    
    print("🏏 Dream11 Team Manager")
    print("=" * 40)
    print(f"🎯 Operation: {args.operation}")
    print(f"📊 Match ID: {args.match_id}")
    print()
    
    if args.operation == 'fetch':
        # Fetch teams
        result = api.fetch_teams(args.match_id)
        
        if result:
            # Save to file
            output_file = args.output_file or f"teams_fetch_{args.match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_to_file(result, output_file)
            
            # Show summary
            teams = result.get('teams_list', [])
            print(f"\n📊 Summary: Fetched {len(teams)} teams")
    
    elif args.operation == 'add':
        # Add single team
        if not all([args.captain, args.vice_captain, args.players]):
            print("❌ For add operation, --captain, --vice-captain, and --players are required")
            sys.exit(1)
        
        players = [int(p.strip()) for p in args.players.split(',')]
        
        if len(players) != 11:
            print(f"❌ Exactly 11 players required, got {len(players)}")
            sys.exit(1)
        
        result = api.add_team(args.match_id, args.captain, args.vice_captain, players)
        
        if result:
            output_file = args.output_file or f"team_add_{args.match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_to_file(result, output_file)
            print(f"\n✅ Team added successfully (ID: {result.get('teamId')})")
    
    elif args.operation == 'bulk-add':
        # Bulk add teams
        if not args.input_file:
            print("❌ For bulk-add operation, --input-file is required")
            sys.exit(1)
        
        teams_data = load_from_file(args.input_file)
        if not teams_data:
            sys.exit(1)
        
        # Convert if needed (if input is from fetch operation)
        if 'teams_list' in teams_data:
            print("🔄 Converting fetched teams format...")
            teams_data = convert_fetched_to_addable(teams_data)
        
        results = api.bulk_add_teams(args.match_id, teams_data)
        
        # Save results
        output_file = args.output_file or f"bulk_add_results_{args.match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_to_file(results, output_file)
        
        # Show summary
        successful = len([r for r in results if r.get('status') == 'success'])
        print(f"\n📊 Summary: {successful}/{len(results)} teams added successfully")
    
    elif args.operation == 'convert':
        # Convert fetched teams to addable format
        if not args.input_file:
            print("❌ For convert operation, --input-file is required")
            sys.exit(1)
        
        fetched_data = load_from_file(args.input_file)
        if not fetched_data:
            sys.exit(1)
        
        converted_teams = convert_fetched_to_addable(fetched_data)
        
        output_file = args.output_file or f"converted_teams_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_to_file(converted_teams, output_file)
        
        print(f"\n✅ Converted {len(converted_teams)} teams")

if __name__ == "__main__":
    main()