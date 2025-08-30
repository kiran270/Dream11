#!/usr/bin/env python3
"""
Automated Dream11 Team Uploader
Automatically reads generated JSON files and uploads teams to Dream11 accounts
"""

import json
import os
import glob
from datetime import datetime
from dream11_api_client import edit_dream11_team
import time

class AutoDream11Uploader:
    def __init__(self, config_file="dream11_config.json"):
        """Initialize with configuration file"""
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            print(f"📂 Loaded configuration from {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_file} not found")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error reading configuration: {e}")
            return None
    
    def find_latest_teams_file(self, pattern="dream11_teams_*.json"):
        """Find the most recent teams JSON file"""
        files = glob.glob(pattern)
        if not files:
            print(f"❌ No files found matching pattern: {pattern}")
            return None
        
        # Sort by modification time, get the latest
        latest_file = max(files, key=os.path.getmtime)
        print(f"📄 Found latest teams file: {latest_file}")
        return latest_file
    
    def load_teams_from_file(self, filename):
        """Load teams data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            teams = data.get('teams', [])
            metadata = data.get('metadata', {})
            
            print(f"📊 Loaded {len(teams)} teams from {filename}")
            print(f"🎯 Match: {metadata.get('match', 'Unknown')}")
            print(f"📅 Generated: {metadata.get('generated_on', 'Unknown')}")
            
            return teams, metadata
        except Exception as e:
            print(f"❌ Error loading teams from {filename}: {e}")
            return [], {}
    
    def distribute_teams_to_users(self, teams, max_teams_per_user=6, selected_users=None):
        """Distribute teams among configured users"""
        if not self.config or not self.config.get('users'):
            print("❌ No users configured")
            return {}
        
        distribution = {}
        team_index = 0
        
        for user in self.config['users']:
            user_name = user['name']
            auth_token = user['auth_token']
            
            # Skip users not in selected list (if provided)
            if selected_users and user_name not in selected_users:
                print(f"⏭️ Skipping {user_name} - Not selected")
                continue
            
            # Skip users with placeholder tokens
            if "YOUR_USER" in auth_token:
                print(f"⚠️ Skipping {user_name} - Auth token not configured")
                continue
            
            # Assign teams to this user
            user_teams = []
            for i in range(max_teams_per_user):
                if team_index < len(teams):
                    team = teams[team_index].copy()
                    team['dream11_team_id'] = i + 1  # Dream11 team IDs 1-6
                    user_teams.append(team)
                    team_index += 1
                else:
                    break
            
            if user_teams:
                distribution[user_name] = {
                    'auth_token': auth_token,
                    'teams': user_teams
                }
                print(f"👤 {user_name}: {len(user_teams)} teams assigned")
        
        return distribution
    
    def upload_teams_for_user(self, user_name, user_data, match_id):
        """Upload teams for a specific user"""
        auth_token = user_data['auth_token']
        teams = user_data['teams']
        
        print(f"\n👤 Uploading teams for {user_name}")
        print(f"   🔑 Auth token: {auth_token[:50]}...")
        print(f"   📊 Teams to upload: {len(teams)}")
        
        success_count = 0
        failed_teams = []
        
        for team in teams:
            dream11_team_id = team['dream11_team_id']
            team_name = team.get('name', f'Team {dream11_team_id}')
            captain = team['captain']
            vice_captain = team['vice_captain']
            players = team['players']
            
            print(f"\n📤 Uploading team {dream11_team_id} for {user_name}")
            print(f"   📝 Team name: {team_name}")
            print(f"   👑 Captain: {captain}")
            print(f"   🥈 Vice-Captain: {vice_captain}")
            print(f"   👥 Players: {len(players)} players")
            
            result = edit_dream11_team(
                match_id,
                dream11_team_id,
                captain,
                vice_captain,
                players,
                auth_token
            )
            
            if result and isinstance(result, dict) and result.get('status') == 'success':
                print(f"   ✅ Team {dream11_team_id} uploaded successfully!")
                success_count += 1
            else:
                print(f"   ❌ Failed to upload team {dream11_team_id}")
                failed_teams.append({
                    'team_id': dream11_team_id,
                    'name': team_name,
                    'user': user_name
                })
            
            # Small delay between requests
            time.sleep(1)
        
        print(f"\n📊 {user_name} Summary: {success_count}/{len(teams)} teams successful")
        return success_count, failed_teams
    
    def upload_all_teams(self, teams_file=None, match_id=None, selected_users=None):
        """Main function to upload all teams"""
        print("🚀 Starting Automated Dream11 Team Upload")
        print("=" * 50)
        
        # Find teams file if not provided
        if not teams_file:
            teams_file = self.find_latest_teams_file()
            if not teams_file:
                return False
        
        # Load teams from file
        teams, metadata = self.load_teams_from_file(teams_file)
        if not teams:
            print("❌ No teams to upload")
            return False
        
        # Prioritize match ID from generated file metadata, then parameter, then config
        if not match_id:
            # First try to get match_id from the generated file metadata
            match_id = metadata.get('match_id')
            if match_id:
                print(f"🎯 Using match_id from generated file: {match_id}")
            else:
                # Fallback to config file
                match_id = self.config.get('match_id') if self.config else None
                if match_id:
                    print(f"🎯 Using match_id from config file: {match_id}")
        else:
            print(f"🎯 Using provided match_id: {match_id}")
        
        if not match_id:
            print("❌ No match ID found in generated file or config")
            return False
        
        # Show warning if config file has different match_id
        config_match_id = self.config.get('match_id') if self.config else None
        if config_match_id and config_match_id != match_id:
            print(f"⚠️ Config file has different match_id ({config_match_id}), using generated match_id ({match_id})")
        
        print(f"🎯 Final match ID: {match_id}")
        
        # Distribute teams among users
        distribution = self.distribute_teams_to_users(teams, selected_users=selected_users)
        if not distribution:
            print("❌ No teams distributed")
            return False
        
        # Upload teams for each user
        total_success = 0
        total_failed = []
        
        for user_name, user_data in distribution.items():
            success, failed = self.upload_teams_for_user(user_name, user_data, match_id)
            total_success += success
            total_failed.extend(failed)
        
        # Final summary
        total_teams = sum(len(user_data['teams']) for user_data in distribution.values())
        print("\n" + "="*50)
        print("🏁 UPLOAD SUMMARY")
        print("="*50)
        print(f"✅ Successfully uploaded: {total_success}/{total_teams} teams")
        print(f"❌ Failed: {len(total_failed)} teams")
        if total_teams > 0:
            print(f"📊 Success rate: {(total_success/total_teams)*100:.1f}%")
        
        if total_failed:
            print(f"\n❌ Failed teams:")
            for failed in total_failed:
                print(f"   - Team {failed['team_id']} ({failed['user']}): {failed['name']}")
        
        return total_success > 0

def main():
    """Main function for command line usage"""
    import sys
    
    uploader = AutoDream11Uploader()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🏏 Automated Dream11 Team Uploader - Usage:")
            print("  python auto_dream11_uploader.py                    # Upload latest teams file")
            print("  python auto_dream11_uploader.py filename.json      # Upload specific file")
            print("  python auto_dream11_uploader.py --help             # Show this help")
        else:
            # Upload specific file
            teams_file = sys.argv[1]
            uploader.upload_all_teams(teams_file)
    else:
        # Upload latest file
        uploader.upload_all_teams()

if __name__ == "__main__":
    main()