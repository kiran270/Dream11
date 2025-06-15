from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure Chrome driver with options
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the website
driver.get("https://www.teamgeneration.in/")
time.sleep(5)  # Let the page load

# Wait and click on the match card
try:
    card = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "card-middle"))
    )
    card.click()
    print("✅ Clicked on the match card successfully.")
except Exception as e:
    print("❌ Failed to click the match card:", str(e))

# Optional: wait to observe post-click page or scrape next content
time.sleep(5)

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
time.sleep(5)

target_team_1 = "IRE"
target_team_2 = "WI"

# Find all match cards
cards = driver.find_elements(By.CLASS_NAME, "card-middle")

clicked = False

for card in cards:
    try:
        left_team = card.find_element(By.CLASS_NAME, "left-team-name").text.strip()
        right_team = card.find_element(By.CLASS_NAME, "right-team-name").text.strip()

        if ({left_team, right_team} == {target_team_1, target_team_2}):
            card.click()
            print(f"✅ Clicked on match: {left_team} vs {right_team}")
            clicked = True
            break
    except Exception as e:
        print(f"❌ Error processing a card: {e}")

if not clicked:
    print("❌ Match not found.")

time.sleep(10)
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "nav.top-nav .role.sport-icon"))
)

tab_elements = driver.find_elements(By.CSS_SELECTOR, "nav.top-nav .role.sport-icon")

all_players = []

for tab in tab_elements:
    try:
        role = tab.text.strip().split("(")[0]  # Get WK, BAT, AL, BOWL

        # Click tab via JavaScript to ensure compatibility
        driver.execute_script("arguments[0].click();", tab)
        print(f"📌 Clicked tab: {role}")
        time.sleep(2)

        player_containers = driver.find_elements(By.CLASS_NAME, "player-container")

        for container in player_containers:
            try:
                name = container.find_element(By.CSS_SELECTOR, ".bobby-name span").text.strip()
                selected_by = container.find_element(By.CLASS_NAME, "bobby-percentage").text.strip()
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

match_id = 4  # Replace with your match ID
default_matchrole = "MID-HIT"  # or customize per player

for p in all_players:
    name = p['name'].replace("'", "''")  # Escape single quotes
    team = p['team']
    role = p['role']
    credits = p['credits'].replace(" Cr", "").strip()
    try:
        percentage = float(p['selected_by'].replace("Sel by", "").replace("%", "").strip())
    except:
        percentage = 0

    sql = f"""INSERT INTO "main"."player" 
("matchid", "teamname", "role", "playername", "credits", "percentage", "matchrole") 
VALUES ({match_id}, '{team}', '{role}', '{name}', '{credits}', {percentage}, '{default_matchrole}');"""

    print(sql)

driver.quit()

