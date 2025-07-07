from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip
import concurrent.futures


def scroll_to_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Failed to scroll to element: {e}")


def generate_team_and_copy_link(target_players):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.teamgeneration.in/")
    time.sleep(5)

    def click_continue_button():
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            driver.execute_script("arguments[0].click();", btn)
        except: pass

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "card-middle"))).click()
    except: pass

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "exampleInputEmail1"))).send_keys("8142848270")
        driver.find_element(By.ID, "exampleInputPassword1").send_keys("@Aug2022")
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
    except: pass

    time.sleep(5)

    try:
        for card in driver.find_elements(By.CLASS_NAME, "card-middle"):
            try:
                teams = {card.find_element(By.CLASS_NAME, "left-team-name").text.strip(),
                         card.find_element(By.CLASS_NAME, "right-team-name").text.strip()}
                if teams == {"ENG", "IND"}:
                    card.click()
                    break
            except: pass
    except: pass

    time.sleep(2)
    clicked_names = []
    tabs = driver.find_elements(By.CSS_SELECTOR, "nav.top-nav .role.sport-icon")

    for tab in tabs:
        try:
            driver.execute_script("arguments[0].click();", tab)
            time.sleep(1.5)
            containers = driver.find_elements(By.CLASS_NAME, "player-container")
            for container in containers:
                try:
                    name = container.find_element(By.CSS_SELECTOR, ".bobby-name span").text.strip()
                    if name in target_players and name not in clicked_names:
                        scroll_to_element(driver, container)
                        driver.execute_script("arguments[0].click();", container)
                        clicked_names.append(name)
                        time.sleep(0.4)
                except: pass
        except: pass

    click_continue_button()

    try:
        cont = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='section-card'][.//img[@src='/ag.jpg']]//button[contains(text(),'Continue')]"))
        )
        driver.execute_script("arguments[0].click();", cont)
    except: pass

    click_continue_button()

    def select_captain(name):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "player-container")))
            for container in driver.find_elements(By.CLASS_NAME, "player-container"):
                try:
                    pname = container.find_element(By.CSS_SELECTOR, ".bobby-name span").text.strip()
                    if pname == name:
                        scroll_to_element(driver, container)
                        driver.execute_script("arguments[0].click();", container)
                        return
                except: pass
        except: pass

    select_captain(target_players[11])
    click_continue_button()
    select_captain(target_players[11])
    select_captain(target_players[12])
    click_continue_button()

    try:
        for card in driver.find_elements(By.CLASS_NAME, "partision-card-container"):
            scroll_to_element(driver, card)
            driver.execute_script("arguments[0].click();", card)
            time.sleep(1)
    except: pass

    click_continue_button()

    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Skip This Section']"))
        )
        driver.execute_script("arguments[0].click();", btn)
    except: pass

    click_continue_button()

    combi_cards = driver.find_elements(By.CLASS_NAME, "combination-card-container")
    if not combi_cards:
        try:
            # Switch to "New Combinations" tab
            new_combi_tab = driver.find_element(By.XPATH, "//div[contains(text(), 'New Combinations')]")
            scroll_to_element(driver, new_combi_tab)
            driver.execute_script("arguments[0].click();", new_combi_tab)
            time.sleep(2)
            print("✅ Switched to New Combinations tab")
        except Exception as e:
            print("⚠️ Failed to click 'New Combinations':", e)

    # Now try to click on the combination cards
    try:
        combo_cards = driver.find_elements(By.CLASS_NAME, "combination-card-container")
        for i, card in enumerate(combo_cards, start=1):
            try:
                scroll_to_element(driver, card)
                driver.execute_script("arguments[0].click();", card)
                print(f"✅ Clicked on combination card {i}")
                time.sleep(0.5)
            except Exception as inner_e:
                print(f"⚠️ Could not click on card {i}: {inner_e}")
    except Exception as e:
        print(f"❌ Combination cards not found: {e}")


    click_continue_button()

    try:
        team_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "teamNumber"))
        )
        team_input.clear()
        team_input.send_keys("1")
    except: pass

    try:
        gen_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Teams')]"))
        )
        driver.execute_script("arguments[0].click();", gen_btn)
    except: pass

    try:
        copy_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Copy To Dream11']"))
        )
        scroll_to_element(driver, copy_btn)
        driver.execute_script("arguments[0].click();", copy_btn)
    except: pass

    time.sleep(3)
    try:
        body = driver.find_element(By.TAG_NAME, 'body')
        body.click()
    except: pass

    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Copy Link']"))
        )
        scroll_to_element(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
    except: pass

    time.sleep(2)
    copied_value = pyperclip.paste()
    driver.quit()
    return copied_value


def run_parallel_thread(player_list, idx):
    try:
        link = generate_team_and_copy_link(player_list)
        return f"Team {idx}: {link}"
    except Exception as e:
        return f"Team {idx}: Failed - {e}"


if __name__ == "__main__":
    target_players_list=[['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'Y Jaiswal', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'P Krishna', 'B Duckett', 'Y Jaiswal'], ['R Jadeja', 'B Stokes', 'S Sudharsa', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'B Duckett', 'C Woakes', 'J Bumrah', 'J Smith', 'B Duckett', 'Y Jaiswal'], ['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'Y Jaiswal', 'S Gill', 'H Brook', 'B Duckett', 'B Carse', 'S Bashir', 'P Krishna', 'Z Crawley', 'Y Jaiswal'], ['R Jadeja', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'J Bumrah', 'J Tongue', 'R Pant', 'Z Crawley', 'L Rahul'], ['S Thakur', 'B Stokes', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'S Gill', 'B Duckett', 'S Bashir', 'J Bumrah', 'R Pant', 'J Smith', 'B Duckett', 'Y Jaiswal'], ['B Stokes', 'K Nair', 'S Sudharsa', 'J Root', 'Z Crawley', 'Y Jaiswal', 'B Duckett', 'B Carse', 'J Bumrah', 'J Tongue', 'P Krishna', 'B Duckett', 'Y Jaiswal'], ['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'H Brook', 'L Rahul', 'B Duckett', 'S Bashir', 'J Bumrah', 'R Pant', 'J Smith', 'B Duckett', 'L Rahul'], ['R Jadeja', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'J Bumrah', 'R Pant', 'J Smith', 'B Duckett', 'Y Jaiswal'], ['S Thakur', 'B Stokes', 'K Nair', 'J Root', 'Z Crawley', 'Y Jaiswal', 'H Brook', 'B Duckett', 'B Carse', 'J Tongue', 'P Krishna', 'B Duckett', 'Y Jaiswal'], ['B Stokes', 'S Sudharsa', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'B Duckett', 'C Woakes', 'J Bumrah', 'J Tongue', 'P Krishna', 'B Duckett', 'J Tongue'], ['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'B Duckett', 'S Bashir', 'J Bumrah', 'R Pant', 'J Smith', 'B Duckett', 'S Bashir'], ['R Jadeja', 'K Nair', 'J Root', 'Z Crawley', 'Y Jaiswal', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'J Bumrah', 'R Pant', 'Z Crawley', 'J Root'], ['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'B Duckett', 'S Bashir', 'J Tongue', 'P Krishna', 'R Pant', 'B Duckett', 'J Tongue'], ['B Stokes', 'J Root', 'Y Jaiswal', 'O Pope', 'S Gill', 'H Brook', 'L Rahul', 'B Carse', 'S Bashir', 'J Bumrah', 'M Siraj', 'Y Jaiswal', 'J Root'], ['B Stokes', 'J Root', 'Y Jaiswal', 'S Gill', 'H Brook', 'B Carse', 'S Bashir', 'P Krishna', 'J Bumrah', 'M Siraj', 'J Smith', 'Y Jaiswal', 'J Root'], ['R Jadeja', 'B Stokes', 'S Sudharsa', 'J Root', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'J Bumrah', 'R Pant', 'J Smith', 'L Rahul', 'J Bumrah'], ['S Thakur', 'R Jadeja', 'B Stokes', 'J Root', 'Y Jaiswal', 'S Gill', 'H Brook', 'B Duckett', 'S Bashir', 'R Pant', 'J Smith', 'Y Jaiswal', 'S Thakur'], ['B Stokes', 'S Sudharsa', 'J Root', 'Z Crawley', 'Y Jaiswal', 'H Brook', 'B Carse', 'J Bumrah', 'J Tongue', 'P Krishna', 'R Pant', 'Y Jaiswal', 'P Krishna'], ['R Jadeja', 'O Pope', 'Y Jaiswal', 'S Gill', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'P Krishna', 'J Bumrah', 'J Smith', 'Y Jaiswal', 'J Bumrah'], ['S Thakur', 'R Jadeja', 'B Stokes', 'Y Jaiswal', 'H Brook', 'B Duckett', 'B Carse', 'J Bumrah', 'J Tongue', 'R Pant', 'J Smith', 'Y Jaiswal', 'S Thakur'], ['R Jadeja', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'J Bumrah', 'J Smith', 'B Duckett', 'L Rahul'], ['S Thakur', 'B Stokes', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'S Gill', 'H Brook', 'B Duckett', 'J Tongue', 'M Siraj', 'J Smith', 'B Duckett', 'Y Jaiswal'], ['B Stokes', 'S Sudharsa', 'J Root', 'Z Crawley', 'Y Jaiswal', 'H Brook', 'B Duckett', 'B Carse', 'S Bashir', 'J Bumrah', 'P Krishna', 'B Duckett', 'Y Jaiswal'], ['B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'S Bashir', 'J Bumrah', 'J Smith', 'B Duckett', 'L Rahul'], ['S Thakur', 'B Stokes', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'S Gill', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'J Tongue', 'B Duckett', 'Y Jaiswal'], ['B Stokes', 'J Root', 'Z Crawley', 'Y Jaiswal', 'S Gill', 'B Duckett', 'B Carse', 'J Tongue', 'M Siraj', 'R Pant', 'J Smith', 'Z Crawley', 'Y Jaiswal'], ['B Stokes', 'K Nair', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'J Bumrah', 'J Smith', 'B Duckett', 'L Rahul'], ['R Jadeja', 'B Stokes', 'S Sudharsa', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'J Bumrah', 'B Duckett', 'Y Jaiswal'], ['S Thakur', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'B Carse', 'S Bashir', 'R Pant', 'B Duckett', 'L Rahul'], ['B Stokes', 'K Nair', 'J Root', 'Z Crawley', 'Y Jaiswal', 'S Gill', 'B Duckett', 'B Carse', 'J Tongue', 'P Krishna', 'J Smith', 'B Duckett', 'Y Jaiswal'], ['R Jadeja', 'B Stokes', 'S Sudharsa', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'R Pant', 'B Duckett', 'Y Jaiswal'], ['R Jadeja', 'B Stokes', 'S Sudharsa', 'J Root', 'Z Crawley', 'O Pope', 'H Brook', 'B Duckett', 'S Bashir', 'J Bumrah', 'R Pant', 'B Duckett', 'S Bashir'], ['S Thakur', 'R Jadeja', 'B Stokes', 'J Root', 'Z Crawley', 'Y Jaiswal', 'H Brook', 'B Duckett', 'J Tongue', 'R Pant', 'J Smith', 'B Duckett', 'J Root'], ['B Stokes', 'K Nair', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'B Duckett', 'B Carse', 'C Woakes', 'J Bumrah', 'R Pant', 'B Duckett', 'O Pope'], ['S Thakur', 'R Jadeja', 'B Stokes', 'J Root', 'Z Crawley', 'S Gill', 'H Brook', 'B Duckett', 'C Woakes', 'J Tongue', 'R Pant', 'B Duckett', 'C Woakes'], ['B Stokes', 'J Root', 'Y Jaiswal', 'O Pope', 'S Gill', 'H Brook', 'L Rahul', 'J Bumrah', 'M Siraj', 'P Krishna', 'R Pant', 'Y Jaiswal', 'O Pope'], ['R Jadeja', 'B Stokes', 'J Root', 'Y Jaiswal', 'S Gill', 'H Brook', 'L Rahul', 'B Carse', 'J Bumrah', 'M Siraj', 'P Krishna', 'Y Jaiswal', 'J Root'], ['S Thakur', 'R Jadeja', 'B Stokes', 'J Root', 'S Gill', 'H Brook', 'L Rahul', 'B Duckett', 'J Bumrah', 'M Siraj', 'R Pant', 'L Rahul', 'J Bumrah'], ['R Jadeja', 'K Nair', 'Y Jaiswal', 'O Pope', 'S Gill', 'H Brook', 'B Duckett', 'B Carse', 'J Bumrah', 'M Siraj', 'P Krishna', 'Y Jaiswal', 'J Bumrah'], ['S Thakur', 'B Stokes', 'S Sudharsa', 'J Root', 'Z Crawley', 'Y Jaiswal', 'B Carse', 'J Bumrah', 'M Siraj', 'P Krishna', 'R Pant', 'Y Jaiswal', 'J Bumrah'], ['B Stokes', 'J Root', 'H Brook', 'L Rahul', 'B Duckett', 'C Woakes', 'P Krishna', 'J Bumrah', 'M Siraj', 'R Pant', 'J Smith', 'L Rahul', 'J Bumrah'], ['R Jadeja', 'B Stokes', 'Z Crawley', 'Y Jaiswal', 'O Pope', 'H Brook', 'J Bumrah', 'J Tongue', 'M Siraj', 'R Pant', 'J Smith', 'Y Jaiswal', 'J Bumrah'], ['S Thakur', 'R Jadeja', 'B Stokes', 'J Root', 'Y Jaiswal', 'B Duckett', 'B Carse', 'S Bashir', 'J Bumrah', 'P Krishna', 'J Smith', 'Y Jaiswal', 'J Bumrah']]
    seen_links = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(run_parallel_thread, player_list, idx)
            for idx, player_list in enumerate(target_players_list, start=1)
        ]
        with open("dream11_links_SAM_HUR.txt", "w") as file:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.startswith("Team") and ": http" in result:
                    link = result.split(": http", 1)[1].strip()
                    if link not in seen_links:
                        seen_links.add(link)
                        file.write(result + "\n")
                        print("✅", result)
                    else:
                        print("⚠️ Duplicate skipped:", result)
                else:
                    # In case of failure messages
                    file.write(result + "\n")
                    print("❌", result)