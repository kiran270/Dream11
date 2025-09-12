#!/usr/bin/env python3
"""
Check exact player differences between all teams
"""

from json_team_generator_simple import generate_teams_from_database, load_teams_from_json

def check_exact_differences():
    """Check exact differences between all team pairs"""
    
    print("🔍 CHECKING EXACT PLAYER DIFFERENCES")
    print("=" * 50)
    print("Requirement: Each team pair must have ≥3 different players")
    print("-" * 50)
    
    # Generate teams with current logic
    filename = generate_teams_from_database(
        matchid="110766",
        num_teams=10,
        min_differences=3
    )
    
    if filename:
        teams_data = load_teams_from_json(filename)
        teams = teams_data.get('teams', [])
        
        print(f"\n📊 ANALYZING ALL TEAM PAIRS:")
        print(f"Generated {len(teams)} teams")
        
        violations = []
        min_difference = 11
        max_difference = 0
        total_differences = 0
        total_comparisons = 0
        
        # Check every team pair
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team_i_players = set(teams[i].get('players', []))
                team_j_players = set(teams[j].get('players', []))
                
                common_players = len(team_i_players & team_j_players)
                different_players = 11 - common_players
                
                total_differences += different_players
                total_comparisons += 1
                min_difference = min(min_difference, different_players)
                max_difference = max(max_difference, different_players)
                
                status = "✅" if different_players >= 3 else "❌"
                
                if different_players < 3:
                    violations.append(f"T{i+1} vs T{j+1}: Only {different_players} different players")
                
                # Show first 10 comparisons in detail
                if len(violations) == 0 and total_comparisons <= 10:
                    print(f"   T{i+1} vs T{j+1}: {different_players} different, {common_players} common {status}")
        
        avg_difference = total_differences / total_comparisons if total_comparisons > 0 else 0
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Total team pairs: {total_comparisons}")
        print(f"   Average different players: {avg_difference:.1f}")
        print(f"   Minimum different players: {min_difference}")
        print(f"   Maximum different players: {max_difference}")
        print(f"   Violations (< 3 different): {len(violations)}")
        
        if violations:
            print(f"\n❌ VIOLATIONS FOUND:")
            for violation in violations[:10]:  # Show first 10
                print(f"   {violation}")
        else:
            print(f"\n✅ PERFECT COMPLIANCE!")
            print(f"   All {total_comparisons} team pairs have ≥3 different players")
        
        # Show distribution of differences
        difference_counts = {}
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team_i_players = set(teams[i].get('players', []))
                team_j_players = set(teams[j].get('players', []))
                different_players = 11 - len(team_i_players & team_j_players)
                difference_counts[different_players] = difference_counts.get(different_players, 0) + 1
        
        print(f"\n📈 DIFFERENCE DISTRIBUTION:")
        for diff in sorted(difference_counts.keys()):
            count = difference_counts[diff]
            percentage = (count / total_comparisons) * 100
            print(f"   {diff} different players: {count} pairs ({percentage:.1f}%)")
    
    else:
        print("❌ Failed to generate teams")

if __name__ == "__main__":
    check_exact_differences()