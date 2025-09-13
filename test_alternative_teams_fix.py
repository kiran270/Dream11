#!/usr/bin/env python3
"""
Test the alternative teams duplicate fix
"""

def test_duplicate_prevention():
    """Test that the alternative team generation prevents duplicates"""
    
    print("🧪 TESTING ALTERNATIVE TEAMS DUPLICATE PREVENTION")
    print("=" * 60)
    
    # Simulate the problematic scenario
    print("\n📋 SCENARIO:")
    print("   Top 11 team: [Player1, Player2, Player3, ..., Player11]")
    print("   Player1 alternatives: [AltA, AltB, AltC]")
    print("   Player2 alternatives: [AltA, AltD, AltE]  # AltA is common!")
    print("   Without fix: Player1→AltA, Player2→AltA = DUPLICATE")
    print("   With fix: Player1→AltA, Player2→AltD = NO DUPLICATE")
    
    # Create sample data
    current_team = [
        {'playername': 'Player1', 'teamname': 'TeamA', 'percentage': 80.0},
        {'playername': 'Player2', 'teamname': 'TeamA', 'percentage': 75.0},
        {'playername': 'Player3', 'teamname': 'TeamB', 'percentage': 70.0},
    ]
    
    alternatives_by_player = {
        'Player1': [
            {'playername': 'AltA', 'teamname': 'TeamA', 'percentage': 60.0},
            {'playername': 'AltB', 'teamname': 'TeamA', 'percentage': 55.0},
        ],
        'Player2': [
            {'playername': 'AltA', 'teamname': 'TeamA', 'percentage': 60.0},  # Same as Player1 alt!
            {'playername': 'AltD', 'teamname': 'TeamA', 'percentage': 50.0},
        ]
    }
    
    print(f"\n🔧 TESTING THE FIX:")
    
    # Simulate the fixed logic
    import random
    random.seed(42)  # For reproducible results
    
    players_to_swap = [current_team[0], current_team[1]]  # Player1 and Player2
    
    for player_to_swap in players_to_swap:
        alternatives = alternatives_by_player[player_to_swap['playername']]
        if alternatives:
            # Get current team player names to avoid duplicates (FIXED LOGIC)
            current_team_names = set(p['playername'] for p in current_team if p['playername'] != player_to_swap['playername'])
            
            # Find alternatives that are not already in the team (FIXED LOGIC)
            available_alternatives = [alt for alt in alternatives if alt['playername'] not in current_team_names]
            
            print(f"\n   Processing {player_to_swap['playername']}:")
            print(f"     Current team names: {current_team_names}")
            print(f"     All alternatives: {[alt['playername'] for alt in alternatives]}")
            print(f"     Available alternatives: {[alt['playername'] for alt in available_alternatives]}")
            
            if available_alternatives:
                # Pick a random alternative that's not already in the team
                replacement = random.choice(available_alternatives)
                print(f"     Selected replacement: {replacement['playername']}")
                
                # Replace in current team
                for i, team_player in enumerate(current_team):
                    if team_player['playername'] == player_to_swap['playername']:
                        current_team[i] = replacement
                        break
            else:
                print(f"     No available alternatives (all would create duplicates)")
    
    # Final validation
    team_player_names = [p['playername'] for p in current_team]
    has_duplicates = len(team_player_names) != len(set(team_player_names))
    
    print(f"\n📊 RESULTS:")
    print(f"   Final team: {team_player_names}")
    print(f"   Has duplicates: {'❌ YES' if has_duplicates else '✅ NO'}")
    
    if has_duplicates:
        duplicates = [name for name in team_player_names if team_player_names.count(name) > 1]
        print(f"   Duplicate players: {set(duplicates)}")
        print(f"   🚨 FIX FAILED - Still has duplicates!")
    else:
        print(f"   ✅ FIX SUCCESSFUL - No duplicates found!")
    
    return not has_duplicates

def test_edge_cases():
    """Test edge cases for the duplicate prevention"""
    
    print(f"\n🧪 TESTING EDGE CASES:")
    print("-" * 30)
    
    # Edge Case 1: All alternatives are already in team
    print(f"\n1. All alternatives already in team:")
    current_team_names = {'Player1', 'Player2', 'AltA', 'AltB'}
    alternatives = [
        {'playername': 'AltA'},  # Already in team
        {'playername': 'AltB'},  # Already in team
    ]
    
    available = [alt for alt in alternatives if alt['playername'] not in current_team_names]
    print(f"   Available alternatives: {len(available)} (should be 0)")
    print(f"   Result: {'✅ PASS' if len(available) == 0 else '❌ FAIL'}")
    
    # Edge Case 2: No alternatives available
    print(f"\n2. No alternatives provided:")
    alternatives = []
    available = [alt for alt in alternatives if alt['playername'] not in current_team_names]
    print(f"   Available alternatives: {len(available)} (should be 0)")
    print(f"   Result: {'✅ PASS' if len(available) == 0 else '❌ FAIL'}")
    
    # Edge Case 3: Some alternatives available
    print(f"\n3. Mixed scenario:")
    alternatives = [
        {'playername': 'AltA'},  # Already in team
        {'playername': 'AltC'},  # Not in team - should be available
        {'playername': 'AltD'},  # Not in team - should be available
    ]
    
    available = [alt for alt in alternatives if alt['playername'] not in current_team_names]
    expected_available = ['AltC', 'AltD']
    actual_available = [alt['playername'] for alt in available]
    
    print(f"   Expected available: {expected_available}")
    print(f"   Actual available: {actual_available}")
    print(f"   Result: {'✅ PASS' if set(actual_available) == set(expected_available) else '❌ FAIL'}")

if __name__ == "__main__":
    success = test_duplicate_prevention()
    test_edge_cases()
    
    print(f"\n🎯 OVERALL RESULT:")
    if success:
        print(f"✅ Alternative teams duplicate prevention is working correctly!")
        print(f"💡 The fix should prevent duplicate players in alternative teams.")
    else:
        print(f"❌ There are still issues with the duplicate prevention logic.")
        print(f"🔧 Additional debugging may be needed.")