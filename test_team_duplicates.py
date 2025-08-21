#!/usr/bin/env python3

def test_team_for_duplicates():
    """Test a sample team for duplicate players"""
    
    # Sample team that might have duplicates
    team = [
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
    
    print("🧪 Testing team for duplicate players...")
    print(f"Team size: {len(team)}")
    
    # Check for duplicate players (comprehensive check)
    player_ids = [p[0] for p in team[:11]]  # Player IDs
    player_names = [p[1] for p in team[:11]]  # Player names (index 1)
    
    print(f"Player IDs: {player_ids}")
    print(f"Player names: {player_names}")
    print(f"Unique IDs: {len(set(player_ids))}")
    print(f"Unique names: {len(set(player_names))}")
    
    # Check for duplicates
    if len(set(player_ids)) != 11:
        print("❌ DUPLICATE PLAYER IDs FOUND!")
        # Find duplicates
        seen = set()
        duplicates = []
        for pid in player_ids:
            if pid in seen:
                duplicates.append(pid)
            seen.add(pid)
        print(f"Duplicate IDs: {duplicates}")
        return False
    
    if len(set(player_names)) != 11:
        print("❌ DUPLICATE PLAYER NAMES FOUND!")
        # Find duplicates
        seen = set()
        duplicates = []
        for name in player_names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        print(f"Duplicate names: {duplicates}")
        return False
    
    print("✅ No duplicate players found!")
    return True

def test_team_with_duplicates():
    """Test a team that definitely has duplicates"""
    
    # Team with intentional duplicates
    team_with_dups = [
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],
        ['p2', 'Player2', 'TeamA', 'BAT', 'role', 60, 110],
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],  # Duplicate
        ['p4', 'Player4', 'TeamB', 'BOWL', 'role', 80, 130],
        ['p5', 'Player5', 'TeamA', 'WK', 'role', 90, 140],
        ['p6', 'Player6', 'TeamB', 'AL', 'role', 55, 105],
        ['p7', 'Player7', 'TeamA', 'AL', 'role', 65, 115],
        ['p8', 'Player8', 'TeamB', 'BAT', 'role', 75, 125],
        ['p9', 'Player9', 'TeamA', 'BOWL', 'role', 85, 135],
        ['p10', 'Player10', 'TeamB', 'BAT', 'role', 95, 145],
        ['p11', 'Player11', 'TeamA', 'AL', 'role', 45, 95]
    ]
    
    print("\n🧪 Testing team with known duplicates...")
    
    player_ids = [p[0] for p in team_with_dups[:11]]
    player_names = [p[1] for p in team_with_dups[:11]]
    
    print(f"Player IDs: {player_ids}")
    print(f"Unique IDs: {len(set(player_ids))}")
    
    if len(set(player_ids)) != 11:
        print("✅ Correctly detected duplicate IDs!")
        # Find duplicates
        seen = set()
        duplicates = []
        for pid in player_ids:
            if pid in seen:
                duplicates.append(pid)
            seen.add(pid)
        print(f"Duplicate IDs found: {duplicates}")
        return True
    else:
        print("❌ Failed to detect duplicates!")
        return False

if __name__ == "__main__":
    print("🔍 Testing duplicate detection logic...\n")
    
    # Test 1: Clean team
    result1 = test_team_for_duplicates()
    
    # Test 2: Team with duplicates
    result2 = test_team_with_duplicates()
    
    print(f"\n📊 Test Results:")
    print(f"Clean team test: {'PASSED' if result1 else 'FAILED'}")
    print(f"Duplicate detection test: {'PASSED' if result2 else 'FAILED'}")
    
    if result1 and result2:
        print("✅ All tests PASSED!")
    else:
        print("❌ Some tests FAILED!")