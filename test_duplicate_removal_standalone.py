#!/usr/bin/env python3
"""
Standalone test of duplicate removal logic
"""

def remove_duplicate_teams_post_generation(teams_list):
	"""
	Remove teams that have more than 8 common players with other teams
	This is called after all teams are generated to clean up duplicates
	"""
	if not teams_list or len(teams_list) <= 1:
		return teams_list
	
	print(f"🔍 Checking {len(teams_list)} teams for duplicates (>8 common players)...")
	
	unique_teams = []
	removed_count = 0
	
	for i, current_team in enumerate(teams_list):
		is_duplicate = False
		
		# Extract player IDs from current team (first 11 players)
		if len(current_team) < 11:
			print(f"⚠️ Team {i+1} has only {len(current_team)} players, skipping")
			continue
			
		current_player_ids = []
		for j in range(11):
			if j < len(current_team) and current_team[j] and len(current_team[j]) > 7:
				player_id = current_team[j][7] if current_team[j][7] is not None else 0
				current_player_ids.append(player_id)
		
		if len(current_player_ids) != 11:
			print(f"⚠️ Team {i+1} doesn't have 11 valid player IDs, skipping")
			continue
		
		# Check against all previously accepted unique teams
		for existing_team in unique_teams:
			existing_player_ids = []
			for j in range(11):
				if j < len(existing_team) and existing_team[j] and len(existing_team[j]) > 7:
					player_id = existing_team[j][7] if existing_team[j][7] is not None else 0
					existing_player_ids.append(player_id)
			
			if len(existing_player_ids) == 11:
				# Calculate common players
				common_players = len(set(current_player_ids) & set(existing_player_ids))
				
				if common_players > 8:  # More than 8 common = duplicate
					is_duplicate = True
					removed_count += 1
					if removed_count <= 5:  # Log first 5 removals
						print(f"🗑️ Removed team {i+1}: {common_players} common players with existing team")
					break
		
		if not is_duplicate:
			unique_teams.append(current_team)
	
	print(f"✅ Duplicate removal completed:")
	print(f"   Original teams: {len(teams_list)}")
	print(f"   Unique teams: {len(unique_teams)}")
	print(f"   Removed duplicates: {removed_count}")
	
	return unique_teams

def test_duplicate_removal():
    """Test duplicate removal logic with sample data"""
    
    print("🧪 TESTING DUPLICATE REMOVAL LOGIC")
    print("=" * 50)
    
    # Create sample teams with some duplicates
    # Each team is represented as a list of 11 player tuples
    # Player tuple format: (playerid, teamname, role, playername, credits, percentage, matchrole, player_id)
    
    # Team 1: Players 1-11
    team1 = []
    for i in range(11):
        player = (i+1, "TeamA", "BAT", f"Player{i+1}", "8.0", 50.0, "MID", 1000+i)
        team1.append(player)
    
    # Team 2: Same as Team 1 (identical - should be removed)
    team2 = team1.copy()
    
    # Team 3: 9 common players with Team 1 (should be removed)
    team3 = team1[:9].copy()  # First 9 players same
    team3.append((12, "TeamB", "BAT", "Player12", "8.0", 50.0, "MID", 1012))
    team3.append((13, "TeamB", "BAT", "Player13", "8.0", 50.0, "MID", 1013))
    
    # Team 4: Only 7 common players with Team 1 (should be kept)
    team4 = team1[:7].copy()  # First 7 players same
    for i in range(4):
        player = (20+i, "TeamB", "BAT", f"PlayerNew{i+1}", "8.0", 50.0, "MID", 1020+i)
        team4.append(player)
    
    # Team 5: Completely different (should be kept)
    team5 = []
    for i in range(11):
        player = (30+i, "TeamC", "BAT", f"PlayerDiff{i+1}", "8.0", 50.0, "MID", 1030+i)
        team5.append(player)
    
    sample_teams = [team1, team2, team3, team4, team5]
    
    print(f"📊 Created {len(sample_teams)} sample teams:")
    print(f"   Team 1: Players 1000-1010")
    print(f"   Team 2: Identical to Team 1 (should be removed)")
    print(f"   Team 3: 9 common with Team 1 (should be removed)")
    print(f"   Team 4: 7 common with Team 1 (should be kept)")
    print(f"   Team 5: Completely different (should be kept)")
    
    # Test the removal function
    result_teams = remove_duplicate_teams_post_generation(sample_teams)
    
    print(f"\n📊 RESULTS:")
    print(f"   Expected: 3 teams (Team 1, Team 4, Team 5)")
    print(f"   Actual: {len(result_teams)} teams")
    
    if len(result_teams) == 3:
        print(f"✅ Duplicate removal working correctly!")
    else:
        print(f"❌ Unexpected result")
        
    # Show which teams were kept
    for i, team in enumerate(result_teams):
        first_player_id = team[0][7] if len(team) > 0 and len(team[0]) > 7 else "Unknown"
        print(f"   Kept Team {i+1}: First player ID {first_player_id}")

if __name__ == "__main__":
    test_duplicate_removal()