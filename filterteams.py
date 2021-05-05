from db import getPitchpointsWithPlayerName,getSquad,create_connection,addMatch,getMactches,getteams,getplayers,addSquad,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller
def getLeagueTypeCombinations(players,leagueType):
	if leagueType == 'Grand':
		Topcombinations=makeCombinations(players[0:4],3)
		Midcombinations=makeCombinations(players[4:8],3)
		Lowcombinations=makeCombinations(players[8:12],3)
		Lastset=makeCombinations(players[12:16],2)
		combinations=[]
		for x in Topcombinations:
			s1=list(x)
			for y in Midcombinations:
				s2=list(y)
				for z in Lowcombinations:
					s3=list(z)
					for k in Lastset:
						s4=list(k)
						team=[]
						team.extend(s1)
						team.extend(s2)
						team.extend(s3)
						team.extend(s4)
						combinations.append(team)
	elif leagueType == '52':
		Topcombinations=players[0:7]
		# print(str(len(Topcombinations))+"......")
		Midcombinations=makeCombinations(players[7:14],4)
		combinations=[]
		for y in Midcombinations:
			s2=list(y)
			team=[]
			team.extend(Topcombinations)
			team.extend(s2)
			combinations.append(team)
		# combinations=tuple(combinations)
	else:
		Topcombinations=players[0:6]
		Midcombinations=makeCombinations(players[6:14],5)
		combinations=[]
		for y in Midcombinations:
			s2=list(y)
			team=[]
			team.extend(Topcombinations)
			team.extend(s2)
			combinations.append(team)
	return combinations
def makeCombinations(players,num):
	combinations=list(itertools.combinations(players,num))
	return combinations
def filterCombinations(inputcombination,validcombinations):
	teams=[]
	x=inputcombination.split("-")
	INWKcount=int(x[0])
	INBATcount=int(x[1])
	INALcount=int(x[2])
	INBOWLCount=int(x[3])
	for team in validcombinations:
		WKcount=0
		BATcount=0
		BOWLCount=0
		ALcount=0
		for y in range(0,11):
			if team[y][2]=="WK":
				WKcount=WKcount+1
			elif team[y][2]=="BOWL":
				BOWLCount=BOWLCount+1
			elif team[y][2]=="ALL":
				ALcount=ALcount+1
			else:
				BATcount=BATcount+1
		if INWKcount==WKcount and INBATcount==BATcount and INALcount==ALcount and INBOWLCount == BOWLCount:
			teams.append(team)
	return teams
def filterBasedOnMatchWinnerAndPitchType(validcombinations,matchwinner,pitchtype,players):
	TeamA=""
	TeamB=""
	teams=[]
	pitchpoints={}
	if pitchtype!="None":
		if pitchtype=="BattingPitch":
			for x in players:
				rows=getPitchpointsWithPlayerName(x[3])
				if len(rows) > 0:
					pitchpoints[x[3]]=rows[0][2]
		if pitchtype=="BalancedPitch":
			for x in players:
				rows=getPitchpointsWithPlayerName(x[3])
				if len(rows) > 0:
					pitchpoints[x[3]]=rows[0][3]
		if pitchtype=="BowlingPitch":
			for x in players:
				rows=getPitchpointsWithPlayerName(x[3])
				if len(rows) > 0:
					pitchpoints[x[3]]=rows[0][4]
	for team in validcombinations:
		TeamA=team[0][1]
		for y in range(0,11):
			if team[y][1] !=TeamA:
				TeamB=team[y][1]
				break;
	if matchwinner=="50/50":
		for team in validcombinations:
			TeamACount=0
			TeamBCount=0
			totalpitchpints=0
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						team[y][3]
						# print("Player Not Exist:"+team[y][3])
				else:
					TeamBCount=TeamBCount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						team[y][3]
						# print("Player Not Exist:"+team[y][3])
			if TeamACount == 5 or TeamACount == 6:
				team.append(totalpitchpints)
				teams.append(team)
	elif TeamA==matchwinner:
		for team in validcombinations:
			TeamACount=0
			TeamBCount=0
			totalpitchpints=0
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						print("Player Not Exist:"+team[y][3])
				else:
					TeamBCount=TeamBCount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						print("Player Not Exist:"+team[y][3])
			if TeamACount == 6 or TeamACount == 7:
				team.append(totalpitchpints)
				teams.append(team)
	elif TeamB==matchwinner:
		for team in validcombinations:
			TeamACount=0
			TeamBCount=0
			totalpitchpints=0
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						print("Player Not Exist:"+team[y][3])
				else:
					TeamBCount=TeamBCount+1
					try:
						totalpitchpints=totalpitchpints+int(pitchpoints[team[y][3]])
					except KeyError:
						print("Player Not Exist:"+team[y][3])
			if TeamBCount == 6 or TeamBCount == 7:
				team.append(totalpitchpints)
				teams.append(team)
	elif matchwinner=="None":
		teams=validcombinations

	return teams
