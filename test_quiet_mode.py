#!/usr/bin/env python3
"""
Test script to demonstrate quiet mode for team generation
"""

from json_team_generator_simple import generate_teams_from_database

def test_quiet_mode():
    """Test team generation in quiet mode"""
    
    print("🔇 TESTING QUIET MODE")
    print("=" * 30)
    
    print("\n🔊 Normal Mode (with progress output):")
    print("-" * 40)
    filename1 = generate_teams_from_database(
        matchid="110766",
        num_teams=20  # Smaller number for demo
    )
    
    print(f"\n🔇 Quiet Mode (minimal output):")
    print("-" * 40)
    
    # Modify the function call to use quiet mode
    # Note: We need to update the function to support quiet mode
    try:
        from json_team_generator_simple import generate_teams_json_only
        from db import getplayers, getteams
        
        # Get match data
        players = getplayers("110766")
        teams = getteams("110766")
        
        if players and teams:
            team_a_name = teams[0][1]
            team_b_name = teams[0][2]
            
            filename2 = generate_teams_json_only(
                players_data=players,
                team_a_name=team_a_name,
                team_b_name=team_b_name,
                match_id="110766",
                num_teams=20,
                quiet=True  # Enable quiet mode
            )
            
            print(f"✅ Quiet mode completed: {filename2}")
        else:
            print("❌ Could not get match data for quiet mode test")
            
    except Exception as e:
        print(f"❌ Quiet mode test failed: {e}")
    
    print(f"\n📊 COMPARISON:")
    print(f"   Normal mode: More detailed progress output")
    print(f"   Quiet mode: Minimal output, just results")

if __name__ == "__main__":
    test_quiet_mode()