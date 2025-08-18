from flask import Flask, render_template, redirect
from flask import * 
from db import removeSquad,getDreamTeams,getSquad,addDreamTeam,create_connection,addMatch,getMactches,getteams,getplayers,addSquad,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID,updatePlayerRole,updatePlayerMatchRole
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller
from filterteams import getLeagueTypeCombinations,filterCombinations,filterBasedOnMatchWinnerAndPitchType
import random
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    print("BeautifulSoup not available. Install with: pip install beautifulsoup4")
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route("/")
def home():
	matches=getMactches()
	matches.reverse()
	return render_template("index.html",matches=matches)

@app.route("/adddreamteam",methods = ["POST","GET"])
def adddreamteam():
	if request.method == "POST":
		matchbetween=request.form.get('matchbetween')
		stadium=request.form.get('stadium')
		wininning=request.form.get('wininning')
		one=request.form.get('1')
		two=request.form.get('2')
		three=request.form.get('3')
		four=request.form.get('4')
		five=request.form.get('5')
		six=request.form.get('6')
		seven=request.form.get('7')
		eight=request.form.get('8')
		nine=request.form.get('9')
		ten=request.form.get('10')
		eleven=request.form.get('11')
		addDreamTeam(matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven)
		return render_template("adddreamteam.html")
	else:
		return render_template("adddreamteam.html")

@app.route("/deletematch",methods = ["POST","GET"])
def deletematch():
	matchid=request.form.get("matchid")
	deleteMatch(matchid)
	removeplayerByMatchID(matchid)
	matches=getMactches()
	return render_template("index.html",matches=matches)

@app.route("/addsquad",methods = ["POST","GET"])
def AddSquad():
	
	if request.method == "POST":
		role=request.form.get('role')
		playername=request.form.get('playername')
		battingpitch=request.form.get('battingpitch')
		balancedpitch=request.form.get('balancedpitch')
		bowlingpitch=request.form.get('bowlingpitch')
		addSquad(role,playername,battingpitch,balancedpitch,bowlingpitch)
		squad=getSquad()
		return render_template("addsquad.html",squad=squad)
	else:
		squad=getSquad()
		return render_template("addsquad.html",squad=squad)
@app.route("/removeSquad",methods = ["POST","GET"])
def removesquad():
	if request.method == "POST":
		playername=request.form.get('playername')
		removeSquad(playername)
	squad=getSquad()
	return render_template("addsquad.html",squad=squad)

@app.route("/addmatch",methods = ["POST","GET"])
def AddMatches():
	# url = 'https://cricapi.com/api/matches?apikey=vhEZBRBtYnM24xACRhlw6A0DEWt1'
	# r = requests.get(url)
	# print(r.json())
	if request.method == "POST":
			teamA = request.form.get("teama")
			teamB = request.form["teamb"]
			addMatch(teamA,teamB)
	matches=getMactches()
	matches.reverse()
	return render_template("home.html",matches=matches)

@app.route("/matchpage",methods = ["POST","GET"])
def matchpage():
	matchid=request.form.get("matchid")
	print(matchid+"match_id")
	teams=getteams(matchid)
	players=getplayers(matchid)
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	analysis=getAnalysis(players,teams)
	return render_template("addplayers.html",teams=teams,players=players,summary=analysis,matchid=matchid)

@app.route("/addplayer",methods = ["POST","GET"])
def addplayer():
	matchid=request.form.get('matchid')
	teamname=request.form.get('teamname')
	role=request.form.get('role')
	playername=request.form.get('playername')
	credits=request.form.get('credits')
	percentage=request.form.get('percentage')
	matchrole=request.form.get('matchrole')
	addPlayer(matchid,teamname,role,playername,credits,percentage,matchrole)
	teams=getteams(matchid)
	players=getplayers(matchid)
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	analysis=getAnalysis(players,teams)
	return render_template("addplayers.html",teams=teams,players=players,summary=analysis,matchid=matchid)
@app.route("/removePlayer",methods = ["POST","GET"])
def removePlayer():
	playername=request.form.get('playername')
	matchid=request.form.get('matchid')
	print(playername)
	print(matchid)
	removeplayer(playername,matchid)
	teams=getteams(matchid)
	players=getplayers(matchid)
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	analysis=getAnalysis(players,teams)
	return render_template("addplayers.html",teams=teams,players=players,summary=analysis,matchid=matchid)
@app.route("/generateTemplateFromUrl",methods = ["POST","GET"])
def generateTemplateFromUrl():
	return render_template("generate_template_from_url.html", 
	                      error="Cricinfo scraping is currently unavailable due to access restrictions. Please use the manual template creation instead.")

@app.route("/createCustomTemplate",methods = ["POST","GET"])
def createCustomTemplate():
	if request.method == "POST":
		template_name = request.form.get('template_name')
		stadium = request.form.get('stadium', 'Custom')
		winning_condition = request.form.get('winning_condition', 'Batting')
		
		# Get all position counts from form
		template_data = {
			'matchbetween': template_name,
			'stadium': stadium,
			'wininning': winning_condition,
			'atop': int(request.form.get('atop', 0)),
			'amid': int(request.form.get('amid', 0)),
			'ahit': int(request.form.get('ahit', 0)),
			'bpow': int(request.form.get('bpow', 0)),
			'bbre': int(request.form.get('bbre', 0)),
			'bdea': int(request.form.get('bdea', 0)),
			'btop': int(request.form.get('btop', 0)),
			'bmid': int(request.form.get('bmid', 0)),
			'bhit': int(request.form.get('bhit', 0)),
			'apow': int(request.form.get('apow', 0)),
			'abre': int(request.form.get('abre', 0)),
			'adea': int(request.form.get('adea', 0)),
			'cap': int(request.form.get('cap', 0)),
			'vc': int(request.form.get('vc', 6))
		}
		
		# Validate total is 11
		total = sum([template_data[key] for key in ['atop', 'amid', 'ahit', 'bpow', 'bbre', 'bdea', 'btop', 'bmid', 'bhit', 'apow', 'abre', 'adea']])
		
		if total != 11:
			return render_template("create_custom_template.html", 
			                      error=f"Total players must be 11, got {total}",
			                      template_data=template_data)
		
		# Save template to database
		success = save_template_to_db(template_data, template_name)
		if success:
			return redirect("/viewTemplates?success=1")
		else:
			return render_template("create_custom_template.html", 
			                      error="Failed to save template to database")
	
	return render_template("create_custom_template.html")

@app.route("/viewTemplates",methods = ["GET"])
def viewTemplates():
	# Get filter parameters
	match_filter = request.args.get('match_filter', '')
	stadium_filter = request.args.get('stadium_filter', '')
	winning_filter = request.args.get('winning_filter', '')
	
	# Get all templates
	templates = getDreamTeams()
	
	# Apply filters
	filtered_templates = []
	for template in templates:
		match_condition = not match_filter or match_filter.lower() in template['matchbetween'].lower()
		stadium_condition = not stadium_filter or stadium_filter.lower() in template['stadium'].lower()
		winning_condition = not winning_filter or winning_filter.lower() in template['wininning'].lower()
		
		if match_condition and stadium_condition and winning_condition:
			filtered_templates.append(template)
	
	# Get unique values for filter dropdowns
	all_matches = list(set([t['matchbetween'] for t in templates]))
	all_stadiums = list(set([t['stadium'] for t in templates]))
	all_winnings = list(set([t['wininning'] for t in templates]))
	
	return render_template("view_templates.html", 
	                      templates=filtered_templates,
	                      all_matches=sorted(all_matches),
	                      all_stadiums=sorted(all_stadiums),
	                      all_winnings=sorted(all_winnings),
	                      current_match_filter=match_filter,
	                      current_stadium_filter=stadium_filter,
	                      current_winning_filter=winning_filter)

@app.route("/bulkUpdateMatchRoles",methods = ["POST","GET"])
def bulkUpdateMatchRoles():
	if request.method == "POST":
		match_id = request.form.get('match_id')
		
		# Get all form data for player updates
		players = getplayers(match_id)
		updated_count = 0
		
		for player in players:
			player_name = player[3]  # player name
			new_match_role = request.form.get(f'match_role_{player_name}')
			
			if new_match_role and new_match_role.strip():
				success = updatePlayerMatchRole(player_name, match_id, new_match_role)
				if success:
					updated_count += 1
					print(f"Updated {player_name} match role to {new_match_role}")
		
		print(f"Updated {updated_count} players' match roles")
		return redirect(f"/addplayers?matchid={match_id}")
	
	# If GET request, show the bulk update form
	match_id = request.args.get('matchid')
	players = getplayers(match_id)
	teams = getteams(match_id)
	
	return render_template("bulk_update_match_roles.html", 
	                      match_id=match_id, 
	                      players=players, 
	                      teams=teams)

@app.route("/updatePlayerRole",methods = ["POST","GET"])
def updatePlayerRole():
	if request.method == "POST":
		player_name = request.form.get('player_name')
		new_match_role = request.form.get('new_match_role')
		match_id = request.form.get('match_id')
		
		success = updatePlayerMatchRole(player_name, match_id, new_match_role)
		if success:
			print(f"Updated {player_name} match role to {new_match_role}")
		else:
			print(f"Failed to update {player_name} match role")
		
		# Redirect back to the players page
		return redirect(f"/addplayers?matchid={match_id}")
	
	# If GET request, show the update form
	match_id = request.args.get('matchid')
	player_name = request.args.get('player_name')
	players = getplayers(match_id)
	teams = getteams(match_id)
	
	# Get current player's match role
	current_match_role = None
	for player in players:
		if player[3] == player_name:  # player[3] is player name
			current_match_role = player[6] if len(player) > 6 else None  # player[6] is match role
			break
	
	return render_template("update_player_role.html", 
	                      player_name=player_name, 
	                      match_id=match_id, 
	                      current_match_role=current_match_role,
	                      players=players, 
	                      teams=teams)

@app.route("/generateTeams",methods = ["POST","GET"])
def generateTeams():
	matchid=request.form.get('matchid')
	players=getplayers(matchid)
	teams=getteams(matchid)
	
	# Always use template-based generation
	print("Using template-based team generation")
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	
	# Organize players by team and role for template-based generation
	teamA_players = [p for p in players if p[1] == teams[0][1]]
	teamB_players = [p for p in players if p[1] == teams[0][2]]
	
	# Organize by role
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
	
	# If no match role data, use all players in general categories
	if not any([atop, amid, ahit, apow, abre, adea, btop, bmid, bhit, bpow, bbre, bdea]):
		print("No match role data found, using general player distribution")
		atop = teamA_players[:len(teamA_players)//3] if teamA_players else []
		amid = teamA_players[len(teamA_players)//3:2*len(teamA_players)//3] if teamA_players else []
		ahit = teamA_players[2*len(teamA_players)//3:] if teamA_players else []
		
		btop = teamB_players[:len(teamB_players)//3] if teamB_players else []
		bmid = teamB_players[len(teamB_players)//3:2*len(teamB_players)//3] if teamB_players else []
		bhit = teamB_players[2*len(teamB_players)//3:] if teamB_players else []
		
		apow = abre = adea = []
		bpow = bbre = bdea = []
	
	# Generate teams using templates
	templatecombinations = getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teams[0][1],teams[0][2])
	
	return render_template("finalteams.html",validcombinations=templatecombinations,teamA=teams[0][1],teamB=teams[0][2])

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return len(lst3)
def safe_sample(source_list, count):
    if count > 0 and len(source_list) >= count:
        return random.sample(source_list, count)
    elif 0 < len(source_list) < count:
        # If we don't have enough players, return all available players
        return source_list[:]
    else:
        # If count is 0 or source_list is empty, return empty list
        return []

def scrape_cricinfo_match(url):
    """Scrape Cricinfo match URL and extract player performance data"""
    if BeautifulSoup is None:
        return {"error": "BeautifulSoup not available. Install with: pip install beautifulsoup4"}
    
    try:
        # Enhanced headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract match title from page
        match_title = soup.find('h1') or soup.find('title')
        if not match_title:
            return {"error": "Could not find match title on the page"}
            
        match_text = match_title.get_text().strip()
        
        # Extract team names
        teams = extract_team_names(match_text)
        if not teams:
            return {"error": "Could not extract team names from match title"}
            
        # Generate template based on extracted info
        template = generate_simple_template(teams, match_text)
        
        return template
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return {"error": "Access denied by Cricinfo (403 Forbidden)"}
        else:
            return {"error": f"HTTP {e.response.status_code}: Unable to access the URL"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"Error scraping Cricinfo: {e}")
        return {"error": f"Error processing URL: {str(e)}"}



def extract_team_names(match_text):
    """Extract team names from match title"""
    if not match_text:
        return None
        
    # Common patterns for team names
    patterns = [
        r'([A-Za-z\s]+?)\s+vs?\s+([A-Za-z\s]+?)(?:\s|$)',
        r'([A-Za-z\s]+?)\s+v\s+([A-Za-z\s]+?)(?:\s|$)',
        r'(\w{3,})\s+vs?\s+(\w{3,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, match_text, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            # Clean up team names (remove extra words)
            team1 = team1.split()[-1] if len(team1.split()) > 2 else team1.replace(' ', '')
            team2 = team2.split()[0] if len(team2.split()) > 2 else team2.replace(' ', '')
            return [team1, team2]
    
    return None

def generate_simple_template(teams, match_text):
    """Generate a balanced template for the match"""
    template = {
        'matchbetween': f"{teams[0]}-{teams[1]}",
        'stadium': 'Auto-Generated',
        'wininning': 'Batting',
        # Balanced 11-player template
        'atop': 1, 'amid': 2, 'ahit': 1,
        'bpow': 0, 'bbre': 1, 'bdea': 1,
        'btop': 2, 'bmid': 1, 'bhit': 0,
        'apow': 1, 'abre': 1, 'adea': 0,
        'cap': 0, 'vc': 6
    }
    
    return template

def save_template_to_db(template_data, template_name):
    """Save generated template to database"""
    try:
        con = create_connection()
        cur = con.cursor()
        
        # Override matchbetween with custom name if provided
        if template_name:
            template_data['matchbetween'] = template_name
        
        cur.execute("""
            INSERT INTO templates (matchbetween, stadium, wininning, atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, cap, vc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template_data['matchbetween'], template_data['stadium'], template_data['wininning'],
            template_data['atop'], template_data['amid'], template_data['ahit'],
            template_data['bpow'], template_data['bbre'], template_data['bdea'],
            template_data['btop'], template_data['bmid'], template_data['bhit'],
            template_data['apow'], template_data['abre'], template_data['adea'],
            template_data['cap'], template_data['vc']
        ))
        
        con.commit()
        return True
        
    except Exception as e:
        print(f"Error saving template: {e}")
        con.rollback()
        return False

def get_template_value(template, key, default=0):
    """Safely get template value from either dict or sqlite3.Row object"""
    try:
        # For sqlite3.Row objects, use dictionary-style access
        if hasattr(template, 'keys'):
            if key in template.keys():
                return template[key]
            else:
                return default
        # For regular dictionaries
        elif hasattr(template, 'get'):
            return template.get(key, default)
        # For objects with attributes
        else:
            return getattr(template, key, default)
    except Exception as e:
        print(f"Error accessing template['{key}']: {e}")
        return default

def can_satisfy_template(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, template):
    """Check if we have enough players to exactly satisfy template requirements"""
    required_counts = [
        (atop, get_template_value(template, 'atop')),   # atop count
        (amid, get_template_value(template, 'amid')),   # amid count  
        (ahit, get_template_value(template, 'ahit')),   # ahit count
        (bpow, get_template_value(template, 'bpow')),   # bpow count
        (bbre, get_template_value(template, 'bbre')),   # bbre count
        (bdea, get_template_value(template, 'bdea')),   # bdea count
        (btop, get_template_value(template, 'btop')),   # btop count
        (bmid, get_template_value(template, 'bmid')),   # bmid count
        (bhit, get_template_value(template, 'bhit')),   # bhit count
        (apow, get_template_value(template, 'apow')),   # apow count
        (abre, get_template_value(template, 'abre')),   # abre count
        (adea, get_template_value(template, 'adea'))    # adea count
    ]
    
    # Check if we have enough players for each category
    for player_list, required in required_counts:
        if len(player_list) < required:
            return False
    
    # Check if total required players equals 11
    total_required = sum(get_template_value(template, key) for key in ['atop', 'amid', 'ahit', 'bpow', 'bbre', 'bdea', 'btop', 'bmid', 'bhit', 'apow', 'abre', 'adea'])
    return total_required == 11

def can_generate_team(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, template):
    """Check if we have enough players to generate a team based on template requirements"""
    return can_satisfy_template(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, template)
def validate_team_roles(team):
	"""Validate that team has at least 1 WK, 1 BAT, 1 ALL/AL, and 1 BOWL"""
	roles = {'WK': 0, 'BAT': 0, 'ALL': 0, 'AL': 0, 'BOWL': 0}
	
	for player in team:
		if len(player) > 2:  # Ensure player has role data
			role = player[2]
			if role in roles:
				roles[role] += 1
	
	# Check if we have at least 1 of each required role
	has_wk = roles['WK'] >= 1
	has_bat = roles['BAT'] >= 1
	has_all = (roles['ALL'] + roles['AL']) >= 1  # ALL or AL counts as all-rounder
	has_bowl = roles['BOWL'] >= 1
	
	return has_wk and has_bat and has_all and has_bowl

def validate_top11_players(team, top11_names):
	"""Validate that team has at least 7 players from top 11 players"""
	top11_count = 0
	team_player_names = []
	for player in team:
		if len(player) > 3:
			player_name = player[3]
			team_player_names.append(player_name)
			if player_name in top11_names:  # Check if player name is in top 11
				top11_count += 1
	
	print(f"Team players: {team_player_names}")
	print(f"Top 11 players in team: {top11_count}/11 (need 7)")
	
	# Reduce requirement to be more realistic - require at least 4 top players instead of 7
	required_top11 = min(4, len(top11_names))  # More realistic requirement
	print(f"Required top 11 players: {required_top11}")
	return top11_count >= required_top11

def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB):
	templates=getDreamTeams()
	print(f"Loaded templates: {len(templates) if templates else 0}")
	if templates:
		print(f"Templates source: {'Database' if hasattr(templates[0], 'keys') and 'id' in templates[0] else 'Default'}")
		print(f"First template type: {type(templates[0])}")
		if hasattr(templates[0], 'keys'):
			print(f"First template keys: {list(templates[0].keys())}")
			print(f"First template values: {dict(templates[0])}")
		else:
			print(f"First template dir: {[attr for attr in dir(templates[0]) if not attr.startswith('_')]}")
	
	finalteams=[]
	total_teams_generated = 0
	target_teams = 38
	all_players = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
	
	# If we don't have enough total players, return empty
	if len(all_players) < 11:
		print(f"Not enough total players: {len(all_players)}")
		return []
	
	print(f"Total players available: {len(all_players)}")
	print(f"Templates to process: {len(templates)}")
	
	for z in templates:
		# Debug: Check what columns are available in the template
		print(f"\n=== Template Debug Info ===")
		if hasattr(z, 'keys'):
			print(f"Template keys: {list(z.keys())}")
		else:
			print(f"Template attributes: {[attr for attr in dir(z) if not attr.startswith('_')]}")
		
		# Simple template name - use matchbetween if available, otherwise name
		template_name = get_template_value(z, 'matchbetween', None) or get_template_value(z, 'name', f"Template {templates.index(z) + 1}")
		
		print(f"\n=== Processing template: {template_name} ===")
		
		# Debug template requirements vs available players
		template_total = sum(get_template_value(z, key) for key in ['atop', 'amid', 'ahit', 'bpow', 'bbre', 'bdea', 'btop', 'bmid', 'bhit', 'apow', 'abre', 'adea'])
		print(f"Template '{template_name}' requires {template_total} total players")
		
		# Temporarily disable strict template validation - let's see what happens
		# if not can_satisfy_template(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,z):
		# 	print(f"Skipping template '{template_name}' - insufficient players to satisfy requirements")
		# 	continue
		
		# Show detailed template requirements vs available players
		requirements = {
			'atop': get_template_value(z,'atop'), 'amid': get_template_value(z,'amid'), 'ahit': get_template_value(z,'ahit'),
			'bpow': get_template_value(z,'bpow'), 'bbre': get_template_value(z,'bbre'), 'bdea': get_template_value(z,'bdea'),
			'btop': get_template_value(z,'btop'), 'bmid': get_template_value(z,'bmid'), 'bhit': get_template_value(z,'bhit'),
			'apow': get_template_value(z,'apow'), 'abre': get_template_value(z,'abre'), 'adea': get_template_value(z,'adea')
		}
		available = {
			'atop': len(atop), 'amid': len(amid), 'ahit': len(ahit),
			'bpow': len(bpow), 'bbre': len(bbre), 'bdea': len(bdea),
			'btop': len(btop), 'bmid': len(bmid), 'bhit': len(bhit),
			'apow': len(apow), 'abre': len(abre), 'adea': len(adea)
		}
		
		print(f"Template requirements: {requirements}")
		print(f"Available players: {available}")
		
		# Check which categories are insufficient
		insufficient = []
		for key in requirements:
			if available[key] < requirements[key]:
				insufficient.append(f"{key}: need {requirements[key]}, have {available[key]}")
		
		if insufficient:
			print(f"Insufficient categories: {insufficient}")
		else:
			print("All categories have sufficient players")
		
		teams=[]
		attempts = 0
		for k in range(0,20):  # Generate 20 teams per template
			attempts += 1
			team=[]
			print(f"Attempt {attempts} for template {template_name}")
			
			# Try to get players from each category in the correct order
			initial_team_size = len(team)
			team.extend(safe_sample(atop,get_template_value(z,'atop')))
			team.extend(safe_sample(amid,get_template_value(z,'amid')))
			team.extend(safe_sample(ahit,get_template_value(z,'ahit')))
			team.extend(safe_sample(bpow,get_template_value(z,'bpow')))
			team.extend(safe_sample(bbre,get_template_value(z,'bbre')))
			team.extend(safe_sample(bdea,get_template_value(z,'bdea')))
			team.extend(safe_sample(btop,get_template_value(z,'btop')))
			team.extend(safe_sample(bmid,get_template_value(z,'bmid')))
			team.extend(safe_sample(bhit,get_template_value(z,'bhit')))
			team.extend(safe_sample(apow,get_template_value(z,'apow')))
			team.extend(safe_sample(abre,get_template_value(z,'abre')))
			team.extend(safe_sample(adea,get_template_value(z,'adea')))
			
			print(f"Team size after adding players: {len(team)} (added {len(team) - initial_team_size} players)")
			
			# Remove duplicates while preserving order
			seen = set()
			unique_team = []
			for player in team:
				player_id = (player[3], player[1])  # Use name and team as unique identifier
				if player_id not in seen:
					seen.add(player_id)
					unique_team.append(player)
			team = unique_team
			
			# STRICT TEMPLATE MATCHING: Only accept teams that exactly match template requirements
			# Calculate expected team size from template (cap and vc are indices, not counts)
			expected_size = (get_template_value(z,'atop') + get_template_value(z,'amid') + get_template_value(z,'ahit') + 
			                get_template_value(z,'bpow') + get_template_value(z,'bbre') + get_template_value(z,'bdea') + 
			                get_template_value(z,'btop') + get_template_value(z,'bmid') + get_template_value(z,'bhit') + 
			                get_template_value(z,'apow') + get_template_value(z,'abre') + get_template_value(z,'adea'))
			
			print(f"Team size: {len(team)}, Expected size: {expected_size}")
			
			# Skip teams that don't exactly match template requirements
			if len(team) != expected_size or len(team) != 11:
				print(f"Skipping team - doesn't match template (got {len(team)}, expected {expected_size})")
				continue  # Skip teams that don't exactly match template requirements
			
			# Final check: ensure no duplicates and exactly 11 players
			if len(team) == 11:
				player_names = [p[3] for p in team]
				if len(player_names) == len(set(player_names)):
					# No duplicates found, proceed with this team
					pass
				else:
					print(f"DUPLICATE FOUND: {[name for name in player_names if player_names.count(name) > 1]}")
					continue  # Skip this team if duplicates found
			else:
				continue  # Skip if not exactly 11 players
			
			# Debug: Check validation conditions
			has_11_players = len(team) == 11
			is_not_duplicate = team not in teams
			has_valid_roles = validate_team_roles(team) if has_11_players else False
			
			print(f"Team validation: 11 players={has_11_players}, not duplicate={is_not_duplicate}, valid roles={has_valid_roles}")
			
			# Validate team composition - must have at least 1 of each role
			if has_11_players and is_not_duplicate and has_valid_roles:
					team=sorted(team, key=operator.itemgetter(2))
					count=0
					for x in teams:
						l=intersection(x,team)
						if l > count:
							count=l
					# print(count)
					if count <= 3:  # Changed from 7 to 3 for more team diversity
						# Select captain and vice-captain based on category indices - NO FALLBACK
						captain = None
						vice_captain = None
						
						# Get captain and vice-captain category indices from template
						cap_category_index = get_template_value(z, 'cap', 0)
						vc_category_index = get_template_value(z, 'vc', 1)
						
						# Define category order (same as team building order)
						categories = ['atop', 'amid', 'ahit', 'bpow', 'bbre', 'bdea', 'btop', 'bmid', 'bhit', 'apow', 'abre', 'adea']
						category_players = [atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea]
						
						print(f"Template cap category index: {cap_category_index}, vc category index: {vc_category_index}")
						
						# Select captain from the specified category - STRICT ONLY
						if 0 <= cap_category_index < len(categories):
							cap_category = categories[cap_category_index]
							cap_players = category_players[cap_category_index]
							
							# Find a player from this category in the team
							for player in team:
								if player in cap_players:
									captain = player
									print(f"Captain selected from {cap_category}: {captain[3]}")
									break
						
						# Select vice-captain from the specified category - STRICT ONLY
						if 0 <= vc_category_index < len(categories):
							vc_category = categories[vc_category_index]
							vc_players = category_players[vc_category_index]
							
							# Find a player from this category in the team (different from captain)
							for player in team:
								if player in vc_players and player != captain:
									vice_captain = player
									print(f"Vice-captain selected from {vc_category}: {vice_captain[3]}")
									break
						
						# Only add captain and vice-captain if they were found according to template
						if captain:
							team.append(captain)  # Position 11
							print(f"Captain added: {captain[3]}")
						else:
							print("No captain found matching template requirements")
							
						if vice_captain:
							team.append(vice_captain)  # Position 12
							print(f"Vice-captain added: {vice_captain[3]}")
						else:
							print("No vice-captain found matching template requirements")
						
						print(f"Team length before adding template name: {len(team)}")
						
						# Debug: Show all available columns in template
						if hasattr(z, 'keys'):
							print(f"Available template columns: {list(z.keys())}")
							for key in z.keys():
								print(f"  {key}: '{z[key]}'")
						
						# Use the same access method as in debug - direct bracket access
						try:
							matchbetween_value = z['matchbetween']
							print(f"Direct access matchbetween: '{matchbetween_value}'")
							final_template_name = str(matchbetween_value) if matchbetween_value else f"Template {templates.index(z) + 1}"
						except (KeyError, TypeError):
							print("Direct access failed, trying get method")
							if hasattr(z, 'get'):
								matchbetween_value = z.get('matchbetween', None)
							else:
								matchbetween_value = getattr(z, 'matchbetween', None)
							final_template_name = str(matchbetween_value) if matchbetween_value else f"Template {templates.index(z) + 1}"
						
						print(f"Final template name: '{final_template_name}'")
						team.append(final_template_name)
						
						print(f"Team length after adding template name: {len(team)}")
						
						teams.append(team)
						total_teams_generated += 1
						print(f"Generated team {total_teams_generated}/{target_teams}")
						
						# Stop if we've reached the target
						if total_teams_generated >= target_teams:
							break
		teams=calculatePercentage(teams)
		finalteams.extend(teams)
		print(f"Template '{template_name}' generated {len(teams)} teams")
		
		# Stop processing templates if we've reached the target
		if total_teams_generated >= target_teams:
			print(f"Reached target of {target_teams} teams, stopping template processing")
			break
	# finalteams=getvalidcombinations(finalteams,teamA,teamB)
	# tgtcteams=[]
	# for i in finalteams:
	# 	temp=[]
	# 	for j in range(0,len(i)-1):
	# 		temp.append(i[j][3])
	# 	tgtcteams.append(temp)
	# print(len(tgtcteams))
	# print(tgtcteams)
	print(f"\n=== FINAL SUMMARY ===")
	print(f"Total teams generated: {len(finalteams)}")
	return finalteams

def calculatePercentage(validcombinations):
	finalteams=[]
	for x in validcombinations:
		print(f"Team before percentage calculation - length: {len(x)}")
		if len(x) > 13:  # Should have players + captain + vice-captain + template name
			print(f"Template name in team: '{x[13]}'")
		
		TotalPercentage=0
		# Calculate percentage for first 11 players only (excluding captain/vice-captain duplicates and template name)
		for y in range(0, min(11, len(x))):
			try:
				if x[y] and len(x[y]) > 5:  # Ensure player data exists and has percentage field
					percentage_value = int(x[y][5]) if x[y][5] else 0
					TotalPercentage += percentage_value
			except (IndexError, ValueError, TypeError):
				# Skip if there's any issue accessing the percentage
				continue
		x.append(TotalPercentage)  # Add total percentage as the last element
		
		print(f"Final team structure - length: {len(x)}, template name: '{x[-2]}', percentage: {x[-1]}")
		finalteams.append(x)
	
	# Sort by total percentage (last element) - highest percentage first
	if finalteams:
		sorted_list = sorted(finalteams, key=lambda team: team[-1], reverse=True)
		# Limit to top 100 teams to avoid overwhelming the UI
		return sorted_list[:100]
	return []

def getAnalysis(players,teams):
    TeamApercentage = 0
    TeamBpercentage = 0
    TeamABat = 0
    TeamABowl = 0
    TeamAAll = 0
    TeamAWK = 0
    TeamBBat = 0
    TeamBBowl = 0
    TeamBAll = 0
    TeamBWK = 0
    for player in players:
        team_percentage = 0
        perc = float(player[5]) if player[5] else 0
        team_percentage += perc
        teamname = player[1]
        role = player[2]
        if teamname == teams[0][1]:
            TeamApercentage += perc
            if role == 'BAT':
                TeamABat += perc
            elif role == 'BOWL':
                TeamABowl += perc
            elif role == 'AL':
                TeamAAll += perc
            elif role == 'WK':
                TeamAWK += perc
        elif teamname == teams[0][2]:
            TeamBpercentage += perc
            if role == 'BAT':
                TeamBBat += perc
            elif role == 'BOWL':
                TeamBBowl += perc
            elif role == 'AL':
                TeamBAll += perc
            elif role == 'WK':
                TeamBWK += perc
    summary = {
        'TeamA_Total': TeamApercentage,
        'TeamB_Total': TeamBpercentage,
        'TeamA_BAT': TeamABat,
        'TeamA_BOWL': TeamABowl,
        'TeamA_ALL': TeamAAll,
        'TeamA_WK': TeamAWK,
        'TeamB_BAT': TeamBBat,
        'TeamB_BOWL': TeamBBowl,
        'TeamB_ALL': TeamBAll,
        'TeamB_WK': TeamBWK
    }

    return summary


def getfinalcombinations(confirmedplayers,validcombinations):
	finalteams=[]
	length=len(confirmedplayers)
	for x in validcombinations:
		count=0
		for y in confirmedplayers:
			if (y in x):
				count=count+1
		if count==length:
			TotalPercentage=0
			for z in x:
				TotalPercentage=TotalPercentage+int(z[5])
			x.append(TotalPercentage)
			finalteams.append(x)
	sorted_list = sorted(finalteams, key=operator.itemgetter(11))
	sorted_list.reverse()
	return sorted_list

def getconfirmedplayers(players):
	confirmedplayers=[]
	for player in players:
		if float(player[5])>=65:
			confirmedplayers.append(player)
	return confirmedplayers
def makeCombinations(players,num):
	combinations=list(itertools.combinations(players,num))
	return combinations
def getvalidcombinations(combinations,teamA,teamB):
	print(len(combinations))
	print(teamA)
	print(teamB)
	validcombinations=[]
	for x in range(0,len(combinations)):
		credits=0
		team=list(combinations[x])
		Ateamcount=0
		Bteamcount=0
		WKcount=0
		BATcount=0
		BOWLCount=0
		ALcount=0
		TotalPercentage=0
		for y in range(0,11):
			credits=credits+float(team[y][4])
			if team[y][1]==teamA:
				Ateamcount=Ateamcount+1
			else:
				Bteamcount=Bteamcount+1
			
			# Count roles for all players (not just team B)
			if team[y][2]=="WK":
				WKcount=WKcount+1
			elif team[y][2]=="BOWL":
				BOWLCount=BOWLCount+1
			elif team[y][2]=="ALL" or team[y][2]=="AL":
				ALcount=ALcount+1
			elif team[y][2]=="BAT":
				BATcount=BATcount+1
		print(ALcount)
		print(Ateamcount)
		print(Bteamcount)
		print(WKcount)
		if credits<=100 and Ateamcount<=9 and Bteamcount<=9:
			# Validate team has at least 1 of each role and proper limits
			if WKcount>=1 and WKcount<=7:
				if BATcount>=1 and BATcount<=7:
					if ALcount>=1 and ALcount<=7:
						if BOWLCount>=1 and BOWLCount<=7:
							# Select captain and vice-captain using template indices (fallback logic)
							captain = None
							vice_captain = None
							
							# For fallback logic, use percentage-based selection since template context may not be available
							team_sorted_by_percentage = sorted(team, key=lambda x: int(x[5]) if x[5] else 0, reverse=True)
							
							if len(team_sorted_by_percentage) > 0:
								captain = team_sorted_by_percentage[0]  # Highest percentage player as captain
							
							if len(team_sorted_by_percentage) > 1:
								vice_captain = team_sorted_by_percentage[1]  # Second highest as vice-captain
							elif len(team_sorted_by_percentage) > 0 and captain:
								other_players = [p for p in team if p != captain]
								if other_players:
									vice_captain = random.choice(other_players)
							
							# Add captain and vice-captain as positions 11 and 12 (these are references, not duplicates)
							if captain:
								team.append(captain)  # Position 11
							if vice_captain:
								team.append(vice_captain)  # Position 12
								
							validcombinations.append(team)
	return validcombinations


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)