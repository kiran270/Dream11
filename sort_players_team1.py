#!/usr/bin/env python3
"""
Sort players by percentage and pick top 11 as team1
"""

from db import create_connection, getplayers
import sqlite3

def get_players_sorted_by_percentage(match_id):
    """
    Get all players for a match sorted by percentage (highest first)
    
    Args:
        match_id: The match ID to get players for
    
    Returns:
        List of player records sorted by percentage
    """
    try:
        con = create_connection()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        # Get all players for the match, sorted by percentage descending
        cur.execute("""
            SELECT * FROM player 
            WHERE matchid = ? 
            ORDER BY CAST(percentage AS REAL) DESC
        """, [match_id])
        
        players = cur.fetchall()
        con.close()
        
        return players
    except Exception as e:
        print(f"❌ Error getting players: {e}")
        return []

def create_team1_from_top_players(match_id):
    """
    Create team1 by selecting top 11 players by percentage
    
    Args:
        match_id: The match ID to create team for
    
    Returns:
        Dictionary containing team1 information
    """
    players = get_players_sorted_by_percentage(match_id)
    
    if len(players) < 11:
        print(f"❌ Not enough players found. Need 11, found {len(players)}")
        return None
    
    # Get top 11 players
    top_11_players = players[:11]
    
    # Calculate total percentage
    total_percentage = sum([float(player['percentage']) for player in top_11_players])
    
    # Assign captain (highest percentage) and vice-captain (second highest)
    captain = top_11_players[0]
    vice_captain = top_11_players[1]
    
    # Create team structure
    team1 = {
        'team_name': 'Team 1 - Top Percentage Players',
        'players': [],
        'captain': {
            'name': captain['playername'],
            'team': captain['teamname'],
            'role': captain['role'],
            'percentage': float(captain['percentage']),
            'credits': captain['credits']
        },
        'vice_captain': {
            'name': vice_captain['playername'],
            'team': vice_captain['teamname'],
            'role': vice_captain['role'],
            'percentage': float(vice_captain['percentage']),
            'credits': vice_captain['credits']
        },
        'total_percentage': total_percentage,
        'total_credits': 0
    }
    
    # Add all players to team
    total_credits = 0
    for i, player in enumerate(top_11_players):
        player_info = {
            'position': i + 1,
            'name': player['playername'],
            'team': player['teamname'],
            'role': player['role'],
            'percentage': float(player['percentage']),
            'credits': player['credits'],
            'is_captain': i == 0,
            'is_vice_captain': i == 1
        }
        
        # Calculate credits (remove 'Cr' and convert to float)
        try:
            credits_value = float(player['credits'].replace(' Cr', '').replace('Cr', '').strip())
            total_credits += credits_value
        except:
            credits_value = 0
        
        player_info['credits_value'] = credits_value
        team1['players'].append(player_info)
    
    team1['total_credits'] = total_credits
    
    return team1

def display_team1(team1):
    """
    Display team1 in a formatted way
    
    Args:
        team1: Team dictionary from create_team1_from_top_players
    """
    if not team1:
        print("❌ No team to display")
        return
    
    print("\n" + "="*60)
    print(f"🏆 {team1['team_name']}")
    print("="*60)
    
    print(f"👑 Captain: {team1['captain']['name']} ({team1['captain']['percentage']:.1f}%)")
    print(f"🥈 Vice Captain: {team1['vice_captain']['name']} ({team1['vice_captain']['percentage']:.1f}%)")
    print(f"📊 Total Percentage: {team1['total_percentage']:.1f}%")
    print(f"💰 Total Credits: {team1['total_credits']:.1f} Cr")
    
    print("\n📋 Team Composition:")
    print("-" * 60)
    print(f"{'#':<3} {'Player':<20} {'Team':<8} {'Role':<6} {'%':<6} {'Cr':<6}")
    print("-" * 60)
    
    for player in team1['players']:
        captain_mark = "👑" if player['is_captain'] else "🥈" if player['is_vice_captain'] else "  "
        print(f"{player['position']:<3} {player['name']:<20} {player['team']:<8} {player['role']:<6} {player['percentage']:<6.1f} {player['credits_value']:<6.1f} {captain_mark}")
    
    print("-" * 60)
    
    # Role distribution
    role_count = {}
    for player in team1['players']:
        role = player['role']
        role_count[role] = role_count.get(role, 0) + 1
    
    print("\n🎯 Role Distribution:")
    for role, count in sorted(role_count.items()):
        print(f"   {role}: {count} players")

def main():
    """
    Main function to demonstrate the functionality
    """
    # Get match ID from user or use default
    try:
        match_id = input("Enter match ID (or press Enter for default): ").strip()
        if not match_id:
            # Try to get the latest match
            con = create_connection()
            cur = con.cursor()
            cur.execute("SELECT MAX(matchid) FROM matches")
            result = cur.fetchone()
            con.close()
            
            if result and result[0]:
                match_id = result[0]
                print(f"Using latest match ID: {match_id}")
            else:
                print("❌ No matches found in database")
                return
        else:
            match_id = int(match_id)
    except ValueError:
        print("❌ Invalid match ID")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print(f"\n🔍 Creating Team 1 for match ID: {match_id}")
    
    # Create team1
    team1 = create_team1_from_top_players(match_id)
    
    if team1:
        display_team1(team1)
        
        # Ask if user wants to save this team
        save_choice = input("\n💾 Save this team to database? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_team1_to_database(team1, match_id)
    else:
        print("❌ Failed to create team")

def save_team1_to_database(team1, match_id):
    """
    Save team1 to the dreamteams table
    
    Args:
        team1: Team dictionary
        match_id: Match ID
    """
    try:
        from db import addDreamTeam
        
        # Get match info
        con = create_connection()
        cur = con.cursor()
        cur.execute("SELECT team1, team2 FROM matches WHERE matchid = ?", [match_id])
        match_info = cur.fetchone()
        con.close()
        
        if not match_info:
            print("❌ Match not found")
            return
        
        team1_name, team2_name = match_info
        match_between = f"{team1_name} vs {team2_name}"
        
        # Prepare player positions (using player names)
        players = team1['players']
        
        success = addDreamTeam(
            matchbetween=match_between,
            stadium="Top Percentage Strategy",
            wininning="Balanced",
            one=players[0]['name'] if len(players) > 0 else "",
            two=players[1]['name'] if len(players) > 1 else "",
            three=players[2]['name'] if len(players) > 2 else "",
            four=players[3]['name'] if len(players) > 3 else "",
            five=players[4]['name'] if len(players) > 4 else "",
            six=players[5]['name'] if len(players) > 5 else "",
            seven=players[6]['name'] if len(players) > 6 else "",
            eight=players[7]['name'] if len(players) > 7 else "",
            nine=players[8]['name'] if len(players) > 8 else "",
            ten=players[9]['name'] if len(players) > 9 else "",
            eleven=players[10]['name'] if len(players) > 10 else "",
            twelve="0",
            cap=0,  # Captain is first player
            vc=1,   # Vice-captain is second player
            source_match_id=match_id
        )
        
        if success:
            print("✅ Team saved to database successfully!")
        else:
            print("❌ Failed to save team to database")
            
    except Exception as e:
        print(f"❌ Error saving team: {e}")

if __name__ == "__main__":
    main()