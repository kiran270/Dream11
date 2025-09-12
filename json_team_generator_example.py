#!/usr/bin/env python3
"""
Dream11 Team Generator - JSON Storage Example
This demonstrates how to generate teams and store them in JSON format
instead of using database tables.
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any

class JSONTeamGenerator:
    def __init__(self):
        self.teams_data = {
            "metadata": {
                "generated_on": "",
                "match": "",
                "total_teams": 0,
                "match_id": "",
                "auth_token": "YOUR_AUTH_TOKEN"
            },
            "teams": []
        }
    
    def generate_teams(self, players: List[Dict], team_a_name: str, team_b_name: str, 
                      num_teams: int = 100, match_id: str = None) -> Dict:
        """
        Generate Dream11 teams and store in JSON format
        
        Args:
            players: List of player dictionaries
            team_a_name: Name of team A
            team_b_name: Name of team B
            num_teams: Number of teams to generate
            match_id: Match ID for Dream11
        
        Returns:
            Dictionary containing all team data in JSON format
        """
        print(f"🏏 Generating {num_teams} teams for {team_a_name} vs {team_b_name}")
        
        # Update metadata with actual or placeholder match_id
        actual_match_id = match_id if match_id else "YOUR_MATCH_ID"
        
        self.teams_data["metadata"].update({
            "generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "match": f"{team_a_name} vs {team_b_name}",
            "match_id": actual_match_id,
            "team_a": team_a_name,
            "team_b": team_b_name
        })
        
        # Separate players by team
        team_a_players = [p for p in players if p.get('team') == 'A']
        team_b_players = [p for p in players if p.get('team') == 'B']
        
        print(f"📊 Team A players: {len(team_a_players)}")
        print(f"📊 Team B players: {len(team_b_players)}")
        
        # Generate teams
        generated_teams = []
        print(f"🔄 Generating teams...")
        for i in range(1, num_teams + 1):
            team = self._generate_single_team(team_a_players, team_b_players, i)
            if team:
                generated_teams.append(team)
            
            # Show progress every 20 teams
            if i % 20 == 0:
                print(f"📊 Progress: {i}/{num_teams} teams processed ({len(generated_teams)} successful)")
        
        print(f"✅ Team generation completed: {len(generated_teams)}/{num_teams} teams generated")
        
        self.teams_data["teams"] = generated_teams
        self.teams_data["metadata"]["total_teams"] = len(generated_teams)
        
        print(f"✅ Generated {len(generated_teams)} valid teams")
        return self.teams_data
    
    def _generate_single_team(self, team_a_players: List[Dict], team_b_players: List[Dict], 
                             team_id: int) -> Dict:
        """Generate a single team with 11 unique players"""
        
        # Ensure we have enough total players
        total_available = len(team_a_players) + len(team_b_players)
        if total_available < 11:
            print(f"⚠️ Team {team_id}: Not enough total players ({total_available}) to form a team")
            return None
        
        # Simple team composition: 6 from team A, 5 from team B (adjust if needed)
        max_from_a = min(6, len(team_a_players))
        max_from_b = min(5, len(team_b_players))
        
        # Adjust if we don't have enough from one team
        if max_from_a + max_from_b < 11:
            if len(team_a_players) >= 11:
                max_from_a = 11
                max_from_b = 0
            elif len(team_b_players) >= 11:
                max_from_a = 0
                max_from_b = 11
            else:
                max_from_a = len(team_a_players)
                max_from_b = len(team_b_players)
        
        selected_a = random.sample(team_a_players, max_from_a) if max_from_a > 0 else []
        selected_b = random.sample(team_b_players, max_from_b) if max_from_b > 0 else []
        
        all_selected = selected_a + selected_b
        
        # If we still need more players, fill from remaining players
        if len(all_selected) < 11:
            remaining_players = [p for p in team_a_players + team_b_players 
                               if p not in all_selected]
            needed = 11 - len(all_selected)
            if len(remaining_players) >= needed:
                additional = random.sample(remaining_players, needed)
                all_selected.extend(additional)
        
        # Ensure exactly 11 players
        all_selected = all_selected[:11]
        
        # Verify no duplicate player IDs
        seen_ids = set()
        unique_players = []
        
        for player in all_selected:
            player_id = player.get('id')
            if player_id not in seen_ids:
                seen_ids.add(player_id)
                unique_players.append(player)
            else:
                print(f"⚠️ Team {team_id}: Duplicate player ID {player_id} found, skipping")
        
        # If we lost players due to duplicates, fill from remaining
        if len(unique_players) < 11:
            remaining_players = [p for p in team_a_players + team_b_players 
                               if p.get('id') not in seen_ids]
            needed = 11 - len(unique_players)
            if len(remaining_players) >= needed:
                additional = random.sample(remaining_players, needed)
                for player in additional:
                    if player.get('id') not in seen_ids:
                        unique_players.append(player)
                        seen_ids.add(player.get('id'))
                        if len(unique_players) >= 11:
                            break
        
        all_selected = unique_players[:11]
        
        if len(all_selected) < 11:
            print(f"⚠️ Team {team_id}: Only {len(all_selected)} unique players available")
            return None
        
        # Verify all player IDs are unique
        player_ids = [p['id'] for p in all_selected]
        if len(set(player_ids)) != len(player_ids):
            print(f"❌ Team {team_id}: Duplicate player IDs found in final team")
            return None
        
        # Select captain and vice-captain (ensure they're different)
        captain = random.choice(all_selected)
        vice_captain_candidates = [p for p in all_selected if p['id'] != captain['id']]
        vice_captain = random.choice(vice_captain_candidates) if vice_captain_candidates else all_selected[1]
        
        # Only print progress for every 10th team to reduce output
        if team_id % 10 == 0 or team_id <= 5:
            print(f"✅ Team {team_id}: Generated with {len(all_selected)} unique players")
        
        return {
            "id": team_id,
            "name": f"Team {team_id}",
            "captain": captain['id'],
            "vice_captain": vice_captain['id'],
            "players": [p['id'] for p in all_selected],
            "player_details": [
                {
                    "id": p['id'],
                    "name": p['name'],
                    "team": p['team'],
                    "role": p['role'],
                    "credits": p.get('credits', 8.0),
                    "selected_by": p.get('selected_by', 50.0)
                } for p in all_selected
            ]
        }
    
    def save_to_file(self, filename: str = None) -> str:
        """Save teams data to JSON file"""
        if not filename:
            timestamp = datetime.now()
            filename = f"dream11_teams_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond:06d}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.teams_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Teams saved to: {filename}")
            print(f"💡 Edit the JSON file to add your match_id and auth_token")
            return filename
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            return ""
    
    def load_from_file(self, filename: str) -> bool:
        """Load teams data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.teams_data = json.load(f)
            print(f"📂 Teams loaded from: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error loading from file: {e}")
            return False
    
    def get_team_summary(self) -> Dict:
        """Get summary statistics of generated teams"""
        teams = self.teams_data.get("teams", [])
        
        if not teams:
            return {"total_teams": 0}
        
        # Calculate statistics
        total_teams = len(teams)
        total_unique_players = len(set(
            player_id for team in teams 
            for player_id in team.get("players", [])
        ))
        
        # Team composition analysis
        team_compositions = {}
        for team in teams:
            player_details = team.get("player_details", [])
            team_a_count = len([p for p in player_details if p.get("team") == "A"])
            team_b_count = len([p for p in player_details if p.get("team") == "B"])
            composition = f"{team_a_count}A-{team_b_count}B"
            team_compositions[composition] = team_compositions.get(composition, 0) + 1
        
        return {
            "total_teams": total_teams,
            "unique_players_used": total_unique_players,
            "team_compositions": team_compositions,
            "metadata": self.teams_data.get("metadata", {})
        }
    
    def validate_teams(self) -> bool:
        """Validate that all teams have unique players"""
        teams = self.teams_data.get("teams", [])
        
        print(f"\n🔍 VALIDATING TEAM UNIQUENESS:")
        print(f"   Checking {len(teams)} teams for duplicate players...")
        
        all_valid = True
        
        for team in teams:
            team_id = team.get("id", "Unknown")
            players = team.get("players", [])
            
            # Check for duplicates within the team
            if len(players) != len(set(players)):
                duplicates = [p for p in players if players.count(p) > 1]
                print(f"❌ Team {team_id}: Has duplicate players: {set(duplicates)}")
                all_valid = False
            elif len(players) != 11:
                print(f"❌ Team {team_id}: Has {len(players)} players instead of 11")
                all_valid = False
            else:
                print(f"✅ Team {team_id}: All {len(players)} players are unique")
        
        if all_valid:
            print(f"✅ All teams passed uniqueness validation!")
        else:
            print(f"❌ Some teams failed uniqueness validation!")
        
        return all_valid

    def export_for_dream11_api(self) -> List[Dict]:
        """Export teams in format suitable for Dream11 API"""
        api_teams = []
        
        for team in self.teams_data.get("teams", []):
            api_team = {
                "match_id": self.teams_data["metadata"]["match_id"],
                "team_id": team["id"],
                "captain": team["captain"],
                "vice_captain": team["vice_captain"],
                "players": team["players"],
                "auth_token": self.teams_data["metadata"]["auth_token"]
            }
            api_teams.append(api_team)
        
        return api_teams


def main():
    """Example usage of the JSON Team Generator"""
    
    # Sample player data
    sample_players = [
        {"id": 1, "name": "Virat Kohli", "team": "A", "role": "BAT", "credits": 11.0, "selected_by": 85.5},
        {"id": 2, "name": "Rohit Sharma", "team": "A", "role": "BAT", "credits": 10.5, "selected_by": 78.2},
        {"id": 3, "name": "KL Rahul", "team": "A", "role": "WK", "credits": 10.0, "selected_by": 72.1},
        {"id": 4, "name": "Hardik Pandya", "team": "A", "role": "AR", "credits": 9.5, "selected_by": 68.9},
        {"id": 5, "name": "Ravindra Jadeja", "team": "A", "role": "AR", "credits": 9.0, "selected_by": 65.3},
        {"id": 6, "name": "Jasprit Bumrah", "team": "A", "role": "BOWL", "credits": 9.5, "selected_by": 71.4},
        {"id": 7, "name": "Mohammed Shami", "team": "A", "role": "BOWL", "credits": 8.5, "selected_by": 58.7},
        {"id": 8, "name": "Yuzvendra Chahal", "team": "A", "role": "BOWL", "credits": 8.0, "selected_by": 52.3},
        {"id": 9, "name": "Shikhar Dhawan", "team": "A", "role": "BAT", "credits": 9.0, "selected_by": 61.8},
        {"id": 10, "name": "Rishabh Pant", "team": "A", "role": "WK", "credits": 9.5, "selected_by": 69.2},
        {"id": 11, "name": "Shreyas Iyer", "team": "A", "role": "BAT", "credits": 8.5, "selected_by": 55.6},
        
        {"id": 12, "name": "Babar Azam", "team": "B", "role": "BAT", "credits": 10.5, "selected_by": 82.1},
        {"id": 13, "name": "Mohammad Rizwan", "team": "B", "role": "WK", "credits": 10.0, "selected_by": 75.8},
        {"id": 14, "name": "Fakhar Zaman", "team": "B", "role": "BAT", "credits": 9.0, "selected_by": 63.4},
        {"id": 15, "name": "Shadab Khan", "team": "B", "role": "AR", "credits": 8.5, "selected_by": 59.7},
        {"id": 16, "name": "Imad Wasim", "team": "B", "role": "AR", "credits": 8.0, "selected_by": 48.9},
        {"id": 17, "name": "Shaheen Afridi", "team": "B", "role": "BOWL", "credits": 9.5, "selected_by": 73.2},
        {"id": 18, "name": "Haris Rauf", "team": "B", "role": "BOWL", "credits": 8.5, "selected_by": 56.1},
        {"id": 19, "name": "Naseem Shah", "team": "B", "role": "BOWL", "credits": 8.0, "selected_by": 51.8},
        {"id": 20, "name": "Mohammad Hafeez", "team": "B", "role": "AR", "credits": 8.0, "selected_by": 47.3},
        {"id": 21, "name": "Sarfaraz Ahmed", "team": "B", "role": "WK", "credits": 7.5, "selected_by": 42.6},
        {"id": 22, "name": "Asif Ali", "team": "B", "role": "BAT", "credits": 7.5, "selected_by": 38.9}
    ]
    
    # Initialize generator
    generator = JSONTeamGenerator()
    
    # Generate teams
    teams_data = generator.generate_teams(
        players=sample_players,
        team_a_name="India",
        team_b_name="Pakistan",
        num_teams=100,
        match_id="IND_vs_PAK_2024"
    )
    
    # Save to file
    filename = generator.save_to_file()
    
    # Validate teams
    generator.validate_teams()
    
    # Show summary
    summary = generator.get_team_summary()
    print(f"\n📊 TEAM GENERATION SUMMARY:")
    print(f"   Total teams: {summary['total_teams']}")
    print(f"   Unique players used: {summary['unique_players_used']}")
    print(f"   Team compositions: {summary['team_compositions']}")
    
    # Export for Dream11 API
    api_teams = generator.export_for_dream11_api()
    print(f"\n🔗 Dream11 API Format:")
    print(f"   Ready for {len(api_teams)} API calls")
    
    # Show first team as example
    if api_teams:
        print(f"\n📋 Example API call for Team 1:")
        first_team = api_teams[0]
        print(f"   match_id: {first_team['match_id']}")
        print(f"   team_id: {first_team['team_id']}")
        print(f"   captain: {first_team['captain']}")
        print(f"   vice_captain: {first_team['vice_captain']}")
        print(f"   players: {first_team['players']}")
    
    return filename


if __name__ == "__main__":
    main()