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
				if temp[0]=="TOP" and player not in atop:
					atop.append(player)
				if temp[0]=="MID" and player not in amid:
					amid.append(player)
				if temp[0]=="HIT" and player not in ahit:
					ahit.append(player)
				if temp[0]=="POW" and player not in apow:
					apow.append(player)
				if temp[0]=="BRE" and player not in abre:
					abre.append(player)
				if temp[0]=="DEA" and player not in adea:
					adea.append(player)
				if len(temp) > 1:
					if temp[1]=="TOP" and player not in atop:
						atop.append(player)
					if temp[1]=="MID" and player not in amid:
						amid.append(player)
					if temp[1]=="HIT" and player not in ahit:
						ahit.append(player)
					if temp[1]=="POW" and player not in apow:
						apow.append(player)
					if temp[1]=="BRE" and player not in abre:
						abre.append(player)
					if temp[1]=="DEA" and player not in adea:
						adea.append(player)
			else:
				temp=player[6].split("-")
				if temp[0]=="TOP" and player not in btop:
					btop.append(player)
				if temp[0]=="MID" and player not in bmid:
					bmid.append(player)
				if temp[0]=="HIT" and player not in bhit:
					bhit.append(player)
				if temp[0]=="POW" and player not in bpow:
					bpow.append(player)
				if temp[0]=="BRE" and player not in bbre:
					bbre.append(player)
				if temp[0]=="DEA" and player not in bdea:
					bdea.append(player)
				if len(temp) > 1:
					if temp[1]=="TOP" and player not in btop:
						btop.append(player)
					if temp[1]=="MID" and player not in bmid:
						bmid.append(player)
					if temp[1]=="HIT" and player not in bhit:
						bhit.append(player)
					if temp[1]=="POW" and player not in bpow:
						bpow.append(player)
					if temp[1]=="BRE" and player not in bbre:
						bbre.append(player)
					if temp[1]=="DEA" and player not in bdea:
						bdea.append(player)
		# print(gettemplateteams[0][0])
		templatecombinations=getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,ahit,teams[0][1],teams[0][2])
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
		validcombinations=calculatePercentage(validcombinations)
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
        # If we don't have enough players, return all available players
        return source_list[:]
    else:
        # If count is 0 or source_list is empty, return empty list
        return []

def can_generate_team(atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, template):
    """Check if we have enough players to generate a team based on template requirements"""
    required_counts = [
        (atop, template[4]),   # atop count
        (amid, template[5]),   # amid count  
        (ahit, template[6]),   # ahit count
        (bpow, template[7]),   # bpow count
        (bbre, template[8]),   # bbre count
        (bdea, template[9]),   # bdea count
        (btop, template[10]),  # btop count
        (bmid, template[11]),  # bmid count
        (bhit, template[12]),  # bhit count
        (apow, template[13]),  # apow count
        (abre, template[14]),  # abre count
        (adea, template[15])   # adea count
    ]
    
    total_available = 0
    for player_list, required in required_counts:
        available = min(len(player_list), required)
        total_available += available
    
    # We need at least 11 players to form a team
    return total_available >= 11
def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB):
	templates=getDreamTeams()
	finalteams=[]
	all_players = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
	
	# If we don't have enough total players, return empty
	if len(all_players) < 11:
		print(f"Not enough total players: {len(all_players)}")
		return []
	
	top5 = sorted(all_players, key=lambda x: float(x[4]), reverse=True)[0:min(7, len(all_players))]
	
	for z in templates:
		teams=[]
		for k in range(0,1000):  # Reduced iterations for better performance
			team=[]
			
			# Try to get players from each category
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
			
			# Remove duplicates while preserving order
			seen = set()
			unique_team = []
			for player in team:
				player_id = (player[3], player[1])  # Use name and team as unique identifier
				if player_id not in seen:
					seen.add(player_id)
					unique_team.append(player)
			team = unique_team
			
			# If we don't have 11 players, try to fill from remaining players
			if len(team) < 11:
				remaining_players = [p for p in all_players if (p[3], p[1]) not in seen]
				needed = 11 - len(team)
				if len(remaining_players) >= needed:
					additional_players = random.sample(remaining_players, needed)
					team.extend(additional_players)
					
					# Update seen set with new players
					for player in additional_players:
						seen.add((player[3], player[1]))
			
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
			
			# Only proceed if we have exactly 11 players
			if len(team) == 11 and team not in teams:
					team=sorted(team, key=operator.itemgetter(2))
					count=0
					for x in teams:
						l=intersection(x,team)
						if l > count:
							count=l
					# print(count)
					if count <= 3:  # Changed from 7 to 3 for more team diversity
						# Select captain and vice-captain from the team and add as positions 11 and 12
						captain = None
						vice_captain = None
						
						# Simple captain selection - pick from team based on highest percentage
						team_sorted_by_percentage = sorted(team, key=lambda x: int(x[5]) if x[5] else 0, reverse=True)
						if len(team_sorted_by_percentage) > 0:
							captain = team_sorted_by_percentage[0]  # Highest percentage player as captain
						
						# Vice-captain selection - pick second highest percentage player (different from captain)
						if len(team_sorted_by_percentage) > 1:
							vice_captain = team_sorted_by_percentage[1]  # Second highest as vice-captain
						elif len(team_sorted_by_percentage) > 0 and captain:
							# If only one player, pick any other player as vice-captain
							other_players = [p for p in team if p != captain]
							if other_players:
								vice_captain = random.choice(other_players)
						
						# Add captain and vice-captain as positions 11 and 12 (these are references, not duplicates)
						if captain:
							team.append(captain)  # Position 11
						if vice_captain:
							team.append(vice_captain)  # Position 12
						
						teams.append(team)
		teams=calculatePercentage(teams)
		finalteams.extend(teams)
	# finalteams=getvalidcombinations(finalteams,teamA,teamB)
	# tgtcteams=[]
	# for i in finalteams:
	# 	temp=[]
	# 	for j in range(0,len(i)-1):
	# 		temp.append(i[j][3])
	# 	tgtcteams.append(temp)
	# print(len(tgtcteams))
	# print(tgtcteams)
	return finalteams

def calculatePercentage(validcombinations):
	finalteams=[]
	for x in validcombinations:
		TotalPercentage=0
		# Calculate percentage for first 11 players only (excluding captain/vice-captain duplicates)
		for y in range(0, min(11, len(x))):
			try:
				if x[y] and len(x[y]) > 5:  # Ensure player data exists and has percentage field
					percentage_value = int(x[y][5]) if x[y][5] else 0
					TotalPercentage += percentage_value
			except (IndexError, ValueError, TypeError):
				# Skip if there's any issue accessing the percentage
				continue
		x.append(TotalPercentage)
		finalteams.append(x)
	
	# Sort by total percentage (last element) - highest percentage first
	if finalteams:
		sorted_list = sorted(finalteams, key=lambda team: team[-1], reverse=True)
		return sorted_list
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
				if team[y][2]=="WK":
					WKcount=WKcount+1
				elif team[y][2]=="BOWL":
					BOWLCount=BOWLCount+1
				elif team[y][2]=="ALL":
					ALcount=ALcount+1
				else:
					BATcount=BATcount+1
		print(ALcount)
		print(Ateamcount)
		print(Bteamcount)
		print(WKcount)
		if credits<=100 and Ateamcount<=9 and Bteamcount<=9:
			if WKcount<=7 and WKcount>=1:
				if BATcount>=1 and BATcount<=7:
					if ALcount >=1 and ALcount<=7:
						if BOWLCount >=1 and BOWLCount<=7:
							# Select captain and vice-captain without adding duplicates
							team_sorted_by_percentage = sorted(team, key=lambda x: int(x[5]) if x[5] else 0, reverse=True)
							captain = None
							vice_captain = None
							
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
    app.run(host='0.0.0.0', port=5000,debug=True)