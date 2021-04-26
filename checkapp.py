from flask import Flask, render_template
from flask import * 
from db import create_connection,addMatch,getMactches,getteams,getplayers,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller

app = Flask(__name__)

@app.route("/")
def home():
	matches=getMactches()
	return render_template("index.html",matches=matches)

@app.route("/deletematch",methods = ["POST","GET"])
def deletematch():
	matchid=request.form.get("matchid")
	deleteMatch(matchid)
	removeplayerByMatchID(matchid)
	matches=getMactches()
	return render_template("index.html",matches=matches)

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
	return render_template("home.html",matches=matches)

@app.route("/matchpage",methods = ["POST","GET"])
def matchpage():
	matchid=request.form.get("matchid")
	print(matchid+"match_id")
	teams=getteams(matchid)
	players=getplayers(matchid)
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	return render_template("addplayers.html",teams=teams,players=players,matchid=matchid)

@app.route("/addplayer",methods = ["POST","GET"])
def addplayer():
	matchid=request.form.get('matchid')
	teamname=request.form.get('teamname')
	role=request.form.get('role')
	playername=request.form.get('playername')
	credits=request.form.get('credits')
	percentage=request.form.get('percentage')
	points=request.form.get('points')
	addPlayer(matchid,teamname,role,playername,credits,percentage,points)
	teams=getteams(matchid)
	players=getplayers(matchid)
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	return render_template("addplayers.html",teams=teams,players=players,matchid=matchid)
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
	return render_template("addplayers.html",teams=teams,players=players,matchid=matchid)
@app.route("/generateTeams",methods = ["POST","GET"])
def generateTeams():
	matchid=request.form.get('matchid')
	players=getplayers(matchid)
	teams=getteams(matchid)
	inputcombination=request.form.get('combination')
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
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
	combinations=tuple(combinations)
	print(len(combinations))
	validcombinations=getvalidcombinations(combinations,teams[0][1],teams[0][2])
	totalteams=len(validcombinations)
	validcombinations=calculatePercentage(validcombinations)
	# validcombinations=validcombinations[0:11]
	if inputcombination!='ALL':
		validcombinations=filterCombinations(inputcombination,validcombinations)
	thiscombinationlength=len(validcombinations)
	return render_template("finalteams.html",validcombinations=validcombinations,totalteams=totalteams,thiscombinationlength=thiscombinationlength)
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
def calculatePercentage(validcombinations):
	finalteams=[]

	for x in validcombinations:
		TotalPercentage=0
		TotalPoints=0
		for y in range(0,11):
			TotalPercentage=TotalPercentage+int(x[y][5])
			TotalPoints=TotalPoints+int(x[y][6])
		x.append(TotalPercentage)
		x.append(TotalPoints)	
		finalteams.append(x)
	sorted_list = sorted(finalteams, key=operator.itemgetter(12))
	sorted_list.reverse()
	return sorted_list

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
			TotalPoints=0
			for z in x:
				TotalPercentage=TotalPercentage+int(z[5])
				TotalPoints=TotalPoints+int(z[6])
			x.append(TotalPercentage)
			x.append(TotalPoints)
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
                        if team[y][2]=="WK":
                                WKcount=WKcount+1
                        elif team[y][2]=="BOWL":
                                BOWLCount=BOWLCount+1
                        elif team[y][2]=="ALL":
                                ALcount=ALcount+1
                        else:
                                BATcount=BATcount+1
                if credits<=100 and Ateamcount<=7 and Bteamcount<=7:
                        if WKcount<=4 and WKcount>=1:
                                if BATcount>=3 and BATcount<=5:
                                        if ALcount >=1 and ALcount<=4:
                                                if BOWLCount >=3 and BOWLCount<=5:
                                                	validcombinations.append(team)
        return validcombinations


if __name__ == "__main__":
    app.run(debug=True)