#!/usr/bin/env python3

def test_select_unique_players():
    """Test the select_unique_players function"""
    
    # Sample player data
    players = [
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],
        ['p2', 'Player2', 'TeamA', 'BAT', 'role', 60, 110],
        ['p3', 'Player3', 'TeamB', 'BOWL', 'role', 70, 120],
        ['p1', 'Player1', 'TeamA', 'BAT', 'role', 50, 100],  # Duplicate
        ['p4', 'Player4', 'TeamB', 'BOWL', 'role', 80, 130],
    ]
    
    selected_players = set()
    
    def select_unique_players(player_list, required_count):
        available = [p for p in player_list if p[0] not in selected_players]
        if len(available) >= required_count:
            import random
            chosen = random.sample(available, required_count)
            for player in chosen:
                selected_players.add(player[0])
            return chosen
        else:
            # Add all available unique players
            for player in available:
                selected_players.add(player[0])
            return available
    
    print("🧪 Testing select_unique_players function...")
    print(f"Input players: {len(players)} (with 1 duplicate)")
    
    # Test selecting 3 players
    result = select_unique_players(players, 3)
    
    print(f"Selected players: {len(result)}")
    print(f"Selected IDs: {[p[0] for p in result]}")
    print(f"Unique IDs: {len(set([p[0] for p in result]))}")
    
    # Check if all selected players are unique
    selected_ids = [p[0] for p in result]
    if len(set(selected_ids)) == len(selected_ids):
        print("✅ Test PASSED: All selected players are unique!")
    else:
        print("❌ Test FAILED: Duplicate players selected!")
        
    # Test selecting more players
    print("\n🔄 Selecting 2 more players...")
    result2 = select_unique_players(players, 2)
    
    print(f"Additional players: {len(result2)}")
    print(f"Additional IDs: {[p[0] for p in result2]}")
    
    # Check total unique players
    all_selected = result + result2
    all_ids = [p[0] for p in all_selected]
    print(f"Total selected: {len(all_selected)}")
    print(f"Total unique: {len(set(all_ids))}")
    
    if len(set(all_ids)) == len(all_ids):
        print("✅ Test PASSED: No duplicates across multiple selections!")
    else:
        print("❌ Test FAILED: Duplicates found across selections!")

if __name__ == "__main__":
    test_select_unique_players()