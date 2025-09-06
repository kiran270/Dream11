from flask import Flask, render_template, redirect, jsonify
from flask import * 
from db import removeSquad,getDreamTeams,getSquad,addDreamTeam,create_connection,addMatch,getMactches,getteams,getplayers,addSquad,addPlayer,removeplayer,deleteMatch,removeplayerByMatchID,updatePlayerRole,updatePlayerMatchRole,bulkRemovePlayers,bulkRemovePlayersByRole,bulkRemovePlayersByTeam,bulkRemovePlayersByPercentage,getPlayerMatchRole,updateMatchId,updatePlayersMatchId,extractMatchIdFromUrl,getDreamTeamsBySourceMatch
import requests
import itertools
import operator
from operator import itemgetter,attrgetter, methodcaller
import random
import re
import time
import os
from datetime import datetime
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    print("BeautifulSoup not available. Install with: pip install beautifulsoup4")
from bs4 import BeautifulSoup

def convert_teams_for_template(teams_list):
	"""Convert teams containing Row objects to JSON-serializable format"""
	if not teams_list:
		return []
	
	import json
	
	serializable_teams = []
	for team in teams_list:
		serializable_team = []
		for item in team:
			try:
				# Try to serialize the item directly
				json.dumps(item)
				# If successful, it's already serializable
				serializable_team.append(item)
			except (TypeError, ValueError):
				# If it fails, try to convert Row objects to lists (preserving index access)
				try:
					if hasattr(item, 'keys'):  # SQLite Row object
						# Convert Row to list to preserve index-based access in template
						row_list = [item[i] for i in range(len(item))]
						serializable_team.append(row_list)
					else:
						# Try converting to dict as fallback
						serializable_team.append(dict(item))
				except (TypeError, ValueError):
					# If that also fails, convert to string as fallback
					serializable_team.append(str(item))
		serializable_teams.append(serializable_team)
	return serializable_teams

# Selenium imports for web scraping
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Install with: pip install selenium webdriver-manager")




app = Flask(__name__)

def extract_player_id_from_image_url(image_url):
    """
    Extract player ID from image URL
    
    Common image URL patterns:
    - https://d13ir53smqqeyp.cloudfront.net/d11-static-content/images/players/d11_player_pic_10920.jpg
    - https://d13ir53smqqeyp.cloudfront.net/d11-static-content/images/players/d11_player_pic_10920_t1.jpg
    - https://images.d11.in/images/players/10920.jpg
    - https://images.d11.in/images/players/10920_t1.jpg
    - https://d13ir53smqqeyp.cloudfront.net/player-images/partner-image/Hundred2025/2186.png
    - https://d13ir53smqqeyp.cloudfront.net/player-images/opta-cricket/71336.png
    
    Args:
        image_url (str): The image URL containing player ID
    
    Returns:
        int or None: Player ID if found, None otherwise
    """
    if not image_url:
        return None
    
    # Pattern 1: d11_player_pic_XXXXX.jpg or d11_player_pic_XXXXX_t1.jpg
    pattern1 = r'd11_player_pic_(\d+)(?:_t\d+)?\.jpg'
    match1 = re.search(pattern1, image_url)
    if match1:
        return int(match1.group(1))
    
    # Pattern 2: /players/XXXXX.jpg or /players/XXXXX_t1.jpg
    pattern2 = r'/players/(\d+)(?:_t\d+)?\.jpg'
    match2 = re.search(pattern2, image_url)
    if match2:
        return int(match2.group(1))
    
    # Pattern 3: New format - /player-images/.../XXXXX.png (flexible path depth)
    pattern3 = r'/player-images/(?:[^/]+/)*(\d+)\.(?:png|jpg|jpeg|webp)'
    match3 = re.search(pattern3, image_url)
    if match3:
        return int(match3.group(1))
    
    # Pattern 4: player_XXXXX or player-XXXXX (more specific)
    pattern4 = r'player[_-](\d+)'
    match4 = re.search(pattern4, image_url, re.IGNORECASE)
    if match4:
        return int(match4.group(1))
    
    # Pattern 5: XXXXX.jpg where XXXXX is 4-6 digits (only in /players/ or similar paths)
    if '/players/' in image_url or '/player/' in image_url:
        pattern5 = r'/players?/(\d{4,6})(?:_t\d+)?\.(?:jpg|jpeg|png|webp)'
        match5 = re.search(pattern5, image_url)
        if match5:
            return int(match5.group(1))
    
    # No aggressive fallback - be conservative to avoid false matches
    print(f"⚠️ Could not extract player ID from URL: {image_url}")
    return None

def scrape_players_for_match(match_id, team1, team2):
    """
    Scrape players for the given match
    
    Args:
        match_id: Database match ID
        team1: First team name
        team2: Second team name
    """
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available. Cannot scrape players.")
        return False
    
    default_matchrole = "DNS"
    
    # Test network connectivity first
    import requests
    try:
        print("🌐 Testing network connectivity...")
        response = requests.get("https://team-generation.netlify.app/", timeout=10)
        print(f"✅ Website is accessible (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network connectivity issue: {e}")
        return False
    
    # Configure Chrome driver with enhanced options
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--host-resolver-rules=MAP team-generation.netlify.app 13.215.239.219")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--ignore-certificate-errors-spki-list")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Try HTTPS first, then HTTP as fallback
        try:
            print("🔗 Navigating to team-generation.netlify.app...")
            driver.get("http://team-generation.netlify.app/")
            time.sleep(3)
            print(f"✅ Successfully loaded page: {driver.title}")
        except Exception as e:
            print(f"❌ HTTPS failed: {e}")
            print("💡 Trying HTTP instead...")
            
            # try:
            #     driver.get("http://team-generation.netlify.app/")
            #     time.sleep(3)
            #     print(f"✅ Successfully loaded with HTTP: {driver.title}")
            # except Exception as e2:
            #     print(f"❌ HTTP also failed: {e2}")
            #     return False
        
        # # Click on match card
        # try:
        #     card = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.CLASS_NAME, "card-middle"))
        #     )
        #     card.click()
        #     print("✅ Clicked on the match card successfully.")
        # except Exception as e:
        #     print("❌ Failed to click the match card:", str(e))
        #     return False
        
        # time.sleep(2)
        
        # # Login
        # try:
        #     phone_input = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.ID, "exampleInputEmail1"))
        #     )
        #     phone_input.send_keys("8142848270")  # You may want to make this configurable
            
        #     password_input = driver.find_element(By.ID, "exampleInputPassword1")
        #     password_input.send_keys("@Aug2022")  # You may want to make this configurable
            
        #     login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        #     login_button.click()
        #     print("✅ Login submitted.")
        # except Exception as e:
        #     print("❌ Login failed:", str(e))
        #     return False
        
        # time.sleep(10)  # Wait for login
        
        # # Check if login was successful
        # if "login" in driver.current_url.lower():
        #     print("⚠️ Still on login page, trying to navigate to main page...")
        #     try:
        #         driver.get("https://team-generation.netlify.app/")
        #         time.sleep(5)
        #         print("🔄 Navigated back to main page")
        #     except Exception as e:
        #         print(f"❌ Failed to navigate to main page: {e}")
        #         return False
        
        # # Find and click the correct match
        cards = driver.find_elements(By.CLASS_NAME, "card-middle")
        clicked = False
        
        # print(f"🔍 Looking for match: {team1} vs {team2}")
        # print(f"📋 Found {len(cards)} match cards on the page")
        
        for i, card in enumerate(cards, 1):
            try:
                left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
                right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()
                
                print(f"   Card {i}: {left_team} vs {right_team}")
                
                # Try exact match first
                if ({left_team, right_team} == {team1, team2}):
                    print(f"🎯 Found matching card: {left_team} vs {right_team}")
                    
                    try:
                        driver.execute_script("arguments[0].click();", card)
                        print(f"✅ Clicked on match (JavaScript): {left_team} vs {right_team}")
                        clicked = True
                        
                        # Wait for URL to change and extract match ID
                        time.sleep(3)
                        current_url = driver.current_url
                        print(f"🔗 Current URL after click: {current_url}")
                        
                        # Extract match ID from URL
                        extracted_match_id = extractMatchIdFromUrl(current_url)
                        if extracted_match_id:
                            print(f"🆔 Extracted match ID from URL: {extracted_match_id}")
                            
                            # Update match ID in database if different
                            if extracted_match_id != match_id:
                                print(f"🔄 Updating match ID from {match_id} to {extracted_match_id}")
                                updateMatchId(match_id, extracted_match_id)
                                updatePlayersMatchId(match_id, extracted_match_id)
                                match_id = extracted_match_id  # Use the extracted match ID for further operations
                        else:
                            print(f"⚠️ Could not extract match ID from URL: {current_url}")
                        
                        break
                    except Exception as e1:
                        print(f"⚠️ JavaScript click failed: {e1}")
                        
                        try:
                            card.click()
                            print(f"✅ Clicked on match (regular): {left_team} vs {right_team}")
                            clicked = True
                            
                            # Wait for URL to change and extract match ID
                            time.sleep(3)
                            current_url = driver.current_url
                            print(f"🔗 Current URL after click: {current_url}")
                            
                            # Extract match ID from URL
                            extracted_match_id = extractMatchIdFromUrl(current_url)
                            if extracted_match_id:
                                print(f"🆔 Extracted match ID from URL: {extracted_match_id}")
                                
                                # Update match ID in database if different
                                if extracted_match_id != match_id:
                                    print(f"🔄 Updating match ID from {match_id} to {extracted_match_id}")
                                    updateMatchId(match_id, extracted_match_id)
                                    updatePlayersMatchId(match_id, extracted_match_id)
                                    match_id = extracted_match_id  # Use the extracted match ID for further operations
                            else:
                                print(f"⚠️ Could not extract match ID from URL: {current_url}")
                            
                            break
                        except Exception as e2:
                            print(f"❌ All click methods failed: {e2}")
                
                # Try partial match (in case of abbreviations)
                elif (team1.upper() in left_team.upper() and team2.upper() in right_team.upper()) or \
                     (team2.upper() in left_team.upper() and team1.upper() in right_team.upper()):
                    print(f"🎯 Found partial matching card: {left_team} vs {right_team}")
                    
                    try:
                        driver.execute_script("arguments[0].click();", card)
                        print(f"✅ Clicked on match (partial): {left_team} vs {right_team}")
                        clicked = True
                        
                        # Wait for URL to change and extract match ID
                        time.sleep(3)
                        current_url = driver.current_url
                        print(f"🔗 Current URL after click: {current_url}")
                        
                        # Extract match ID from URL
                        extracted_match_id = extractMatchIdFromUrl(current_url)
                        if extracted_match_id:
                            print(f"🆔 Extracted match ID from URL: {extracted_match_id}")
                            
                            # Update match ID in database if different
                            if extracted_match_id != match_id:
                                print(f"🔄 Updating match ID from {match_id} to {extracted_match_id}")
                                updateMatchId(match_id, extracted_match_id)
                                updatePlayersMatchId(match_id, extracted_match_id)
                                match_id = extracted_match_id  # Use the extracted match ID for further operations
                        else:
                            print(f"⚠️ Could not extract match ID from URL: {current_url}")
                        
                        break
                    except Exception as e:
                        print(f"❌ Partial match click failed: {e}")
                        
            except Exception as e:
                print(f"❌ Error processing card {i}: {e}")
        
        if not clicked:
            print("❌ Match not found.")
            print(f"💡 Available matches:")
            for i, card in enumerate(cards, 1):
                try:
                    left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
                    right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()
                    print(f"   {i}. {left_team} vs {right_team}")
                except:
                    print(f"   {i}. Could not read team names")
            return False
        
        time.sleep(5)
        print("⏳ Waiting for page to load after match selection...")
        
        # Wait for tabs to load with better error handling
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
            )
            print("✅ Player tabs loaded successfully")
        except Exception as e:
            print(f"❌ Player tabs not found: {e}")
            print("🔍 Checking current page URL:", driver.current_url)
            
            # Check if we're back on login page and handle re-login
            if "login" in driver.current_url.lower():
                print("⚠️ Redirected to login page, attempting re-login...")
                
                try:
                    # Re-login
                    phone_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "exampleInputEmail1"))
                    )
                    phone_input.clear()
                    phone_input.send_keys("8142848270")
                    
                    password_input = driver.find_element(By.ID, "exampleInputPassword1")
                    password_input.clear()
                    password_input.send_keys("@Aug2022")
                    
                    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
                    login_button.click()
                    print("✅ Re-login submitted.")
                    
                    time.sleep(5)
                    
                    # Try to find the match again
                    cards = driver.find_elements(By.CLASS_NAME, "card-middle")
                    for card in cards:
                        try:
                            left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
                            right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()
                            
                            if ({left_team, right_team} == {team1, team2}):
                                driver.execute_script("arguments[0].click();", card)
                                print(f"✅ Re-clicked on match: {left_team} vs {right_team}")
                                time.sleep(5)
                                
                                # Extract match ID from URL after re-click
                                current_url = driver.current_url
                                print(f"🔗 Current URL after re-click: {current_url}")
                                
                                extracted_match_id = extractMatchIdFromUrl(current_url)
                                if extracted_match_id:
                                    print(f"🆔 Extracted match ID from URL: {extracted_match_id}")
                                    
                                    # Update match ID in database if different
                                    if extracted_match_id != match_id:
                                        print(f"🔄 Updating match ID from {match_id} to {extracted_match_id}")
                                        updateMatchId(match_id, extracted_match_id)
                                        updatePlayersMatchId(match_id, extracted_match_id)
                                        match_id = extracted_match_id  # Use the extracted match ID for further operations
                                else:
                                    print(f"⚠️ Could not extract match ID from URL: {current_url}")
                                
                                break
                        except:
                            continue
                    
                    # Try to find tabs again
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
                    )
                    print("✅ Player tabs loaded after re-login")
                    
                except Exception as e3:
                    print(f"❌ Re-login failed: {e3}")
                    return False
            else:
                return False
        
        tab_elements = driver.find_elements(By.CSS_SELECTOR, "nav.top-nav .role.sport-icon")
        all_players = []
        
        # Scrape players from each tab
        for tab in tab_elements:
            try:
                role = tab.text.strip().split("(")[0]  # Get WK, BAT, AL, BOWL
                
                # Click tab via JavaScript
                driver.execute_script("arguments[0].click();", tab)
                print(f"📌 Clicked tab: {role}")
                time.sleep(1)
                
                player_containers = driver.find_elements(By.CLASS_NAME, "player-container")
                
                for container in player_containers:
                    try:
                        name = container.find_element(By.CSS_SELECTOR, ".bobby-name span").text.strip()
                        selected_by = container.find_element(By.CLASS_NAME, "bobby-percentage").text.strip()
                        team = container.find_element(By.CLASS_NAME, "p-team").text.strip()
                        credits = container.find_elements(By.CLASS_NAME, "player-item-two")[1].text.strip()
                        
                        # Extract player ID from image URL
                        player_id = None
                        image_url = None
                        try:
                            img_element = container.find_element(By.CSS_SELECTOR, "img")
                            image_url = img_element.get_attribute("src")
                            player_id = extract_player_id_from_image_url(image_url)
                            
                            if player_id:
                                print(f"✅ Extracted Player ID {player_id} for {name}")
                            else:
                                print(f"⚠️ Could not extract Player ID for {name}")
                        except Exception as img_error:
                            print(f"⚠️ Could not find image for {name}: {img_error}")
                        
                        all_players.append({
                            "name": name,
                            "team": team,
                            "selected_by": selected_by,
                            "credits": credits,
                            "role": role,
                            "player_id": player_id,
                            "image_url": image_url
                        })
                    except Exception as e:
                        print(f"⚠️ Skipped a player due to error: {e}")
            except Exception as e:
                print(f"❌ Could not process tab: {e}")
        
        # Save players to database
        for p in all_players:
            name = p['name'].replace("'", "''")  # Escape single quotes
            team = p['team']
            role = p['role']
            credits = p['credits'].replace(" Cr", "").strip()
            player_id = p.get('player_id')
            
            try:
                percentage = float(p['selected_by'].replace("Sel by", "").replace("%", "").strip())
            except:
                percentage = 0
            
            print(f"💾 Saving: {name} (ID: {player_id}) - {team} - {role} - {percentage}%")
            addPlayer(match_id, team, role, name, credits, percentage, default_matchrole, player_id)
        
        # Print summary
        print(f"\n📊 SCRAPING SUMMARY:")
        print(f"👥 Total players extracted: {len(all_players)}")
        players_with_ids = [p for p in all_players if p.get('player_id')]
        print(f"🆔 Players with IDs: {len(players_with_ids)}")
        print(f"❓ Players without IDs: {len(all_players) - len(players_with_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return False
    finally:
        if driver:
            driver.quit()



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
		winning=request.form.get('winning')
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
		addDreamTeam(matchbetween,stadium,winning,one,two,three,four,five,six,seven,eight,nine,ten,eleven)
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
	if request.method == "POST":
		teamA = request.form.get("teama")
		teamB = request.form.get("teamb")
		ground_url = request.form.get("ground_url")
		auto_scrape = request.form.get("auto_scrape") == "1"
		analyze_ground = request.form.get("analyze_ground") == "1"
		
		# Add match to database with ground URL
		match_id = addMatch(teamA, teamB, ground_url)
		
		# If ground analysis is enabled and URL provided, scrape and analyze ground
		if analyze_ground and ground_url:
			try:
				from ground_scraper_integration import scrape_and_analyze_ground, validate_cricinfo_url
				
				if validate_cricinfo_url(ground_url):
					print(f"🏟️ Analyzing ground for {teamA} vs {teamB}...")
					analysis = scrape_and_analyze_ground(ground_url, match_id)
					if analysis:
						print(f"✅ Ground analysis completed for match {match_id}")
					else:
						print(f"⚠️ Ground analysis failed for match {match_id}")
				else:
					print(f"❌ Invalid ground URL provided: {ground_url}")
			except Exception as e:
				print(f"❌ Ground analysis failed: {e}")
				# Continue anyway - match is still created
		
		# If auto-scrape is enabled, scrape players
		if auto_scrape:
			try:
				print(f"🤖 Auto-scraping players for {teamA} vs {teamB}...")
				scrape_players_for_match(match_id, teamA, teamB)
				print(f"✅ Auto-scraping completed for match {match_id}")
			except Exception as e:
				print(f"❌ Auto-scraping failed: {e}")
				# Continue anyway - match is still created
	
	matches=getMactches()
	matches.reverse()
	return render_template("home.html",matches=matches)

@app.route("/scrape_match",methods = ["POST"])
def scrape_match():
	"""Manually trigger scraping for an existing match"""
	match_id = request.form.get("match_id")
	team_a = request.form.get("team_a")
	team_b = request.form.get("team_b")
	
	if not match_id or not team_a or not team_b:
		return jsonify({"success": False, "message": "Missing required parameters"})
	
	try:
		print(f"🤖 Manual scraping triggered for match {match_id}: {team_a} vs {team_b}")
		success = scrape_players_for_match(int(match_id), team_a, team_b)
		
		if success:
			return jsonify({"success": True, "message": f"Successfully scraped players for {team_a} vs {team_b}"})
		else:
			return jsonify({"success": False, "message": "Scraping failed. Check console for details."})
	except Exception as e:
		print(f"❌ Manual scraping failed: {e}")
		return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route("/auto_upload_teams", methods=["POST"])
def auto_upload_teams():
	"""Automatically upload the latest generated teams to Dream11 accounts"""
	try:
		from auto_dream11_uploader import AutoDream11Uploader
		
		# Get parameters
		teams_file = request.form.get("teams_file")  # Optional specific file
		match_id = request.form.get("match_id")      # Optional match ID override
		selected_users = request.form.getlist("selected_users")  # List of selected users
		
		print(f"🚀 Auto upload triggered")
		print(f"   📄 Teams file: {teams_file or 'Latest'}")
		print(f"   🎯 Match ID: {match_id or 'From config'}")
		print(f"   👥 Selected users: {selected_users or 'All users'}")
		
		# Create uploader and upload teams
		uploader = AutoDream11Uploader()
		success = uploader.upload_all_teams(teams_file, match_id, selected_users)
		
		if success:
			return jsonify({
				"success": True, 
				"message": "Teams uploaded successfully! Check console for details."
			})
		else:
			return jsonify({
				"success": False, 
				"message": "Upload failed. Check console for details."
			})
			
	except Exception as e:
		print(f"❌ Auto upload failed: {e}")
		return jsonify({
			"success": False, 
			"message": f"Error: {str(e)}"
		})

@app.route("/team_analysis")
def team_analysis_home():
	"""Redirect to team comparison form for match selection"""
	return redirect(url_for('compare_teams'))

@app.route("/analyze_teams", methods=["POST"])
def analyze_teams():
	"""Analyze specific teams file or match"""
	try:
		import json
		import statistics
		from collections import Counter, defaultdict
		
		# Get parameters
		teams_file = request.form.get("teams_file")
		match_id = request.form.get("match_id")
		
		analysis_data = {}
		
		if teams_file:
			# Analyze teams from file
			with open(teams_file, 'r') as f:
				data = json.load(f)
			
			teams = data.get('teams', [])
			metadata = data.get('metadata', {})
			
			# Basic statistics
			analysis_data['total_teams'] = len(teams)
			analysis_data['match_info'] = metadata.get('match', 'Unknown')
			analysis_data['generated_on'] = metadata.get('generated_on', 'Unknown')
			
			# Player analysis
			all_players = []
			captain_counts = Counter()
			vice_captain_counts = Counter()
			player_frequency = Counter()
			
			for team in teams:
				players = team.get('players', [])
				captain = team.get('captain')
				vice_captain = team.get('vice_captain')
				
				all_players.extend(players)
				if captain:
					captain_counts[captain] += 1
				if vice_captain:
					vice_captain_counts[vice_captain] += 1
				
				for player in players:
					player_frequency[player] += 1
			
			# Get player details from database if match_id available
			player_details = {}
			if match_id:
				try:
					players_db = getplayers(match_id)
					for player in players_db:
						if hasattr(player, 'player_id') and player.player_id:
							player_details[int(player.player_id)] = {
								'name': player.playername,
								'team': player.teamname,
								'role': player.role,
								'percentage': float(player.percentage) if player.percentage else 0,
								'credits': player.credits,
								'matchrole': player.matchrole
							}
				except Exception as e:
					print(f"Error getting player details: {e}")
			
			# Team composition analysis
			unique_players = set(all_players)
			analysis_data['unique_players'] = len(unique_players)
			analysis_data['avg_players_per_team'] = len(all_players) / len(teams) if teams else 0
			
			# Most popular players
			popular_players = []
			for player_id, count in player_frequency.most_common(10):
				player_info = player_details.get(player_id, {'name': f'Player {player_id}'})
				popular_players.append({
					'id': player_id,
					'name': player_info.get('name', f'Player {player_id}'),
					'team': player_info.get('team', 'Unknown'),
					'role': player_info.get('role', 'Unknown'),
					'frequency': count,
					'percentage': (count / len(teams)) * 100
				})
			analysis_data['popular_players'] = popular_players
			
			# Captain analysis
			top_captains = []
			for player_id, count in captain_counts.most_common(5):
				player_info = player_details.get(player_id, {'name': f'Player {player_id}'})
				top_captains.append({
					'id': player_id,
					'name': player_info.get('name', f'Player {player_id}'),
					'team': player_info.get('team', 'Unknown'),
					'role': player_info.get('role', 'Unknown'),
					'count': count,
					'percentage': (count / len(teams)) * 100
				})
			analysis_data['top_captains'] = top_captains
			
			# Vice-captain analysis
			top_vice_captains = []
			for player_id, count in vice_captain_counts.most_common(5):
				player_info = player_details.get(player_id, {'name': f'Player {player_id}'})
				top_vice_captains.append({
					'id': player_id,
					'name': player_info.get('name', f'Player {player_id}'),
					'team': player_info.get('team', 'Unknown'),
					'role': player_info.get('role', 'Unknown'),
					'count': count,
					'percentage': (count / len(teams)) * 100
				})
			analysis_data['top_vice_captains'] = top_vice_captains
			
			# Role distribution analysis
			role_distribution = defaultdict(int)
			for player_id in unique_players:
				player_info = player_details.get(player_id, {})
				role = player_info.get('role', 'Unknown')
				role_distribution[role] += 1
			
			analysis_data['role_distribution'] = dict(role_distribution)
			
			# Team diversity analysis
			team_similarities = []
			for i, team1 in enumerate(teams):
				for j, team2 in enumerate(teams[i+1:], i+1):
					common_players = set(team1.get('players', [])) & set(team2.get('players', []))
					similarity = len(common_players) / 11 * 100  # Assuming 11 players per team
					team_similarities.append(similarity)
			
			if team_similarities:
				analysis_data['avg_team_similarity'] = statistics.mean(team_similarities)
				analysis_data['min_team_similarity'] = min(team_similarities)
				analysis_data['max_team_similarity'] = max(team_similarities)
			else:
				analysis_data['avg_team_similarity'] = 0
				analysis_data['min_team_similarity'] = 0
				analysis_data['max_team_similarity'] = 0
		
		return render_template("team_analysis_results.html", analysis=analysis_data, teams_file=teams_file)
		
	except Exception as e:
		print(f"Error analyzing teams: {e}")
		return render_template("team_analysis_results.html", analysis={}, error=str(e))

@app.route("/export_analysis", methods=["POST"])
def export_analysis_general():
	"""Export team analysis as CSV or JSON"""
	try:
		import json
		import csv
		from io import StringIO
		from flask import make_response
		
		teams_file = request.form.get("teams_file")
		export_format = request.form.get("format", "csv")
		
		if not teams_file:
			return jsonify({"error": "No teams file specified"}), 400
		
		# Re-run analysis to get data
		with open(teams_file, 'r') as f:
			data = json.load(f)
		
		teams = data.get('teams', [])
		
		if export_format == "csv":
			# Create CSV export
			output = StringIO()
			writer = csv.writer(output)
			
			# Write headers
			writer.writerow(['Team ID', 'Team Name', 'Captain', 'Vice Captain', 'Players'])
			
			# Write team data
			for team in teams:
				writer.writerow([
					team.get('id', ''),
					team.get('name', ''),
					team.get('captain', ''),
					team.get('vice_captain', ''),
					','.join(map(str, team.get('players', [])))
				])
			
			# Create response
			response = make_response(output.getvalue())
			response.headers['Content-Type'] = 'text/csv'
			response.headers['Content-Disposition'] = f'attachment; filename=team_analysis_{teams_file.replace(".json", ".csv")}'
			return response
		
		else:  # JSON format
			response = make_response(json.dumps(data, indent=2))
			response.headers['Content-Type'] = 'application/json'
			response.headers['Content-Disposition'] = f'attachment; filename={teams_file}'
			return response
		
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@app.route("/team_analysis/<int:match_id>")
def team_analysis(match_id):
	"""Team Analysis page with comprehensive statistics and insights"""
	try:
		from db import (get_team_composition_analysis, get_player_performance_metrics, 
		               get_team_balance_analysis, get_historical_performance, getteams, getplayers)
		
		# Get match details
		match_data = getteams(match_id)
		if not match_data:
			return render_template("error.html", message="Match not found")
		
		match = match_data[0]
		players = getplayers(match_id)
		
		# Get analysis data
		composition_analysis = get_team_composition_analysis(match_id)
		performance_metrics = get_player_performance_metrics(match_id)
		balance_analysis = get_team_balance_analysis(match_id)
		historical_data = get_historical_performance(match_id)
		
		# Calculate additional insights
		total_players = len(players)
		avg_selection = sum([p['percentage'] for p in players]) / max(total_players, 1)
		
		# Get templates for this match
		templates = getDreamTeamsBySourceMatch(match_id)
		
		return render_template("team_analysis.html",
		                     match=match,
		                     players=players,
		                     composition_analysis=composition_analysis,
		                     performance_metrics=performance_metrics,
		                     balance_analysis=balance_analysis,
		                     historical_data=historical_data,
		                     templates=templates,
		                     total_players=total_players,
		                     avg_selection=avg_selection)
		
	except Exception as e:
		print(f"Error in team analysis: {e}")
		return render_template("error.html", message=f"Analysis error: {str(e)}")

@app.route("/export_analysis/<int:match_id>")
def export_analysis(match_id):
	"""Export team analysis as JSON/CSV"""
	try:
		from db import (get_team_composition_analysis, get_player_performance_metrics, 
		               get_team_balance_analysis, getteams, getplayers)
		import json
		from datetime import datetime
		
		# Get all analysis data
		match_data = getteams(match_id)[0]
		players = getplayers(match_id)
		composition_analysis = get_team_composition_analysis(match_id)
		performance_metrics = get_player_performance_metrics(match_id)
		balance_analysis = get_team_balance_analysis(match_id)
		
		# Convert Row objects to dictionaries
		def convert_rows(data):
			if isinstance(data, list):
				return [dict(row) if hasattr(row, 'keys') else row for row in data]
			elif hasattr(data, 'keys'):
				return dict(data)
			return data
		
		# Prepare export data
		export_data = {
			"metadata": {
				"match_id": match_id,
				"teams": f"{match_data['team1']} vs {match_data['team2']}",
				"exported_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
				"total_players": len(players)
			},
			"composition_analysis": {
				"role_distribution": convert_rows(composition_analysis['role_distribution']) if composition_analysis else [],
				"team_distribution": convert_rows(composition_analysis['team_distribution']) if composition_analysis else []
			},
			"performance_metrics": {
				"top_performers": convert_rows(performance_metrics['top_performers']) if performance_metrics else [],
				"captain_suggestions": convert_rows(performance_metrics['captain_suggestions']) if performance_metrics else []
			},
			"balance_analysis": balance_analysis,
			"players": convert_rows(players)
		}
		
		# Return as JSON download
		response = jsonify(export_data)
		response.headers['Content-Disposition'] = f'attachment; filename=team_analysis_{match_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
		return response
		
	except Exception as e:
		print(f"Error exporting analysis: {e}")
		return jsonify({"error": str(e)}), 500

@app.route("/compare_teams", methods=["GET", "POST"])
def compare_teams():
	"""Compare multiple teams side by side"""
	if request.method == "POST":
		team_ids = request.form.getlist("team_ids")
		match_id = request.form.get("match_id")
		
		try:
			# Get comparison data for selected teams
			comparison_data = []
			for team_id in team_ids:
				# This would need to be implemented based on your team storage structure
				# For now, we'll use template data
				pass
			
			return render_template("team_comparison.html", 
			                     comparison_data=comparison_data,
			                     match_id=match_id)
		except Exception as e:
			return render_template("error.html", message=f"Comparison error: {str(e)}")
	
	# GET request - show comparison form
	matches = getMactches()
	return render_template("team_comparison_form.html", matches=matches)

@app.route("/list_teams_files", methods=["GET"])
def list_teams_files():
	"""List available teams JSON files"""
	try:
		import glob
		files = glob.glob("dream11_teams_*.json")
		files.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time, newest first
		
		file_info = []
		for file in files:
			try:
				with open(file, 'r') as f:
					data = json.load(f)
				metadata = data.get('metadata', {})
				file_info.append({
					'filename': file,
					'generated_on': metadata.get('generated_on', 'Unknown'),
					'match': metadata.get('match', 'Unknown'),
					'total_teams': len(data.get('teams', [])),
					'size': os.path.getsize(file)
				})
			except:
				file_info.append({
					'filename': file,
					'generated_on': 'Unknown',
					'match': 'Unknown',
					'total_teams': 0,
					'size': os.path.getsize(file)
				})
		
		return jsonify({"success": True, "files": file_info})
		
	except Exception as e:
		return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route("/list_users", methods=["GET"])
def list_users():
	"""List configured users from dream11_config.json"""
	try:
		config_file = 'dream11_config.json'
		if not os.path.exists(config_file):
			return jsonify({"success": False, "message": "Configuration file not found"})
		
		with open(config_file, 'r') as f:
			config = json.load(f)
		
		users = config.get('users', [])
		user_info = []
		
		for user in users:
			user_info.append({
				'name': user.get('name', 'Unknown'),
				'team_range': user.get('team_range', [1, 6]),
				'configured': "YOUR_USER" not in user.get('auth_token', '')
			})
		
		return jsonify({"success": True, "users": user_info})
		
	except Exception as e:
		return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route("/delete_teams_file", methods=["POST"])
def delete_teams_file():
	"""Delete a specific teams JSON file"""
	try:
		filename = request.form.get("filename")
		if not filename:
			return jsonify({"success": False, "message": "No filename provided"})
		
		# Security check: only allow deletion of dream11_teams_*.json files
		if not filename.startswith("dream11_teams_") or not filename.endswith(".json"):
			return jsonify({"success": False, "message": "Invalid filename format"})
		
		# Check if file exists
		if not os.path.exists(filename):
			return jsonify({"success": False, "message": "File not found"})
		
		# Delete the file
		os.remove(filename)
		print(f"🗑️ Deleted teams file: {filename}")
		
		return jsonify({
			"success": True, 
			"message": f"File '{filename}' deleted successfully"
		})
		
	except Exception as e:
		print(f"❌ Error deleting file: {e}")
		return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route("/delete_all_teams_files", methods=["POST"])
def delete_all_teams_files():
	"""Delete all teams JSON files"""
	try:
		import glob
		files = glob.glob("dream11_teams_*.json")
		
		if not files:
			return jsonify({"success": False, "message": "No teams files found to delete"})
		
		deleted_count = 0
		failed_files = []
		
		for filename in files:
			try:
				os.remove(filename)
				print(f"🗑️ Deleted teams file: {filename}")
				deleted_count += 1
			except Exception as e:
				print(f"❌ Failed to delete {filename}: {e}")
				failed_files.append(filename)
		
		if failed_files:
			return jsonify({
				"success": False, 
				"message": f"Deleted {deleted_count} files, but failed to delete: {', '.join(failed_files)}"
			})
		else:
			return jsonify({
				"success": True, 
				"message": f"Successfully deleted all {deleted_count} teams files"
			})
		
	except Exception as e:
		print(f"❌ Error deleting files: {e}")
		return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route("/auto_upload")
def auto_upload_page():
	"""Serve the auto upload interface"""
	return render_template("auto_upload.html")

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
	player_id=request.form.get('player_id')  # Get player_id from form
	
	# If no player_id provided, set to None
	if not player_id:
		player_id = None
	
	addPlayer(matchid,teamname,role,playername,credits,percentage,matchrole,player_id)
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
			'winning': winning_condition,
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
	templates = getDreamTeams()  # Get all templates for viewing
	
	# Apply filters
	filtered_templates = []
	for template in templates:
		match_condition = not match_filter or match_filter.lower() in template['matchbetween'].lower()
		stadium_condition = not stadium_filter or stadium_filter.lower() in template['stadium'].lower()
		winning_condition = not winning_filter or winning_filter.lower() in template['winning'].lower()
		
		if match_condition and stadium_condition and winning_condition:
			filtered_templates.append(template)
	
	# Get unique values for filter dropdowns
	all_matches = list(set([t['matchbetween'] for t in templates]))
	all_stadiums = list(set([t['stadium'] for t in templates]))
	all_winnings = list(set([t['winning'] for t in templates]))
	
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
			player_name = player['playername']  # player name
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

@app.route("/bulkRemovePlayers",methods = ["POST","GET"])
def bulkRemovePlayersRoute():
	if request.method == "POST":
		matchid = request.form.get('matchid')
		removal_type = request.form.get('removal_type')
		
		removed_count = 0
		
		if removal_type == 'selected_players':
			# Get selected player names from checkboxes
			selected_players = request.form.getlist('selected_players')
			if selected_players:
				removed_count = bulkRemovePlayers(selected_players, matchid)
		
		elif removal_type == 'by_role':
			role = request.form.get('role_filter')
			if role:
				removed_count = bulkRemovePlayersByRole(role, matchid)
		
		elif removal_type == 'by_team':
			team = request.form.get('team_filter')
			if team:
				removed_count = bulkRemovePlayersByTeam(team, matchid)
		
		elif removal_type == 'by_percentage':
			min_perc = request.form.get('min_percentage')
			max_perc = request.form.get('max_percentage')
			if min_perc and max_perc:
				removed_count = bulkRemovePlayersByPercentage(float(min_perc), float(max_perc), matchid)
		
		elif removal_type == 'all_players':
			removed_count = removeplayerByMatchID(matchid)
		
		# Redirect back to match page with success message
		teams = getteams(matchid)
		players = getplayers(matchid)
		players.reverse()  # Match the existing sorting
		analysis = getAnalysis(players, teams)
		
		return render_template("addplayers.html", 
		                      teams=teams, 
		                      players=players, 
		                      summary=analysis, 
		                      matchid=matchid,
		                      success_message=f"Successfully removed {removed_count} players")
	
	else:
		# GET request - show bulk remove form
		matchid = request.args.get('matchid')
		
		teams = getteams(matchid)
		players = getplayers(matchid)
		
		# Get unique roles and teams for filters
		unique_roles = list(set([p['role'] for p in players]))
		unique_teams = list(set([p['teamname'] for p in players]))
		
		return render_template("bulk_remove_players.html", 
		                      teams=teams, 
		                      players=players, 
		                      matchid=matchid,
		                      unique_roles=unique_roles,
		                      unique_teams=unique_teams)

def generate_teams_single_set(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names,fixed_players_names,enforce_top13,ensure_diversity):
	"""Generate teams with a single set of fixed players"""
	return getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names,fixed_players_names,enforce_top13,ensure_diversity)

def generate_teams_multiple_sets(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names,fixed_sets,enforce_top13,ensure_diversity):
	"""Generate teams with multiple sets of fixed players - 1 team per template per set"""
	all_teams = []
	
	print(f"🎯 Generating teams for {len(fixed_sets)} sets")
	
	for set_index, fixed_players_names in enumerate(fixed_sets, 1):
		print(f"\n🔒 Processing Set {set_index}: {fixed_players_names}")
		
		# Generate teams for this set
		set_teams = getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,top13_names,fixed_players_names,enforce_top13,ensure_diversity)
		
		# Add set identifier to team names
		for j, team in enumerate(set_teams):
			if len(team) > 13:  # Has template name
				original_name = team[13]
				
				# Clean the original name if it contains percentage data
				if isinstance(original_name, str) and '%' in original_name:
					# Only remove the percentage part, keep everything before it
					clean_name = str(original_name).split('%')[0]
					original_name = clean_name
				
				team[13] = f"Set{set_index}-{original_name}"
		
		all_teams.extend(set_teams)
		print(f"✅ Set {set_index} generated {len(set_teams)} teams")
	
	print(f"\n📊 Total teams generated: {len(all_teams)} from {len(fixed_sets)} sets")
	return all_teams

@app.route("/customTeams",methods = ["POST","GET"])
def customTeams():
	matchid = request.form.get('matchid') if request.method == "POST" else request.args.get('matchid')
	if not matchid:
		return redirect("/")
	
	players = getplayers(matchid)
	teams = getteams(matchid)
	
	if not players or not teams:
		return redirect("/")
	
	# Filter out DNS (Did Not Start) players
	players = [p for p in players if len(p) > 6 and str(p[6]).upper() != 'DNS']
	
	# Load and apply ground analysis - first try database, then fallback to files
	from db import get_ground_analysis
	import json
	
	ground_analyzer = None
	ground_insights = ""
	
	# Try to get ground analysis from database first
	db_analysis = get_ground_analysis(matchid)
	if db_analysis and db_analysis.get('analysis_data'):
		try:
			analysis_data = json.loads(db_analysis['analysis_data'])
			# GroundAnalyzer not available - using basic ground insights
			ground_insights = f"Ground analysis data available for {analysis_data.get('ground_name', 'this ground')}"
			print("🏟️ Using stored ground analysis from database (basic mode)")
		except Exception as e:
			print(f"⚠️ Error loading database ground analysis: {e}")
	
	# Ground analysis features disabled - using standard player percentages
	print("⚠️ Ground analysis features disabled, using standard player percentages")
	
	# Sort players by percentage (highest first) - now includes ground adjustments
	players = sorted(players, key=operator.itemgetter(5), reverse=True)
	
	# Organize players by team and role
	teamA_players = [p for p in players if p[1] == teams[0][1]]
	teamB_players = [p for p in players if p[1] == teams[0][2]]
	
	# Organize by role
	all_wk = [p for p in players if p[2] == 'WK']
	all_bat = [p for p in players if p[2] == 'BAT']
	all_all = [p for p in players if p[2] in ['ALL', 'AL']]
	all_bowl = [p for p in players if p[2] == 'BOWL']
	
	teamA_bat = [p for p in teamA_players if p[2] == 'BAT']
	teamB_bat = [p for p in teamB_players if p[2] == 'BAT']
	
	custom_teams = []
	
	def validate_team_composition(selected_players):
		"""Validate that team has at least 1 WK, 1 BAT, 1 ALL/AL, and 1 BOWL"""
		roles = {'WK': 0, 'BAT': 0, 'ALL': 0, 'AL': 0, 'BOWL': 0}
		
		for player in selected_players:
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
	
	def create_team(name, strategy_title, strategy_description, selected_players):
		"""Helper function to create a team object - no fallbacks"""
		if not selected_players or len(selected_players) != 11:
			return None
		
		# Validate team composition
		if not validate_team_composition(selected_players):
			return None
		
		# Find captain and vice-captain (highest percentage players in the team)
		team_sorted = sorted(selected_players, key=lambda x: float(x[5]), reverse=True)
		captain = team_sorted[0]
		vice_captain = team_sorted[1]
		
		team = {
			'name': name,
			'strategy_title': strategy_title,
			'strategy_description': strategy_description,
			'players': [],
			'total_percentage': sum([float(p[5]) for p in selected_players])
		}
		
		for player in selected_players:
			team['players'].append({
				'name': player[3],
				'team': player[1],
				'role': player[2],
				'credits': player[4],
				'percentage': player[5],
				'is_captain': player == captain,
				'is_vice_captain': player == vice_captain
			})
		
		return team
	
	def safe_extend(target_list, source_list, count):
		"""Safely extend list with specified count - no fallbacks"""
		if len(source_list) < count:
			return 0  # Not enough players, don't add any
		target_list.extend(source_list[:count])
		return count
	
	# Team 1: Top 11 based on % selection
	team1_players = players[:11]
	team1 = create_team(
		'Team 1: Top Performers',
		'Highest Selection Percentage Strategy',
		'Top 11 players with highest selection percentages for maximum crowd confidence.',
		team1_players
	)
	if team1: custom_teams.append(team1)
	
	# Team 2: Team A Dominance
	team2_players = []
	if (len(teamA_players) >= 7 and len(teamB_bat) >= 2 and 
		len(all_all) >= 1 and len(all_bowl) >= 1):
		safe_extend(team2_players, teamA_players, 7)
		safe_extend(team2_players, teamB_bat, 2)
		safe_extend(team2_players, all_all, 1)
		safe_extend(team2_players, all_bowl, 1)
		
		team2 = create_team(
			'Team 2: Team A Dominance',
			f'{teams[0][1]} Heavy Strategy',
			f'7 top players from {teams[0][1]}, 2 best batsmen from {teams[0][2]}, plus best all-rounder and bowler.',
			team2_players
		)
		if team2: custom_teams.append(team2)
	
	# Team 3: Team B Dominance
	team3_players = []
	if (len(teamB_players) >= 7 and len(teamA_bat) >= 2 and 
		len(all_all) >= 1 and len(all_bowl) >= 1):
		safe_extend(team3_players, teamB_players, 7)
		safe_extend(team3_players, teamA_bat, 2)
		safe_extend(team3_players, all_all, 1)
		safe_extend(team3_players, all_bowl, 1)
		
		team3 = create_team(
			'Team 3: Team B Dominance',
			f'{teams[0][2]} Heavy Strategy',
			f'7 top players from {teams[0][2]}, 2 best batsmen from {teams[0][1]}, plus best all-rounder and bowler.',
			team3_players
		)
		if team3: custom_teams.append(team3)
	
	# Team 4: Batting Heavy
	team4_players = []
	if (len(all_wk) >= 1 and len(all_bat) >= 6 and 
		len(all_all) >= 2 and len(all_bowl) >= 2):
		safe_extend(team4_players, all_wk, 1)
		safe_extend(team4_players, all_bat, 6)
		safe_extend(team4_players, all_all, 2)
		safe_extend(team4_players, all_bowl, 2)
		
		team4 = create_team(
			'Team 4: Batting Powerhouse',
			'Batting Heavy Strategy',
			'6 batsmen, 2 all-rounders, 2 bowlers, and 1 wicket-keeper for maximum batting depth.',
			team4_players
		)
		if team4: custom_teams.append(team4)
	
	# Team 5: Bowling Heavy
	team5_players = []
	if (len(all_wk) >= 1 and len(all_bat) >= 3 and 
		len(all_all) >= 3 and len(all_bowl) >= 4):
		safe_extend(team5_players, all_wk, 1)
		safe_extend(team5_players, all_bat, 3)
		safe_extend(team5_players, all_all, 3)
		safe_extend(team5_players, all_bowl, 4)
		
		team5 = create_team(
			'Team 5: Bowling Attack',
			'Bowling Heavy Strategy',
			'4 bowlers, 3 all-rounders, 3 batsmen, and 1 wicket-keeper for strong bowling attack.',
			team5_players
		)
		if team5: custom_teams.append(team5)
	
	# Team 6: All-Rounder Heavy
	team6_players = []
	if (len(all_wk) >= 1 and len(all_bat) >= 3 and 
		len(all_all) >= 5 and len(all_bowl) >= 2):
		safe_extend(team6_players, all_wk, 1)
		safe_extend(team6_players, all_bat, 3)
		safe_extend(team6_players, all_all, 5)
		safe_extend(team6_players, all_bowl, 2)
		
		team6 = create_team(
			'Team 6: All-Rounder Special',
			'All-Rounder Heavy Strategy',
			'5 all-rounders for maximum flexibility, supported by 3 batsmen, 2 bowlers, and 1 keeper.',
			team6_players
		)
		if team6: custom_teams.append(team6)
	
	# Team 7: Budget Friendly
	budget_players = sorted(players, key=lambda x: float(x[4]))  # Sort by credits (ascending)
	team7_players = budget_players[:11]
	
	team7 = create_team(
		'Team 7: Budget Warriors',
		'Low Credit Strategy',
		'Lowest credit players who can still deliver value - perfect for budget constraints.',
		team7_players
	)
	if team7: custom_teams.append(team7)
	
	# Team 8: Premium Players
	premium_players = sorted(players, key=lambda x: float(x[4]), reverse=True)  # Sort by credits (descending)
	team8_players = premium_players[:11]
	
	team8 = create_team(
		'Team 8: Premium Squad',
		'High Credit Strategy',
		'Most expensive players - premium quality team with highest credit players.',
		team8_players
	)
	if team8: custom_teams.append(team8)
	
	# Team 9: Balanced 50-50
	team9_players = []
	if len(teamA_players) >= 5 and len(teamB_players) >= 6:
		safe_extend(team9_players, teamA_players, 5)
		safe_extend(team9_players, teamB_players, 6)
		
		team9 = create_team(
			'Team 9: Perfect Balance',
			'50-50 Team Split',
			f'Balanced representation: 5 from {teams[0][1]} and 6 from {teams[0][2]}.',
			team9_players
		)
		if team9: custom_teams.append(team9)
	
	# Team 10: Wicket-Keeper Heavy
	team10_players = []
	if (len(all_wk) >= 2 and len(all_bat) >= 4 and 
		len(all_all) >= 3 and len(all_bowl) >= 2):
		safe_extend(team10_players, all_wk, 2)
		safe_extend(team10_players, all_bat, 4)
		safe_extend(team10_players, all_all, 3)
		safe_extend(team10_players, all_bowl, 2)
		
		team10 = create_team(
			'Team 10: Double Keeper',
			'Wicket-Keeper Heavy Strategy',
			'2 wicket-keepers for extra batting depth and flexibility in team selection.',
			team10_players
		)
		if team10: custom_teams.append(team10)
	
	# Teams 11-20: Percentage Range Teams
	for i in range(10):
		start_idx = i * 2
		end_idx = start_idx + 11
		if end_idx <= len(players):
			range_players = players[start_idx:end_idx]
			team = create_team(
				f'Team {11+i}: Range {start_idx+1}-{end_idx}',
				f'Players Ranked {start_idx+1}-{end_idx}',
				f'Players ranked {start_idx+1} to {end_idx} by selection percentage.',
				range_players
			)
			if team: custom_teams.append(team)
	
	# Teams 21-30: Role-based Combinations
	role_combinations = [
		(2, 5, 2, 2, 'Keeper + Batting Focus'),
		(1, 4, 4, 2, 'All-Rounder Focus'),
		(1, 3, 3, 4, 'Bowling Focus'),
		(1, 6, 1, 3, 'Pure Batting'),
		(1, 2, 5, 3, 'All-Rounder Heavy'),
		(2, 3, 3, 3, 'Balanced Roles'),
		(1, 5, 3, 2, 'Batting + All-Rounder'),
		(1, 4, 2, 4, 'Bowling Heavy'),
		(2, 4, 2, 3, 'Keeper + Balanced'),
		(1, 3, 4, 3, 'All-Rounder + Bowling')
	]
	
	for i, (wk_count, bat_count, all_count, bowl_count, strategy) in enumerate(role_combinations):
		if (len(all_wk) >= wk_count and len(all_bat) >= bat_count and 
			len(all_all) >= all_count and len(all_bowl) >= bowl_count):
			team_players = []
			safe_extend(team_players, all_wk, wk_count)
			safe_extend(team_players, all_bat, bat_count)
			safe_extend(team_players, all_all, all_count)
			safe_extend(team_players, all_bowl, bowl_count)
			
			team = create_team(
				f'Team {21+i}: {strategy}',
				f'Role Strategy: {wk_count}WK-{bat_count}BAT-{all_count}ALL-{bowl_count}BOWL',
				f'{strategy} with {wk_count} keepers, {bat_count} batsmen, {all_count} all-rounders, {bowl_count} bowlers.',
				team_players
			)
			if team: custom_teams.append(team)
	
	# Teams 31-35: Credit Range Teams
	credit_ranges = [
		('Budget', 0, 8.5),
		('Mid-Range', 8.5, 10.0),
		('Premium', 10.0, 12.0),
		('Super Premium', 12.0, 15.0),
		('Mixed Budget', 0, 15.0)
	]
	
	for i, (range_name, min_credit, max_credit) in enumerate(credit_ranges):
		team_players = []
		
		if range_name == 'Mixed Budget':
			# Mix of budget and premium - only if we have enough
			budget_players_filtered = [p for p in players if float(p[4]) <= 8.5]
			premium_players_filtered = [p for p in players if float(p[4]) >= 10.0]
			if len(budget_players_filtered) >= 6 and len(premium_players_filtered) >= 5:
				safe_extend(team_players, budget_players_filtered, 6)
				safe_extend(team_players, premium_players_filtered, 5)
		else:
			credit_filtered = [p for p in players if min_credit <= float(p[4]) <= max_credit]
			if len(credit_filtered) >= 11:
				team_players = credit_filtered[:11]
		
		if len(team_players) == 11:
			team = create_team(
				f'Team {31+i}: {range_name}',
				f'{range_name} Credit Strategy',
				f'Players with credits between {min_credit} and {max_credit}.',
				team_players
			)
			if team: custom_teams.append(team)
	
	# Teams 36-40: Special Strategies
	special_strategies = []
	
	# Only add strategies if we have enough players
	if len(players) >= 11:
		special_strategies.append(('Differential Picks', 'Low ownership players for unique team', players[-11:]))  # Lowest percentage
		special_strategies.append(('Crowd Favorites', 'Most popular players', players[:11]))  # Highest percentage
		
		# Value picks - best percentage per credit ratio
		value_sorted = sorted(players, key=lambda x: float(x[5])/float(x[4]), reverse=True)
		if len(value_sorted) >= 11:
			special_strategies.append(('Value Picks', 'Best percentage per credit ratio', value_sorted[:11]))
		
		# Contrarian - middle range players
		if len(players) >= 22:  # Need at least 22 players for middle range
			middle_start = len(players)//2 - 5
			middle_end = middle_start + 11
			special_strategies.append(('Contrarian', 'Against the crowd picks', players[middle_start:middle_end]))
		
		# Wildcard - every second player
		wildcard_players = players[::2]
		if len(wildcard_players) >= 11:
			special_strategies.append(('Wildcard', 'Random mix strategy', wildcard_players[:11]))
	
	for i, (strategy_name, description, strategy_players) in enumerate(special_strategies):
		if len(strategy_players) == 11:
			team = create_team(
				f'Team {36+i}: {strategy_name}',
				f'{strategy_name} Strategy',
				description,
				strategy_players
			)
			if team: custom_teams.append(team)
	
	return render_template("custom_teams.html", 
	                      custom_teams=custom_teams,
	                      teamA=teams[0][1],
	                      teamB=teams[0][2],
	                      matchid=matchid,
	                      ground_insights=ground_insights)

@app.route("/scorecardTeams",methods = ["POST","GET"])
def scorecardTeams():
	matchid = request.form.get('matchid') if request.method == "POST" else request.args.get('matchid')
	if not matchid:
		return redirect("/")
	
	players = getplayers(matchid)
	teams = getteams(matchid)
	
	if not players or not teams:
		return redirect("/")
	
	# Filter out DNS (Did Not Start) players
	players = [p for p in players if len(p) > 6 and str(p[6]).upper() != 'DNS']
	
	# Generate scorecard-based templates first
	generator = ScorecardTemplateGenerator()
	if generator.load_ground_analysis(match_id=matchid):
		print("🏟️ Generating scorecard-based templates...")
		templates_generated = generator.generate_and_save_templates(match_id=matchid)
		if templates_generated:
			print("✅ Scorecard templates generated successfully")
		else:
			print("⚠️ Using existing templates")
	
	# Load and apply ground analysis for player adjustments
	from db import get_ground_analysis
	import json
	
	ground_insights = ""
	
	# Try to get ground analysis from database
	db_analysis = get_ground_analysis(matchid)
	if db_analysis and db_analysis.get('analysis_data'):
		try:
			analysis_data = json.loads(db_analysis['analysis_data'])
			# GroundAnalyzer not available - using basic ground insights
			ground_insights = f"Ground analysis data available for {analysis_data.get('ground_name', 'this ground')}"
			print("🏟️ Using stored ground analysis for scorecard teams (basic mode)")
		except Exception as e:
			print(f"⚠️ Error loading database ground analysis: {e}")
	
	# Ground analysis features disabled for scorecard teams
	print("⚠️ Ground analysis features disabled for scorecard teams, using standard player percentages")
	
	# Sort players by percentage (highest first) - now includes ground adjustments
	players = sorted(players, key=operator.itemgetter(5), reverse=True)
	
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
	
	# If no match role data, use general distribution
	if not any([atop, amid, ahit, apow, abre, adea, btop, bmid, bhit, bpow, bbre, bdea]):
		print("No match role data found, using general player distribution")
		
		teamA_sixth = len(teamA_players) // 6 if teamA_players else 0
		teamB_sixth = len(teamB_players) // 6 if teamB_players else 0
		
		atop = teamA_players[:teamA_sixth] if teamA_players else []
		amid = teamA_players[teamA_sixth:teamA_sixth*2] if teamA_players else []
		ahit = teamA_players[teamA_sixth*2:teamA_sixth*3] if teamA_players else []
		apow = teamA_players[teamA_sixth*3:teamA_sixth*4] if teamA_players else []
		abre = teamA_players[teamA_sixth*4:] if teamA_players else []
		
		btop = teamB_players[:teamB_sixth] if teamB_players else []
		bmid = teamB_players[teamB_sixth:teamB_sixth*2] if teamB_players else []
		bhit = teamB_players[teamB_sixth*2:teamB_sixth*3] if teamB_players else []
		bpow = teamB_players[teamB_sixth*3:teamB_sixth*4] if teamB_players else []
		bbre = teamB_players[teamB_sixth*4:teamB_sixth*5] if teamB_players else []
		bdea = teamB_players[teamB_sixth*5:] if teamB_players else []
	
	# Identify top 13 players by percentage (highest first)
	top13_players = players[:13] if len(players) >= 13 else players
	top13_names = [p[3] for p in top13_players]
	
	# Generate teams using ONLY scorecard-based templates from the same ground
	from db import getDreamTeamsBySourceMatch
	scorecard_templates = getDreamTeamsBySourceMatch(matchid)
	
	# Fallback to all scorecard templates if no ground-specific templates found
	if not scorecard_templates:
		all_templates = getDreamTeams()  # Get all templates for scorecard analysis
		scorecard_templates = []
		for t in all_templates:
			try:
				# Access sqlite3.Row columns by name
				stadium = t['stadium'] if 'stadium' in t.keys() else ''
				if 'Scorecard Analysis' in str(stadium):
					scorecard_templates.append(t)
			except (KeyError, TypeError):
				continue
	
	if not scorecard_templates:
		print("❌ No scorecard templates found")
		return render_template("finalteams.html",
		                      validcombinations=[],
		                      teamA=teams[0][1],
		                      teamB=teams[0][2],
		                      top13_names=top13_names,
		                      ground_insights=ground_insights,
		                      error_message="No scorecard-based templates available")
	
	print(f"🎯 Using {len(scorecard_templates)} scorecard-based templates")
	
	# Generate teams using scorecard templates
	scorecard_teams = []
	
	for template in scorecard_templates:
		try:
			# Generate team using this specific template
			team = []
			
			# Add players according to template composition (convert to int)
			# Use a set to track already added players to avoid duplicates
			added_players = set()
			
			def add_unique_players(player_list, count):
				"""Add players from list avoiding duplicates"""
				added = 0
				for player in player_list:
					if added >= count:
						break
					player_id = (player[3], player[1])  # Use name and team as unique identifier
					if player_id not in added_players:
						team.append(player)
						added_players.add(player_id)
						added += 1
				return added
			
			# Add players from each category
			add_unique_players(atop, int(template['one']))
			add_unique_players(amid, int(template['two']))
			add_unique_players(ahit, int(template['three']))
			add_unique_players(bpow, int(template['four']))
			add_unique_players(bbre, int(template['five']))
			add_unique_players(bdea, int(template['six']))
			add_unique_players(btop, int(template['seven']))
			add_unique_players(bmid, int(template['eight']))
			add_unique_players(bhit, int(template['nine']))
			add_unique_players(apow, int(template['ten']))
			add_unique_players(abre, int(template['eleven']))
			add_unique_players(adea, int(template['twelve']) if 'twelve' in template.keys() else 0)
			
			# Fill remaining slots if we have less than 11 players due to duplicates
			if len(team) < 11:
				# Get all available players not already in team
				all_available = atop + amid + ahit + bpow + bbre + bdea + btop + bmid + bhit + apow + abre + adea
				
				for player in all_available:
					if len(team) >= 11:
						break
					player_id = (player[3], player[1])
					if player_id not in added_players:
						team.append(player)
						added_players.add(player_id)
			
			# Validate team
			if len(team) == 11 and validate_team_roles(team):
				# Add captain and vice-captain based on template preferences
				cap_index = int(template['cap']) if template['cap'] is not None else 0
				vc_index = int(template['vc']) if template['vc'] is not None else 1
				
				captain = team[cap_index] if len(team) > cap_index else team[0]
				vice_captain = team[vc_index] if len(team) > vc_index else team[1]
				
				# Ensure VC is different from captain
				if vice_captain == captain and len(team) > 1:
					vice_captain = team[1] if team[1] != captain else (team[2] if len(team) > 2 else team[0])
				
				team.append(captain)  # Captain at index 11
				team.append(vice_captain)  # Vice-captain at index 12
				team.append(template['matchbetween'])  # Template name at index 13
				
				# Calculate total percentage
				total_percentage = sum([float(p[5]) for p in team[:11]])
				team.append(total_percentage)  # Total percentage at index 14
				
				# Count top 13 players
				top13_count = sum(1 for p in team[:11] if p[3] in top13_names)
				team.append(top13_count)  # Top 13 count at index 15
				
				scorecard_teams.append(team)
				print(f"✅ Generated team using template: {template['matchbetween']} ({len(team)} players)")
			else:
				print(f"⚠️ Failed to generate valid team for template: {template['matchbetween']} ({len(team)} players, valid roles: {validate_team_roles(team) if len(team) == 11 else 'N/A'})")
		
		except Exception as e:
			try:
				template_name = template['matchbetween'] if 'matchbetween' in template.keys() else 'Unknown'
			except:
				template_name = 'Unknown'
			print(f"❌ Error generating team for template {template_name}: {e}")
	
	# Sort teams by total percentage (highest first)
	scorecard_teams.sort(key=lambda x: x[-2], reverse=True)
	
	print(f"📊 Generated {len(scorecard_teams)} scorecard-based teams")
	
	# Always save scorecard teams to JSON file (similar to generateTeams)
	from datetime import datetime
	import json
	
	# Create filename with timestamp
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	filename = f"scorecard_teams_{timestamp}.json"
	
	try:
		# Prepare teams data for JSON (Dream11 API format)
		teams_data = {
			"metadata": {
				"generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				"match": f"{teams[0][1]} vs {teams[0][2]}",
				"total_teams": 0,
				"match_id": "YOUR_MATCH_ID",
				"generation_type": "scorecard_based",
				"ground_insights": ground_insights,
				"auth_token": "YOUR_AUTH_TOKEN"
			},
			"teams": []
		}
		
		valid_teams_count = 0
		
		for i, team in enumerate(scorecard_teams, 1):
			if len(team) < 11:
				continue
				
			# Extract numeric player IDs
			player_ids = []
			for j in range(11):
				if j < len(team) and team[j]:
					try:
						# For sqlite3.Row objects, access by column name
						if hasattr(team[j], 'keys'):  # sqlite3.Row object
							player_id = team[j]['player_id'] if 'player_id' in team[j].keys() else 0
						else:  # Regular tuple/list (player_id should be at index 7)
							player_id = team[j][7] if len(team[j]) > 7 else 0
						
						# Ensure numeric player ID
						if isinstance(player_id, (int, float)) and player_id > 0:
							player_ids.append(int(player_id))
						else:
							player_ids.append(0)
					except (ValueError, TypeError, IndexError):
						player_ids.append(0)
				else:
					player_ids.append(0)
			
			# Get captain and vice-captain IDs
			captain_id = 0
			vice_captain_id = 0
			
			# Find captain and vice-captain from team structure
			if len(team) >= 13:
				try:
					# Handle captain index
					cap_index = 0
					if team[-3] is not None:
						if isinstance(team[-3], (int, float)):
							cap_index = int(team[-3])
						elif isinstance(team[-3], str) and team[-3].isdigit():
							cap_index = int(team[-3])
					
					# Handle vice-captain index
					vc_index = 1
					if team[-4] is not None:
						if isinstance(team[-4], (int, float)):
							vc_index = int(team[-4])
						elif isinstance(team[-4], str) and team[-4].isdigit():
							vc_index = int(team[-4])
					
					# Get captain numeric ID
					if cap_index < len(team) and team[cap_index]:
						try:
							if hasattr(team[cap_index], 'keys'):  # sqlite3.Row object
								cap_player_id = team[cap_index]['player_id'] if 'player_id' in team[cap_index].keys() else 0
							else:  # Regular tuple/list
								cap_player_id = team[cap_index][7] if len(team[cap_index]) > 7 else 0
							
							if isinstance(cap_player_id, (int, float)) and cap_player_id > 0:
								captain_id = int(cap_player_id)
						except (IndexError, TypeError):
							pass
					
					# Get vice-captain numeric ID
					if vc_index < len(team) and team[vc_index]:
						try:
							if hasattr(team[vc_index], 'keys'):  # sqlite3.Row object
								vc_player_id = team[vc_index]['player_id'] if 'player_id' in team[vc_index].keys() else 0
							else:  # Regular tuple/list
								vc_player_id = team[vc_index][7] if len(team[vc_index]) > 7 else 0
							
							if isinstance(vc_player_id, (int, float)) and vc_player_id > 0:
								vice_captain_id = int(vc_player_id)
						except (IndexError, TypeError):
							pass
							
				except (ValueError, IndexError, TypeError):
					pass
			
			# Create team object in Dream11 API format
			team_obj = {
				"id": i,
				"name": f"{teams[0][1]}-{teams[0][2]}",
				"captain": captain_id,
				"vice_captain": vice_captain_id,
				"players": player_ids
			}
			
			teams_data["teams"].append(team_obj)
			valid_teams_count += 1
		
		# Update total teams count
		teams_data["metadata"]["total_teams"] = valid_teams_count
		
		# Write JSON file
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(teams_data, f, indent=2, ensure_ascii=False)
		
		print(f"\n📁 Scorecard teams saved to: {filename}")
		print(f"💡 Edit the JSON file to add your auth_token in the metadata section")
		print(f"📊 Total scorecard teams saved: {valid_teams_count}")
		
	except Exception as e:
		print(f"❌ Error saving scorecard teams to JSON file: {e}")
	
	# Check if JSON format is requested for response
	if request.args.get('format') == 'json' or request.form.get('format') == 'json':
		return jsonify(teams_data)
	
	return render_template("finalteams.html",
	                      validcombinations=convert_teams_for_template(scorecard_teams),
	                      teamA=teams[0][1],
	                      teamB=teams[0][2],
	                      top13_names=top13_names,
	                      ground_insights=ground_insights,
	                      page_title="Scorecard-Based Teams")

@app.route("/generateTeams",methods = ["POST","GET"])
def generateTeams():
	matchid=request.form.get('matchid')
	winning=request.form.get('winning', 'Batting')  # Default to 'Batting' if not provided
	print(f"🎯 Team generation strategy: {winning}")
	players=getplayers(matchid)
	teams=getteams(matchid)
	
	# Load and apply ground analysis - first try database, then fallback to files
	from db import get_ground_analysis
	import json
	
	ground_analyzer = None
	ground_insights = ""
	
	# Try to get ground analysis from database first
	db_analysis = get_ground_analysis(matchid)
	if db_analysis and db_analysis.get('analysis_data'):
		try:
			analysis_data = json.loads(db_analysis['analysis_data'])
			ground_analyzer = GroundAnalyzer()
			ground_analyzer.analysis = analysis_data
			ground_insights = ground_analyzer.get_ground_insights()
			print("🏟️ Using stored ground analysis from database for template generation")
		except Exception as e:
			print(f"⚠️ Error loading database ground analysis: {e}")
	
	# File-based analysis not available - using database analysis only
	
	# Apply ground analysis if available
	if ground_analyzer:
		print("🏟️ Applying ground-based player adjustments to template generation...")
		players = ground_analyzer.apply_ground_bias_to_players(players)
		print("✅ Ground analysis applied to template team generation")
	else:
		print("⚠️ No ground data available for template generation")
	
	enforce_top13 = request.form.get('enforce_top13') == '1'
	ensure_diversity = request.form.get('ensure_diversity') == '1'
	
	print(f"🎯 Enforce top 13 rule: {enforce_top13}")
	print(f"🔄 Ensure team diversity: {ensure_diversity}")
	
	# Always use template-based generation
	print("Using template-based team generation with ground analysis")
	players=sorted(players, key=operator.itemgetter(5))
	players.reverse()
	
	# Identify top 13 players by percentage (highest first)
	top13_players = players[:13] if len(players) >= 13 else players
	top13_names = [p[3] for p in top13_players]  # Extract player names
	print(f"🔝 Top 13 players identified: {top13_names}")
	print(f"📊 Top 13 percentages: {[f'{p[3]}: {p[5]}%' for p in top13_players]}")
	print(f"🎯 Team constraint: Each team must have 7-8 players from top 13 (not more than 8)")
	
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
	print(atop)
	print(amid)
	print(ahit)
	# If no match role data, use all players in general categories
	# Generate teams using templates - Loop 5 times for more variety
	templatecombinations = []
	for iteration in range(5):
		print(f"🔄 Generating teams - Iteration {iteration + 1}/5 (Strategy: {winning})")
		teams_batch = getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teams[0][1],teams[0][2],winning)
		templatecombinations.extend(teams_batch)
		print(f"✅ Iteration {iteration + 1} completed: {len(teams_batch)} teams generated, Total: {len(templatecombinations)}")
	
	# Final validation: ensure exactly 1 team per template
	expected_teams = len(getDreamTeams(winning)) if getDreamTeams(winning) else 0
	actual_teams = len(templatecombinations)
	success_rate = (actual_teams / expected_teams * 100) if expected_teams > 0 else 0
	
	print(f"\n📊 FINAL GENERATION SUMMARY:")
	print(f"   Templates processed: {expected_teams}")
	print(f"   Teams generated: {actual_teams}")
	print(f"   Success rate: {success_rate:.1f}%")
	print(f"   Failed templates: {expected_teams - actual_teams}")
	
	if actual_teams == expected_teams:
		print(f"✅ Perfect success! All templates generated exactly 1 team")
	elif actual_teams > 0:
		print(f"⚠️ Partial success: {actual_teams}/{expected_teams} templates succeeded")
	else:
		print(f"❌ Complete failure: No templates could generate valid teams")
	
	# Remove duplicates and validate team diversity if enabled
	# if ensure_diversity and templatecombinations:
	# 	print(f"\n🔄 DIVERSITY PROCESSING:")
		
	# 	# First, remove obvious duplicates
	# 	templatecombinations = remove_duplicate_teams(templatecombinations)
		
	# 	# Then validate remaining diversity
	# 	check_final_team_diversity(templatecombinations)
		
	# 	print(f"📊 Final team count after duplicate removal: {len(templatecombinations)}")
	
	# Validate final teams against top 13 requirement and add top 13 count to each team
	valid_teams_count = 0
	enhanced_teams = []
	
	for i, team in enumerate(templatecombinations):
		# Calculate top 13 count for this team
		top13_count = 0
		for player in team[:11]:  # Only check first 11 players
			if len(player) > 3 and player[3] in top13_names:
				top13_count += 1
		
		# Create enhanced team with consistent structure:
		# Expected input: [11 players, captain, vice-captain, template_name, total_percentage] (length 15)
		# Target output: [11 players, captain, vice-captain, template_name, top13_count, total_percentage] (length 16)
		
		enhanced_team = list(team)
		
		# Clean up template name if it got corrupted with percentage data
		if len(enhanced_team) > 13 and enhanced_team[13]:
			template_name = str(enhanced_team[13])
			if '%' in template_name:
				# Only remove the percentage part, keep everything before it
				clean_name = template_name.split('%')[0]
				enhanced_team[13] = clean_name
				print(f"🧹 Cleaned corrupted template name: '{template_name}' → '{clean_name}'")
			elif len(template_name) > 6 and template_name[-6:].isdigit():
				# Only remove if the last 6 characters are all digits (likely a percentage value)
				import re
				clean_name = re.sub(r'-\d{4,}$', '', template_name)  # Remove dash followed by 4+ digits at end
				if clean_name != template_name:
					enhanced_team[13] = clean_name
					print(f"🧹 Cleaned trailing numbers: '{template_name}' → '{clean_name}'")
		
		# Standard case: team has the expected structure from calculatePercentage
		if len(enhanced_team) == 15:
			# Insert top13_count before the last element (total_percentage)
			total_percentage = enhanced_team.pop()  # Remove percentage from end
			enhanced_team.append(top13_count)       # Add top13_count at position 14
			enhanced_team.append(total_percentage)  # Add percentage back at position 15
		else:
			# Handle edge cases - ensure we have the right structure
			print(f"⚠️ Team {i+1} has unexpected length {len(enhanced_team)}, fixing...")
			
			# Ensure we have at least template name at position 13
			while len(enhanced_team) < 14:
				enhanced_team.append(f"Team {i+1}")
			
			# Add top13_count at position 14
			enhanced_team.append(top13_count)
			
			# Add total_percentage at position 15 (calculate if missing)
			if len(enhanced_team) < 16:
				total_percentage = 0
				for player in team[:11]:
					try:
						if player and len(player) > 5:
							total_percentage += int(player[5]) if player[5] else 0
					except (IndexError, ValueError, TypeError):
						continue
				enhanced_team.append(total_percentage)
		
		enhanced_teams.append(enhanced_team)
		
		if validate_top13_players(team[:11], top13_names):
			valid_teams_count += 1
	
	# Show template-to-team mapping with correct indices
	print(f"\n📋 Template-to-Team Mapping:")
	for i, team in enumerate(enhanced_teams, 1):
		# Enhanced team structure: [11 players, captain, vice-captain, template_name, top13_count, total_percentage]
		template_name = team[13] if len(team) > 13 else f"Team {i}"
		top13_count = team[14] if len(team) > 14 else "Unknown"
		total_percentage = team[15] if len(team) > 15 else "Unknown"
		
		# Show if it's from a set
		if "Set" in str(template_name):
			print(f"   {i:2d}. {template_name} → {top13_count}/13 top players, {total_percentage}%")
		else:
			print(f"   {i:2d}. {template_name} → {top13_count}/13 top players, {total_percentage}%")
	

	
	print(f"🎯 Final validation: {valid_teams_count}/{len(templatecombinations)} teams have 7-8 players from top 13")
	
	# Calculate team diversity statistics
	if len(templatecombinations) > 1:
		total_comparisons = 0
		total_differences = 0
		min_difference = 11
		max_difference = 0
		
		for i, team1 in enumerate(templatecombinations):
			for j, team2 in enumerate(templatecombinations[i+1:], i+1):
				common_players = intersection(team1[:11], team2[:11])
				difference = 11 - common_players
				total_comparisons += 1
				total_differences += difference
				min_difference = min(min_difference, difference)
				max_difference = max(max_difference, difference)
		
		avg_difference = total_differences / total_comparisons if total_comparisons > 0 else 0
		
		print(f"📊 Team Diversity Statistics:")
		print(f"   Average player difference: {avg_difference:.1f}")
		print(f"   Minimum difference: {min_difference} players")
		print(f"   Maximum difference: {max_difference} players")
		print(f"   Total team comparisons: {total_comparisons}")
	
	# Save teams to JSON file
	print(f"🔍 DEBUG: enhanced_teams length: {len(enhanced_teams) if enhanced_teams else 0}")
	if enhanced_teams:
		print(f"🔍 DEBUG: First team structure: {type(enhanced_teams[0])}, length: {len(enhanced_teams[0]) if enhanced_teams[0] else 0}")
		print(f"🔍 DEBUG: Calling save_teams_to_file with {len(enhanced_teams)} teams")
		save_teams_to_file(enhanced_teams, teams[0][1], teams[0][2])
	else:
		print("❌ DEBUG: No enhanced_teams to save to JSON")
	
	# Sort templatecombinations by percentage (descending order - highest percentage first)
	print(f"🔄 Sorting {len(templatecombinations)} teams by percentage...")
	try:
		# Each team should have percentage as the last element (index -1)
		# Sort in descending order (highest percentage first)
		templatecombinations = sorted(templatecombinations, key=lambda team: float(team[-1]) if team and len(team) > 0 and str(team[-1]).replace('.', '').replace('-', '').isdigit() else 0, reverse=True)
		print(f"✅ Teams sorted successfully by percentage")
		if templatecombinations:
			print(f"📊 Top team percentage: {templatecombinations[0][-1] if templatecombinations[0] else 'N/A'}")
			print(f"📊 Bottom team percentage: {templatecombinations[-1][-1] if templatecombinations[-1] else 'N/A'}")
	except Exception as e:
		print(f"⚠️ Error sorting teams by percentage: {e}")
		print("📝 Using original order")
	
	# Export sorted teams to JSON file (dream11_teams_...)
	print(f"💾 Exporting {len(templatecombinations)} sorted teams to JSON...")
	try:
		# Debug: Check team structure
		if templatecombinations:
			print(f"🔍 DEBUG: First team structure:")
			first_team = templatecombinations[0]
			print(f"   Team length: {len(first_team) if first_team else 0}")
			if first_team and len(first_team) > 0:
				print(f"   First player: {first_team[0] if len(first_team) > 0 else 'None'}")
				print(f"   Player structure: {type(first_team[0]) if len(first_team) > 0 else 'None'}")
				if len(first_team) > 0 and hasattr(first_team[0], '__len__'):
					print(f"   Player length: {len(first_team[0])}")
					if len(first_team[0]) > 7:
						print(f"   Player ID (index 7): {first_team[0][7]}")
				print(f"   Last element (percentage): {first_team[-1] if first_team else 'None'}")
		
		# Convert templatecombinations to the format expected by save_teams_to_file
		if templatecombinations:
			# Create enhanced_teams from sorted templatecombinations for JSON export
			sorted_enhanced_teams = []
			for i, team in enumerate(templatecombinations):
				print(f"🔍 Processing team {i+1}: length={len(team) if team else 0}")
				
				if team and len(team) >= 11:  # Ensure team has enough players
					# Extract the first 11 players for the team
					team_players = team[:11]
					print(f"   Team players extracted: {len(team_players)}")
					
					# Debug player IDs extraction
					player_ids = []
					for j, player in enumerate(team_players):
						if player and hasattr(player, '__len__') and len(player) > 7:
							player_id = player[7] if player[7] is not None else 0
							player_ids.append(player_id)
							if j < 3:  # Show first 3 for debugging
								print(f"     Player {j+1}: {player[3] if len(player) > 3 else 'Unknown'} ID: {player_id}")
						else:
							print(f"     Player {j+1}: Invalid structure - {type(player)}")
							player_ids.append(0)
					
					# Get captain and vice-captain
					captain_id = 0
					vc_id = 0
					
					if len(team) > 11 and team[11] and hasattr(team[11], '__len__') and len(team[11]) > 7:
						captain_id = team[11][7] if team[11][7] is not None else 0
					elif team_players and len(team_players[0]) > 7:
						captain_id = team_players[0][7] if team_players[0][7] is not None else 0
					
					if len(team) > 12 and team[12] and hasattr(team[12], '__len__') and len(team[12]) > 7:
						vc_id = team[12][7] if team[12][7] is not None else 0
					elif len(team_players) > 1 and len(team_players[1]) > 7:
						vc_id = team_players[1][7] if team_players[1][7] is not None else 0
					
					# Get team name
					team_name = f"Team {i + 1}"
					if len(team) > 13:  # Template name might be at index 13
						team_name = str(team[13]) if team[13] else team_name
					elif len(team) > 12:  # Or at index -2
						team_name = str(team[-2]) if team[-2] else team_name
					
					enhanced_team = {
						'id': i + 1,
						'name': team_name,
						'players': player_ids,
						'captain': captain_id,
						'vice_captain': vc_id,
						'percentage': team[-1] if team else 0
					}
					
					print(f"   Enhanced team: {len(enhanced_team['players'])} players, captain: {enhanced_team['captain']}, vc: {enhanced_team['vice_captain']}")
					sorted_enhanced_teams.append(enhanced_team)
				else:
					print(f"   Skipping team {i+1}: insufficient length ({len(team) if team else 0})")
			
			print(f"🔍 Total enhanced teams created: {len(sorted_enhanced_teams)}")
			
			if sorted_enhanced_teams:
				# Export directly to JSON with our enhanced format
				from datetime import datetime
				import json
				
				filename = f"dream11_teams_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
				
				# Get match ID from the current match
				current_match_id = "YOUR_MATCH_ID"
				try:
					if hasattr(request, 'form') and request.form.get('matchid'):
						current_match_id = request.form.get('matchid')
				except:
					pass
				
				# Prepare final JSON structure
				json_data = {
					"metadata": {
						"generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
						"match": f"{teams[0][1]} vs {teams[0][2]}",
						"total_teams": len(sorted_enhanced_teams),
						"match_id": current_match_id,
						"auth_token": "YOUR_AUTH_TOKEN"
					},
					"teams": sorted_enhanced_teams
				}
				
				# Write to file
				with open(filename, 'w') as f:
					json.dump(json_data, f, indent=2)
				
				print(f"📁 Teams saved to: {filename}")
				print(f"💡 Edit the JSON file to add your match_id and auth_token in the metadata section")
				print(f"📊 Total valid teams saved: {len(sorted_enhanced_teams)}")
				print(f"✅ Sorted teams exported to dream11_teams_*.json successfully")
			else:
				print("⚠️ No valid teams to export after sorting")
		else:
			print("⚠️ No teams available for JSON export")
	except Exception as e:
		print(f"❌ Error exporting sorted teams to JSON: {e}")
		import traceback
		traceback.print_exc()
	
	return render_template("finalteams.html",
	                      validcombinations=convert_teams_for_template(templatecombinations),
	                      teamA=teams[0][1],
	                      teamB=teams[0][2],
	                      top13_players=top13_players,
	                      top13_names=top13_names,
	                      ground_insights=ground_insights)

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return len(lst3)

def validate_team_diversity(teams, min_difference=4):
    """
    Validate that teams have sufficient diversity (at least min_difference players different)
    """
    if len(teams) < 2:
        return True
    
    print(f"\n🔍 DIVERSITY VALIDATION: Checking {len(teams)} teams")
    print(f"📊 Requirement: At least {min_difference} different players between teams")
    
    diversity_violations = 0
    max_similarity = 0
    
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team1 = teams[i][:11] if len(teams[i]) > 11 else teams[i]
            team2 = teams[j][:11] if len(teams[j]) > 11 else teams[j]
            
            common_players = intersection(team1, team2)
            different_players = 11 - common_players
            
            if different_players < min_difference:
                diversity_violations += 1
                if i < 3 and j < 6:  # Only log first few violations
                    print(f"❌ Teams {i+1} & {j+1}: Only {different_players} different players ({common_players} common)")
            
            max_similarity = max(max_similarity, common_players)
    
    print(f"📊 Diversity Results:")
    print(f"   - Violations: {diversity_violations}")
    print(f"   - Max similarity: {max_similarity} common players")
    print(f"   - Min difference: {11 - max_similarity} different players")
    
    if diversity_violations == 0:
        print(f"✅ All teams meet diversity requirement!")
    else:
        print(f"⚠️ {diversity_violations} team pairs violate diversity requirement")
    
    return diversity_violations == 0

def check_for_duplicate_teams(teams):
    """
    Check for exact duplicate teams and near-duplicates
    """
    print(f"\n🔍 DUPLICATE DETECTION: Checking {len(teams)} teams")
    
    exact_duplicates = 0
    near_duplicates = 0
    duplicate_pairs = []
    
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team1_players = set()
            team2_players = set()
            
            # Extract player IDs from first 11 players
            for player in teams[i][:11]:
                if player and len(player) > 0:
                    team1_players.add(player[0])
            
            for player in teams[j][:11]:
                if player and len(player) > 0:
                    team2_players.add(player[0])
            
            # Check for exact duplicates
            if team1_players == team2_players:
                exact_duplicates += 1
                duplicate_pairs.append((i+1, j+1, "EXACT"))
                if len(duplicate_pairs) <= 5:  # Log first 5 duplicates
                    print(f"❌ EXACT DUPLICATE: Teams {i+1} & {j+1} have identical players")
            
            # Check for near-duplicates (10+ common players)
            elif len(team1_players.intersection(team2_players)) >= 10:
                near_duplicates += 1
                common_count = len(team1_players.intersection(team2_players))
                duplicate_pairs.append((i+1, j+1, f"{common_count} common"))
                if len(duplicate_pairs) <= 5:  # Log first 5 near-duplicates
                    print(f"⚠️ NEAR DUPLICATE: Teams {i+1} & {j+1} have {common_count} common players")
    
    print(f"📊 Duplicate Results:")
    print(f"   - Exact duplicates: {exact_duplicates}")
    print(f"   - Near duplicates (10+ common): {near_duplicates}")
    print(f"   - Total problematic pairs: {len(duplicate_pairs)}")
    
    return exact_duplicates == 0 and near_duplicates == 0

def remove_duplicate_teams(teams):
    """
    Remove duplicate and near-duplicate teams, keeping the first occurrence
    """
    print(f"\n🧹 REMOVING DUPLICATES from {len(teams)} teams")
    
    unique_teams = []
    removed_count = 0
    
    for i, team in enumerate(teams):
        is_duplicate = False
        current_team_players = set()
        
        # Extract player IDs from current team
        for player in team[:11]:
            if player and len(player) > 0:
                current_team_players.add(player[0])
        
        # Check against all previously added unique teams
        for existing_team in unique_teams:
            existing_team_players = set()
            for player in existing_team[:11]:
                if player and len(player) > 0:
                    existing_team_players.add(player[0])
            
            # Check for exact match or too many common players
            common_players = len(current_team_players.intersection(existing_team_players))
            
            if common_players >= 10:  # 10+ common players = too similar
                is_duplicate = True
                removed_count += 1
                if removed_count <= 5:  # Log first 5 removals
                    print(f"🗑️ Removed team {i+1}: {common_players} common players with existing team")
                break
        
        if not is_duplicate:
            unique_teams.append(team)
    
    print(f"✅ Duplicate removal complete:")
    print(f"   - Original teams: {len(teams)}")
    print(f"   - Unique teams: {len(unique_teams)}")
    print(f"   - Removed duplicates: {removed_count}")
    
    return unique_teams

def check_final_team_diversity(teams):
    """
    Check and report on the diversity of the final team set
    """
    if len(teams) < 2:
        return True, "Not enough teams to validate diversity"
    
    # Check for duplicates first
    has_no_duplicates = check_for_duplicate_teams(teams)
    
    # Then check overall diversity
    has_good_diversity = validate_team_diversity(teams, min_difference=5)  # Require 5+ different players
    
    return has_no_duplicates and has_good_diversity, "Diversity and duplicate check completed"
    
    violations = []
    for i, team1 in enumerate(teams):
        for j, team2 in enumerate(teams[i+1:], i+1):
            common_players = intersection(team1[:11], team2[:11])
            difference = 11 - common_players
            
            if difference < min_difference:
                violations.append({
                    'team1_index': i,
                    'team2_index': j,
                    'common_players': common_players,
                    'difference': difference
                })
    
    is_valid = len(violations) == 0
    message = f"All teams have at least {min_difference} different players" if is_valid else f"Found {len(violations)} team pairs with insufficient diversity"
    
    return is_valid, message, violations
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
        'winning': 'Batting',
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
            INSERT INTO templates (matchbetween, stadium, winning, atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, cap, vc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template_data['matchbetween'], template_data['stadium'], template_data['winning'],
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

def validate_top13_players(team, top13_names):
	"""Count top 13 players in team (no constraints applied)"""
	if not top13_names:
		return True  # Skip validation if no top 13 list provided
		
	top13_count = 0
	team_player_names = []
	top13_in_team = []
	
	for player in team:
		if len(player) > 3:
			player_name = player[3]
			team_player_names.append(player_name)
			if player_name in top13_names:  # Check if player name is in top 13
				top13_count += 1
				top13_in_team.append(player_name)
	
	# No constraints - just return True (all teams are valid regardless of top 13 count)
	print(f"📊 Team has {top13_count}/13 top players: {top13_in_team}")
	
	return True

def validate_template_adherence(team, template, atop, amid, ahit, bpow, bbre, bdea, btop, bmid, bhit, apow, abre, adea, scale_factor):
	"""Validate that team strictly follows template composition"""
	if not template:
		return False
	
	# Count players from each category in the team
	team_composition = {
		'atop': 0, 'amid': 0, 'ahit': 0,
		'bpow': 0, 'bbre': 0, 'bdea': 0,
		'btop': 0, 'bmid': 0, 'bhit': 0,
		'apow': 0, 'abre': 0, 'adea': 0
	}
	
	# Create sets for quick lookup
	player_sets = {
		'atop': set((p[3], p[1]) for p in atop),
		'amid': set((p[3], p[1]) for p in amid),
		'ahit': set((p[3], p[1]) for p in ahit),
		'bpow': set((p[3], p[1]) for p in bpow),
		'bbre': set((p[3], p[1]) for p in bbre),
		'bdea': set((p[3], p[1]) for p in bdea),
		'btop': set((p[3], p[1]) for p in btop),
		'bmid': set((p[3], p[1]) for p in bmid),
		'bhit': set((p[3], p[1]) for p in bhit),
		'apow': set((p[3], p[1]) for p in apow),
		'abre': set((p[3], p[1]) for p in abre),
		'adea': set((p[3], p[1]) for p in adea)
	}
	
	# Count each player in the team
	for player in team:
		if len(player) > 3:
			player_id = (player[3], player[1])
			
			# Check which category this player belongs to
			for category, player_set in player_sets.items():
				if player_id in player_set:
					team_composition[category] += 1
					break
	
	# Calculate expected composition from template
	expected_composition = {
		'atop': int(get_template_value(template, 'atop') * scale_factor),
		'amid': int(get_template_value(template, 'amid') * scale_factor),
		'ahit': int(get_template_value(template, 'ahit') * scale_factor),
		'bpow': int(get_template_value(template, 'bpow') * scale_factor),
		'bbre': int(get_template_value(template, 'bbre') * scale_factor),
		'bdea': int(get_template_value(template, 'bdea') * scale_factor),
		'btop': int(get_template_value(template, 'btop') * scale_factor),
		'bmid': int(get_template_value(template, 'bmid') * scale_factor),
		'bhit': int(get_template_value(template, 'bhit') * scale_factor),
		'apow': int(get_template_value(template, 'apow') * scale_factor),
		'abre': int(get_template_value(template, 'abre') * scale_factor),
		'adea': int(get_template_value(template, 'adea') * scale_factor)
	}
	
	# Allow some tolerance (±1) for rounding differences
	tolerance = 1
	for category in team_composition:
		actual = team_composition[category]
		expected = expected_composition[category]
		
		if abs(actual - expected) > tolerance:
			return False
	
	return True

def get_top13_summary(team, top13_names):
	"""Get summary of top 13 players in a team for display"""
	if not top13_names:
		return {"count": 0, "players": [], "valid": True}
		
	top13_in_team = []
	for player in team:
		if len(player) > 3 and player[3] in top13_names:
			top13_in_team.append(player[3])
	
	count = len(top13_in_team)
	return {
		"count": count,
		"players": top13_in_team,
		"valid": True  # All teams are valid regardless of top 13 count
	}

def getTeams(atop,amid,ahit,bpow,bbre,bdea,btop,bmid,bhit,apow,abre,adea,teamA,teamB,winning=None):
	templates=getDreamTeams(winning)
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
	target_teams = 500
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
		for k in range(0,5000):  # Generate 20 teams per template
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
			is_not_duplicate = team not in finalteams
			has_valid_roles = validate_team_roles(team) if has_11_players else False
			
			print(f"Team validation: 11 players={has_11_players}, not duplicate={is_not_duplicate}, valid roles={has_valid_roles}")
			
			# Validate team composition - must have at least 1 of each role
			if has_11_players and is_not_duplicate and has_valid_roles:
					team=sorted(team, key=operator.itemgetter(2))
					count=0
					team_player_ids = [player[7] for player in team[0:11]]
					for x in finalteams:
						# Extract player IDs for comparison instead of full player objects
						x_player_ids = [player[7] for player in x[0:11]]
						l=intersection(x_player_ids, team_player_ids)
						print(x_player_ids)
						print(team_player_ids)
						print("coming here")
						print(l)
						if l > count:
							count=l
					print(count)
					if count <= 8:  # Changed from 7 to 3 for more team diversity
						# Select captain and vice-captain based on category indices - NO FALLBACK
						captain = None
						vice_captain = None
						print("coming here")
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
						break
						total_teams_generated += 1
						print(f"Generated team {total_teams_generated}/{target_teams}")
						
						# Stop if we've reached the target
						# if total_teams_generated >= target_teams:
						# 	break
		teams=calculatePercentage(teams)
		finalteams.extend(teams)
		print(f"Template '{template_name}' generated {len(teams)} teams")
		
		# Stop processing templates if we've reached the target
		# if total_teams_generated >= target_teams:
		# 	print(f"Reached target of {target_teams} teams, stopping template processing")
		# 	break
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

def save_teams_to_file(teams, teamA_name, teamB_name):
	"""Save teams to a file in Dream11 API format"""
	from datetime import datetime
	
	if not teams:
		print("❌ DEBUG: No teams provided to save_teams_to_file")
		return
	
	print(f"🔍 DEBUG: save_teams_to_file called with {len(teams)} teams")
	
	filename = f"dream11_teams_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
	
	try:
		import json
		
		# Get match ID from the current match (if available)
		current_match_id = "YOUR_MATCH_ID"
		try:
			# Try to get match ID from the teams generation context
			if hasattr(request, 'form') and request.form.get('matchid'):
				current_match_id = request.form.get('matchid')
		except:
			pass
		
		# Prepare teams data for JSON
		teams_data = {
			"metadata": {
				"generated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				"match": f"{teamA_name} vs {teamB_name}",
				"total_teams": 0,
				"match_id": current_match_id,
				"auth_token": "YOUR_AUTH_TOKEN"
			},
			"teams": []
		}
		
		valid_teams_count = 0
		
		for i, team in enumerate(teams, 1):
			print(f"🔍 DEBUG: Processing team {i}, length: {len(team)}")
			
			# More flexible team length check
			if len(team) < 11:
				print(f"❌ DEBUG: Team {i} skipped - length {len(team)} < 11 (need at least 11 players)")
				continue
			
			# Extract player IDs with better error handling
			player_ids = []
			for j in range(min(11, len(team))):
				player_id = 0
				try:
					if team[j] and hasattr(team[j], '__len__') and len(team[j]) > 7:
						player_id = team[j][7] if team[j][7] is not None else 0
					elif team[j] and hasattr(team[j], '__getitem__'):
						# Try to get player_id from different possible locations
						if hasattr(team[j], 'get'):
							player_id = team[j].get('player_id', 0) or team[j].get('id', 0)
						else:
							player_id = team[j][7] if len(team[j]) > 7 else 0
				except (IndexError, TypeError, AttributeError) as e:
					print(f"⚠️ DEBUG: Error extracting player ID for team {i}, player {j}: {e}")
					player_id = j + 1000 + (i * 100)  # Generate fallback ID
				
				player_ids.append(int(player_id) if player_id else (j + 1000 + (i * 100)))
			
			print(f"🔍 DEBUG: Team {i} player IDs: {player_ids}")
			
			# Get captain and vice-captain IDs with fallbacks
			captain_id = 0
			vice_captain_id = 0
			
			try:
				if len(team) > 11 and team[11]:
					if hasattr(team[11], '__len__') and len(team[11]) > 7:
						captain_id = team[11][7] if team[11][7] is not None else 0
			except (IndexError, TypeError):
				pass
			
			try:
				if len(team) > 12 and team[12]:
					if hasattr(team[12], '__len__') and len(team[12]) > 7:
						vice_captain_id = team[12][7] if team[12][7] is not None else 0
			except (IndexError, TypeError):
				pass
			
			# Use first two players as captain/vc if not specified
			if not captain_id and player_ids:
				captain_id = player_ids[0]
			if not vice_captain_id and len(player_ids) > 1:
				vice_captain_id = player_ids[1]
			
			# Get template name
			template_name = f"Team {i}"
			try:
				if len(team) > 13 and team[13]:
					template_name = str(team[13])
			except (IndexError, TypeError):
				pass
			
			print(f"🔍 DEBUG: Team {i} - Captain: {captain_id}, VC: {vice_captain_id}, Name: {template_name}")
			
			# Create team object (always create if we have players)
			team_obj = {
				"id": i,
				"name": template_name,
				"captain": int(captain_id) if captain_id else player_ids[0],
				"vice_captain": int(vice_captain_id) if vice_captain_id else player_ids[1],
				"players": player_ids[:11]
			}
			
			teams_data["teams"].append(team_obj)
			valid_teams_count += 1
			print(f"✅ DEBUG: Team {i} added to JSON")
		
		# Update total teams count
		teams_data["metadata"]["total_teams"] = valid_teams_count
		
		print(f"🔍 DEBUG: Final teams_data structure:")
		print(f"   - Total teams processed: {len(teams)}")
		print(f"   - Valid teams: {valid_teams_count}")
		print(f"   - Teams in JSON: {len(teams_data['teams'])}")
		
		# Write JSON file
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(teams_data, f, indent=2, ensure_ascii=False)
		
		print(f"\n📁 Teams saved to: {filename}")
		print(f"💡 Edit the JSON file to add your match_id and auth_token in the metadata section")
		print(f"📊 Total valid teams saved: {valid_teams_count}")
		
	except Exception as e:
		print(f"❌ Error saving teams to JSON file: {e}")
		import traceback
		print(f"🔍 DEBUG: Full error traceback:")
		traceback.print_exc()

def print_teams_for_dream11_api(teams, teamA_name, teamB_name):
	"""Print teams in Dream11 API client format"""
	print("\n" + "="*80)
	print("🏏 TEAMS FOR DREAM11 API CLIENT")
	print("="*80)
	
	if not teams:
		print("❌ No teams to export")
		return
	
	print(f"📊 Total Teams: {len(teams)}")
	print(f"🏆 Match: {teamA_name} vs {teamB_name}")
	print("\n📋 Format for dream11_api_client.py:")
	print("-" * 50)
	
	for i, team in enumerate(teams, 1):
		if len(team) < 13:  # Should have 11 players + captain + vice-captain + template name
			print(f"⚠️ Team {i}: Invalid structure (length: {len(team)})")
			continue
			
		# Extract player IDs from the first 11 players
		player_ids = []
		for j in range(11):
			if j < len(team) and team[j] and hasattr(team[j], '__len__') and len(team[j]) > 7:
				# Player ID is at index 7 (8th element) in player tuple
				player_id = team[j][7] if team[j][7] is not None else 0
				player_ids.append(int(player_id) if player_id else 0)
			else:
				player_ids.append(0)  # Fallback for missing player ID
		
		# Get captain and vice-captain IDs
		captain_id = 0
		vice_captain_id = 0
		
		if len(team) > 11 and team[11]:  # Captain at index 11
			captain_id = team[11][7] if hasattr(team[11], '__len__') and len(team[11]) > 7 and team[11][7] else 0
			
		if len(team) > 12 and team[12]:  # Vice-captain at index 12
			vice_captain_id = team[12][7] if hasattr(team[12], '__len__') and len(team[12]) > 7 and team[12][7] else 0
		
		# Template name
		template_name = team[13] if len(team) > 13 else f"Team {i}"
		
		# Filter out zero IDs
		valid_player_ids = [pid for pid in player_ids if pid != 0]
		
		if len(valid_player_ids) < 11:
			print(f"⚠️ Team {i} ({template_name}): Only {len(valid_player_ids)} valid player IDs")
			continue
		
		print(f"\n# Team {i}: {template_name}")
		print(f"match_id = \"YOUR_MATCH_ID\"")
		print(f"team_id = {i}")
		print(f"captain = {int(captain_id) if captain_id else valid_player_ids[0]}")
		print(f"vice_captain = {int(vice_captain_id) if vice_captain_id else valid_player_ids[1]}")
		print(f"players = {valid_player_ids[:11]}")
		print(f"auth_token = \"YOUR_AUTH_TOKEN\"")
		print(f"")
		print(f"# Call: edit_dream11_team(match_id, team_id, captain, vice_captain, players, auth_token)")
		
		# Show player details for verification
		print(f"# Player Details:")
		for j, player in enumerate(team[:11]):
			if player and hasattr(player, '__len__') and len(player) > 3:
				player_name = player[3] if len(player) > 3 else "Unknown"
				player_team = player[1] if len(player) > 1 else "Unknown"
				player_id = player[7] if len(player) > 7 and player[7] else 0
				print(f"#   {j+1}. {player_name} ({player_team}) - ID: {player_id}")
		
		if i >= 5:  # Show only first 5 teams to avoid too much output
			remaining = len(teams) - 5
			if remaining > 0:
				print(f"\n... and {remaining} more teams")
			break
	
	print("\n" + "="*80)
	print("💡 Copy the team data above and use with dream11_api_client.py")
	print("💡 Replace YOUR_MATCH_ID and YOUR_AUTH_TOKEN with actual values")
	print("="*80)
	
	# Save teams to file for easy copying
	save_teams_to_file(teams, teamA_name, teamB_name)

def calculatePercentage(validcombinations):
	finalteams=[]
	print(f"🔍 CALCULATE PERCENTAGE: Processing {len(validcombinations)} teams with STRICT diversity check")
	
	for i, x in enumerate(validcombinations):
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
		finalteams.append(x)
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


@app.route("/debug_matches")
def debug_matches():
    """Debug route to list all matches"""
    try:
        matches = getMactches()
        return jsonify([dict(match) for match in matches])
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/debug_players/<matchid>")
def debug_players(matchid):
    """Debug route to check player data and match roles"""
    try:
        players = getplayers(matchid)
        teams = getteams(matchid)
        
        debug_info = {
            "match_id": matchid,
            "total_players": len(players),
            "teams": [{"name": team[1], "vs": team[2]} for team in teams] if teams else [],
            "players_by_role": {},
            "players_without_roles": [],
            "all_players": []
        }
        
        # Organize players by match role
        role_counts = {}
        for player in players:
            player_info = {
                "name": player['playername'],
                "team": player['teamname'],
                "role": player['role'],
                "match_role": player.get('matchrole', 'None'),
                "percentage": player.get('percentage', 0)
            }
            debug_info["all_players"].append(player_info)
            
            match_role = player.get('matchrole', 'None')
            if match_role and match_role != 'None':
                if match_role not in debug_info["players_by_role"]:
                    debug_info["players_by_role"][match_role] = []
                debug_info["players_by_role"][match_role].append(player_info)
                role_counts[match_role] = role_counts.get(match_role, 0) + 1
            else:
                debug_info["players_without_roles"].append(player_info)
        
        debug_info["role_counts"] = role_counts
        debug_info["players_without_match_roles"] = len(debug_info["players_without_roles"])
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)