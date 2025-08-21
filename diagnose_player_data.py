#!/usr/bin/env python3

def diagnose_player_data(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea):
    """Diagnose issues with player data"""
    
    print("🔍 PLAYER DATA DIAGNOSIS")
    print("=" * 50)
    
    # Check category sizes
    categories = {
        'atop': atop, 'amid': amid, 'ahit': ahit,
        'bpow': bpow, 'bbre': bbre, 'bdea': bdea,
        'btop': btop, 'bmid': bmid, 'bhit': bhit,
        'apow': apow, 'abre': abre, 'adea': adea
    }
    
    print("📊 Category sizes:")
    total_players = 0
    empty_categories = []
    
    for name, category in categories.items():
        size = len(category)
        total_players += size
        print(f"   {name}: {size} players")
        if size == 0:
            empty_categories.append(name)
    
    print(f"\n📈 Total player entries: {total_players}")
    
    if empty_categories:
        print(f"⚠️ Empty categories: {empty_categories}")
    
    # Check for duplicate players across categories
    all_players = []
    for category in categories.values():
        all_players.extend(category)
    
    if not all_players:
        print("❌ NO PLAYERS FOUND IN ANY CATEGORY!")
        return
    
    # Check player data structure
    print(f"\n🔍 Player data structure:")
    sample_player = all_players[0]
    print(f"   Sample player: {sample_player}")
    print(f"   Player length: {len(sample_player)}")
    
    if len(sample_player) < 3:
        print("❌ Player data structure is invalid! Expected at least [id, name, team, ...]")
        return
    
    # Check for duplicates
    player_ids = [p[0] for p in all_players if p and len(p) > 0]
    unique_ids = set(player_ids)
    
    print(f"\n🎯 Duplicate analysis:")
    print(f"   Total player entries: {len(player_ids)}")
    print(f"   Unique player IDs: {len(unique_ids)}")
    
    if len(unique_ids) != len(player_ids):
        print("⚠️ DUPLICATE PLAYERS DETECTED!")
        from collections import Counter
        duplicates = [pid for pid, count in Counter(player_ids).items() if count > 1]
        print(f"   Duplicate IDs: {duplicates[:10]}...")  # Show first 10
        
        # Show which categories have the duplicates
        print(f"\n🔍 Duplicate distribution:")
        for name, category in categories.items():
            cat_ids = [p[0] for p in category if p and len(p) > 0]
            cat_duplicates = [pid for pid in cat_ids if pid in duplicates]
            if cat_duplicates:
                print(f"   {name}: {len(cat_duplicates)} duplicates")
    else:
        print("✅ No duplicate players found!")
    
    # Check if we have enough unique players for a team
    if len(unique_ids) < 11:
        print(f"❌ NOT ENOUGH UNIQUE PLAYERS! Need 11, have {len(unique_ids)}")
        return
    
    print(f"✅ Sufficient unique players for team generation: {len(unique_ids)}")
    
    # Test simple team generation
    print(f"\n🧪 Testing simple team generation...")
    try:
        import random
        unique_players = []
        seen_ids = set()
        
        for player in all_players:
            if player and len(player) > 0 and player[0] not in seen_ids:
                unique_players.append(player)
                seen_ids.add(player[0])
        
        if len(unique_players) >= 11:
            test_team = random.sample(unique_players, 11)
            test_ids = [p[0] for p in test_team]
            print(f"   ✅ Test team created: {len(test_team)} players")
            print(f"   ✅ All unique: {len(set(test_ids)) == 11}")
        else:
            print(f"   ❌ Cannot create test team: only {len(unique_players)} unique players")
            
    except Exception as e:
        print(f"   ❌ Test team generation failed: {e}")

if __name__ == "__main__":
    # Example usage - you can call this function with your actual player data
    print("This is a diagnostic tool. Import and call diagnose_player_data() with your player categories.")