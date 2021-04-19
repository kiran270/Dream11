import sqlite3
from sqlite3 import Error


def create_connection():
	db_file= r"C:\Users\user\Desktop\Team6\pythonsqlite.db"
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return conn


def create_tables():
	conn=create_connection()
	conn.execute("drop table matches")
	conn.execute("drop table player")
	conn.execute("create table matches (uniqueid INTEGER PRIMARY KEY AUTOINCREMENT, team1 TEXT NOT NULL, team2 TEXT  NOT NULL)")
	conn.execute("create table player (matchid INTEGER, teamname TEXT NOT NULL, role TEXT NOT NULL,playername TEXT  NOT NULL,credits TEXT  NOT NULL,percentage INTEGER  NOT NULL,points INTEGER)")

def addMatch(team1,team2):
	# create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into matches (team1, team2) values (?,?)",(team1,team2))
		con.commit()
	except:
		con.rollback()
def addPlayer(matchid,teamname,role,playername,credits,percentage,points):
	# create_tables()
	try:
		con=create_connection()
		cur = con.cursor()
		cur.execute("INSERT into player (matchid,teamname,role,playername,credits,percentage,points) values (?,?,?,?,?,?,?)",(matchid,teamname,role,playername,credits,percentage,points))
		con.commit()
	except:
		con.rollback()
def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
		return d
def getMactches():
	con =create_connection()
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("select * from matches")
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