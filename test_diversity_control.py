#!/usr/bin/env python3
"""
Test script to verify diversity control logic
"""

from json_team_generator_simple import generate_teams_from_database, analyze_team_diversity, load_teams_from_json

def test_diversity_control():
    """Test team generation with diversity control"""
    
    print("🔍 TESTING DIVERSITY CONTROL")
    print("=" * 40)
    
    print("\n🔄 Generating teams with min 3 differences...")
    filename = generate_teams_from_database(
        matchid="110766",
        num_teams=20,  # Smaller number for testing
        min_differences=3
    )
    
    if filename:
        print(f"\n📊 Loading teams from: {filename}")
        teams_data = load_teams_from_json(filename)
        
        if teams_data:
            print(f"✅ Loaded {len(teams_data.get('teams', []))} teams")
            
            # Analyze diversity
            diversity_stats = analyze_team_diversity(teams_data)
            
            print(f"\n📈 DIVERSITY ANALYSIS RESULTS:")
            print(f"   Total teams: {diversity_stats.get('total_teams', 0)}")
            print(f"   Total comparisons: {diversity_stats.get('total_comparisons', 0)}")
            print(f"   Average different players: {diversity_stats.get('avg_different_players', 0):.1f}")
            print(f"   Min different players: {diversity_stats.get('min_different_players', 0)}")
            print(f"   Max different players: {diversity_stats.get('max_different_players', 0)}")
            print(f"   Diversity violations: {diversity_stats.get('diversity_violations', 0)}")
            print(f"   Compliance: {'✅ PASS' if diversity_stats.get('diversity_compliance') else '❌ FAIL'}")
            
            # Show first few team comparisons manually
            teams = teams_data.get('teams', [])
            if len(teams) >= 2:
                print(f"\n🔍 MANUAL VERIFICATION (First 3 teams):")
                for i in range(min(3, len(teams))):
                    for j in range(i + 1, min(3, len(teams))):
                        team1_players = set(teams[i].get('players', []))
                        team2_players = set(teams[j].get('players', []))
                        common = len(team1_players & team2_players)
                        different = 11 - common
                        print(f"   Team {i+1} vs Team {j+1}: {different} different players, {common} common")
        else:
            print("❌ Failed to load teams data")
    else:
        print("❌ Failed to generate teams")

if __name__ == "__main__":
    test_diversity_control()