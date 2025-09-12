#!/usr/bin/env python3
"""
Debug team generation to find why teams are identical
"""

import random
import time
from json_team_generator_simple import generate_teams_from_database, load_teams_from_json

def debug_team_generation():
    """Debug why teams are identical"""
    
    print("🐛 DEBUGGING TEAM GENERATION")
    print("=" * 50)
    
    # Set different random seeds to ensure different results
    random.seed(int(time.time()))
    
    print("🔍 Generating teams with debug info...")
    
    # Generate just 3 teams to debug
    filename = generate_teams_from_database(
        matchid="110766",
        num_teams=3,
        min_differences=3
    )
    
    if filename:
        teams_data = load_teams_from_json(filename)
        teams = teams_data.get('teams', [])
        
        print(f"\n📊 DEBUGGING RESULTS:")
        print(f"Generated {len(teams)} teams")
        
        # Show each team's players
        for i, team in enumerate(teams):
            players = team.get('players', [])
            print(f"\n🏏 Team {i+1}:")
            print(f"   Player IDs: {players}")
            print(f"   Captain: {team.get('captain')}")
            print(f"   Vice-Captain: {team.get('vice_captain')}")
        
        # Check if teams are identical
        if len(teams) >= 2:
            team1_players = set(teams[0].get('players', []))
            team2_players = set(teams[1].get('players', []))
            
            if team1_players == team2_players:
                print(f"\n❌ CRITICAL BUG: Teams 1 and 2 are IDENTICAL!")
                print(f"   This should never happen with diversity control")
            else:
                common = len(team1_players & team2_players)
                different = 11 - common
                print(f"\n✅ Teams 1 and 2 are different:")
                print(f"   Common players: {common}")
                print(f"   Different players: {different}")
        
        # Check all pairs
        print(f"\n🔍 CHECKING ALL PAIRS:")
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team_i_players = set(teams[i].get('players', []))
                team_j_players = set(teams[j].get('players', []))
                
                if team_i_players == team_j_players:
                    print(f"❌ Teams {i+1} and {j+1} are IDENTICAL!")
                else:
                    common = len(team_i_players & team_j_players)
                    different = 11 - common
                    print(f"✅ Teams {i+1} and {j+1}: {different} different, {common} common")
    
    else:
        print("❌ Failed to generate teams")

def test_random_generation():
    """Test if random generation is working"""
    
    print(f"\n🎲 TESTING RANDOM GENERATION:")
    print("-" * 30)
    
    # Test basic randomization
    test_list = list(range(1, 21))  # 20 numbers
    
    print("Testing random.sample with same list 5 times:")
    for i in range(5):
        sample = random.sample(test_list, 11)
        print(f"   Sample {i+1}: {sample[:5]}... (showing first 5)")
    
    # Check if samples are different
    samples = []
    for i in range(5):
        sample = random.sample(test_list, 11)
        samples.append(set(sample))
    
    all_different = True
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            if samples[i] == samples[j]:
                print(f"❌ Samples {i+1} and {j+1} are identical!")
                all_different = False
    
    if all_different:
        print("✅ Random sampling is working correctly")
    else:
        print("❌ Random sampling is broken!")

if __name__ == "__main__":
    test_random_generation()
    debug_team_generation()