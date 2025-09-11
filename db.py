import sqlite3
from sqlite3 import Error


def create_connection():
	db_file= "pythonsqlite.db"  # Use relative path for cross-platform compatibility
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return conn


def create_tables():
	conn=create_connection()
	try:
		# Create matches table
		conn.execute("""
			CREATE TABLE IF NOT EXISTS matches (
				matchid INTEGER PRIMARY KEY AUTOINCREMENT,
				team1 TEXT NOT NULL,
				team2 TEXT NOT NULL,
				ground_url TEXT
			)
		""")
		
		# Create players table
		conn.execute("""
			CREATE TABLE IF NOT EXISTS players (
				playerid INTEGER PRIMARY KEY AUTOINCREMENT,
				matchid INTEGER NOT NULL,
				teamname TEXT NOT NULL,
				role TEXT NOT NULL,
				playername TEXT NOT NULL,
				credits TEXT NOT NULL,
				percentage REAL NOT NULL,
				matchrole TEXT DEFAULT 'MID',
				player_id INTEGER,
				FOREIGN KEY (matchid) REFERENCES matches (matchid)
			)
		""")
		
		# Create dreamteams table with all required columns
		conn.execute("""
			CREATE TABLE IF NOT EXISTS dreamteams (
				dreamteamid INTEGER PRIMARY KEY AUTOINCREMENT,
				matchbetween TEXT NOT NULL,
				stadium TEXT NOT NULL,
				wininning TEXT NOT NULL,
				one TEXT NOT NULL,
				two TEXT NOT NULL,
				three TEXT NOT NULL,
				four TEXT NOT NULL,
				five TEXT NOT NULL,
				six TEXT NOT NULL,
				seven TEXT NOT NULL,
				eight INTEGER NOT NULL,
				nine INTEGER NOT NULL,
				ten TEXT NOT NULL,
				eleven TEXT NOT NULL,
				twelve TEXT DEFAULT '0',
				cap INTEGER DEFAULT 0,
				vc INTEGER DEFAULT 1,
				source_match_id INTEGER
			)
		""")
		
		# Create templates table
		conn.execute("""
			CREATE TABLE IF NOT EXISTS templates (
				templateid INTEGER PRIMARY KEY AUTOINCREMENT,
				matchbetween TEXT NOT NULL,
				stadium TEXT NOT NULL,
				wininning TEXT NOT NULL,
				one TEXT NOT NULL,
				two TEXT NOT NULL,
				three TEXT NOT NULL,
				four TEXT NOT NULL,
				five TEXT NOT NULL,
				six TEXT NOT NULL,
				seven TEXT NOT NULL,
				eight INTEGER NOT NULL,
				nine INTEGER NOT NULL,
				ten TEXT NOT NULL,
				eleven TEXT NOT NULL,
				twelve TEXT DEFAULT '0',
				cap INTEGER DEFAULT 0,
				vc INTEGER DEFAULT 1,
				source_match_id INTEGER
			)
		""")
		
		# Create ground_analysis table
		conn.execute("""
			CREATE TABLE IF NOT EXISTS ground_analysis (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				match_id INTEGER NOT NULL,
				ground_name TEXT,
				analysis_data TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (match_id) REFERENCES matches (matchid)
			)
		""")
		
		conn.commit()
		print("✅ All database tables created successfully")
	except Exception as e:
		print(f"❌ Error creating tables: {e}")

def addDreamTeam(matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve="0",cap=0,vc=1,source_match_id=None):
	create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		
		# Try to add missing columns if they don't exist
		try:
			cur.execute("ALTER TABLE dreamteams ADD COLUMN cap INTEGER DEFAULT 0")
			cur.execute("ALTER TABLE dreamteams ADD COLUMN vc INTEGER DEFAULT 1")
			cur.execute("ALTER TABLE dreamteams ADD COLUMN source_match_id INTEGER")
			cur.execute("ALTER TABLE dreamteams ADD COLUMN twelve TEXT DEFAULT '0'")
			con.commit()
		except:
			pass  # Columns might already exist
		
		cur.execute("INSERT into dreamteams (matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,cap,vc,source_match_id) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,cap,vc,source_match_id))
		con.commit()
		return True
	except Exception as e:
		print(f"Error adding dream team: {e}")
		con.rollback()
		return False

def addMatch(team1, team2, ground_url=None):
	"""Add match and automatically generate ground-specific templates"""
	try:
		con = create_connection()
		cur = con.cursor()
		
		# Try to add ground_url column if it doesn't exist
		try:
			cur.execute("ALTER TABLE matches ADD COLUMN ground_url TEXT")
			con.commit()
		except:
			pass  # Column might already exist
		
		# Insert the match
		cur.execute("INSERT into matches (team1, team2, ground_url) values (?,?,?)", (team1, team2, ground_url))
		match_id = cur.lastrowid  # Get the ID of the inserted match
		con.commit()
		
		print(f"✅ Match added: {team1} vs {team2} (ID: {match_id})")
		
		# Automatically generate templates if ground_url is provided
		if ground_url and match_id:
			print(f"🏟️ Generating templates for ground: {ground_url}")
			success = _generate_templates_for_match(match_id, team1, team2, ground_url)
			if success:
				print(f"🎯 Templates generated successfully for match {match_id}")
			else:
				print(f"⚠️ Ground analysis failed, creating default templates for match {match_id}")
				default_success = _create_default_templates_for_match(match_id, team1, team2)
				if default_success:
					print(f"✅ Default templates created for match {match_id}")
		else:
			print(f"⚠️ No ground URL provided, creating default templates")
			if match_id:
				default_success = _create_default_templates_for_match(match_id, team1, team2)
				if default_success:
					print(f"✅ Default templates created for match {match_id}")
		
		return match_id
		
	except Exception as e:
		print(f"❌ Error adding match: {e}")
		con.rollback()
		return None

def _generate_templates_for_match(match_id, team1, team2, ground_url):
	"""Generate templates for a specific match using ground analysis"""
	try:
		# Import here to avoid circular imports
		from ground_scorecard_analyzer import GroundScorecardAnalyzer
		
		# Determine ground name from teams or URL
		ground_name = f"{team1} vs {team2} Ground"
		if 'stadium' in ground_url.lower():
			# Try to extract stadium name from URL
			parts = ground_url.split('/')
			for part in parts:
				if 'stadium' in part.lower() or 'ground' in part.lower():
					ground_name = part.replace('-', ' ').title()
					break
		
		# Initialize analyzer
		analyzer = GroundScorecardAnalyzer()
		
		# Generate templates based on ground analysis
		success = analyzer.analyze_ground_and_generate_templates(
			ground_results_url=ground_url,
			match_id=match_id,
			ground_name=ground_name
		)
		
		return success
		
	except ImportError:
		print("⚠️ Ground analyzer not available, creating default templates")
		return _create_default_templates_for_match(match_id, team1, team2)
	except Exception as e:
		print(f"❌ Error in template generation: {e}")
		return _create_default_templates_for_match(match_id, team1, team2)

def _create_default_templates_for_match(match_id, team1, team2):
	"""Create default templates when ground analysis is not available"""
	try:
		print(f"🔧 Creating default templates for {team1} vs {team2}")
		
		# Template 1: Balanced Strategy
		success1 = addDreamTeam(
			matchbetween=f"{team1} vs {team2} - Balanced Strategy",
			stadium="Default Ground Analysis",
			wininning="Balanced",
			one="2",    # atop
			two="2",    # amid
			three="1",  # ahit
			four="1",   # bpow
			five="1",   # bbre
			six="1",    # bdea
			seven="1",  # btop
			eight="1",  # bmid
			nine="1",   # bhit
			ten="0",    # apow
			eleven="0", # abre
			twelve="0", # adea
			cap=0,
			vc=1,
			source_match_id=match_id
		)
		
		# Template 2: Batting Heavy Strategy
		success2 = addDreamTeam(
			matchbetween=f"{team1} vs {team2} - Batting Heavy Strategy",
			stadium="Default Ground Analysis",
			wininning="Batting First",
			one="2",    # atop
			two="3",    # amid
			three="2",  # ahit
			four="1",   # bpow
			five="0",   # bbre
			six="1",    # bdea
			seven="1",  # btop
			eight="1",  # bmid
			nine="0",   # bhit
			ten="0",    # apow
			eleven="0", # abre
			twelve="0", # adea
			cap=0,
			vc=1,
			source_match_id=match_id
		)
		
		# Template 3: Bowling Heavy Strategy
		success3 = addDreamTeam(
			matchbetween=f"{team1} vs {team2} - Bowling Heavy Strategy",
			stadium="Default Ground Analysis",
			wininning="Defending",
			one="1",    # atop
			two="1",    # amid
			three="1",  # ahit
			four="2",   # bpow
			five="2",   # bbre
			six="2",    # bdea
			seven="1",  # btop
			eight="1",  # bmid
			nine="0",   # bhit
			ten="0",    # apow
			eleven="0", # abre
			twelve="0", # adea
			cap=0,
			vc=1,
			source_match_id=match_id
		)
		
		successful_templates = sum([success1, success2, success3])
		print(f"✅ Created {successful_templates}/3 default templates")
		
		return successful_templates > 0
		
	except Exception as e:
		print(f"❌ Error creating default templates: {e}")
		return False
def create_ground_analysis_table():
	"""Create ground analysis table if it doesn't exist"""
	con = create_connection()
	cur = con.cursor()
	
	# Drop existing table to recreate with new schema
	cur.execute('DROP TABLE IF EXISTS ground_analysis')
	
	cur.execute('''
		CREATE TABLE ground_analysis (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			match_id INTEGER,
			ground_name TEXT,
			ground_url TEXT,
			total_matches INTEGER,
			avg_runs_per_over REAL,
			avg_runs_per_match REAL,
			ground_type TEXT,
			batting_friendly INTEGER,
			bowling_friendly INTEGER,
			balanced_ground INTEGER,
			batting_strategy TEXT,
			bowling_strategy TEXT,
			captain_preference TEXT,
			team_composition TEXT,
			toss_strategy TEXT,
			completed_matches INTEGER,
			wins_batting_first INTEGER,
			wins_chasing INTEGER,
			wins_by_runs INTEGER,
			wins_by_wickets INTEGER,
			batting_first_success_rate REAL,
			chasing_success_rate REAL,
			avg_winning_margin_runs REAL,
			avg_winning_margin_wickets REAL,
			abandoned_matches INTEGER,
			key_player_types TEXT,
			powerplay_strategy TEXT,
			death_overs_strategy TEXT,
			openers_importance REAL,
			middle_order_importance REAL,
			finishers_importance REAL,
			wicket_keeper_importance REAL,
			pace_bowlers_importance REAL,
			spin_bowlers_importance REAL,
			death_bowlers_importance REAL,
			all_rounders_importance REAL,
			analysis_data TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (match_id) REFERENCES matches (matchid)
		)
	''')
	con.commit()
	con.close()

def save_ground_analysis(match_id, analysis_data):
	"""Save ground analysis to database"""
	try:
		create_ground_analysis_table()
		con = create_connection()
		cur = con.cursor()
		
		# Extract data from analysis
		ground_name = analysis_data.get('ground_name', 'Unknown')
		ground_url = analysis_data.get('url', '')
		total_matches = analysis_data.get('total_matches', 0)
		avg_rpo = analysis_data.get('avg_runs_per_over', 0)
		avg_runs_match = analysis_data.get('avg_runs_per_match', 0)
		
		# Ground type
		ground_type = 'Balanced'
		if analysis_data.get('batting_friendly'):
			ground_type = 'Batting Friendly'
		elif analysis_data.get('bowling_friendly'):
			ground_type = 'Bowling Friendly'
		
		# Recommendations
		recommendations = analysis_data.get('recommendations', {})
		batting_strategy = recommendations.get('batting_strategy', '')
		bowling_strategy = recommendations.get('bowling_strategy', '')
		captain_preference = recommendations.get('captain_preference', '')
		team_composition = recommendations.get('team_composition', '')
		toss_strategy = recommendations.get('toss_strategy', '')
		key_player_types = recommendations.get('key_player_types', '')
		powerplay_strategy = recommendations.get('powerplay_strategy', '')
		death_overs_strategy = recommendations.get('death_overs_strategy', '')
		
		# Player importance data
		player_importance = analysis_data.get('player_importance', {})
		openers_imp = player_importance.get('openers', 0)
		middle_order_imp = player_importance.get('middle_order_batsmen', 0)
		finishers_imp = player_importance.get('finishers', 0)
		wk_imp = player_importance.get('wicket_keeper_batsmen', 0)
		pace_imp = player_importance.get('pace_bowlers', 0)
		spin_imp = player_importance.get('spin_bowlers', 0)
		death_imp = player_importance.get('death_bowlers', 0)
		ar_imp = player_importance.get('all_rounders', 0)
		
		# Match results data
		match_results = analysis_data.get('match_results', {})
		completed_matches = match_results.get('total_completed_matches', 0)
		wins_batting_first = match_results.get('wins_batting_first', 0)
		wins_chasing = match_results.get('wins_chasing', 0)
		wins_by_runs = match_results.get('wins_by_runs', 0)
		wins_by_wickets = match_results.get('wins_by_wickets', 0)
		batting_first_rate = match_results.get('batting_first_success_rate', 0)
		chasing_rate = match_results.get('chasing_success_rate', 0)
		avg_margin_runs = match_results.get('avg_winning_margin_runs', 0)
		avg_margin_wickets = match_results.get('avg_winning_margin_wickets', 0)
		abandoned = match_results.get('abandoned_matches', 0)
		
		# Store complete analysis as JSON
		import json
		analysis_json = json.dumps(analysis_data)
		
		cur.execute('''
			INSERT INTO ground_analysis (
				match_id, ground_name, ground_url, total_matches, 
				avg_runs_per_over, avg_runs_per_match, ground_type,
				batting_friendly, bowling_friendly, balanced_ground,
				batting_strategy, bowling_strategy, captain_preference, 
				team_composition, toss_strategy, completed_matches,
				wins_batting_first, wins_chasing, wins_by_runs, wins_by_wickets,
				batting_first_success_rate, chasing_success_rate,
				avg_winning_margin_runs, avg_winning_margin_wickets,
				abandoned_matches, key_player_types, powerplay_strategy,
				death_overs_strategy, openers_importance, middle_order_importance,
				finishers_importance, wicket_keeper_importance, pace_bowlers_importance,
				spin_bowlers_importance, death_bowlers_importance, all_rounders_importance,
				analysis_data
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		''', (
			match_id, ground_name, ground_url, total_matches,
			avg_rpo, avg_runs_match, ground_type,
			1 if analysis_data.get('batting_friendly') else 0,
			1 if analysis_data.get('bowling_friendly') else 0,
			1 if analysis_data.get('balanced_ground') else 0,
			batting_strategy, bowling_strategy, captain_preference,
			team_composition, toss_strategy, completed_matches,
			wins_batting_first, wins_chasing, wins_by_runs, wins_by_wickets,
			batting_first_rate, chasing_rate, avg_margin_runs, avg_margin_wickets,
			abandoned, key_player_types, powerplay_strategy, death_overs_strategy,
			openers_imp, middle_order_imp, finishers_imp, wk_imp,
			pace_imp, spin_imp, death_imp, ar_imp, analysis_json
		))
		
		con.commit()
		con.close()
		return True
		
	except Exception as e:
		print(f"Error saving ground analysis: {e}")
		return False

def get_ground_analysis(match_id):
	"""Get ground analysis for a match"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("SELECT * FROM ground_analysis WHERE match_id = ?", (match_id,))
		result = cur.fetchone()
		con.close()
		
		if result:
			# Convert to dictionary
			columns = [description[0] for description in cur.description]
			return dict(zip(columns, result))
		return None
		
	except Exception as e:
		print(f"Error getting ground analysis: {e}")
		return None

def addSquad(role,playername,battingpitch,balancedpitch,bowlingpitch):
	# create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into pitchpoints (role,playername,battingpitch,balancedpitch,bowlingpitch) values (?,?,?,?,?)",(role,playername,battingpitch,balancedpitch,bowlingpitch))
		con.commit()
	except:
		con.rollback()
def removeSquad(playername):
	con =create_connection()
	cur = con.cursor()
	cur.execute("DELETE FROM pitchpoints where playername = ?",[playername])
	con.commit() 
	rows = cur.fetchall()

def getPlayerMatchRole(teamname, playername):
	"""
	Check if a player exists in the players table by team and player name.
	Returns the player's match role if found, None otherwise.
	
	Args:
		teamname (str): Team name to search for
		playername (str): Player name to search for
	
	Returns:
		str or None: Match role if player exists, None otherwise
	"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("SELECT matchrole FROM players WHERE teamname = ? AND playername = ? LIMIT 1", 
		           (teamname, playername))
		result = cur.fetchone()
		con.close()
		
		if result:
			return result[0]  # Return the match role
		return None
	except Exception as e:
		print(f"Error checking player existence: {e}")
		return None

def addPlayer(matchid,teamname,role,playername,credits,percentage,matchrole,player_id):
	# create_tables()
	con = None
	try:
		# Check if player already exists in the database for this team
		existing_matchrole = getPlayerMatchRole(teamname, playername)
		
		# If player exists and has a match role other than DNS, use that role
		if existing_matchrole and existing_matchrole != "DNS":
			print(f"🔄 Player {playername} ({teamname}) already exists with match role: {existing_matchrole} - using existing role")
			matchrole = existing_matchrole
		elif existing_matchrole == "DNS":
			print(f"⚠️ Player {playername} ({teamname}) exists but has DNS role - using provided match role: {matchrole}")
		else:
			print(f"➕ New player {playername} ({teamname}) - using provided match role: {matchrole}")
		
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into player (matchid,teamname,role,playername,credits,percentage,matchrole,player_id) values (?,?,?,?,?,?,?,?)",(matchid,teamname,role,playername,credits,percentage,matchrole,player_id))
		con.commit()
		con.close()
		print(f"✅ Successfully added player: {playername}")
	except Exception as e:
		print(f"❌ Error adding player {playername}: {e}")
		if con:
			con.rollback()
			con.close()
def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
		return d
def getMactches():
	create_tables()
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("select * from matches")
	rows = cur.fetchall()
	return rows
def getDreamTeams(winning=None):
	create_tables()
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	# Query dreamteams table for all templates, optionally filtered by winning
	try:
		if winning:
			cur.execute("select * from templates where wininning = ? and matchbetween='equal'", [winning])
			print(f"Filtering templates by winning: {winning}")
		else:
			cur.execute("select * from templates")
			print("Getting all templates (no filter)")
		
		rows = cur.fetchall()
		print(f"Found {len(rows)} templates in database")
		return rows
	except Exception as e:
		print(f"Error querying dreamteams table: {e}")
		return []  # Return empty list if no database templates

def getDreamTeamsBySourceMatch(source_match_id):
	"""Get dream teams that were generated from a specific source match (same ground)"""
	con = create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	try:
		cur.execute("SELECT * FROM dreamteams WHERE source_match_id = ?", [source_match_id]) 
		rows = cur.fetchall()
		print(f"Found {len(rows)} templates from source match {source_match_id}")
		return rows
	except Exception as e:
		print(f"Error querying dreamteams by source match: {e}")
		return []
def getMatchIdColumnName():
	"""Determine the correct column name for match ID in matches table"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("PRAGMA table_info(matches)")
		columns = cur.fetchall()
		con.close()
		
		# Check for different possible column names
		column_names = [col[1] for col in columns]
		
		if 'matchid' in column_names:
			return 'matchid'
		elif 'id' in column_names:
			return 'id'
		elif 'uniqueid' in column_names:
			return 'uniqueid'
		else:
			# Default to the first column (usually the primary key)
			return column_names[0] if column_names else 'id'
	except:
		return 'id'  # Default fallback

def getteams(matchid):
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	
	# Dynamically determine the correct column name
	id_column = getMatchIdColumnName()
	query = f"SELECT * FROM matches where {id_column} = ?"
	
	cur.execute(query, [matchid])
	rows = cur.fetchall()
	return rows
def getplayers(matchid):
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM player where matchid = ?",[matchid]) 
	rows = cur.fetchall()
	return rows
def removeplayer(playername,matchid):
	con =create_connection()
	cur = con.cursor()
	print(playername)
	cur.execute("DELETE FROM players where playername = ? and matchid = ?",[playername,matchid])
	con.commit() 
	rows = cur.fetchall()
def removeplayerByMatchID(matchid):
	con =create_connection()
	cur = con.cursor()
	cur.execute("DELETE FROM players where matchid = ?",[matchid])
	con.commit() 
	rows = cur.fetchall()
def deleteMatch(matchid):
	con =create_connection()
	cur = con.cursor()
	
	# Dynamically determine the correct column name
	id_column = getMatchIdColumnName()
	query = f"DELETE FROM matches where {id_column} = ?"
	
	cur.execute(query, [matchid])
	con.commit() 
	rows = cur.fetchall()
def getSquad():
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pitchpoints") 
	rows = cur.fetchall()
	return rows
def getPitchpointsWithPlayerName(playername):
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pitchpoints where playername = ?",[playername]) 
	rows = cur.fetchall()
	return rows

def updatePlayerRole(playername, matchid, new_role):
	"""Update player role in the database"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("UPDATE player SET role = ? WHERE playername = ? AND matchid = ?", (new_role, playername, matchid))
		con.commit()
		return True
	except Exception as e:
		print(f"Error updating player role: {e}")
		con.rollback()
		return False

def updatePlayerMatchRole(playername, matchid, new_matchrole):
	"""Update player match role in the database"""
	con = None
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("UPDATE player SET matchrole = ? WHERE playername = ? AND matchid = ?", (new_matchrole, playername, matchid))
		con.commit()
		con.close()
		return True
	except Exception as e:
		print(f"Error updating player match role: {e}")
		if con:
			con.rollback()
			con.close()
		return False

def updateMatchId(old_match_id, new_match_id):
	"""Update match ID in matches table"""
	try:
		con = create_connection()
		cur = con.cursor()
		
		# Dynamically determine the correct column name
		id_column = getMatchIdColumnName()
		query = f"UPDATE matches SET {id_column} = ? WHERE {id_column} = ?"
		
		cur.execute(query, (new_match_id, old_match_id))
		con.commit()
		con.close()
		print(f"✅ Updated match ID from {old_match_id} to {new_match_id} in matches table")
		return True
	except Exception as e:
		print(f"❌ Error updating match ID in matches table: {e}")
		return False

def updatePlayersMatchId(old_match_id, new_match_id):
	"""Update match ID in players table"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("UPDATE player SET matchid = ? WHERE matchid = ?", (new_match_id, old_match_id))
		affected_rows = cur.rowcount
		con.commit()
		con.close()
		print(f"✅ Updated match ID from {old_match_id} to {new_match_id} for {affected_rows} players")
		return True
	except Exception as e:
		print(f"❌ Error updating match ID in players table: {e}")
		return False

def extractMatchIdFromUrl(url):
	"""Extract match ID from URL like https://team-generation.netlify.app/match/110745"""
	try:
		import re
		pattern = r'/match/(\d+)'
		match = re.search(pattern, url)
		if match:
			return int(match.group(1))
		return None
	except Exception as e:
		print(f"❌ Error extracting match ID from URL: {e}")
		return None

def bulkRemovePlayers(player_names, matchid):
	"""Bulk remove multiple players from a match"""
	try:
		con = create_connection()
		cur = con.cursor()
		
		# Create placeholders for the IN clause
		placeholders = ','.join(['?' for _ in player_names])
		query = f"DELETE FROM player WHERE playername IN ({placeholders}) AND matchid = ?"
		
		# Add matchid to the parameters
		params = player_names + [matchid]
		
		cur.execute(query, params)
		con.commit()
		
		return cur.rowcount  # Return number of rows affected
	except Exception as e:
		print(f"Error bulk removing players: {e}")
		con.rollback()
		return 0

def bulkRemovePlayersByRole(role, matchid):
	"""Remove all players of a specific role from a match"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("DELETE FROM player WHERE role = ? AND matchid = ?", (role, matchid))
		con.commit()
		return cur.rowcount
	except Exception as e:
		print(f"Error removing players by role: {e}")
		con.rollback()
		return 0

def bulkRemovePlayersByTeam(team, matchid):
	"""Remove all players from a specific team in a match"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("DELETE FROM player WHERE teamname = ? AND matchid = ?", (team, matchid))
		con.commit()
		return cur.rowcount
	except Exception as e:
		print(f"Error removing players by team: {e}")
		con.rollback()
		return 0

def bulkRemovePlayersByPercentage(min_percentage, max_percentage, matchid):
	"""Remove players within a specific percentage range"""
	try:
		con = create_connection()
		cur = con.cursor()
		cur.execute("DELETE FROM player WHERE percentage BETWEEN ? AND ? AND matchid = ?", 
		           (min_percentage, max_percentage, matchid))
		con.commit()
		return cur.rowcount
	except Exception as e:
		print(f"Error removing players by percentage: {e}")
		con.rollback()
		return 0

def create_team_analysis_tables():
	"""Create tables for team analysis functionality"""
	try:
		con = create_connection()
		cur = con.cursor()
		
		# Team performance history table
		cur.execute("""
			CREATE TABLE IF NOT EXISTS team_performance (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				team_id TEXT NOT NULL,
				match_id INTEGER,
				total_points REAL DEFAULT 0,
				captain_points REAL DEFAULT 0,
				vice_captain_points REAL DEFAULT 0,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (match_id) REFERENCES matches (matchid)
			)
		""")
		
		# Player performance history table
		cur.execute("""
			CREATE TABLE IF NOT EXISTS player_performance (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				player_id INTEGER,
				player_name TEXT NOT NULL,
				match_id INTEGER,
				points REAL DEFAULT 0,
				is_captain BOOLEAN DEFAULT 0,
				is_vice_captain BOOLEAN DEFAULT 0,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (match_id) REFERENCES matches (matchid)
			)
		""")
		
		con.commit()
		print("✅ Team analysis tables created successfully")
		return True
	except Exception as e:
		print(f"❌ Error creating team analysis tables: {e}")
		return False

def get_team_composition_analysis(match_id):
	"""Analyze team composition for a match"""
	try:
		con = create_connection()
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		
		# Get role distribution
		cur.execute("""
			SELECT role, COUNT(*) as count, 
			       AVG(percentage) as avg_selection,
			       AVG(CAST(REPLACE(credits, ' Cr', '') AS REAL)) as avg_credits
			FROM players 
			WHERE matchid = ? 
			GROUP BY role
		""", [match_id])
		
		role_distribution = cur.fetchall()
		
		# Get team distribution
		cur.execute("""
			SELECT teamname, COUNT(*) as player_count,
			       AVG(percentage) as avg_selection,
			       SUM(CAST(REPLACE(credits, ' Cr', '') AS REAL)) as total_credits
			FROM players 
			WHERE matchid = ? 
			GROUP BY teamname
		""", [match_id])
		
		team_distribution = cur.fetchall()
		
		con.close()
		return {
			'role_distribution': role_distribution,
			'team_distribution': team_distribution
		}
	except Exception as e:
		print(f"Error in team composition analysis: {e}")
		return None

def get_player_performance_metrics(match_id):
	"""Get player performance metrics for analysis"""
	try:
		con = create_connection()
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		
		# Get top performers by selection percentage
		cur.execute("""
			SELECT playername, teamname, role, percentage, credits,
			       CAST(REPLACE(credits, ' Cr', '') AS REAL) as credit_value
			FROM players 
			WHERE matchid = ? 
			ORDER BY percentage DESC
			LIMIT 20
		""", [match_id])
		
		top_performers = cur.fetchall()
		
		# Get captain/vice-captain suggestions
		cur.execute("""
			SELECT playername, teamname, role, percentage, credits,
			       CAST(REPLACE(credits, ' Cr', '') AS REAL) as credit_value,
			       (percentage * 0.7 + (100 - CAST(REPLACE(credits, ' Cr', '') AS REAL)) * 0.3) as captain_score
			FROM players 
			WHERE matchid = ? AND role IN ('BAT', 'AL', 'WK')
			ORDER BY captain_score DESC
			LIMIT 10
		""", [match_id])
		
		captain_suggestions = cur.fetchall()
		
		con.close()
		return {
			'top_performers': top_performers,
			'captain_suggestions': captain_suggestions
		}
	except Exception as e:
		print(f"Error in player performance metrics: {e}")
		return None

def get_team_balance_analysis(match_id):
	"""Analyze team balance and provide recommendations"""
	try:
		con = create_connection()
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		
		# Get current team balance from templates
		cur.execute("""
			SELECT matchbetween, stadium, wininning,
			       one as atop, two as amid, three as ahit,
			       four as bpow, five as bbre, six as bdea,
			       seven as btop, eight as bmid, nine as bhit,
			       ten as apow, eleven as abre, twelve as adea
			FROM dreamteams 
			WHERE source_match_id = ?
		""", [match_id])
		
		templates = cur.fetchall()
		
		# Calculate balance metrics
		balance_analysis = []
		for template in templates:
			total_players = sum([
				int(template['atop']), int(template['amid']), int(template['ahit']),
				int(template['bpow']), int(template['bbre']), int(template['bdea']),
				int(template['btop']), int(template['bmid']), int(template['bhit']),
				int(template['apow']), int(template['abre']), int(template['adea'])
			])
			
			batting_heavy = (int(template['atop']) + int(template['amid']) + int(template['ahit']) + 
			                int(template['btop']) + int(template['bmid']) + int(template['bhit']))
			
			bowling_heavy = (int(template['bpow']) + int(template['bbre']) + int(template['bdea']) +
			                int(template['apow']) + int(template['abre']) + int(template['adea']))
			
			balance_analysis.append({
				'template': template['matchbetween'],
				'strategy': template['wininning'],
				'total_players': total_players,
				'batting_players': batting_heavy,
				'bowling_players': bowling_heavy,
				'balance_ratio': round(batting_heavy / max(bowling_heavy, 1), 2)
			})
		
		con.close()
		return balance_analysis
	except Exception as e:
		print(f"Error in team balance analysis: {e}")
		return []

def save_team_performance(team_data, match_id):
	"""Save team performance data"""
	try:
		create_team_analysis_tables()
		con = create_connection()
		cur = con.cursor()
		
		cur.execute("""
			INSERT INTO team_performance (team_id, match_id, total_points, captain_points, vice_captain_points)
			VALUES (?, ?, ?, ?, ?)
		""", (team_data['team_id'], match_id, team_data['total_points'], 
		      team_data['captain_points'], team_data['vice_captain_points']))
		
		con.commit()
		con.close()
		return True
	except Exception as e:
		print(f"Error saving team performance: {e}")
		return False

def get_historical_performance(match_id):
	"""Get historical performance data for analysis"""
	try:
		create_team_analysis_tables()
		con = create_connection()
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		
		cur.execute("""
			SELECT * FROM team_performance 
			WHERE match_id = ? 
			ORDER BY total_points DESC
		""", [match_id])
		
		performance_data = cur.fetchall()
		con.close()
		return performance_data
	except Exception as e:
		print(f"Error getting historical performance: {e}")
		return []