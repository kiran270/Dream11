from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from db import addPlayer

# Config
target_team_1 = "MCI"
target_team_2 = "WYD"
match_id = 13
default_matchrole = "MID-HIT"

# Launch Chrome
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.teamgeneration.in/")
time.sleep(5)

# Step 1: Click login card
try:
    card = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "card-middle"))
    )
    card.click()
    print("✅ Clicked on the match card successfully.")
except Exception as e:
    print("❌ Failed to click match card:", str(e))

time.sleep(5)

# Step 2: Login
try:
    driver.find_element(By.ID, "exampleInputEmail1").send_keys("8142848270")
    driver.find_element(By.ID, "exampleInputPassword1").send_keys("@Aug2022")
    driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
    print("✅ Login submitted.")
except Exception as e:
    print("❌ Login failed:", str(e))

time.sleep(5)

# Step 3: Click Football Tab
try:
    football_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='sport-icon']//span[text()='Football']"))
    )
    driver.execute_script("arguments[0].click();", football_tab)
    print("⚽ Football tab clicked.")
except Exception as e:
    print(f"❌ Failed to click Football tab: {e}")

# Step 4: Click correct match card
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "card-middle"))
    )
    match_cards = driver.find_elements(By.CLASS_NAME, "card-middle")
    for card in match_cards:
        left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
        right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()
        if left_team == target_team_1 and right_team == target_team_2:
            driver.execute_script("arguments[0].click();", card)
            print(f"✅ Clicked on match: {left_team} vs {right_team}")
            break
    else:
        print("❌ Match not found.")
except Exception as e:
    print(f"❌ Error finding match: {e}")

time.sleep(10)

# Step 5: Scrape players from all role tabs
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
)
tab_elements = driver.find_elements(By.CSS_SELECTOR, "nav.top-nav .role.sport-icon")

all_players = []

for tab in tab_elements:
    try:
        role = tab.text.strip().split("(")[0]
        driver.execute_script("arguments[0].click();", tab)
        print(f"📌 Clicked tab: {role}")
        time.sleep(2)

        # Scroll to load all players
        SCROLL_PAUSE_TIME = 1.5
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        player_containers = driver.find_elements(By.CLASS_NAME, "player-container")
        for container in player_containers:
            try:
                status_texts = container.find_elements(By.CLASS_NAME, "bobby-percentage")
                if not any("Playing" in s.text for s in status_texts):
                    continue  # Only "Playing" players

                name = container.find_element(By.CSS_SELECTOR, ".bobby-name span").text.strip()
                selected_by = status_texts[0].text.strip()
                team = container.find_element(By.CLASS_NAME, "p-team").text.strip()
                credits = container.find_elements(By.CLASS_NAME, "player-item-two")[1].text.strip()

                all_players.append({
                    "name": name,
                    "team": team,
                    "selected_by": selected_by,
                    "credits": credits,
                    "role": role
                })
            except Exception as e:
                print(f"⚠️ Skipped a player due to error: {e}")
    except Exception as e:
        print(f"❌ Could not process tab: {e}")

# Step 6: Store in DB
for p in all_players:
    name = p['name'].replace("'", "''")
    team = p['team']
    role = p['role']
    credits = p['credits'].replace(" Cr", "").strip()
    try:
        percentage = float(p['selected_by'].replace("Sel by", "").replace("%", "").strip())
    except:
        percentage = 0
    print(f"✅ Adding {name} ({team})")
    # addPlayer(match_id, team, role, name, credits, percentage, default_matchrole)

driver.quit()
