#!/usr/bin/env python3

def test_duplicate_team_detection():
    """Test the duplicate team detection logic"""
    
    # Sample teams for testing
    team1 = [
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],
        ['p2', 'Player2', 'TeamA', 'BAT', 'role', 60, 110],
        ['p3', 'Player3', 'TeamB', 'BOWL', 'role', 70, 120],
        ['p4', 'Player4', 'TeamB', 'BOWL', 'role', 80, 130],
        ['p5', 'Player5', 'TeamA', 'WK', 'role', 90, 140],
        ['p6', 'Player6', 'TeamB', 'AL', 'role', 55, 105],
        ['p7', 'Player7', 'TeamA', 'AL', 'role', 65, 115],
        ['p8', 'Player8', 'TeamB', 'BAT', 'role', 75, 125],
        ['p9', 'Player9', 'TeamA', 'BOWL', 'role', 85, 135],
        ['p10', 'Player10', 'TeamB', 'BAT', 'role', 95, 145],
        ['p11', 'Player11', 'TeamA', 'AL', 'role', 45, 95]
    ]
    
    # Same team with different captain/vice-captain (should be detected as duplicate)
    team2 = [
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],
        ['p2', 'Player2', 'TeamA', 'BAT', 'role', 60, 110],
        ['p3', 'Player3', 'TeamB', 'BOWL', 'role', 70, 120],
        ['p4', 'Player4', 'TeamB', 'BOWL', 'role', 80, 130],
        ['p5', 'Player5', 'TeamA', 'WK', 'role', 90, 140],
        ['p6', 'Player6', 'TeamB', 'AL', 'role', 55, 105],
        ['p7', 'Player7', 'TeamA', 'AL', 'role', 65, 115],
        ['p8', 'Player8', 'TeamB', 'BAT', 'role', 75, 125],
        ['p9', 'Player9', 'TeamA', 'BOWL', 'role', 85, 135],
        ['p10', 'Player10', 'TeamB', 'BAT', 'role', 95, 145],
        ['p11', 'Player11', 'TeamA', 'AL', 'role', 45, 95]
    ]
    
    # Different team (should not be detected as duplicate)
    team3 = [
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],
        ['p2', 'Player2', 'TeamA', 'BAT', 'role', 60, 110],
        ['p3', 'Player3', 'TeamB', 'BOWL', 'role', 70, 120],
        ['p4', 'Player4', 'TeamB', 'BOWL', 'role', 80, 130],
        ['p5', 'Player5', 'TeamA', 'WK', 'role', 90, 140],
        ['p6', 'Player6', 'TeamB', 'AL', 'role', 55, 105],
        ['p7', 'Player7', 'TeamA', 'AL', 'role', 65, 115],
        ['p8', 'Player8', 'TeamB', 'BAT', 'role', 75, 125],
        ['p9', 'Player9', 'TeamA', 'BOWL', 'role', 85, 135],
        ['p10', 'Player10', 'TeamB', 'BAT', 'role', 95, 145],
        ['p12', 'Player12', 'TeamA', 'AL', 'role', 45, 95]  # Different player
    ]
    
    # Test duplicate detection logic
    finalteams = []
    
    def add_team_if_unique(team):
        # Check for duplicate teams before adding
        team_player_ids = set([p[0] for p in team[:11]])  # Only check first 11 players
        is_duplicate = False
        
        for existing_team in finalteams:
            existing_player_ids = set([p[0] for p in existing_team[:11]])
            if team_player_ids == existing_player_ids:
                is_duplicate = True
                print(f"   ⚠️ Duplicate team detected, skipping...")
                break
        
        if not is_duplicate:
            finalteams.append(team)
            print(f"   ✅ Team added. Total teams: {len(finalteams)}")
            return True
        else:
            print(f"   ❌ Duplicate team rejected")
            return False
    
    print("🧪 Testing duplicate team detection...")
    print("\n1. Adding first team:")
    add_team_if_unique(team1)
    
    print("\n2. Adding duplicate team (same players):")
    add_team_if_unique(team2)
    
    print("\n3. Adding different team:")
    add_team_if_unique(team3)
    
    print(f"\n📊 Final result: {len(finalteams)} unique teams")
    
    # Expected: 2 teams (team1 and team3), team2 should be rejected as duplicate
    if len(finalteams) == 2:
        print("✅ Test PASSED: Duplicate detection working correctly!")
    else:
        print("❌ Test FAILED: Expected 2 teams, got", len(finalteams))

if __name__ == "__main__":
    test_duplicate_team_detection()