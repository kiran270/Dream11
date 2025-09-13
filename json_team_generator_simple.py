#!/usr/bin/env python3
"""
Simple JSON-based Team Generator
Demonstrates the approach used in your generateTeams functionality
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any, Tuple

def calculate_team_intersection(team1_players: List[int], team2_players: List[int]) -> int:
    """
    Calculate number of common players between two teams
    
    Args:
        team1_players: List of player IDs in team 1
        team2_players: List of player IDs in team 2
    
    Returns:
        Number of common players
    """
    return len(set(team1_players) & set(team2_players))

def remove_json_duplicate_teams(teams_list: List[Dict], quiet: bool = False) -> List[Dict]:
    """
    Remove teams that have more than 8 common players with other teams
    This works with JSON team format: {"players": [id1, id2, ...]}
    """
    if not teams_list or len(teams_list) <= 1:
        return teams_list
    
    if not quiet:
        print(f"🔍 Final cleanup: Checking {len(teams_list)} teams for duplicates (>8 common players)...")
    
    unique_teams = []
    removed_count = 0
    
    for i, current_team in enumerate(teams_list):
        is_duplicate = False
        current_players = set(current_team.get('players', []))
        
        if len(current_players) != 11:
            continue  # Skip invalid teams
        
        # Check against all previously accepted unique teams
        for existing_team in unique_teams:
            existing_players = set(existing_team.get('players', []))
            
            if len(existing_players) == 11:
                common_players = len(current_players & existing_players)
                
                if common_players > 8:  # More than 8 common = duplicate
                    is_duplicate = True
                    removed_count += 1
                    if not quiet and removed_count <= 3:  # Log first 3 removals
                        print(f"🗑️ Removed team {i+1}: {common_players} common players")
                    break
        
        if not is_duplicate:
            unique_teams.append(current_team)
    
    if not quiet and removed_count > 0:
        print(f"✅ Cleanup completed: Removed {removed_count} duplicate teams")
    
    return unique_teams

def check_sequential_team_diversity(new_team_players: List[int], existing_teams: List[Dict], 
                                   min_differences: int = 3, quiet: bool = False) -> bool:
    """
    Check if new team has sufficient diversity compared to ALL existing teams sequentially
    
    Sequential Logic:
    - T1 to T2: 3 players change
    - T1 to T3 AND T2 to T3: 3 players change each
    - T1 to T4 AND T2 to T4 AND T3 to T4: 3 players change each
    - And so on...
    
    Args:
        new_team_players: Player IDs in the new team
        existing_teams: List of existing team dictionaries (in order)
        min_differences: Minimum number of different players required (default: 3)
        quiet: If True, suppress detailed logging
    
    Returns:
        True if team has sufficient diversity from ALL existing teams, False otherwise
    """
    max_common_allowed = 11 - min_differences  # If min 3 differences, max 8 common
    
    team_number = len(existing_teams) + 1
    
    if not quiet and team_number <= 5:
        print(f"🔍 Checking T{team_number} diversity against {len(existing_teams)} existing teams...")
    
    # Check against EVERY existing team
    for i, existing_team in enumerate(existing_teams, 1):
        existing_players = existing_team.get('players', [])
        common_players = calculate_team_intersection(new_team_players, existing_players)
        different_players = 11 - common_players
        
        if common_players > max_common_allowed:
            if not quiet and team_number <= 5:
                print(f"❌ T{team_number} vs T{i}: Only {different_players} different players (need ≥{min_differences})")
            return False
        else:
            if not quiet and team_number <= 5:
                print(f"✅ T{team_number} vs T{i}: {different_players} different players")
    
    if not quiet and team_number <= 5:
        print(f"✅ T{team_number} passes diversity check against all {len(existing_teams)} teams")
    
    return True

def generate_teams_from_database(matchid: str, num_teams: int = 100, min_differences: int = 3) -> str:
    """
    Generate teams using actual database match data
    This integrates with your existing database functions
    
    Args:
        matchid: Database match ID
        num_teams: Number of teams to generate
        min_differences: Minimum number of different players between teams
    
    Returns:
        Filename of the generated JSON file
    """
    try:
        # Import your database functions
        from db import getplayers, getteams
        
        # Get actual match data from database
        players = getplayers(matchid)
        teams = getteams(matchid)
        
        if not players:
            print(f"❌ No players found for match ID: {matchid}")
            return ""
        
        if not teams:
            print(f"❌ No team information found for match ID: {matchid}")
            return ""
        
        # Extract team names from database
        team_a_name = teams[0][1] if len(teams) > 0 else "Team A"
        team_b_name = teams[0][2] if len(teams) > 0 else "Team B"
        
        print(f"🏏 Using database match ID: {matchid}")
        print(f"🏏 Teams: {team_a_name} vs {team_b_name}")
        print(f"📊 Players loaded from database: {len(players)}")
        
        # Convert database players to the expected format
        # Database format: (playerid, teamname, role, playername, credits, percentage, matchrole, player_id)
        players_data = []
        for player in players:
            players_data.append(player)
        
        # Generate teams with actual match data
        return generate_teams_json_only(
            players_data=players_data,
            team_a_name=team_a_name,
            team_b_name=team_b_name,
            match_id=str(matchid),  # Use actual database match ID
            num_teams=num_teams,
            min_differences=min_differences
        )
        
    except ImportError:
        print("❌ Database functions not available. Using sample data.")
        return ""
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return ""

from typing import List, Dict, Any, Tuple

def generate_teams_json_only(players_data: List[Tuple], team_a_name: str, team_b_name: str, 
                            match_id: str = None, num_teams: int = 100, quiet: bool = False, 
                            min_differences: int = 3) -> str:
    """
    Generate Dream11 teams and store directly in JSON format
    This follows the same approach as your existing generateTeams function
    
    Args:
        players_data: List of player tuples (similar to your database format)
        team_a_name: Name of team A
        team_b_name: Name of team B
        match_id: Actual Dream11 match ID (if None, will use placeholder)
        num_teams: Number of teams to generate
        quiet: If True, minimal output (default: False)
        min_differences: Minimum number of different players between teams (default: 3)
    
    Returns:
        Filename of the generated JSON file
    """
    
    if not quiet:
        print(f"🏏 Generating {num_teams} teams for {team_a_name} vs {team_b_name}")
        print(f"📊 Total players available: {len(players_data)}")
    
    # Separate players by team (assuming team name is at index 1)
    team_a_players = [p for p in players_data if p[1] == team_a_name]
    team_b_players = [p for p in players_data if p[1] == team_b_name]
    
    if not quiet:
        print(f"📊 {team_a_name} players: {len(team_a_players)}")
        print(f"📊 {team_b_name} players: {len(team_b_players)}")
    
    # Generate teams with diversity control
    generated_teams = []
    attempts = 0
    max_attempts = num_teams * 10  # Allow more attempts to find diverse teams
    
    if not quiet:
        print(f"🔄 Generating {num_teams} teams with min {min_differences} differences between teams...")
    
    while len(generated_teams) < num_teams and attempts < max_attempts:
        attempts += 1
        team_id = len(generated_teams) + 1
        
        team = generate_single_team(team_a_players, team_b_players, team_id, quiet=quiet)
        
        if team:
            # Sequential diversity check: new team must differ from ALL existing teams
            if check_sequential_team_diversity(team['players'], generated_teams, min_differences, quiet):
                generated_teams.append(team)
                
                if not quiet:
                    print(f"✅ Team {team_id} accepted: {len(generated_teams)}/{num_teams} teams generated")
                
                # Show progress every 25 teams (only if not quiet)
                if not quiet and len(generated_teams) % 25 == 0:
                    print(f"📊 Progress: {len(generated_teams)}/{num_teams} teams ({attempts} attempts)")
            else:
                # Team too similar to one or more existing teams, skip it
                if not quiet and attempts % 50 == 0:
                    print(f"🔄 Searching for diverse teams... {len(generated_teams)}/{num_teams} found ({attempts} attempts)")
        else:
            # Failed to generate valid team
            if not quiet and attempts % 100 == 0:
                print(f"⚠️ Team generation issues... {len(generated_teams)}/{num_teams} found ({attempts} attempts)")
    
    if not quiet:
        success_rate = (len(generated_teams) / attempts * 100) if attempts > 0 else 0
        print(f"✅ Generation completed: {len(generated_teams)}/{num_teams} teams created")
        print(f"📊 Diversity control: {attempts} attempts, {success_rate:.1f}% success rate")
    
    # Remove any remaining duplicates (teams with >8 common players) as final cleanup
    if len(generated_teams) > 1:
        original_count = len(generated_teams)
        generated_teams = remove_json_duplicate_teams(generated_teams, quiet)
        if not quiet and len(generated_teams) < original_count:
            print(f"🗑️ Final cleanup: Removed {original_count - len(generated_teams)} duplicate teams")
    
    # Create JSON structure (same as your existing format)
    # Use actual match_id if provided, otherwise use placeholder
    actual_match_id = match_id if match_id else "YOUR_MATCH_ID"
    
    teams_data = {
        "metadata": {
            "generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "match": f"{team_a_name} vs {team_b_name}",
            "total_teams": len(generated_teams),
            "match_id": actual_match_id,
            "auth_token": "YOUR_AUTH_TOKEN",
            "team_a": team_a_name,
            "team_b": team_b_name
        },
        "teams": generated_teams
    }
    
    # Save to JSON file (same naming convention as your existing code)
    # Add microseconds to ensure uniqueness even for rapid successive runs
    timestamp = datetime.now()
    filename = f"dream11_teams_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond:06d}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(teams_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Teams saved to: {filename}")
        print(f"💡 Edit the JSON file to add your match_id and auth_token")
        print(f"📊 Total valid teams saved: {len(generated_teams)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error saving teams to JSON file: {e}")
        return ""

def generate_single_team(team_a_players: List[Tuple], team_b_players: List[Tuple], 
                        team_id: int, quiet: bool = False) -> Dict:
    """
    Generate a single team with 11 unique players
    This mimics your existing team generation logic
    """
    
    # Simple balanced team composition
    # Select 6 players from team A and 5 from team B (or adjust as needed)
    try:
        # Ensure we have enough players
        if len(team_a_players) + len(team_b_players) < 11:
            print(f"⚠️ Team {team_id}: Not enough total players ({len(team_a_players) + len(team_b_players)}) to form a team")
            return None
        
        # Start with balanced selection
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
                # Use all available players
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
        
        # Ensure exactly 11 unique players
        all_selected = all_selected[:11]
        
        # Verify no duplicates by checking player IDs
        seen_ids = set()
        unique_players = []
        for player in all_selected:
            player_id = player[7] if len(player) > 7 and player[7] is not None else None
            if player_id is not None and player_id not in seen_ids:
                seen_ids.add(player_id)
                unique_players.append(player)
            elif player_id is None:
                # Handle players without IDs
                unique_players.append(player)
        
        # If we lost players due to duplicates, fill from remaining
        if len(unique_players) < 11:
            remaining_players = [p for p in team_a_players + team_b_players 
                               if p not in unique_players]
            needed = 11 - len(unique_players)
            if len(remaining_players) >= needed:
                additional = random.sample(remaining_players, needed)
                unique_players.extend(additional)
        
        all_selected = unique_players[:11]
        
        if len(all_selected) < 11:
            print(f"⚠️ Team {team_id}: Only {len(all_selected)} unique players available")
            return None
        
        # Extract player IDs and ensure uniqueness
        player_ids = []
        seen_ids = set()
        
        for i, player in enumerate(all_selected):
            if len(player) > 7 and player[7] is not None:
                player_id = int(player[7])
                if player_id not in seen_ids:
                    player_ids.append(player_id)
                    seen_ids.add(player_id)
                else:
                    # No fallback ID generation - skip duplicate players
                    print(f"⚠️ Team {team_id}: Duplicate player ID {player_id} - skipping team")
                    return None
            else:
                # No fallback ID generation - skip teams with missing player IDs
                print(f"⚠️ Team {team_id}: Missing player ID for player {i} - skipping team")
                return None
        
        # Verify we have exactly 11 unique player IDs
        if len(set(player_ids)) != 11:
            print(f"❌ Team {team_id}: Failed to generate 11 unique players. Got {len(set(player_ids))} unique IDs")
            return None
        
        # Select captain and vice-captain (ensure they're different)
        captain_id = player_ids[0] if player_ids else team_id * 1000
        vice_captain_id = player_ids[1] if len(player_ids) > 1 and player_ids[1] != captain_id else (player_ids[2] if len(player_ids) > 2 else team_id * 1000 + 1)
        
        # Final validation
        if captain_id == vice_captain_id:
            print(f"⚠️ Team {team_id}: Captain and Vice-Captain are the same, fixing...")
            vice_captain_id = player_ids[2] if len(player_ids) > 2 else team_id * 1000 + 1
        
        # Only print progress for first few teams and milestones (if not quiet)
        if not quiet and (team_id <= 3 or team_id % 25 == 0):
            print(f"✅ Team {team_id}: Generated with {len(player_ids)} unique players")
        
        return {
            "id": team_id,
            "name": f"Team {team_id}",
            "captain": captain_id,
            "vice_captain": vice_captain_id,
            "players": player_ids
        }
        
    except Exception as e:
        print(f"❌ Error generating team {team_id}: {e}")
        return None

def load_teams_from_json(filename: str) -> Dict:
    """Load teams from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading teams from {filename}: {e}")
        return {}

def analyze_sequential_team_diversity(teams_data: Dict, min_differences: int = 3) -> Dict:
    """Analyze sequential diversity statistics of generated teams"""
    teams = teams_data.get("teams", [])
    
    if len(teams) < 2:
        return {"total_teams": len(teams), "diversity_analysis": "Need at least 2 teams for analysis"}
    
    total_comparisons = 0
    total_common_players = 0
    min_common = 11
    max_common = 0
    diversity_violations = 0
    sequential_violations = []
    
    print(f"\n🔍 ANALYZING SEQUENTIAL TEAM DIVERSITY:")
    print(f"   Verifying {len(teams)} teams meet sequential diversity requirement...")
    print(f"   Requirement: Each team must differ by ≥{min_differences} players from ALL previous teams")
    
    # Check sequential diversity: each team against all previous teams
    for i in range(len(teams)):
        team_violations = 0
        
        for j in range(i):  # Check against all previous teams
            team1_players = teams[i].get("players", [])
            team2_players = teams[j].get("players", [])
            
            common_players = calculate_team_intersection(team1_players, team2_players)
            different_players = 11 - common_players
            
            total_comparisons += 1
            total_common_players += common_players
            min_common = min(min_common, common_players)
            max_common = max(max_common, common_players)
            
            # Check if diversity requirement is met
            if different_players < min_differences:
                diversity_violations += 1
                team_violations += 1
                if len(sequential_violations) < 10:  # Show first 10 violations
                    sequential_violations.append(f"T{i+1} vs T{j+1}: Only {different_players} different players")
        
        # Report team-level compliance
        if i < 5 or team_violations > 0:  # Show first 5 teams or any with violations
            if team_violations == 0:
                print(f"✅ T{i+1}: Compliant with all {i} previous teams")
            else:
                print(f"❌ T{i+1}: {team_violations} violations with previous teams")
    
    avg_common = total_common_players / total_comparisons if total_comparisons > 0 else 0
    avg_different = 11 - avg_common
    
    print(f"\n📊 Sequential Diversity Statistics:")
    print(f"   Total teams: {len(teams)}")
    print(f"   Total comparisons: {total_comparisons}")
    print(f"   Average different players: {avg_different:.1f}")
    print(f"   Minimum different players: {11 - max_common}")
    print(f"   Maximum different players: {11 - min_common}")
    print(f"   Sequential violations: {diversity_violations}/{total_comparisons}")
    
    if sequential_violations:
        print(f"\n⚠️ Sequential Diversity Violations:")
        for violation in sequential_violations:
            print(f"   {violation}")
    
    if diversity_violations == 0:
        print(f"✅ Perfect sequential compliance! All teams meet diversity requirement!")
    else:
        print(f"⚠️ {diversity_violations} sequential diversity violations found")
    
    return {
        "total_teams": len(teams),
        "total_comparisons": total_comparisons,
        "avg_different_players": avg_different,
        "min_different_players": 11 - max_common,
        "max_different_players": 11 - min_common,
        "sequential_violations": diversity_violations,
        "sequential_compliance": diversity_violations == 0,
        "violation_details": sequential_violations
    }

def validate_team_uniqueness(teams_data: Dict) -> bool:
    """Validate that all teams have unique players and no duplicates within teams"""
    teams = teams_data.get("teams", [])
    
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
            # Only show validation for first few teams and any with issues
            if team_id <= 3:
                print(f"✅ Team {team_id}: All {len(players)} players are unique")
    
    if all_valid:
        print(f"✅ All {len(teams)} teams passed uniqueness validation!")
    else:
        print(f"❌ Some teams failed uniqueness validation!")
    
    return all_valid

def convert_json_to_api_format(json_data: Dict) -> List[Dict]:
    """Convert JSON teams to Dream11 API format"""
    api_teams = []
    
    metadata = json_data.get("metadata", {})
    teams = json_data.get("teams", [])
    
    for team in teams:
        api_team = {
            "match_id": metadata.get("match_id", "YOUR_MATCH_ID"),
            "team_id": team.get("id", 1),
            "captain": team.get("captain", 0),
            "vice_captain": team.get("vice_captain", 0),
            "players": team.get("players", []),
            "auth_token": metadata.get("auth_token", "YOUR_AUTH_TOKEN")
        }
        api_teams.append(api_team)
    
    return api_teams

def main():
    """Example usage with both database and sample data approaches"""
    
    print("🏏 DREAM11 TEAM GENERATOR - JSON APPROACH")
    print("=" * 50)
    
    # Method 1: Try to use actual database data (if available)
    print("\n🔄 METHOD 1: Using Database Match Data")
    print("-" * 40)
    
    # You can change this to your actual match ID from the database
    database_match_id = "110766"  # Using actual match ID from database: IND vs UAE
    
    database_filename = generate_teams_from_database(
        matchid=database_match_id,
        num_teams=100
    )
    
    if database_filename:
        print(f"✅ Database method successful: {database_filename}")
        
        # Load and validate
        teams_data = load_teams_from_json(database_filename)
        validate_team_uniqueness(teams_data)
        
        # Analyze sequential team diversity
        analyze_sequential_team_diversity(teams_data, min_differences=3)
        
        print(f"📊 Database Teams Summary:")
        print(f"   Match: {teams_data.get('metadata', {}).get('match', 'Unknown')}")
        print(f"   Match ID: {teams_data.get('metadata', {}).get('match_id', 'Unknown')}")
        print(f"   Total teams: {teams_data.get('metadata', {}).get('total_teams', 0)}")
        
        return database_filename
    
    # No fallback to sample data - if database method fails, return None
    print("\n❌ Database method failed - no fallback available")
    return None

if __name__ == "__main__":
    main()