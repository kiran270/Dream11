#!/usr/bin/env python3
"""
Test sequential diversity control logic
"""

from json_team_generator_simple import generate_teams_from_database, analyze_sequential_team_diversity, load_teams_from_json

def test_sequential_diversity():
    """Test sequential diversity with detailed output"""
    
    print("🔍 TESTING SEQUENTIAL DIVERSITY CONTROL")
    print("=" * 50)
    print("Logic: T1→T2: 3 diff, T1→T3 & T2→T3: 3 diff each, etc.")
    print("-" * 50)
    
    # Test with small number to see detailed output
    filename = generate_teams_from_database(
        matchid="110766",
        num_teams=10,  # Small number to see detailed logic
        min_differences=3
    )
    
    if filename:
        print(f"\n📊 Loading and analyzing teams from: {filename}")
        teams_data = load_teams_from_json(filename)
        
        if teams_data:
            # Show manual verification for first few teams
            teams = teams_data.get('teams', [])
            print(f"\n🔍 MANUAL SEQUENTIAL VERIFICATION:")
            print(f"   Generated {len(teams)} teams")
            
            for i in range(min(5, len(teams))):
                print(f"\n   T{i+1} vs all previous teams:")
                violations = 0
                
                for j in range(i):
                    team1_players = set(teams[i].get('players', []))
                    team2_players = set(teams[j].get('players', []))
                    common = len(team1_players & team2_players)
                    different = 11 - common
                    
                    status = "✅" if different >= 3 else "❌"
                    print(f"     T{i+1} vs T{j+1}: {different} different, {common} common {status}")
                    
                    if different < 3:
                        violations += 1
                
                if i == 0:
                    print(f"     T1: No previous teams to check")
                elif violations == 0:
                    print(f"     T{i+1}: ✅ Compliant with all {i} previous teams")
                else:
                    print(f"     T{i+1}: ❌ {violations} violations")
            
            # Run full analysis
            print(f"\n" + "="*50)
            analyze_sequential_team_diversity(teams_data, min_differences=3)
            
        else:
            print("❌ Failed to load teams data")
    else:
        print("❌ Failed to generate teams")

if __name__ == "__main__":
    test_sequential_diversity()