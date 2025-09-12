#!/usr/bin/env python3
"""
Test script to demonstrate file generation behavior
Shows how each run creates a separate file with unique timestamp
"""

import json
import os
from datetime import datetime
from json_team_generator_simple import generate_teams_json_only

def test_multiple_runs():
    """Test that multiple runs create separate files"""
    
    print("🧪 TESTING FILE GENERATION BEHAVIOR")
    print("=" * 50)
    
    # Sample player data
    sample_players = [
        (1, "India", "BAT", "Virat Kohli", "11.0 Cr", 85.5, "TOP-HIT", 10001),
        (2, "India", "BAT", "Rohit Sharma", "10.5 Cr", 78.2, "TOP-HIT", 10002),
        (3, "India", "WK", "KL Rahul", "10.0 Cr", 72.1, "MID-HIT", 10003),
        (4, "India", "AR", "Hardik Pandya", "9.5 Cr", 68.9, "MID-HIT", 10004),
        (5, "India", "AR", "Ravindra Jadeja", "9.0 Cr", 65.3, "MID-HIT", 10005),
        (6, "India", "BOWL", "Jasprit Bumrah", "9.5 Cr", 71.4, "POW-BRE", 10006),
        (7, "India", "BOWL", "Mohammed Shami", "8.5 Cr", 58.7, "POW-BRE", 10007),
        (8, "India", "BOWL", "Yuzvendra Chahal", "8.0 Cr", 52.3, "BRE-DEA", 10008),
        (9, "India", "BAT", "Shikhar Dhawan", "9.0 Cr", 61.8, "TOP-MID", 10009),
        (10, "India", "WK", "Rishabh Pant", "9.5 Cr", 69.2, "MID-HIT", 10010),
        (11, "India", "BAT", "Shreyas Iyer", "8.5 Cr", 55.6, "MID-HIT", 10011),
        
        (12, "Pakistan", "BAT", "Babar Azam", "10.5 Cr", 82.1, "TOP-HIT", 20001),
        (13, "Pakistan", "WK", "Mohammad Rizwan", "10.0 Cr", 75.8, "TOP-MID", 20002),
        (14, "Pakistan", "BAT", "Fakhar Zaman", "9.0 Cr", 63.4, "TOP-MID", 20003),
        (15, "Pakistan", "AR", "Shadab Khan", "8.5 Cr", 59.7, "MID-HIT", 20004),
        (16, "Pakistan", "AR", "Imad Wasim", "8.0 Cr", 48.9, "MID-BRE", 20005),
        (17, "Pakistan", "BOWL", "Shaheen Afridi", "9.5 Cr", 73.2, "POW-BRE", 20006),
        (18, "Pakistan", "BOWL", "Haris Rauf", "8.5 Cr", 56.1, "BRE-DEA", 20007),
        (19, "Pakistan", "BOWL", "Naseem Shah", "8.0 Cr", 51.8, "POW-BRE", 20008),
        (20, "Pakistan", "AR", "Mohammad Hafeez", "8.0 Cr", 47.3, "MID-HIT", 20009),
        (21, "Pakistan", "WK", "Sarfaraz Ahmed", "7.5 Cr", 42.6, "MID-HIT", 20010),
        (22, "Pakistan", "BAT", "Asif Ali", "7.5 Cr", 38.9, "HIT-DEA", 20011)
    ]
    
    # Get list of existing JSON files before test
    existing_files = [f for f in os.listdir('.') if f.startswith('dream11_teams_') and f.endswith('.json')]
    print(f"📁 Existing JSON files before test: {len(existing_files)}")
    
    generated_files = []
    
    # Run multiple generations
    for run in range(1, 4):  # 3 runs
        print(f"\n🔄 RUN {run}:")
        print("-" * 30)
        
        filename = generate_teams_json_only(
            players_data=sample_players,
            team_a_name="India",
            team_b_name="Pakistan",
            match_id=f"TEST_RUN_{run}",
            num_teams=5  # Smaller number for faster testing
        )
        
        if filename:
            generated_files.append(filename)
            print(f"✅ Generated file: {filename}")
            
            # Verify file exists and has content
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    teams_count = data.get('metadata', {}).get('total_teams', 0)
                    match_id = data.get('metadata', {}).get('match_id', 'Unknown')
                    print(f"   📊 Teams in file: {teams_count}")
                    print(f"   🆔 Match ID: {match_id}")
            else:
                print(f"❌ File not found: {filename}")
        else:
            print(f"❌ Failed to generate file for run {run}")
        
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.1)
    
    # Final verification
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 50)
    print(f"✅ Total files generated: {len(generated_files)}")
    print(f"📁 Generated files:")
    for i, filename in enumerate(generated_files, 1):
        print(f"   {i}. {filename}")
    
    # Verify all files are unique
    unique_files = set(generated_files)
    if len(unique_files) == len(generated_files):
        print(f"✅ All {len(generated_files)} files have unique names!")
    else:
        print(f"❌ Found duplicate filenames! Unique: {len(unique_files)}, Total: {len(generated_files)}")
    
    # Show file sizes
    print(f"\n📏 File sizes:")
    for filename in generated_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   {filename}: {size:,} bytes")
    
    return generated_files

def cleanup_test_files(files_to_remove):
    """Clean up test files"""
    print(f"\n🧹 CLEANUP:")
    print("-" * 20)
    
    for filename in files_to_remove:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Removed: {filename}")
            else:
                print(f"⚠️ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error removing {filename}: {e}")

if __name__ == "__main__":
    # Run the test
    generated_files = test_multiple_runs()
    
    # Ask user if they want to clean up
    print(f"\n❓ Do you want to remove the {len(generated_files)} test files? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            cleanup_test_files(generated_files)
        else:
            print("📁 Test files kept for your review")
    except:
        print("📁 Test files kept for your review")