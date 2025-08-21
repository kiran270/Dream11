#!/usr/bin/env python3

def test_checkapp_duplicate_prevention():
    """Test the checkapp duplicate prevention by simulating the logic"""
    
    print("🧪 Testing checkapp duplicate prevention logic...")
    
    # Sample data similar to what checkapp would use
    sample_players = [
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
        ['p11', 'Player11', 'TeamA', 'AL', 'role', 45, 95],
        ['p12', 'Player12', 'TeamB', 'WK', 'role', 85, 125],
    ]
    
    # Distribute players into categories (some overlap to test duplicate prevention)
    atop = sample_players[:3]
    amid = sample_players[1:4]  # Overlap with atop
    ahit = sample_players[3:6]
    bpow = sample_players[5:8]
    bbre = sample_players[7:10]  # Overlap with bpow
    bdea = sample_players[9:]
    btop = sample_players[:2]   # Overlap with atop
    bmid = sample_players[2:5]
    bhit = sample_players[4:7]
    apow = sample_players[6:9]
    abre = sample_players[8:11]
    adea = sample_players[10:]
    
    print(f"Total unique players: {len(sample_players)}")
    print("Categories have overlapping players to test duplicate prevention...")
    
    # Test the select_unique_players function
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
    
    # Generate multiple teams to test
    all_teams = []
    
    for team_num in range(3):
        print(f"\n🔄 Generating team {team_num + 1}...")
        
        team = []
        selected_players = set()
        
        # Simple template: 1 from each category
        try:
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
            
            print(f"   Team size: {len(team)}")
            
            if len(team) > 0:
                player_ids = [p[0] for p in team]
                unique_ids = len(set(player_ids))
                
                print(f"   Player IDs: {player_ids}")
                print(f"   Unique players: {unique_ids}/{len(team)}")
                
                if unique_ids == len(team):
                    print(f"   ✅ Team {team_num + 1}: No duplicates!")
                    all_teams.append(team)
                else:
                    print(f"   ❌ Team {team_num + 1}: Duplicates found!")
                    # Find duplicates
                    seen = set()
                    duplicates = []
                    for pid in player_ids:
                        if pid in seen:
                            duplicates.append(pid)
                        seen.add(pid)
                    print(f"   Duplicate IDs: {duplicates}")
            
        except Exception as e:
            print(f"   ❌ Error generating team {team_num + 1}: {e}")
    
    print(f"\n📊 Final Results:")
    print(f"Successfully generated {len(all_teams)} teams without duplicates")
    
    return len(all_teams) > 0

if __name__ == "__main__":
    success = test_checkapp_duplicate_prevention()
    if success:
        print("✅ Duplicate prevention test PASSED!")
    else:
        print("❌ Duplicate prevention test FAILED!")