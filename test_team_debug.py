#!/usr/bin/env python3

# Simple test to debug team generation
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_team_generation():
    """Test the team generation with debugging"""
    
    print("🧪 Testing team generation with debugging...")
    
    # Import the necessary functions
    try:
        from checkapp import getTeams, getDreamTeams
        print("✅ Successfully imported functions")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Create sample player data
    sample_players = []
    for i in range(20):
        player = [f'p{i}', f'Player{i}', 'TeamA' if i % 2 == 0 else 'TeamB', 
                 'BAT' if i < 5 else 'BOWL' if i < 10 else 'AL' if i < 15 else 'WK', 
                 'role', 50 + i, 100 + i]
        sample_players.append(player)
    
    # Distribute players into categories
    atop = sample_players[:3]
    amid = sample_players[3:6]
    ahit = sample_players[6:9]
    bpow = sample_players[9:11]
    bbre = sample_players[11:13]
    bdea = sample_players[13:15]
    btop = sample_players[15:17]
    bmid = sample_players[17:19]
    bhit = sample_players[19:20]
    apow = sample_players[0:1]  # Reuse some players
    abre = sample_players[1:2]
    adea = sample_players[2:3]
    
    print(f"📊 Sample data created:")
    print(f"   Total players: {len(sample_players)}")
    print(f"   atop: {len(atop)}, amid: {len(amid)}, ahit: {len(ahit)}")
    
    # Try to generate teams
    try:
        teams = getTeams(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, "TeamA", "TeamB")
        print(f"🎯 Result: {len(teams)} teams generated")
        
        if teams:
            print("✅ Team generation successful!")
            for i, team in enumerate(teams[:3]):  # Show first 3 teams
                print(f"   Team {i+1}: {len(team)} players")
        else:
            print("❌ No teams generated")
            
    except Exception as e:
        print(f"❌ Team generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_team_generation()