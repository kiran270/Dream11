from flask import Flask, render_template
from flask import * 
from db import removeSquad,getDreamTeams,getSquad,addDreamTeam,create_connection,addMatch,getMactches,getteams,getplayers,addSquad,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller
from filterteams import getLeagueTypeCombinations,filterCombinations,filterBasedOnMatchWinnerAndPitchType
import random


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
	return render_template("addplayers.html",teams=teams,players=players,matchid=matchid)

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
	leaguetype=request.form.get('leaguetype')
	matchwinner=request.form.get('matchwinner')
	pitchtype=request.form.get('pitchtype')
	battingfirst=request.form.get('battingfirst')
	if battingfirst!="None":
		playersdict={}
		templatecombinations=[]
		gettemplateteams=getDreamTeams()
		# for player in players:
		# 	if player[1]==battingfirst:
		# 		playercurrentrole='A'+player[6]
		# 		playersdict[playercurrentrole]=player
		# 	else:
		# 		playercurrentrole='B'+player[6]
		# 		playersdict[playercurrentrole]=player
		# # print(playersdict)
		atop=[]
		amid=[]
		ahit=[]
		bpow=[]
		bbre=[]
		bdea=[]
		btop=[]
		bmid=[]
		bhit=[]
		apow=[]
		abre=[]
		adea=[]
		for player in players:
			if player[1]==battingfirst:
				temp=player[6].split("-")
				if temp[0]=="TOP":
					atop.append(player)
				if temp[0]=="MID":
					amid.append(player)
				if temp[0]=="HIT":
					ahit.append(player)
				if temp[0]=="POW":
					apow.append(player)
				if temp[0]=="BRE":
					abre.append(player)
				if temp[0]=="DEA":
					adea.append(player)
				if len(temp) > 1:
					if temp[1]=="TOP":
						atop.append(player)
					if temp[1]=="MID":
						amid.append(player)
					if temp[1]=="HIT":
						ahit.append(player)
					if temp[1]=="POW":
						apow.append(player)
					if temp[1]=="BRE":
						abre.append(player)
					if temp[1]=="DEA":
						adea.append(player)
			else:
				temp=player[6].split("-")
				if temp[0]=="TOP":
					btop.append(player)
				if temp[0]=="MID":
					bmid.append(player)
				if temp[0]=="HIT":
					bhit.append(player)
				if temp[0]=="POW":
					bpow.append(player)
				if temp[0]=="BRE":
					bbre.append(player)
				if temp[0]=="DEA":
					bdea.append(player)
				if len(temp) > 1:
					if temp[1]=="TOP":
						btop.append(player)
					if temp[1]=="MID":
						bmid.append(player)
					if temp[1]=="HIT":
						bhit.append(player)
					if temp[1]=="POW":
						bpow.append(player)
					if temp[1]=="BRE":
						bbre.append(player)
					if temp[1]=="DEA":
						bdea.append(player)
		# print(gettemplateteams[0][0])
		templatecombinations=getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,ahit)
		# templatecombinations=getvalidcombinations(templatecombinations,teams[0][1],teams[0][2])
		# validcombinations=calculatePercentage(templatecombinations)
		return render_template("finalteams.html",validcombinations=templatecombinations)
	else:
		print("coming")
		players=sorted(players, key=operator.itemgetter(5))
		players.reverse()
		combinations=getLeagueTypeCombinations(players,leaguetype)
		print(len(combinations))
		validcombinations=getvalidcombinations(combinations,teams[0][1],teams[0][2])
		totalteams=len(validcombinations)
		print(totalteams)
		# validcombinations=calculatePercentage(validcombinations)
		if inputcombination!='ALL':
			validcombinations=filterCombinations(inputcombination,validcombinations)
		validcombinations=filterBasedOnMatchWinnerAndPitchType(validcombinations,matchwinner,pitchtype,players)
		thiscombinationlength=len(validcombinations)
		return render_template("finalteams.html",validcombinations=validcombinations,totalteams=totalteams,thiscombinationlength=thiscombinationlength,currentcombination=inputcombination)

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return len(lst3)
def safe_sample(source_list, count):
    if count > 0 and len(source_list) >= count:
        return random.sample(source_list, count)
    elif 0 < len(source_list) < count:
        # print(f"Only {len(source_list)} available in , using all.")
        return source_list[:]
    else:
        # print(f"Cannot sample from: requested {count}, available {len(source_list)}")
        return []
def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea):
	templates=getDreamTeams()
	finalteams=[]
	all_players = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
	top_11 = sorted(all_players, key=lambda x: float(x[4]), reverse=True)[:11]
	for z in templates:
		teams=[]
		for k in range(0,5000):
			team=[]
			team.extend(safe_sample(atop,z[4]))
			team.extend(safe_sample(amid,z[5]))
			team.extend(safe_sample(ahit,z[6]))
			team.extend(safe_sample(bpow,z[7]))
			team.extend(safe_sample(bbre,z[8]))
			team.extend(safe_sample(bdea,z[9]))
			team.extend(safe_sample(btop,z[10]))
			team.extend(safe_sample(bmid,z[11]))
			team.extend(safe_sample(bhit,z[12]))
			team.extend(safe_sample(apow,z[13]))
			team.extend(safe_sample(abre,z[14]))
			team.extend(safe_sample(adea,z[15]))
			if team not in teams:
				team=set(team)
				team=list(team)
				# print(team)
				if len(team)==11:
					team=sorted(team, key=operator.itemgetter(2))
					count=0
					for x in teams:
						l=intersection(x,team)
						if l > count:
							count=l
					# print(count)
					if count <= 8:
						if z[16]==0:
							valid_choices = [p for p in atop if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==1:
							valid_choices = [p for p in amid if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==2:
							valid_choices = [p for p in ahit if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==3:
							valid_choices = [p for p in bpow if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==4:
							valid_choices = [p for p in bbre if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==5:
							valid_choices = [p for p in bdea if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==6:
							valid_choices = [p for p in btop if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==7:
							valid_choices = [p for p in bmid if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==8:
							valid_choices = [p for p in bhit if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==9:
							valid_choices = [p for p in apow if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==10:
							valid_choices = [p for p in abre if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[16]==11:
							valid_choices = [p for p in adea if p in team]
							team.extend(random.sample(valid_choices,1))
						if z[17]==0:
							valid_choices = [p for p in atop if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==1:
							valid_choices = [p for p in amid if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==2:
							valid_choices = [p for p in ahit if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==3:
							valid_choices = [p for p in bpow if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==4:
							valid_choices = [p for p in bbre if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==5:
							valid_choices = [p for p in bdea if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==6:
							valid_choices = [p for p in btop if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==7:
							valid_choices = [p for p in bmid if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==8:
							valid_choices = [p for p in bhit if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==9:
							valid_choices = [p for p in apow if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==10:
							valid_choices = [p for p in abre if p in team]
							team.extend(random.sample(valid_choices,1))
						elif z[17]==11:
							valid_choices = [p for p in adea if p in team]
							team.extend(random.sample(valid_choices,1))
						top_count = sum(1 for p in team if p in top_11)
						if top_count >= 7:
						    teams.append(team)
		teams=calculatePercentage(teams)
		finalteams.extend(teams[0:200])
	tgtcteams=[]
	for i in finalteams:
		temp=[]
		for j in range(0,len(i)-1):
			temp.append(i[j][3])
		tgtcteams.append(temp)
	print(len(tgtcteams))
	print(tgtcteams)
	return finalteams

def calculatePercentage(validcombinations):
	finalteams=[]
	for x in validcombinations:
		TotalPercentage=0
		for y in range(0,11):
			TotalPercentage=TotalPercentage+int(x[y][5])
		x.append(TotalPercentage)
		finalteams.append(x)
	sorted_list = sorted(finalteams, key=operator.itemgetter(13))
	sorted_list.reverse()
	# random.shuffle(finalteams)
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
				if team[y][2]=="WK":
					WKcount=WKcount+1
				elif team[y][2]=="BOWL":
					BOWLCount=BOWLCount+1
				elif team[y][2]=="ALL":
					ALcount=ALcount+1
				else:
					BATcount=BATcount+1
		if credits<=100 and Ateamcount<=9 and Bteamcount<=9:
			if WKcount<=7 and WKcount>=1:
				if BATcount>=1 and BATcount<=7:
					if ALcount >=1 and ALcount<=7:
						if BOWLCount >=1 and BOWLCount<=7:
							validcombinations.append(team)
	return validcombinations


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)