#!/usr/bin/env python3
"""
Add all 40 Dream11 teams using the edit team API with multiple users
"""

from dream11_api_client import edit_dream11_team
import time
import json
import os
import glob

def load_generated_teams():
    """Load teams and match_id from the latest generated JSON file"""
    # Find the latest generated teams file
    team_files = glob.glob("dream11_teams_*.json")
    if not team_files:
        raise FileNotFoundError("No generated teams file found. Please run team generation first.")
    
    # Get the most recent file
    latest_file = max(team_files, key=os.path.getctime)
    print(f"📂 Loading teams from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data

# Load teams and configuration from generated file
generated_data = load_generated_teams()
teams_data = generated_data['teams']
match_id = generated_data['metadata']['match_id']

# JSON Configuration with users
CONFIG = {
    "match_id": match_id,
    "users": [
        {
            "name": "kiran",
            "auth_token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IlRqb0FsLVdyZWN3Z3MtZVVvcm5xWWE5Y2x4dyJ9.eyJhdWQiOlsiYXBpLmRyZWFtMTEuY29tIiwiZ3VhcmRpYW4iXSwiZXhwIjoxNzcxMzE5OTg3LCJpYXQiOjE3NTU3Njc5ODcsImlzcyI6ImRyZWFtMTEuY29tIiwic3ViIjoiNDY4MTYxIiwiYXpwIjoiMiIsInJmdCI6IjEifQ.KvlKZ8fzvkikfKmzW02iaqDRUkcmdyaCFy33SnFBJBfqQBrU0uZjmK6hSYQ1yhJMceIuKpbP51yU_KFC-DB2Ftkrhpt3DeTq-06G-JRoTFAGphCFyQe7UseMs5V_RHRCAuyPP1etLlYPJEFp5jxbutwAI_-ayrSUq8B31buVl9d5L1dcK1cmorY5-10D6kTjmSVS_eKc79WExcdo1MMScJP60V82TypdVUbrtjfnx-9U6HbH6f1OcGam8zIk4lHEZgRLg_HDiJgHKlNXZedBSdkYgoxpvFV8dH8o8Xq6CKeRzotrzJGbn2lZ8EZVfw_noSN-hh8Z9ISlA7GG7sm3Ow",
            "team_range": [1, 6]
        },
        {
            "name": "eswar",
            "auth_token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IlRqb0FsLVdyZWN3Z3MtZVVvcm5xWWE5Y2x4dyJ9.eyJhdWQiOlsiYXBpLmRyZWFtMTEuY29tIiwiZ3VhcmRpYW4iXSwiZXhwIjoxNzcyMDMxMzY3LCJpYXQiOjE3NTY0NzkzNjcsImlzcyI6ImRyZWFtMTEuY29tIiwic3ViIjoiMTAwMzA5OTQiLCJhenAiOiIyIiwicmZ0IjoiMSJ9.FUMTOyL57Xlf4GiGW4_8FCYp16zAHxrTZufd4UWAOBiH1nZsOWGCJdgGYW9JVKan8urSN6OfpijIax63fFkasdHVpIbNP_x3qdOzcJlBa_rKyUCnkrE46I_KPgth7HRhVWvEs_8dOCkuGaAz0IX7QgRsyuNDvIKHcQXtns5FE3NAkvsrjopRyHSZfAiXnqXEUVIx_Rl-03TqatP3TvQwC1klSkxT6xrDI2bcELNKZ9xesr-afJXxoo-1zf0VFsSTZ8jmU-nM37smS00XvLkFcYWpmWTWis8690Q29mffUWa2oqRFUK5zjfpMwrloukJ8E6wxEUxOebAtTa7Q5hSisw",
            "team_range": [7, 12]
        }
    ]
}

def add_all_teams(specific_user=None):
    """Add teams to Dream11 using edit team API with multiple users
    Each user gets 6 teams from the JSON configuration
    
    Args:
        specific_user (str, optional): Add teams for specific user only.
    """
    success_count = 0
    failed_teams = []
    
    print(f"🏏 Adding Dream11 Teams with Multiple Users")
    print("=" * 60)
    print(f"📊 Total teams available: {len(teams_data)}")
    print(f"🎯 Match ID: {CONFIG['match_id']}")
    print(f"👥 Users configured: {len(CONFIG['users'])}")
    print()
    
    # Process teams for each user (6 teams per user)
    for user in CONFIG['users']:
        if specific_user and user['name'] != specific_user:
            continue
            
        user_name = user['name']
        auth_token = user['auth_token']
        
        print(f"\n👤 Processing 6 teams for {user_name}")
        print(f"   🔑 Auth token: {auth_token[:50]}...")
        
        # Skip if auth token is placeholder
        if "YOUR_USER" in auth_token:
            print(f"   ⚠️ Skipping {user_name} - Auth token not configured")
            continue
        
        user_success = 0
        user_failed = []
        
        # Process 6 teams for this user
        for dream11_team_id in range(1, 7):  # Dream11 team IDs 1-6
            if dream11_team_id - 1 >= len(teams_data):
                print(f"   ⚠️ Not enough teams in data for team ID {dream11_team_id}")
                break
                
            team_data = teams_data[dream11_team_id - 1]  # Use team data by index
            
            print(f"\n📤 Adding team {dream11_team_id} for {user_name}")
            print(f"   📝 Team name: {team_data['name']}")
            print(f"   👑 Captain: {team_data['captain']}")
            print(f"   🥈 Vice-Captain: {team_data['vice_captain']}")
            print(f"   👥 Players: {len(team_data['players'])} players")
            
            result = edit_dream11_team(
                CONFIG['match_id'],
                dream11_team_id,
                team_data['captain'],
                team_data['vice_captain'],
                team_data['players'],
                auth_token
            )
            
            if result:
                if isinstance(result, dict) and result.get('status') == 'success':
                    print(f"   ✅ Team {dream11_team_id} added successfully for {user_name}!")
                    if result.get('status_code') == 200:
                        print("   📦 Received 200 OK (Success)")
                    elif result.get('status_code') == 204:
                        print("   📦 Received 204 No Content (Success)")
                    user_success += 1
                    success_count += 1
                else:
                    print(f"   ⚠️ Team {dream11_team_id} - Unexpected response: {result}")
                    user_failed.append({
                        "team": dream11_team_id, 
                        "name": team_data['name'], 
                        "user": user_name,
                        "dream11_id": dream11_team_id
                    })
                    failed_teams.append(user_failed[-1])
            else:
                print(f"   ❌ Failed to add team {dream11_team_id} for {user_name}")
                user_failed.append({
                    "team": dream11_team_id, 
                    "name": team_data['name'], 
                    "user": user_name,
                    "dream11_id": dream11_team_id
                })
                failed_teams.append(user_failed[-1])
            
            # Small delay between requests
            time.sleep(1)
        
        # User summary
        print(f"\n📊 {user_name} Summary: {user_success}/6 teams successful")
        if user_failed:
            print(f"   ❌ Failed teams for {user_name}:")
            for failed in user_failed:
                print(f"      - Team {failed['team']}: {failed['name']}")
    
    # Final summary
    total_expected = len([u for u in CONFIG['users'] if "YOUR_USER" not in u['auth_token']]) * 6
    print("\n" + "="*60)
    print("🏁 FINAL SUMMARY")
    print("="*60)
    print(f"✅ Successfully added: {success_count}/{total_expected} teams")
    print(f"❌ Failed: {len(failed_teams)} teams")
    if total_expected > 0:
        print(f"📊 Success rate: {(success_count/total_expected)*100:.1f}%")
    
    if failed_teams:
        print(f"\n❌ Failed teams:")
        for failed in failed_teams:
            print(f"   - Team {failed['team']} ({failed['user']}): {failed['name']}")
        
        # Save failed teams to JSON file
        with open('failed_teams.json', 'w') as f:
            json.dump(failed_teams, f, indent=2)
        print(f"💾 Failed teams saved to 'failed_teams.json'")
    else:
        print(f"\n🎉 All teams added successfully!")
        # Clean up failed teams file if it exists
        if os.path.exists('failed_teams.json'):
            os.remove('failed_teams.json')
            print("🧹 Cleaned up previous failed teams file")
    
    return success_count, failed_teams

def retry_failed_teams():
    """Retry adding failed teams from JSON file"""
    print("🔄 Retrying failed teams...")
    
    if not os.path.exists('failed_teams.json'):
        print("❌ No failed teams file found")
        return
    
    with open('failed_teams.json', 'r') as f:
        failed_teams = json.load(f)
    
    if not failed_teams:
        print("❌ No failed teams to retry")
        return
    
    print(f"📂 Loaded {len(failed_teams)} failed teams from file")
    
    success_count = 0
    still_failed = []
    
    for failed_team in failed_teams:
        team_idx = failed_team['team'] - 1
        if team_idx >= len(teams_data):
            continue
            
        team_data = teams_data[team_idx]
        user_name = failed_team['user']
        dream11_id = failed_team['dream11_id']
        
        # Find user config
        user_config = None
        for user in CONFIG['users']:
            if user['name'] == user_name:
                user_config = user
                break
        
        if not user_config:
            print(f"❌ User config not found for {user_name}")
            still_failed.append(failed_team)
            continue
        
        print(f"\n🔄 Retrying team {failed_team['team']} for {user_name} (Dream11 ID: {dream11_id})")
        
        result = edit_dream11_team(
            CONFIG['match_id'],
            dream11_id,
            team_data['captain'],
            team_data['vice_captain'],
            team_data['players'],
            user_config['auth_token']
        )
        
        if result and isinstance(result, dict) and result.get('status') == 'success':
            print(f"   ✅ Retry successful!")
            success_count += 1
        else:
            print(f"   ❌ Retry failed")
            still_failed.append(failed_team)
        
        time.sleep(1)
    
    print(f"\n🏁 Retry Summary: {success_count}/{len(failed_teams)} teams successful")
    
    if still_failed:
        with open('failed_teams.json', 'w') as f:
            json.dump(still_failed, f, indent=2)
        print(f"💾 {len(still_failed)} teams still failed, saved to 'failed_teams.json'")
    else:
        if os.path.exists('failed_teams.json'):
            os.remove('failed_teams.json')
        print("🎉 All retry attempts successful!")

def show_config_summary():
    """Show configuration summary"""
    print("🏏 Dream11 Team Updater with Multiple Users")
    print("=" * 50)
    print(f"📊 Available teams: {len(teams_data)}")
    print(f"👥 Configured users: {len(CONFIG['users'])}")
    print(f"🎯 Match ID: {CONFIG['match_id']}")
    print(f"🏆 Match: {generated_data['metadata'].get('match', 'Unknown')}")
    
    # Show user configuration
    print("\n👥 User Configuration:")
    for user in CONFIG['users']:
        team_range = f"{user['team_range'][0]}-{user['team_range'][1]}"
        token_status = "✅ Configured" if "YOUR_USER" not in user['auth_token'] else "❌ Not configured"
        print(f"   {user['name']}: Teams {team_range} - {token_status}")
    
    print(f"\n📋 Will process {len(teams_data)} teams total (6 teams per user)")
    print("="*50)

def save_config_template():
    """Save configuration template to JSON file"""
    config_file = 'dream11_config.json'
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        print(f"📄 Configuration template saved to '{config_file}'")
        print("   Please update the auth tokens for each user before running.")
    else:
        print(f"📄 Configuration file '{config_file}' already exists")

def load_config():
    """Load configuration from JSON file if it exists"""
    config_file = 'dream11_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            print(f"📂 Loaded user configuration from '{config_file}'")
            # Update only the users part, keep match_id from generated data
            if 'users' in loaded_config:
                CONFIG['users'] = loaded_config['users']
            # Always keep match_id from generated data, not from config file
            print(f"🎯 Using match_id from generated teams: {CONFIG['match_id']}")
            if 'match_id' in loaded_config and loaded_config['match_id'] != CONFIG['match_id']:
                print(f"⚠️ Config file has different match_id ({loaded_config['match_id']}), using generated match_id ({CONFIG['match_id']})")
            return CONFIG
        except json.JSONDecodeError:
            print(f"❌ Error reading '{config_file}', using default configuration")
    return CONFIG

if __name__ == "__main__":
    import sys
    import os
    
    # Load configuration from file if available (this will update users)
    CONFIG = load_config()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--retry":
            # Retry mode
            retry_failed_teams()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🏏 Dream11 Team Updater with Multiple Users - Usage:")
            print("  python add_all_40_teams.py                    # Add 6 teams for all users")
            print("  python add_all_40_teams.py --retry            # Retry failed teams")
            print("  python add_all_40_teams.py --user kiran       # Add 6 teams for specific user")
            print("  python add_all_40_teams.py --config           # Generate config template")
            print("  python add_all_40_teams.py --help             # Show this help")
        elif sys.argv[1] == "--user" and len(sys.argv) > 2:
            # Command line mode for specific user
            user_name = sys.argv[2]
            success_count, failed_teams = add_all_teams(specific_user=user_name)
        elif sys.argv[1] == "--config":
            # Generate configuration template
            save_config_template()
        else:
            print("❌ Unknown option. Use --help for usage information.")
    else:
        # Default mode - show config and add all teams
        show_config_summary()
        success_count, failed_teams = add_all_teams()