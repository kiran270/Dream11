from db import getSquad,create_connection,addMatch,getMactches,getteams,getplayers,addSquad,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller
def getImpactCombinations(players,impact):
	if impact == 'Average':
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
	elif impact == 'High':
		Topcombinations=makeCombinations(players[0:9],7)
		Midcombinations=makeCombinations(players[9:14],4)
		combinations=[]
		for x in Topcombinations:
			s1=list(x)
			for y in Midcombinations:
				s2=list(y)
				team=[]
				team.extend(s1)
				team.extend(s2)
				combinations.append(team)
		combinations=tuple(combinations)
	else:
		Topcombinations=makeCombinations(players[0:4],4)
		Midcombinations=makeCombinations(players[4:10],3)
		Lowcombinations=makeCombinations(players[10:15],2)
		Lastset=makeCombinations(players[15:18],2)
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
def filterBasedOnMatchWinner(validcombinations,matchwinner):
	TeamA=""
	TeamB=""
	teams=[]
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
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
				else:
					TeamBCount=TeamBCount+1
			if TeamACount == 5 or TeamACount == 6:
				teams.append(team)
	elif TeamA==matchwinner:
		for team in validcombinations:
			TeamACount=0
			TeamBCount=0
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
				else:
					TeamBCount=TeamBCount+1
			if TeamACount == 6 or TeamACount == 7:
				teams.append(team)
	elif TeamB==matchwinner:
		for team in validcombinations:
			TeamACount=0
			TeamBCount=0
			for y in range(0,11):
				if team[y][1]==TeamA:
					TeamACount=TeamACount+1
				else:
					TeamBCount=TeamBCount+1
			if TeamBCount == 6 or TeamBCount == 7:
				teams.append(team)

	return teams
