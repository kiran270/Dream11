#!/usr/bin/env python3

# Simple test to debug team generation
def create_sample_players():
    """Create sample player data for testing"""
    
    # Sample players for different categories
    atop = [
        ['a1', 'ATop1', 'TeamA', 'BAT', 'role', 80, 120],
        ['a2', 'ATop2', 'TeamA', 'BAT', 'role', 85, 125],
    ]
    
    amid = [
        ['a3', 'AMid1', 'TeamA', 'BAT', 'role', 70, 110],
        ['a4', 'AMid2', 'TeamA', 'BAT', 'role', 75, 115],
    ]
    
    ahit = [
        ['a5', 'AHit1', 'TeamA', 'BAT', 'role', 60, 100],
        ['a6', 'AHit2', 'TeamA', 'BAT', 'role', 65, 105],
    ]
    
    bpow = [
        ['b1', 'BPow1', 'TeamB', 'BOWL', 'role', 90, 130],
    ]
    
    bbre = [
        ['b2', 'BBre1', 'TeamB', 'BOWL', 'role', 80, 120],
    ]
    
    bdea = [
        ['b3', 'BDea1', 'TeamB', 'BOWL', 'role', 70, 110],
    ]
    
    btop = [
        ['b4', 'BTop1', 'TeamB', 'BAT', 'role', 85, 125],
    ]
    
    bmid = [
        ['b5', 'BMid1', 'TeamB', 'BAT', 'role', 75, 115],
    ]
    
    bhit = [
        ['b6', 'BHit1', 'TeamB', 'BAT', 'role', 65, 105],
    ]
    
    apow = [
        ['a7', 'APow1', 'TeamA', 'BOWL', 'role', 85, 125],
    ]
    
    abre = [
        ['a8', 'ABre1', 'TeamA', 'BOWL', 'role', 75, 115],
    ]
    
    adea = [
        ['a9', 'ADea1', 'TeamA', 'BOWL', 'role', 65, 105],
    ]
    
    return atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea

def test_select_unique_players():
    """Test the select_unique_players logic"""
    
    atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea = create_sample_players()
    
    print("🧪 Testing select_unique_players with sample data...")
    
    # Simulate the team generation logic
    import random
    
    def select_unique_players(player_list, required_count, selected_players):
        available = [p for p in player_list if p[0] not in selected_players]
        if len(available) >= required_count:
            chosen = random.sample(available, required_count)
            for player in chosen:
                selected_players.add(player[0])
            return chosen
        else:
            # Add all available unique players
            for player in available:
                selected_players.add(player[0])
            return available
    
    # Generate a team
    team = []
    selected_players = set()
    
    # Template requirements (simple 1-1-1 pattern)
    team.extend(select_unique_players(atop, 1, selected_players))
    team.extend(select_unique_players(amid, 1, selected_players))
    team.extend(select_unique_players(ahit, 1, selected_players))
    team.extend(select_unique_players(bpow, 1, selected_players))
    team.extend(select_unique_players(bbre, 1, selected_players))
    team.extend(select_unique_players(bdea, 1, selected_players))
    team.extend(select_unique_players(btop, 1, selected_players))
    team.extend(select_unique_players(bmid, 1, selected_players))
    team.extend(select_unique_players(bhit, 1, selected_players))
    team.extend(select_unique_players(apow, 1, selected_players))
    team.extend(select_unique_players(abre, 1, selected_players))
    
    print(f"Generated team size: {len(team)}")
    print(f"Selected players: {selected_players}")
    
    if len(team) > 0:
        player_ids = [p[0] for p in team]
        player_names = [p[1] for p in team]
        
        print(f"Player IDs: {player_ids}")
        print(f"Player names: {player_names}")
        print(f"Unique IDs: {len(set(player_ids))}")
        print(f"Unique names: {len(set(player_names))}")
        
        if len(set(player_ids)) == len(player_ids):
            print("✅ No duplicate players in generated team!")
            return True
        else:
            print("❌ Duplicate players found!")
            return False
    else:
        print("❌ No team generated!")
        return False

if __name__ == "__main__":
    test_select_unique_players()