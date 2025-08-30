from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from flask import * 
from db import addMatch,addPlayer



def extract_player_id_from_image_url(image_url):
    """
    Extract player ID from Dream11 image URL
    
    Common Dream11 image URL patterns:
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
    
    # Pattern 3: New Dream11 format - /player-images/.../XXXXX.png (flexible path depth)
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



# Configure Chrome driver with options
# ⚠️ IMPORTANT: Update these team names to match the exact names shown on Dream11 website
target_team_1 = "TRT-W"  # Update this to match first team name on Dream11
target_team_2 = "BPH-W"  # Update this to match second team name on Dream11
match_id = 70  # Replace with your match ID (from the log above)
run=1
default_matchrole = "MID-HIT"  # or customize per player

# 💡 If match is not found, run the script once to see available matches,
# then update target_team_1 and target_team_2 with the correct names

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
options.add_argument("--disable-images")
# JavaScript is needed for the site to work
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Add DNS settings
options.add_argument("--host-resolver-rules=MAP team-generation.netlify.app 13.215.239.219")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--ignore-certificate-errors-spki-list")

# Test network connectivity first
import requests
try:
    print("🌐 Testing network connectivity...")
    response = requests.get("https://team-generation.netlify.app/", timeout=10)
    print(f"✅ Website is accessible (Status: {response.status_code})")
except requests.exceptions.RequestException as e:
    print(f"❌ Network connectivity issue: {e}")
    print("💡 Possible solutions:")
    print("   1. Check your internet connection")
    print("   2. Try using a VPN if the site is blocked")
    print("   3. Check if the website is down: https://downforeveryoneorjustme.com/team-generation.netlify.app")
    exit(1)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("🔗 Navigating to team-generation.netlify.app...")
    driver.get("https://team-generation.netlify.app/")
    time.sleep(30)
    print(f"✅ Successfully loaded page: {driver.title}")
except Exception as e:
    print(f"❌ HTTPS failed: {e}")
    print("💡 Trying HTTP instead...")
    
    try:
        driver.get("http://team-generation.netlify.app/")
        time.sleep(3)
        print(f"✅ Successfully loaded with HTTP: {driver.title}")
    except Exception as e2:
        print(f"❌ HTTP also failed: {e2}")
        print("💡 Trying with fresh Chrome instance...")
        
        # Try completely fresh Chrome instance
        driver.quit()
        
        # Minimal options
        minimal_options = Options()
        minimal_options.add_argument("--no-sandbox")
        minimal_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=minimal_options)
        
        try:
            driver.get("http://team-generation.netlify.app/")
            time.sleep(5)
            print(f"✅ Successfully loaded with minimal options: {driver.title}")
        except Exception as e3:
            print(f"❌ All attempts failed: {e3}")
            print("\n🔧 Troubleshooting steps:")
            print("   1. Check if Chrome is updated")
            print("   2. Try running with sudo: sudo python3 teamgenration.py")
            print("   3. Disable antivirus/firewall temporarily")
            print("   4. Try from a different network")
            driver.quit()
            exit(1)
time.sleep(2)
try:
    card = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "card-middle"))
    )
    card.click()
    print("✅ Clicked on the match card successfully.")
except Exception as e:
    print("❌ Failed to click the match card:", str(e))
time.sleep(2)

try:
    # Fill phone number
    phone_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "exampleInputEmail1"))
    )
    phone_input.send_keys("8142848270")  # Replace with your phone number

    # Fill password
    password_input = driver.find_element(By.ID, "exampleInputPassword1")
    password_input.send_keys("@Aug2022")  # Replace with your password

    # Click Login button
    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    login_button.click()
    print("✅ Login submitted.")

except Exception as e:
    print("❌ Login failed:", str(e))

# Wait for post-login page load (adjust if needed)
time.sleep(10)

# Check if login was successful
if "login" in driver.current_url.lower():
    print("⚠️ Still on login page, trying to navigate to main page...")
    try:
        driver.get("https://team-generation.netlify.app/")
        time.sleep(5)
        print("🔄 Navigated back to main page")
    except Exception as e:
        print(f"❌ Failed to navigate to main page: {e}")

# Wait a bit more for dynamic content
time.sleep(5)

# Debug: Check current page
print(f"🔍 Current URL: {driver.current_url}")
print(f"🔍 Page title: {driver.title}")

# Find all match cards
cards = driver.find_elements(By.CLASS_NAME, "card-middle")

# If no cards found, try alternative methods
if len(cards) == 0:
    print("⚠️ No cards found with 'card-middle' class, trying alternatives...")
    
    # Try different selectors
    alt_selectors = [
        ".match-card",
        "[class*='card']",
        "[class*='match']",
        ".card",
        ".contest-card"
    ]
    
    for selector in alt_selectors:
        alt_cards = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"🔍 Selector '{selector}': {len(alt_cards)} elements")
        if len(alt_cards) > 0:
            cards = alt_cards
            break
    
    # Check if we need to navigate somewhere
    if len(cards) == 0:
        # Look for navigation links or buttons
        nav_links = driver.find_elements(By.TAG_NAME, "a")
        for link in nav_links[:10]:  # Check first 10 links
            link_text = link.text.strip().lower()
            if any(word in link_text for word in ['contest', 'match', 'game', 'play']):
                print(f"🔗 Found navigation link: {link.text} -> {link.get_attribute('href')}")

clicked = False

print(f"🔍 Looking for match: {target_team_1} vs {target_team_2}")
print(f"📋 Found {len(cards)} match cards on the page")

for i, card in enumerate(cards, 1):
    try:
        left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
        right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()
        
        print(f"   Card {i}: {left_team} vs {right_team}")
        
        # Try exact match first
        if ({left_team, right_team} == {target_team_1, target_team_2}):
            print(f"🎯 Found matching card: {left_team} vs {right_team}")
            
            # Try multiple click strategies
            try:
                # Strategy 1: Direct click on card
                driver.execute_script("arguments[0].click();", card)
                print(f"✅ Clicked on match (JavaScript): {left_team} vs {right_team}")
                clicked = True
                break
            except Exception as e1:
                print(f"⚠️ JavaScript click failed: {e1}")
                
                try:
                    # Strategy 2: Click on the card-middle element specifically
                    card_middle = card.find_element(By.CLASS_NAME, "card-middle")
                    driver.execute_script("arguments[0].click();", card_middle)
                    print(f"✅ Clicked on match (card-middle): {left_team} vs {right_team}")
                    clicked = True
                    break
                except Exception as e2:
                    print(f"⚠️ Card-middle click failed: {e2}")
                    
                    try:
                        # Strategy 3: Regular click with wait
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(card))
                        card.click()
                        print(f"✅ Clicked on match (wait+click): {left_team} vs {right_team}")
                        clicked = True
                        break
                    except Exception as e3:
                        print(f"⚠️ Wait+click failed: {e3}")
                        
                        try:
                            # Strategy 4: Scroll to element and click
                            driver.execute_script("arguments[0].scrollIntoView(true);", card)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", card)
                            print(f"✅ Clicked on match (scroll+click): {left_team} vs {right_team}")
                            clicked = True
                            break
                        except Exception as e4:
                            print(f"❌ All click strategies failed: {e4}")
        
        # Try partial match (in case of abbreviations)
        elif (target_team_1.upper() in left_team.upper() and target_team_2.upper() in right_team.upper()) or \
             (target_team_2.upper() in left_team.upper() and target_team_1.upper() in right_team.upper()):
            print(f"🎯 Found partial matching card: {left_team} vs {right_team}")
            
            try:
                driver.execute_script("arguments[0].click();", card)
                print(f"✅ Clicked on match (partial): {left_team} vs {right_team}")
                clicked = True
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
    
    print(f"\n🔧 To fix this issue:")
    print(f"   1. Update the team names in teamgenration.py:")
    print(f"      target_team_1 = \"EXACT_TEAM_NAME_FROM_ABOVE\"")
    print(f"      target_team_2 = \"EXACT_TEAM_NAME_FROM_ABOVE\"")
    print(f"   2. Or run: python check_available_matches.py")
    print(f"   3. Current search: {target_team_1} vs {target_team_2}")
    
    # Don't continue if match not found
    driver.quit()
    exit(1)

# Wait longer after clicking to ensure page loads
time.sleep(5)
print("⏳ Waiting for page to load after match selection...")

# Wait for the player tabs to load
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
    )
    print("✅ Player tabs loaded successfully")
except Exception as e:
    print(f"❌ Player tabs not found: {e}")
    print("🔍 Checking current page URL:", driver.current_url)
    print("🔍 Page title:", driver.title)
    
    # Check if we're back on login page
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
                    
                    if ({left_team, right_team} == {target_team_1, target_team_2}):
                        print(f"🎯 Re-found matching card: {left_team} vs {right_team}")
                        driver.execute_script("arguments[0].click();", card)
                        print(f"✅ Re-clicked on match: {left_team} vs {right_team}")
                        time.sleep(5)
                        break
                except:
                    continue
            
            # Try to find tabs again
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
                )
                print("✅ Player tabs loaded after re-login")
            except:
                print("❌ Still no player tabs after re-login")
                driver.quit()
                exit(1)
                
        except Exception as e3:
            print(f"❌ Re-login failed: {e3}")
            driver.quit()
            exit(1)
    else:
        # Try alternative selectors
        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, ".role")
            if tabs:
                print(f"✅ Found {len(tabs)} tabs with alternative selector")
            else:
                print("❌ No tabs found with alternative selector either")
                driver.quit()
                exit(1)
        except Exception as e2:
            print(f"❌ Alternative selector also failed: {e2}")
            driver.quit()
            exit(1)

tab_elements = driver.find_elements(By.CSS_SELECTOR, "nav.top-nav .role.sport-icon")

all_players = []

for tab in tab_elements:
    try:
        role = tab.text.strip().split("(")[0]  # Get WK, BAT, AL, BOWL

        # Click tab via JavaScript to ensure compatibility
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
                try:
                    # Look for player image element
                    img_element = container.find_element(By.CSS_SELECTOR, "img")
                    image_url = img_element.get_attribute("src")
                    player_id = extract_player_id_from_image_url(image_url)
                    
                    if player_id:
                        print(f"✅ Extracted Player ID {player_id} for {name}")
                    else:
                        print(f"⚠️ Could not extract Player ID for {name} from URL: {image_url}")
                        
                except Exception as img_error:
                    print(f"⚠️ Could not find image for {name}: {img_error}")

                all_players.append({
                    "name": name,
                    "team": team,
                    "selected_by": selected_by,
                    "credits": credits,
                    "role": role,
                    "player_id": player_id,
                    "image_url": image_url if 'image_url' in locals() else None
                })
            except Exception as e:
                print(f"⚠️ Skipped a player due to error: {e}")

    except Exception as e:
        print(f"❌ Could not process tab: {e}")
for p in all_players:
    name = p['name'].replace("'", "''")  # Escape single quotes
    team = p['team']
    role = p['role']
    credits = p['credits'].replace(" Cr", "").strip()
    player_id = p.get('player_id')
    image_url = p.get('image_url', '')
    
    try:
        percentage = float(p['selected_by'].replace("Sel by", "").replace("%", "").strip())
    except:
        percentage = 0
    
    # Print player info with ID
    print(f"💾 Saving: {name} (ID: {player_id}) - {team} - {role} - {percentage}%")
    
    addPlayer(match_id,team,role,name,credits,percentage,default_matchrole,player_id)
    


# Print summary
print(f"\n📊 EXTRACTION SUMMARY:")
print(f"👥 Total players extracted: {len(all_players)}")
players_with_ids = [p for p in all_players if p.get('player_id')]
print(f"🆔 Players with IDs: {len(players_with_ids)}")
print(f"❓ Players without IDs: {len(all_players) - len(players_with_ids)}")

if players_with_ids:
    print(f"\n✅ Sample players with IDs:")
    for player in players_with_ids[:5]:
        print(f"  {player['name']} (ID: {player['player_id']}) - {player['team']} - {player['role']}")



# all_players_sorted = sorted(all_players, key=lambda p: float(p['selected_by'].replace("Sel by", "").replace("%", "").strip() or 0), reverse=True)
# teams=[]
# team1=
driver.quit()

