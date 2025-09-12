#!/usr/bin/env python3
"""
Debug player categories to see why teams are identical
"""

from db import getplayers, getteams

def debug_player_categories():
    """Debug player categorization"""
    
    print("🔍 DEBUGGING PLAYER CATEGORIES")
    print("=" * 50)
    
    matchid = "110766"
    players = getplayers(matchid)
    teams = getteams(matchid)
    
    if not players:
        print("❌ No players found")
        return
    
    if not teams:
        print("❌ No teams found")
        return
    
    print(f"📊 Total players: {len(players)}")
    print(f"🏏 Teams: {teams[0][1]} vs {teams[0][2]}")
    
    # Separate by team
    teamA_players = [p for p in players if p[1] == teams[0][1]]
    teamB_players = [p for p in players if p[1] == teams[0][2]]
    
    print(f"📊 {teams[0][1]} players: {len(teamA_players)}")
    print(f"📊 {teams[0][2]} players: {len(teamB_players)}")
    
    # Show match roles distribution
    print(f"\n🎯 MATCH ROLES DISTRIBUTION:")
    
    # Count match roles for Team A
    teamA_roles = {}
    for player in teamA_players:
        role = str(player[6]) if len(player) > 6 else "Unknown"
        teamA_roles[role] = teamA_roles.get(role, 0) + 1
    
    print(f"\n{teams[0][1]} Match Roles:")
    for role, count in sorted(teamA_roles.items()):
        print(f"   {role}: {count} players")
    
    # Count match roles for Team B
    teamB_roles = {}
    for player in teamB_players:
        role = str(player[6]) if len(player) > 6 else "Unknown"
        teamB_roles[role] = teamB_roles.get(role, 0) + 1
    
    print(f"\n{teams[0][2]} Match Roles:")
    for role, count in sorted(teamB_roles.items()):
        print(f"   {role}: {count} players")
    
    # Categorize players like the original code
    atop = [p for p in teamA_players if 'TOP' in str(p[6])]
    amid = [p for p in teamA_players if 'MID' in str(p[6])]
    ahit = [p for p in teamA_players if 'HIT' in str(p[6])]
    apow = [p for p in teamA_players if 'POW' in str(p[6])]
    abre = [p for p in teamA_players if 'BRE' in str(p[6])]
    adea = [p for p in teamA_players if 'DEA' in str(p[6])]
    
    btop = [p for p in teamB_players if 'TOP' in str(p[6])]
    bmid = [p for p in teamB_players if 'MID' in str(p[6])]
    bhit = [p for p in teamB_players if 'HIT' in str(p[6])]
    bpow = [p for p in teamB_players if 'POW' in str(p[6])]
    bbre = [p for p in teamB_players if 'BRE' in str(p[6])]
    bdea = [p for p in teamB_players if 'DEA' in str(p[6])]
    
    print(f"\n📋 CATEGORIZED PLAYERS:")
    print(f"{teams[0][1]} Categories:")
    print(f"   TOP: {len(atop)} players")
    print(f"   MID: {len(amid)} players") 
    print(f"   HIT: {len(ahit)} players")
    print(f"   POW: {len(apow)} players")
    print(f"   BRE: {len(abre)} players")
    print(f"   DEA: {len(adea)} players")
    
    print(f"\n{teams[0][2]} Categories:")
    print(f"   TOP: {len(btop)} players")
    print(f"   MID: {len(bmid)} players")
    print(f"   HIT: {len(bhit)} players")
    print(f"   POW: {len(bpow)} players")
    print(f"   BRE: {len(bbre)} players")
    print(f"   DEA: {len(bdea)} players")
    
    # Show actual players in each category (first few)
    print(f"\n👥 SAMPLE PLAYERS BY CATEGORY:")
    
    categories = [
        ("atop", atop), ("amid", amid), ("ahit", ahit),
        ("btop", btop), ("bmid", bmid), ("bhit", bhit),
        ("apow", apow), ("abre", abre), ("adea", adea),
        ("bpow", bpow), ("bbre", bbre), ("bdea", bdea)
    ]
    
    for cat_name, cat_players in categories:
        if len(cat_players) > 0:
            print(f"\n{cat_name} ({len(cat_players)} players):")
            for i, player in enumerate(cat_players[:3]):  # Show first 3
                name = player[3] if len(player) > 3 else "Unknown"
                role = player[2] if len(player) > 2 else "Unknown"
                match_role = player[6] if len(player) > 6 else "Unknown"
                print(f"   {i+1}. {name} ({role}) - {match_role}")
            if len(cat_players) > 3:
                print(f"   ... and {len(cat_players) - 3} more")
        else:
            print(f"\n{cat_name}: ❌ NO PLAYERS")
    
    # Check for problematic categories
    print(f"\n⚠️ POTENTIAL ISSUES:")
    empty_categories = [name for name, players in categories if len(players) == 0]
    small_categories = [name for name, players in categories if 0 < len(players) <= 2]
    
    if empty_categories:
        print(f"   Empty categories: {empty_categories}")
    if small_categories:
        print(f"   Small categories (≤2 players): {small_categories}")
    
    if empty_categories or small_categories:
        print(f"\n💡 SOLUTION:")
        print(f"   The issue is likely that players have similar match roles,")
        print(f"   causing some categories to be empty or have very few players.")
        print(f"   This forces the template system to select the same players repeatedly.")

if __name__ == "__main__":
    debug_player_categories()