#!/usr/bin/env python3
"""
Integration example showing how to use JSON team generation 
with your existing Flask app and database
"""

from json_team_generator_simple import generate_teams_from_database, generate_teams_json_only
import json

def integrate_json_generation_with_flask():
    """
    Example of how to integrate JSON team generation with your existing Flask app
    This shows how to modify your existing generateTeams route
    """
    
    # This is how you would modify your existing @app.route("/generateTeams") function
    def generateTeams_with_json():
        """
        Modified version of your existing generateTeams function
        Now saves teams to JSON files with actual match data
        """
        
        # Get match ID from form (same as your existing code)
        matchid = request.form.get('matchid')
        winning = request.form.get('winning', 'Batting')
        
        if not matchid:
            return "Match ID required"
        
        print(f"🎯 Generating teams for match ID: {matchid}")
        print(f"🎯 Strategy: {winning}")
        
        # Method 1: Use the new JSON generation with database integration
        try:
            filename = generate_teams_from_database(
                matchid=matchid,
                num_teams=100,  # Or get from form: request.form.get('num_teams', 100)
                min_differences=3  # Or get from form: request.form.get('min_differences', 3)
            )
            
            if filename:
                print(f"✅ Teams saved to JSON: {filename}")
                
                # Load the generated teams for display
                with open(filename, 'r') as f:
                    teams_data = json.load(f)
                
                # Convert to format expected by your existing template
                teams_for_template = convert_json_to_template_format(teams_data)
                
                # Get additional data for template (same as your existing code)
                from db import getplayers, getteams
                players = getplayers(matchid)
                teams = getteams(matchid)
                
                # Return success message (in real app, render template)
                return f"Teams generated successfully: {filename}"
            else:
                return "Error generating teams", 500
                
        except Exception as e:
            print(f"❌ Error in JSON generation: {e}")
            return f"Error: {e}", 500
    
    return generateTeams_with_json

def convert_json_to_template_format(teams_data):
    """
    Convert JSON teams format to the format expected by your existing templates
    """
    template_teams = []
    
    for team in teams_data.get("teams", []):
        # Convert to format expected by finalteams.html
        # You may need to adjust this based on your template requirements
        template_team = {
            'id': team.get('id'),
            'name': team.get('name'),
            'players': team.get('players', []),
            'captain': team.get('captain'),
            'vice_captain': team.get('vice_captain'),
            'player_details': team.get('player_details', [])
        }
        template_teams.append(template_team)
    
    return template_teams

def add_json_download_route():
    """
    Example of adding a new route to download JSON files
    """
    
    def download_json_teams():
        """
        New route to download generated JSON teams
        Usage: /download_json_teams?filename=dream11_teams_20240115_143025.json
        """
        filename = request.args.get('filename')
        
        if not filename:
            return "Filename required", 400
        
        try:
            with open(filename, 'r') as f:
                teams_data = json.load(f)
            
            return teams_data  # In real app, use jsonify(teams_data)
            
        except FileNotFoundError:
            return "File not found", 404
        except Exception as e:
            return f"Error: {e}", 500
    
    return download_json_teams

def get_available_matches_with_json():
    """
    Example function to show available matches with JSON generation capability
    """
    try:
        from db import getMactches
        matches = getMactches()
        
        matches_info = []
        for match in matches:
            match_info = {
                'id': match[0],  # Assuming match ID is first column
                'team_a': match[1],  # Assuming team A is second column
                'team_b': match[2],  # Assuming team B is third column
                'can_generate_json': True  # All matches can generate JSON
            }
            matches_info.append(match_info)
        
        return matches_info
        
    except Exception as e:
        print(f"Error getting matches: {e}")
        return []

def main():
    """
    Example usage showing integration possibilities
    """
    
    print("🔗 INTEGRATION WITH EXISTING FLASK APP")
    print("=" * 50)
    
    print("\n📋 Available Integration Options:")
    print("1. Modify existing /generateTeams route to use JSON")
    print("2. Add new /generateTeamsJSON route alongside existing")
    print("3. Add /download_json_teams route for JSON downloads")
    print("4. Update templates to show JSON filename")
    
    print("\n🔧 Code Changes Needed:")
    print("1. Import: from json_team_generator_simple import generate_teams_from_database")
    print("2. Replace team generation logic with JSON approach")
    print("3. Update templates to handle JSON filenames")
    print("4. Add download links for JSON files")
    
    print("\n📁 Example Integration in checkapp.py:")
    print("""
@app.route("/generateTeams", methods=["POST", "GET"])
def generateTeams():
    matchid = request.form.get('matchid')
    winning = request.form.get('winning', 'Batting')
    
    # Generate teams using JSON approach
    filename = generate_teams_from_database(matchid=matchid, num_teams=100)
    
    if filename:
        # Load teams for template display
        with open(filename, 'r') as f:
            teams_data = json.load(f)
        
        # Get match info for template
        teams = getteams(matchid)
        
        return render_template("finalteams.html",
                             validcombinations=convert_json_to_template_format(teams_data),
                             teamA=teams[0][1],
                             teamB=teams[0][2],
                             json_filename=filename,
                             match_id=matchid)
    else:
        return "Error generating teams", 500
    """)
    
    print("\n📄 Template Updates (finalteams.html):")
    print("""
<!-- Add download link for JSON file -->
<div class="json-download">
    <h3>📁 Generated Teams File</h3>
    <p>Teams saved to: <strong>{{ json_filename }}</strong></p>
    <a href="/download_json_teams?filename={{ json_filename }}" 
       class="btn btn-primary" download>
        📥 Download JSON File
    </a>
</div>
    """)
    
    # Show available matches
    matches = get_available_matches_with_json()
    if matches:
        print(f"\n📊 Available Matches for JSON Generation:")
        for match in matches[:5]:  # Show first 5
            print(f"   ID: {match['id']} - {match['team_a']} vs {match['team_b']}")
    
    print(f"\n💡 To test with real data, update the match ID in json_team_generator_simple.py")
    print(f"   Change: database_match_id = \"70\"")
    print(f"   To your actual match ID from the database")

if __name__ == "__main__":
    main()