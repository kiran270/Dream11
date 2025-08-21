def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names=None,fixed_players_names=None,enforce_top13=True,ensure_diversity=True):
	"""
	BASIC WORKING VERSION - Just return some teams
	"""
	import random
	
	# Get all available players
	all_players = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
	
	if len(all_players) < 11:
		print(f"Not enough players: {len(all_players)}")
		return []
	
	print(f"Generating teams from {len(all_players)} available players")
	
	finalteams = []
	
	# Generate 10 random teams
	for i in range(10):
		if len(all_players) >= 11:
			# Randomly select 11 players
			team = random.sample(all_players, 11)
			
			# Calculate total percentage
			total_percentage = 0
			for player in team:
				if player and len(player) > 5:
					try:
						total_percentage += float(player[5]) if player[5] else 0
					except:
						pass
			
			# Add percentage to team
			team_with_percentage = team + [total_percentage]
			finalteams.append(team_with_percentage)
	
	# Sort by percentage
	finalteams.sort(key=lambda x: x[-1], reverse=True)
	
	print(f"Generated {len(finalteams)} teams")
	return finalteams