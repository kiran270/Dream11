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
                if teams == {"HAM", "SUR"}:
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
    target_players_list=[['W Jacks', 'B Howell', 'M Santner', 'L Evans', 'D Sibley', 'J Roy', 'J Vince', 'D Worrall', 'S Currie', 'L Pretoriu', 'T Albert', 'W Jacks', 'J Vince'], ['S Curran', 'W Jacks', 'J Fuller', 'M Santner', 'L Evans', 'D Sibley', 'O Sykes', 'J Vince', 'S Currie', 'N Smith', 'T Albert', 'D Sibley', 'J Vince'], ['L Dawson', 'W Jacks', 'M Santner', 'L Evans', 'D Sibley', 'J Roy', 'D Brevis', 'J Vince', 'S Currie', 'N Smith', 'T Albert', 'D Sibley', 'J Vince'], ['S Curran', 'W Jacks', 'J Fuller', 'L Evans', 'D Sibley', 'J Vince', 'D Worrall', 'C Jordan', 'J Turner', 'S Currie', 'T Albert', 'W Jacks', 'J Vince'], ['S Curran', 'M Santner', 'L Evans', 'J Weatherl', 'J Roy', 'O Sykes', 'J Vince', 'S Currie', 'N Smith', 'C Wood', 'L Pretoriu', 'L Pretoriu', 'J Roy'], ['L Dawson', 'B Howell', 'L Evans', 'D Sibley', 'J Roy', 'O Sykes', 'J Vince', 'C Jordan', 'S Currie', 'N Smith', 'T Albert', 'J Vince', 'S Currie'], ['W Jacks', 'J Fuller', 'M Santner', 'L Evans', 'J Roy', 'O Sykes', 'D Brevis', 'J Vince', 'D Worrall', 'S Currie', 'T Albert', 'J Vince', 'S Currie'], ['S Curran', 'W Jacks', 'L Evans', 'J Weatherl', 'O Sykes', 'D Brevis', 'J Vince', 'C Jordan', 'J Turner', 'S Currie', 'N Smith', 'J Vince', 'S Currie'], ['S Curran', 'W Jacks', 'J Fuller', 'L Evans', 'D Sibley', 'O Sykes', 'J Vince', 'C Jordan', 'S Currie', 'N Smith', 'T Albert', 'W Jacks', 'J Vince'], ['W Jacks', 'M Santner', 'L Evans', 'D Sibley', 'J Roy', 'O Sykes', 'J Vince', 'D Worrall', 'S Currie', 'N Smith', 'T Albert', 'W Jacks', 'J Vince'], ['W Jacks', 'B Howell', 'M Santner', 'L Evans', 'D Sibley', 'J Roy', 'O Sykes', 'J Vince', 'S Currie', 'N Smith', 'T Albert', 'D Sibley', 'J Vince'], ['S Curran', 'L Evans', 'J Roy', 'O Sykes', 'D Brevis', 'J Vince', 'J Turner', 'S Currie', 'C Wood', 'L Pretoriu', 'T Albert', 'J Vince', 'J Roy'], ['B Howell', 'L Evans', 'J Roy', 'O Sykes', 'D Brevis', 'J Vince', 'C Jordan', 'J Turner', 'S Currie', 'C Wood', 'L Pretoriu', 'J Vince', 'L Evans'], ['S Curran', 'B Howell', 'J Fuller', 'M Santner', 'L Evans', 'D Sibley', 'J Vince', 'J Turner', 'S Currie', 'C Wood', 'T Albert', 'J Vince', 'S Currie'], ['W Jacks', 'J Fuller', 'L Evans', 'J Weatherl', 'J Roy', 'D Brevis', 'J Vince', 'C Jordan', 'J Turner', 'S Currie', 'C Wood', 'J Vince', 'S Currie'], ['L Dawson', 'L Evans', 'D Sibley', 'J Roy', 'O Sykes', 'D Brevis', 'J Vince', 'C Jordan', 'S Currie', 'N Smith', 'C Wood', 'J Vince', 'S Currie'], ['S Curran', 'W Jacks', 'B Howell', 'J Fuller', 'L Evans', 'O Sykes', 'J Vince', 'C Jordan', 'J Turner', 'S Currie', 'N Smith', 'J Vince', 'S Currie']]
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