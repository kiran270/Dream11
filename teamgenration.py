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

driver.quit()
