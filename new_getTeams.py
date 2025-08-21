def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names=None,fixed_players_names=None,enforce_top13=True,ensure_diversity=True):
	"""
	SIMPLE TEAM GENERATION WITH DIVERSITY CHECK
	1. Loop through all templates systematically
	2. Generate one team per template
	3. Check if team has 8+ common players with existing teams
	4. If yes, reject; if no, add to final teams
	"""
	import random
	
	templates = getDreamTeams()
	print(f"📋 Loaded {len(templates) if templates else 0} templates")
	
	finalteams = []
	all_players = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
	
	# Basic validation
	if len(all_players) < 11:
		print(f"❌ Not enough total players: {len(all_players)}")
		return []
	
	if not templates:
		print("❌ No templates available")
		return []
	
	print(f"🎯 SIMPLE APPROACH: Loop through {len(templates)} templates systematically")
	print(f"🔍 DIVERSITY CHECK: Reject teams with 8+ common players")
	
	# Loop through all templates systematically
	for template_index, template in enumerate(templates):
		template_name = get_template_value(template, 'matchbetween', f"Template {template_index + 1}")
		print(f"\n🔄 Processing template {template_index + 1}/{len(templates)}: {template_name}")
		
		# Generate team for this template
		team = []
		max_attempts = 50
		
		for attempt in range(max_attempts):
			team = []
			
			# Get template requirements
			atop_req = get_template_value(template, 'atop', 0)
			amid_req = get_template_value(template, 'amid', 0)
			ahit_req = get_template_value(template, 'ahit', 0)
			bpow_req = get_template_value(template, 'bpow', 0)
			bbre_req = get_template_value(template, 'bbre', 0)
			bdea_req = get_template_value(template, 'bdea', 0)
			btop_req = get_template_value(template, 'btop', 0)
			bmid_req = get_template_value(template, 'bmid', 0)
			bhit_req = get_template_value(template, 'bhit', 0)
			apow_req = get_template_value(template, 'apow', 0)
			abre_req = get_template_value(template, 'abre', 0)
			adea_req = get_template_value(template, 'adea', 0)
			
			# Debug template requirements on first attempt
			if attempt == 0:
				print(f"   📋 Template requirements: atop:{atop_req}, amid:{amid_req}, ahit:{ahit_req}, btop:{btop_req}, bmid:{bmid_req}, bhit:{bhit_req}, others:{bpow_req+bbre_req+bdea_req+apow_req+abre_req+adea_req}")
			
			# Select players for each category
			try:
				team.extend(random.sample(atop, atop_req) if len(atop) >= atop_req else atop)
				team.extend(random.sample(amid, amid_req) if len(amid) >= amid_req else amid)
				team.extend(random.sample(ahit, ahit_req) if len(ahit) >= ahit_req else ahit)
				team.extend(random.sample(bpow, bpow_req) if len(bpow) >= bpow_req else bpow)
				team.extend(random.sample(bbre, bbre_req) if len(bbre) >= bbre_req else bbre)
				team.extend(random.sample(bdea, bdea_req) if len(bdea) >= bdea_req else bdea)
				team.extend(random.sample(btop, btop_req) if len(btop) >= btop_req else btop)
				team.extend(random.sample(bmid, bmid_req) if len(bmid) >= bmid_req else bmid)
				team.extend(random.sample(bhit, bhit_req) if len(bhit) >= bhit_req else bhit)
				team.extend(random.sample(apow, apow_req) if len(apow) >= apow_req else apow)
				team.extend(random.sample(abre, abre_req) if len(abre) >= abre_req else abre)
				team.extend(random.sample(adea, adea_req) if len(adea) >= adea_req else adea)
			except ValueError:
				continue
			
			# Basic validations
			if len(team) != 11:
				if attempt == 0:
					print(f"   ❌ Team size wrong: {len(team)} players (need 11)")
				continue
			
			# Check for duplicate players in the team
			player_ids = [p[0] for p in team]
			if len(set(player_ids)) != 11:
				continue
			
			# TEAM COMPOSITION VALIDATION: Check if team has required roles
			role_counts = {'WK': 0, 'BAT': 0, 'AL': 0, 'BOWL': 0}
			for player in team:
				if player and len(player) > 2:
					role = player[2]  # Role is at index 2
					if role == 'WK':
						role_counts['WK'] += 1
					elif role == 'BAT':
						role_counts['BAT'] += 1
					elif role in ['AL', 'ALL']:  # Handle both AL and ALL for all-rounders
						role_counts['AL'] += 1
					elif role == 'BOWL':
						role_counts['BOWL'] += 1
			
			# TEMPORARILY DISABLED - Check minimum requirements: at least 1 WK, 1 BAT, 1 AL, 1 BOWL
			# if (role_counts['WK'] < 1 or role_counts['BAT'] < 1 or 
			# 	role_counts['AL'] < 1 or role_counts['BOWL'] < 1):
			# 	print(f"   ❌ Team rejected - Invalid composition: WK:{role_counts['WK']}, BAT:{role_counts['BAT']}, AL:{role_counts['AL']}, BOWL:{role_counts['BOWL']}")
			# 	continue
			# else:
			print(f"   ✅ Team composition: WK:{role_counts['WK']}, BAT:{role_counts['BAT']}, AL:{role_counts['AL']}, BOWL:{role_counts['BOWL']}")
			
			# SIMPLE DIVERSITY CHECK: If current team has 8+ common players with any existing team, reject it
			current_team_players = set(player_ids)
			is_diverse = True
			
			for existing_team in finalteams:
				existing_players = set([p[0] for p in existing_team[:11]])
				common_players = len(current_team_players.intersection(existing_players))
				
				if common_players >= 8:  # 8 or more common players = reject
					print(f"   ❌ Team rejected - {common_players} common players >= 8 with existing team")
					is_diverse = False
					break
			
			if not is_diverse:
				continue
			
			# Simple captain and vice-captain assignment
			# Sort players by percentage (highest first)
			team_sorted = sorted(team, key=lambda p: float(p[5]) if p and len(p) > 5 and p[5] else 0, reverse=True)
			
			# Captain is the highest percentage player
			captain_player = team_sorted[0]
			# Vice-captain is the second highest percentage player
			vice_captain_player = team_sorted[1] if len(team_sorted) > 1 else team_sorted[0]
			
			# Add captain and vice-captain info to the team
			team.append(captain_player)  # Captain at index 11
			team.append(vice_captain_player)  # Vice-captain at index 12
			
			# Team is valid and diverse
			print(f"   ✅ Team generated successfully - Captain: {captain_player[3]}, VC: {vice_captain_player[3]}")
			break
		
		# Add team if successfully generated (team now has 13 elements: 11 players + captain + vice-captain)
		if len(team) == 13:
			# Double-check team composition before adding to final teams
			role_counts = {'WK': 0, 'BAT': 0, 'AL': 0, 'BOWL': 0}
			for player in team:
				if player and len(player) > 2:
					role = player[2]
					if role == 'WK':
						role_counts['WK'] += 1
					elif role == 'BAT':
						role_counts['BAT'] += 1
					elif role in ['AL', 'ALL']:
						role_counts['AL'] += 1
					elif role == 'BOWL':
						role_counts['BOWL'] += 1
			
			# Final validation before adding to finalteams
			if (role_counts['WK'] >= 1 and role_counts['BAT'] >= 1 and 
				role_counts['AL'] >= 1 and role_counts['BOWL'] >= 1):
				finalteams.append(team)
				print(f"   ✅ Team added to final list: WK:{role_counts['WK']}, BAT:{role_counts['BAT']}, AL:{role_counts['AL']}, BOWL:{role_counts['BOWL']}")
			else:
				print(f"   ❌ FINAL CHECK FAILED - Team NOT added: WK:{role_counts['WK']}, BAT:{role_counts['BAT']}, AL:{role_counts['AL']}, BOWL:{role_counts['BOWL']}")
		else:
			print(f"   ❌ Failed to generate valid team after {max_attempts} attempts")
	
	print(f"\n📊 GENERATION COMPLETE:")
	print(f"   - Templates processed: {len(templates)}")
	print(f"   - Teams generated: {len(finalteams)}")
	print(f"   - Success rate: {(len(finalteams) / len(templates) * 100):.1f}%")
	
	if len(finalteams) == 0:
		print("❌ No teams were generated")
		return []
	
	# Calculate percentages and sort teams
	print("🔢 Calculating team percentages...")
	teams_with_percentage = []
	
	for team in finalteams:
		total_percentage = 0
		for player in team[:11]:
			if player and len(player) > 5:
				try:
					total_percentage += float(player[5]) if player[5] else 0
				except (IndexError, ValueError, TypeError):
					continue
		
		team_with_percentage = team + [total_percentage]
		teams_with_percentage.append(team_with_percentage)
	
	# Sort by percentage (highest first)
	teams_with_percentage.sort(key=lambda x: x[-1], reverse=True)
	
	if teams_with_percentage:
		print(f"📊 Teams sorted by percentage. Top: {teams_with_percentage[0][-1]:.1f}%, Bottom: {teams_with_percentage[-1][-1]:.1f}%")
	else:
		print("⚠️ No teams were generated successfully")
	
	return teams_with_percentage