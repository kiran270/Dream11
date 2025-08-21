#!/usr/bin/env python3
"""
Dream11 API Client
Script to fetch team data from Dream11 API
"""

import requests
import json
import sys
from datetime import datetime

def fetch_dream11_teams(match_id, auth_token):
    """
    Fetch teams from Dream11 API
    
    Args:
        match_id (str): The match ID
        auth_token (str): JWT authentication token
    
    Returns:
        dict: API response data
    """
    
    # API endpoint
    url = "https://tg-backend.site/api/fantasy/list-of-teams"
    
    # Request payload
    payload = {
        "fantasyApp": "dream11",
        "matchId": match_id,
        "authToken": auth_token
    }
    
    return make_api_request(url, payload, "Fetch Teams")

def add_dream11_team(match_id, captain, vice_captain, players, auth_token, sport_index=0, team_type="new"):
    """
    Add a team to Dream11 API
    
    Args:
        match_id (str): The match ID
        captain (int): Captain player ID
        vice_captain (int): Vice-captain player ID
        players (list): List of 11 player IDs
        auth_token (str): JWT authentication token
        sport_index (int): Sport index (default: 0)
        team_type (str): Team type (default: "new")
    
    Returns:
        dict: API response data
    """
    
    # API endpoint
    url = "https://tg-backend.site/api/fantasy/add-team"
    
    # Request payload
    payload = {
        "matchId": match_id,
        "captain": captain,
        "vice_captain": vice_captain,
        "players": players,
        "fantasyApp": "dream11",
        "authToken": auth_token,
        "sportIndex": sport_index,
        "type": team_type,
        "id": id
    }
    
    return make_api_request(url, payload, "Add Team")

def edit_dream11_team(match_id, team_id, captain, vice_captain, players, auth_token, sport_index=0):
    """
    Edit an existing team in Dream11 API
    
    Args:
        match_id (str): The match ID
        team_id (int): The team ID to edit
        captain (int): Captain player ID
        vice_captain (int): Vice-captain player ID
        players (list): List of 11 player IDs
        auth_token (str): JWT authentication token
        sport_index (int): Sport index (default: 0)
    
    Returns:
        dict: API response data
    """
    
    # API endpoint
    url = "https://tg-backend.site/api/fantasy/edit-team"
    
    # Request payload
    payload = {
        "matchId": match_id,
        "id": team_id,
        "captain": captain,
        "vice_captain": vice_captain,
        "players": players,
        "fantasyApp": "dream11",
        "authToken": auth_token,
        "sportIndex": sport_index,
        "type": "edit"
    }
    
    return make_api_request(url, payload, "Edit Team")

def make_api_request(url, payload, operation_name):
    """
    Make API request with common headers and error handling
    
    Args:
        url (str): API endpoint URL
        payload (dict): Request payload
        operation_name (str): Name of the operation for logging
    
    Returns:
        dict: API response data
    """
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site'
    }
    
    try:
        print(f"🚀 {operation_name} - Making API request...")
        print(f"🌐 URL: {url}")
        print(f"📊 Match ID: {payload.get('matchId', 'N/A')}")
        if 'authToken' in payload:
            print(f"🔑 Auth Token: {payload['authToken'][:50]}...")
        
        # Show payload details for add team requests
        if 'captain' in payload and 'players' in payload:
            print(f"👑 Captain: {payload.get('captain')}")
            print(f"🥈 Vice-Captain: {payload.get('vice_captain')}")
            print(f"👥 Players: {payload.get('players')}")
            print(f"🏏 Fantasy App: {payload.get('fantasyApp')}")
            print(f"🎯 Sport Index: {payload.get('sportIndex')}")
            print(f"📝 Type: {payload.get('type')}")
        print()
        
        # Make the API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        print()
        
        # Check if request was successful
        if response.status_code in [200, 201, 204]:
            print(f"✅ {operation_name} successful!")
            
            # Handle 204 No Content response
            if response.status_code == 204:
                print(f"📦 Response: 204 No Content (Success - Team added successfully)")
                return {"status": "success", "message": "Team added successfully", "status_code": 204}
            
            # Handle responses with content (200, 201)
            try:
                if response.text.strip():  # Check if there's actually content
                    data = response.json()
                    print(f"📦 Response data type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"🔍 Response keys: {list(data.keys())}")
                        
                        # Check for success indicators
                        if 'status' in data:
                            print(f"📊 Status: {data['status']}")
                        if 'message' in data:
                            print(f"💬 Message: {data['message']}")
                    
                    return data
                else:
                    # Empty response body but successful status
                    print(f"📦 Empty response body with status {response.status_code}")
                    return {"status": "success", "message": f"Request successful (status {response.status_code})", "status_code": response.status_code}
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📄 Raw response: {response.text[:500]}...")
                # Still return success for 2xx status codes even if JSON parsing fails
                return {"status": "success", "message": f"Request successful but response not JSON (status {response.status_code})", "status_code": response.status_code}
                
        else:
            print(f"❌ {operation_name} failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏰ {operation_name} timeout - API took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🌐 {operation_name} connection error - Unable to reach the API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ {operation_name} request error: {e}")
        return None

def save_response_to_file(data, filename=None):
    """Save API response to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dream11_teams_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Response saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None

def analyze_teams_data(data):
    """Analyze the teams data structure"""
    if not data:
        return
    
    print("\n" + "="*50)
    print("📊 TEAMS DATA ANALYSIS")
    print("="*50)
    
    # Check for teams_list in the response
    teams = None
    if isinstance(data, dict):
        if 'teams_list' in data:
            teams = data['teams_list']
            print(f"✅ Found teams in 'teams_list'")
        elif 'teams' in data:
            teams = data['teams']
        elif 'data' in data:
            teams = data['data']
        elif 'result' in data:
            teams = data['result']
    elif isinstance(data, list):
        teams = data
    
    if teams and isinstance(teams, list) and len(teams) > 0:
        print(f"🏏 Total teams found: {len(teams)}")
        
        # Analyze first team structure
        first_team = teams[0]
        print(f"\n📋 First team structure:")
        if isinstance(first_team, dict):
            for key, value in first_team.items():
                value_type = type(value).__name__
                if isinstance(value, (list, dict)):
                    value_preview = f"{value_type} with {len(value)} items"
                else:
                    value_preview = str(value)
                print(f"  {key}: {value_preview}")
        
        # Analyze team composition
        print(f"\n🔍 Team Analysis:")
        for i, team in enumerate(teams[:3]):  # Analyze first 3 teams
            if isinstance(team, dict):
                team_num = team.get('team_number', i+1)
                player_list = team.get('player_list', [])
                captain = team.get('captain')
                vice_captain = team.get('vice_captain')
                
                print(f"\n  Team {team_num}:")
                print(f"    👥 Players: {len(player_list)} - {player_list}")
                print(f"    👑 Captain: {captain}")
                print(f"    🥈 Vice-Captain: {vice_captain}")
        
        # Summary statistics
        print(f"\n📈 Summary Statistics:")
        total_unique_players = set()
        captain_counts = {}
        vc_counts = {}
        
        for team in teams:
            if isinstance(team, dict):
                # Collect unique players
                players = team.get('player_list', [])
                total_unique_players.update(players)
                
                # Count captain selections
                captain = team.get('captain')
                if captain:
                    captain_counts[captain] = captain_counts.get(captain, 0) + 1
                
                # Count vice-captain selections
                vc = team.get('vice_captain')
                if vc:
                    vc_counts[vc] = vc_counts.get(vc, 0) + 1
        
        print(f"  🎯 Total unique players: {len(total_unique_players)}")
        print(f"  👑 Most popular captain: Player {max(captain_counts, key=captain_counts.get)} ({captain_counts[max(captain_counts, key=captain_counts.get)]} times)")
        print(f"  🥈 Most popular vice-captain: Player {max(vc_counts, key=vc_counts.get)} ({vc_counts[max(vc_counts, key=vc_counts.get)]} times)")
        
    else:
        print("⚠️  No teams data found or data is in unexpected format")

def test_add_team_api():
    """Test the add team API with sample data"""
    print("\n" + "="*50)
    print("🧪 TESTING ADD TEAM API")
    print("="*50)
    
    # Sample data from the provided URL
    match_id = "108980"
    captain = 10851
    vice_captain = 11306
    players = [10853, 10686, 10917, 10851, 11306, 10920, 46614, 12722, 97321, 17497, 166118]
    auth_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IlRqb0FsLVdyZWN3Z3MtZVVvcm5xWWE5Y2x4dyJ9.eyJhdWQiOlsiYXBpLmRyZWFtMTEuY29tIiwiZ3VhcmRpYW4iXSwiZXhwIjoxNzcxMDczODQwLCJpYXQiOjE3NTU1MjE4NDAsImlzcyI6ImRyZWFtMTEuY29tIiwic3ViIjoiNDY4MTYxIiwiYXpwIjoiMiIsInJmdCI6IjEifQ.jrxb75QWsdUnYbBdci5ll5MqijEb8Tjvrk9IKUkQqQKEYNQEdyyQ1kncCmN-i3hfmPQzFNgAe6IzYduyePc3gQZ2VX6mulZFjCq_mDkFI8agvgYSlQjSQ2rq8b5LQIoktWxoiTlCGZmhUQ1w6NJF9aQAaAxGAnU5ShGbPEFfA1zP6I9JjtOopNSpMAnAVOoP8YXqy3N3S92-nGeFwbSucSWndUjjWG3coEjX58gcc7lcS8QIlaVHn37igi6u3gzyUoV42e7SjeSSy9fvD8qirUkGkENn5VEbZmkKBWjIVHzbRLJAHxfEaJ0kno74YlSGp0UxikE1LOnJpcnmwDPP3Q"
    
    print(f"🏏 Adding team with:")
    print(f"  👑 Captain: {captain}")
    print(f"  🥈 Vice-Captain: {vice_captain}")
    print(f"  👥 Players: {players}")
    print(f"  📊 Total Players: {len(players)}")
    
    # Add the team
    result = add_dream11_team(match_id, captain, vice_captain, players, auth_token)
    
    if result:
        print(f"\n✅ Add team test completed!")
        return result
    else:
        print(f"\n❌ Add team test failed!")
        return None

def main():
    """Main function"""
    print("🏏 Dream11 API Client")
    print("=" * 30)
    
    # Default values
    match_id = "108980"
    auth_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IlRqb0FsLVdyZWN3Z3MtZVVvcm5xWWE5Y2x4dyJ9.eyJhdWQiOlsiYXBpLmRyZWFtMTEuY29tIiwiZ3VhcmRpYW4iXSwiZXhwIjoxNzcxMDczODQwLCJpYXQiOjE3NTU1MjE4NDAsImlzcyI6ImRyZWFtMTEuY29tIiwic3ViIjoiNDY4MTYxIiwiYXpwIjoiMiIsInJmdCI6IjEifQ.jrxb75QWsdUnYbBdci5ll5MqijEb8Tjvrk9IKUkQqQKEYNQEdyyQ1kncCmN-i3hfmPQzFNgAe6IzYduyePc3gQZ2VX6mulZFjCq_mDkFI8agvgYSlQjSQ2rq8b5LQIoktWxoiTlCGZmhUQ1w6NJF9aQAaAxGAnU5ShGbPEFfA1zP6I9JjtOopNSpMAnAVOoP8YXqy3N3S92-nGeFwbSucSWndUjjWG3coEjX58gcc7lcS8QIlaVHn37igi6u3gzyUoV42e7SjeSSy9fvD8qirUkGkENn5VEbZmkKBWjIVHzbRLJAHxfEaJ0kno74YlSGp0UxikE1LOnJpcnmwDPP3Q"
    
    # Check command line arguments for operation type
    operation = "fetch"  # default operation
    if len(sys.argv) > 1:
        if sys.argv[1] in ["fetch", "add", "both"]:
            operation = sys.argv[1]
        else:
            match_id = sys.argv[1]
    
    if len(sys.argv) > 2 and operation == "fetch":
        auth_token = sys.argv[2]
    
    print(f"🎯 Operation: {operation}")
    print()
    
    if operation in ["fetch", "both"]:
        # Fetch teams data
        print("📥 FETCHING TEAMS...")
        data = fetch_dream11_teams(match_id, auth_token)
        
        if data:
            # Save response to file
            filename = save_response_to_file(data, f"dream11_teams_fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            # Analyze the data
            analyze_teams_data(data)
            
            print(f"\n✅ Fetch operation completed!")
            if filename:
                print(f"📁 Data saved to: {filename}")
        else:
            print("\n❌ Fetch operation failed")
            if operation == "fetch":
                sys.exit(1)
    
    if operation in ["add", "both"]:
        # Add team functionality would go here
        print("\n📤 ADD TEAM FUNCTIONALITY...")
        add_result = None  # Placeholder for actual implementation
        
        if add_result:
            # Save add team response
            filename = save_response_to_file(add_result, f"dream11_add_team_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            print(f"📁 Add team response saved to: {filename}")
        else:
            print("\n❌ Add team operation failed")
            if operation == "add":
                sys.exit(1)
    
    print(f"\n🎉 All operations completed successfully!")

if __name__ == "__main__":
    main()