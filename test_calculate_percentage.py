#!/usr/bin/env python3
"""
Direct test of calculatePercentage function to verify diversity checking
"""

import sys
import os
sys.path.append('.')

def test_calculate_percentage():
    print("🧪 Testing calculatePercentage Diversity Check")
    print("=" * 60)
    
    # Create dummy teams with overlapping players to test diversity
    dummy_teams = []
    
    # Team 1: Players 1-11
    team1 = []
    for i in range(11):
        team1.append([f'player_{i+1}', f'Player {i+1}', 'TeamA', 'BAT', 'role', 50, 100])
    dummy_teams.append(team1)
    
    # Team 2: Players 1-11 (identical to team 1 - should be rejected)
    team2 = []
    for i in range(11):
        team2.append([f'player_{i+1}', f'Player {i+1}', 'TeamA', 'BAT', 'role', 55, 110])
    dummy_teams.append(team2)
    
    # Team 3: Players 1-9 + 12-13 (9 common with team 1 - should be rejected)
    team3 = []
    for i in range(9):
        team3.append([f'player_{i+1}', f'Player {i+1}', 'TeamA', 'BAT', 'role', 45, 90])
    team3.append(['player_12', 'Player 12', 'TeamB', 'BAT', 'role', 60, 120])
    team3.append(['player_13', 'Player 13', 'TeamB', 'BAT', 'role', 65, 130])
    dummy_teams.append(team3)
    
    # Team 4: Players 1-2 + 14-22 (2 common with team 1 - should be accepted)
    team4 = []
    team4.append(['player_1', 'Player 1', 'TeamA', 'BAT', 'role', 70, 140])
    team4.append(['player_2', 'Player 2', 'TeamA', 'BAT', 'role', 75, 150])
    for i in range(14, 23):
        team4.append([f'player_{i}', f'Player {i}', 'TeamB', 'BAT', 'role', 40, 80])
    dummy_teams.append(team4)
    
    # Team 5: Players 25-35 (0 common with any team - should be accepted)
    team5 = []
    for i in range(25, 36):
        team5.append([f'player_{i}', f'Player {i}', 'TeamB', 'BAT', 'role', 35, 70])
    dummy_teams.append(team5)
    
    print(f"📊 Created {len(dummy_teams)} test teams:")
    print(f"   Team 1: Players 1-11")
    print(f"   Team 2: Players 1-11 (identical - should be rejected)")
    print(f"   Team 3: Players 1-9,12-13 (9 common - should be rejected)")
    print(f"   Team 4: Players 1-2,14-22 (2 common - should be accepted)")
    print(f"   Team 5: Players 25-35 (0 common - should be accepted)")
    print()
    
    # Import and test calculatePercentage
    try:
        # We need to mock the Flask environment
        import sys
        from unittest.mock import MagicMock
        
        # Mock Flask modules
        sys.modules['flask'] = MagicMock()
        sys.modules['flask'].Flask = MagicMock()
        sys.modules['flask'].render_template = MagicMock()
        sys.modules['flask'].redirect = MagicMock()
        sys.modules['flask'].jsonify = MagicMock()
        sys.modules['flask'].request = MagicMock()
        
        # Now import calculatePercentage
        from checkapp import calculatePercentage
        
        print("🔍 Calling calculatePercentage with test data...")
        result = calculatePercentage(dummy_teams)
        
        print(f"\n✅ calculatePercentage returned {len(result)} teams")
        
        if len(result) > 0:
            print(f"🎯 Expected: 3 teams (Team 1, Team 4, Team 5)")
            print(f"🎯 Actual: {len(result)} teams")
            
            if len(result) == 3:
                print("✅ SUCCESS: Diversity filtering worked correctly!")
                print("   - Team 2 rejected (identical to Team 1)")
                print("   - Team 3 rejected (9 common players > 2)")
                print("   - Teams 1, 4, 5 accepted (within diversity limits)")
            else:
                print("❌ ISSUE: Unexpected number of teams returned")
                
            # Show team percentages
            for i, team in enumerate(result):
                if len(team) > 11:
                    percentage = team[-1] if isinstance(team[-1], (int, float)) else "Unknown"
                    print(f"   Team {i+1}: {percentage}% total")
        else:
            print("❌ ISSUE: No teams returned")
            
        return len(result)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    test_calculate_percentage()