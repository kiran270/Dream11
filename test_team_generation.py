#!/usr/bin/env python3
"""
Test script to debug team generation
"""

import sys
sys.path.append('.')

# Mock Flask modules
from unittest.mock import MagicMock
sys.modules['flask'] = MagicMock()
sys.modules['flask'].Flask = MagicMock()
sys.modules['flask'].render_template = MagicMock()
sys.modules['flask'].redirect = MagicMock()
sys.modules['flask'].jsonify = MagicMock()
sys.modules['flask'].request = MagicMock()

from db import getteams, getplayers
from checkapp import getTeams

def test_team_generation():
    print("🧪 Testing Team Generation")
    print("=" * 50)
    
    # Use match ID 64 (OVI-W vs TRT-W)
    matchid = 64
    
    try:
        # Get teams and players
        teams = getteams(matchid)
        players = getplayers(matchid)
        
        if not teams or not players:
            print(f"❌ No data found for match {matchid}")
            return
            
        print(f"📊 Found {len(teams)} teams and {len(players)} players")
        
        # Separate players by team
        teamA_players = [p for p in players if p[1] == teams[0][1]]  # p[1] is teamname
        teamB_players = [p for p in players if p[1] == teams[0][2]]
        
        print(f"👥 Team A ({teams[0][1]}): {len(teamA_players)} players")
        print(f"👥 Team B ({teams[0][2]}): {len(teamB_players)} players")
        
        # Distribute players across all categories
        # Team A players
        atop = teamA_players[:3] if len(teamA_players) >= 3 else teamA_players
        amid = teamA_players[3:5] if len(teamA_players) >= 5 else []
        ahit = teamA_players[5:7] if len(teamA_players) >= 7 else []
        apow = teamA_players[7:9] if len(teamA_players) >= 9 else []
        abre = teamA_players[9:11] if len(teamA_players) >= 11 else []
        adea = teamA_players[11:] if len(teamA_players) >= 11 else []
        
        # Team B players  
        btop = teamB_players[:3] if len(teamB_players) >= 3 else teamB_players
        bmid = teamB_players[3:5] if len(teamB_players) >= 5 else []
        bhit = teamB_players[5:7] if len(teamB_players) >= 7 else []
        bpow = teamB_players[7:9] if len(teamB_players) >= 9 else []
        bbre = teamB_players[9:11] if len(teamB_players) >= 11 else []
        bdea = teamB_players[11:] if len(teamB_players) >= 11 else []
        
        print(f"🎯 Calling getTeams...")
        
        # Generate teams
        result_teams = getTeams(
            atop, amid, ahit, apow, abre, adea,
            btop, bmid, bhit, bpow, bbre, bdea,
            teams[0][1], teams[0][2],
            top13_names=None,
            fixed_players_names=None,
            enforce_top13=False,
            ensure_diversity=True
        )
        
        print(f"\n✅ RESULT: Generated {len(result_teams)} teams")
        
        if result_teams:
            print(f"🏆 First team has {len(result_teams[0])} elements")
            if len(result_teams[0]) >= 13:
                print(f"👑 Captain: {result_teams[0][11][3] if len(result_teams[0][11]) > 3 else 'Unknown'}")
                print(f"🥈 Vice-Captain: {result_teams[0][12][3] if len(result_teams[0][12]) > 3 else 'Unknown'}")
        
        return len(result_teams)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    test_team_generation()