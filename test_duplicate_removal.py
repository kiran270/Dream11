#!/usr/bin/env python3
"""
Test the duplicate removal function
"""

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
    print(f"   Team 1: Players 1-11")
    print(f"   Team 2: Identical to Team 1 (should be removed)")
    print(f"   Team 3: 9 common with Team 1 (should be removed)")
    print(f"   Team 4: 7 common with Team 1 (should be kept)")
    print(f"   Team 5: Completely different (should be kept)")
    
    # Test the removal function
    try:
        # Import the function from checkapp
        import sys
        sys.path.append('.')
        from checkapp import remove_duplicate_teams_post_generation
        
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
            first_player_name = team[0][3] if len(team) > 0 and len(team[0]) > 3 else "Unknown"
            print(f"   Kept Team {i+1}: {first_player_name}")
            
    except ImportError as e:
        print(f"❌ Could not import function: {e}")
        print("💡 The function should be added to checkapp.py")
    except Exception as e:
        print(f"❌ Error testing function: {e}")

if __name__ == "__main__":
    test_duplicate_removal()