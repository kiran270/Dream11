def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names=None,fixed_players_names=None,enforce_top13=True,ensure_diversity=True):
	"""
	SIMPLE WORKING TEAM GENERATION - NO COMPLEX VALIDATIONS
	Just generate teams that work
	"""
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
	
	print(f"🎯 SIMPLE APPROACH: Generate teams from {len(templates)} templates")
	
	# Loop through templates and try to generate teams
	for template_index, template in enumerate(templates):
		if len(finalteams) >= 40:  # Limit to 40 teams
			break
			
		template_name = get_template_value(template, 'matchbetween', f"Template {template_index + 1}")
		
		# Try to generate a team
		for attempt in range(10):  # Only 10 attempts per template
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
			
			# Basic validation - just check team size and no duplicates
			if len(team) == 11:
				player_ids = [p[0] for p in team]
				if len(set(player_ids)) == 11:  # No duplicate players
					# Add captain and vice-captain (highest percentage players)
					team_sorted = sorted(team, key=lambda p: float(p[5]) if p and len(p) > 5 and p[5] else 0, reverse=True)
					captain_player = team_sorted[0]
					vice_captain_player = team_sorted[1] if len(team_sorted) > 1 else team_sorted[0]
					
					team.append(captain_player)  # Captain
					team.append(vice_captain_player)  # Vice-captain
					
					finalteams.append(team)
					print(f"✅ Template {template_index + 1}: Team generated")
					break
	
	print(f"\n📊 GENERATION COMPLETE:")
	print(f"   - Templates processed: {len(templates)}")
	print(f"   - Teams generated: {len(finalteams)}")
	
	if len(finalteams) == 0:
		print("❌ No teams were generated")
		return []
	
	# Calculate percentages and sort teams
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
	
	print(f"📊 Teams sorted by percentage. Generated {len(teams_with_percentage)} teams")
	
	return teams_with_percentage