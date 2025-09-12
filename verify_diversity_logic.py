#!/usr/bin/env python3
"""
Verify that diversity logic is working correctly
Show exact player differences between teams
"""

from json_team_generator_simple import generate_teams_from_database, load_teams_from_json

def verify_diversity_logic():
    """Verify diversity logic with detailed player comparison"""
    
    print("🔍 VERIFYING DIVERSITY LOGIC")
    print("=" * 50)
    print("Checking that captain/vc are included in the 11 players")
    print("And that teams actually have 3+ different players")
    print("-" * 50)
    
    # Generate a small number of teams for detailed analysis
    filename = generate_teams_from_database(
        matchid="110766",
        num_teams=5,  # Small number for detailed verification
        min_differences=3
    )
    
    if filename:
        teams_data = load_teams_from_json(filename)
        teams = teams_data.get('teams', [])
        
        print(f"\n📊 DETAILED TEAM ANALYSIS:")
        print(f"Generated {len(teams)} teams from file: {filename}")
        
        # Show team structure for first 3 teams
        for i in range(min(3, len(teams))):
            team = teams[i]
            players = team.get('players', [])
            captain = team.get('captain')
            vice_captain = team.get('vice_captain')
            
            print(f"\n🏏 Team {i+1}:")
            print(f"   Players ({len(players)}): {players}")
            print(f"   Captain: {captain} {'✅' if captain in players else '❌ NOT IN PLAYERS'}")
            print(f"   Vice-Captain: {vice_captain} {'✅' if vice_captain in players else '❌ NOT IN PLAYERS'}")
        
        # Now verify diversity between teams
        print(f"\n🔍 DIVERSITY VERIFICATION:")
        print(f"Checking that each team differs by ≥3 players from previous teams")
        
        for i in range(len(teams)):
            team_i_players = set(teams[i].get('players', []))
            
            print(f"\n📋 Team {i+1} diversity check:")
            
            for j in range(i):
                team_j_players = set(teams[j].get('players', []))
                
                common_players = team_i_players & team_j_players
                different_players = team_i_players ^ team_j_players  # Symmetric difference
                
                common_count = len(common_players)
                different_count = len(different_players)
                
                status = "✅" if different_count >= 6 else "❌"  # 6 different = 3 from each team
                
                print(f"   vs Team {j+1}: {different_count//2} different players each, {common_count} common {status}")
                print(f"      Common: {sorted(list(common_players))}")
                print(f"      T{i+1} unique: {sorted(list(team_i_players - team_j_players))}")
                print(f"      T{j+1} unique: {sorted(list(team_j_players - team_i_players))}")
                
                if different_count < 6:
                    print(f"      ⚠️ VIOLATION: Only {different_count//2} different players (need ≥3)")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   All captains/VCs are within the 11 players: {'✅' if all(team.get('captain') in team.get('players', []) and team.get('vice_captain') in team.get('players', []) for team in teams) else '❌'}")
        print(f"   All teams have exactly 11 players: {'✅' if all(len(team.get('players', [])) == 11 for team in teams) else '❌'}")
        
    else:
        print("❌ Failed to generate teams")

if __name__ == "__main__":
    verify_diversity_logic()