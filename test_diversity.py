#!/usr/bin/env python3
"""
Test script to verify diversity checking is working
"""

import sys
import os
sys.path.append('.')

# Import required modules
from db import create_connection, getplayers, getteams
from checkapp import getTeams

def test_diversity():
    print("🧪 Testing Team Diversity Check")
    print("=" * 50)
    
    # Use a real match ID from the database
    matchid = 64  # OVI-W vs TRT-W
    
    try:
        # Get teams and players
        teams = getteams(matchid)
        players = getplayers(matchid)
        
        if not teams or not players:
            print("❌ No teams or players found for match ID:", matchid)
            return
            
        print(f"📊 Found {len(teams)} teams and {len(players)} players")
        
        # Separate players by team and role (simplified version)
        # players structure: (matchid, teamname, role, playername, credits, percentage, matchrole, player_id)
        teamA_players = [p for p in players if p[1] == teams[0][1]]  # p[1] is teamname
        teamB_players = [p for p in players if p[1] == teams[0][2]]  # p[1] is teamname
        
        print(f"👥 Team A ({teams[0][1]}): {len(teamA_players)} players")
        print(f"👥 Team B ({teams[0][2]}): {len(teamB_players)} players")
        
        # Simple role distribution for testing
        atop = teamA_players[:3] if len(teamA_players) >= 3 else teamA_players
        amid = teamA_players[3:6] if len(teamA_players) >= 6 else []
        ahit = teamA_players[6:9] if len(teamA_players) >= 9 else []
        
        btop = teamB_players[:3] if len(teamB_players) >= 3 else teamB_players
        bmid = teamB_players[3:6] if len(teamB_players) >= 6 else []
        bhit = teamB_players[6:9] if len(teamB_players) >= 9 else []
        
        # Empty bowling categories for simplicity
        apow = abre = adea = bpow = bbre = bdea = []
        
        print(f"🎯 Generating teams with diversity check enabled...")
        
        # Generate teams with diversity enabled
        result_teams = getTeams(
            atop, amid, ahit, apow, abre, adea,
            btop, bmid, bhit, bpow, bbre, bdea,
            teams[0][1], teams[0][2],
            top13_names=None,
            fixed_players_names=None,
            enforce_top13=False,
            ensure_diversity=True
        )
        
        print(f"✅ Generated {len(result_teams)} teams")
        
        if result_teams:
            print(f"🏆 Top team percentage: {result_teams[0][-1]:.1f}%")
            print(f"📉 Bottom team percentage: {result_teams[-1][-1]:.1f}%")
            
            # Check diversity between first few teams
            if len(result_teams) >= 2:
                team1_players = set([p[0] for p in result_teams[0][:11]])
                team2_players = set([p[0] for p in result_teams[1][:11]])
                common = len(team1_players.intersection(team2_players))
                print(f"🔍 Common players between team 1 & 2: {common}/11")
                
        return len(result_teams)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    test_diversity()