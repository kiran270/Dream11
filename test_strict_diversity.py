#!/usr/bin/env python3
"""
Test strict diversity control with higher requirements
"""

from json_team_generator_simple import generate_teams_from_database, analyze_team_diversity, load_teams_from_json

def test_strict_diversity():
    """Test with stricter diversity requirements"""
    
    print("🔍 TESTING STRICT DIVERSITY CONTROL")
    print("=" * 45)
    
    # Test with different diversity levels
    diversity_levels = [3, 4, 5]
    
    for min_diff in diversity_levels:
        print(f"\n🎯 Testing with min {min_diff} differences (max {11-min_diff} common players):")
        print("-" * 50)
        
        filename = generate_teams_from_database(
            matchid="110766",
            num_teams=15,  # Smaller number for stricter requirements
            min_differences=min_diff
        )
        
        if filename:
            teams_data = load_teams_from_json(filename)
            
            if teams_data:
                diversity_stats = analyze_team_diversity(teams_data)
                
                print(f"📊 Results for min {min_diff} differences:")
                print(f"   Teams generated: {diversity_stats.get('total_teams', 0)}")
                print(f"   Average different: {diversity_stats.get('avg_different_players', 0):.1f}")
                print(f"   Min different: {diversity_stats.get('min_different_players', 0)}")
                print(f"   Violations: {diversity_stats.get('diversity_violations', 0)}")
                print(f"   Status: {'✅ PASS' if diversity_stats.get('diversity_compliance') else '❌ FAIL'}")
            else:
                print("❌ Failed to load teams")
        else:
            print("❌ Failed to generate teams")

if __name__ == "__main__":
    test_strict_diversity()