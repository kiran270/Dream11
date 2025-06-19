import sqlite3
from sqlite3 import Error


def create_connection():
	db_file= r"C:\Users\korubilli lakshmi\OneDrive\Desktop\Kiran\Dream11\pythonsqlite.db"
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return conn


def create_tables():
	conn=create_connection()
	# conn.execute("drop table dreamteams")
	# conn.execute("drop table matches")
	# conn.execute("drop table player")
	# conn.execute("drop table squad")
	# conn.execute("create table matches (uniqueid INTEGER PRIMARY KEY AUTOINCREMENT, team1 TEXT NOT NULL, team2 TEXT  NOT NULL)")
	# conn.execute("create table player (matchid INTEGER, teamname TEXT NOT NULL, role TEXT NOT NULL,playername TEXT  NOT NULL,credits TEXT  NOT NULL,percentage INTEGER  NOT NULL,matchrole TEXT  NOT NULL)")
	# # # conn.execute("create table squad (plyerid INTEGER PRIMARY KEY AUTOINCREMENT, teamname TEXT NOT NULL, role TEXT NOT NULL,playername TEXT  NOT NULL,credits TEXT  NOT NULL,percentage INTEGER  NOT NULL,points INTEGER)")
	# conn.execute("create table dreamteams (dreamteamid INTEGER PRIMARY KEY AUTOINCREMENT,matchbetween TEXT  NOT NULL,stadium TEXT  NOT NULL,wininning TEXT  NOT NULL,one TEXT  NOT NULL,two TEXT  NOT NULL,three TEXT  NOT NULL,four TEXT  NOT NULL,five TEXT  NOT NULL,six TEXT  NOT NULL,seven TEXT  NOT NULL,eight INTEGER  NOT NULL,nine INTEGER NOT NULL,ten TEXT  NOT NULL,eleven TEXT  NOT NULL)")

def addDreamTeam(matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven):
	create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into dreamteams (matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(matchbetween,stadium,wininning,one,two,three,four,five,six,seven,eight,nine,ten,eleven))
		con.commit()
	except:
		con.rollback()

def addMatch(team1,team2):
	# create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into matches (team1, team2) values (?,?)",(team1,team2))
		con.commit()
	except:
		con.rollback()
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

def addPlayer(matchid,teamname,role,playername,credits,percentage,matchrole):
	# create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into player (matchid,teamname,role,playername,credits,percentage,matchrole) values (?,?,?,?,?,?,?)",(matchid,teamname,role,playername,credits,percentage,matchrole))
		con.commit()
	except:
		con.rollback()
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
def getDreamTeams():
	create_tables()
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("select * from templates where stadium='ALL'")
	rows = cur.fetchall()
	return rows
def getteams(matchid):
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM matches where uniqueid = ?",[matchid])
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
	cur.execute("DELETE FROM player where playername = ? and matchid = ?",[playername,matchid])
	con.commit() 
	rows = cur.fetchall()
def removeplayerByMatchID(matchid):
	con =create_connection()
	cur = con.cursor()
	cur.execute("DELETE FROM player where matchid = ?",[matchid])
	con.commit() 
	rows = cur.fetchall()
def deleteMatch(matchid):
	con =create_connection()
	cur = con.cursor()
	cur.execute("DELETE FROM matches where uniqueid = ?",[matchid])
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