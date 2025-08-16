from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# List of tournament URLs
base_urls = [
    "https://www.oddsportal2.com/cricket/world/twenty20-international-women/results/"
    # "https://www.oddsportal2.com/cricket/india/ipl/results/"
    # "https://www.oddsportal2.com/cricket/india/ipl-2024/results/"
    # "https://www.oddsportal2.com/cricket/world/twenty20-international/results/"
    # "https://www.oddsportal2.com/cricket/world/twenty20-international-2024/results/",
    # "https://www.oddsportal2.com/cricket/world/twenty20-international-2023/results/",
    # "https://www.oddsportal2.com/cricket/world/twenty20-international-2022/results/",
    # "https://www.oddsportal2.com/cricket/world/twenty20-international-2021/results/",
    # "https://www.oddsportal2.com/cricket/world/twenty20-international-2020/results/",
]

all_data = []

for base_url in base_urls:
    page_num = 1
    while page_num <= 3:
        url = f"{base_url}/#/page/{page_num}/"
        print(f"📄 Fetching: {url}")
        driver.get(url)
        time.sleep(4)

        # Scroll to load all data on the page
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        matches = soup.select("div[data-testid='game-row']")

        if not matches:
            print(f"🚫 No matches found on page {page_num}. Stopping.")
            break  # No more data

        for match in matches:
            try:
                time_tag = match.select_one("div[data-testid='time-item'] p")
                time_text = time_tag.text.strip() if time_tag else ''

                teams = match.select("p.participant-name")
                team1 = teams[0].text.strip() if len(teams) > 0 else ''
                team2 = teams[1].text.strip() if len(teams) > 1 else ''

                result_text = match.select_one("span.font-bold")
                result = result_text.text.strip() if result_text else ''

                odds = match.select("p[data-testid^='odd-container']")
                odd1 = odds[0].text.strip() if len(odds) > 0 else ''
                odd2 = odds[1].text.strip() if len(odds) > 1 else ''

                if odd1 and odd2:
                    all_data.append({
                        "Tournament": base_url.split("/")[-3].capitalize(),
                        "Time": time_text,
                        "Team1": team1,
                        "Team2": team2,
                        "Result": result,
                        "Odds1": odd1,
                        "Odds2": odd2
                    })

            except Exception as e:
                print(f"⚠️ Error parsing match: {e}")

        page_num += 1  # Go to next page

driver.quit()

# Convert to DataFrame
df = pd.DataFrame(all_data).drop_duplicates()

# Clean result
df["Clean_Result"] = df["Result"].str.replace(r"won.*", "", regex=True).str.strip()

# Profit calculation
def calculate_profit(row):
    try:
        odds1 = float(row["Odds1"])
        odds2 = float(row["Odds2"])
        team1 = row["Team1"]
        team2 = row["Team2"]
        winner = row["Clean_Result"]

        if "tie" in row["Result"].lower() or "no result" in row["Result"].lower() or "Match abandoned without a ball bowled." in row["Result"]:
            return 0

        selected_team = team1 if odds1 < odds2 else team2
        selected_odds = min(odds1, odds2)
        return selected_odds * 1000 - 1000 if selected_team == winner else -1000
    except:
        return 0
# Profit if betting on home team (Team1) always
def profit_bet_home(row):
    try:
        if "tie" in row["Result"].lower() or "no result" in row["Result"].lower() or "abandoned" in row["Result"].lower():
            return 0
        odds1 = float(row["Odds1"])
        return odds1 * 1000 - 1000 if row["Clean_Result"] == row["Team1"] else -1000
    except:
        return 0

df["Profit_Loss_Fav"] = df.apply(calculate_profit, axis=1)
df["Profit_Loss_Home"] = df.apply(profit_bet_home, axis=1)


# Home/Away win counts
home_wins = (df["Clean_Result"] == df["Team1"]).sum()
away_wins = (df["Clean_Result"] == df["Team2"]).sum()
Profit_Loss_Fav = df["Profit_Loss_Fav"].sum()
Profit_Loss_Home = df["Profit_Loss_Home"].sum()
# Summary row
summary_row = pd.DataFrame([{
    "Tournament": "TOTAL",
    "Time": "",
    "Team1": f"Home Wins: {home_wins}",
    "Team2": f"Away Wins: {away_wins}",
    "Result": "",
    "Odds1": "",
    "Odds2": "",
    "Clean_Result": "",
    "Profit_Loss_Fav": Profit_Loss_Fav,
    "Profit_Loss_Home": Profit_Loss_Home
}])

df = pd.concat([df, summary_row], ignore_index=True)

# Save
df.to_csv("all_tournaments_results.csv", index=False)
print("✅ Saved to all_tournaments_results.csv")
print(f"🏠 Home Wins: {home_wins}, 🛫 Away Wins: {away_wins}")
print(f"💰 Total Profit/Loss: ₹{Profit_Loss_Fav:.2f}")
print(f"💰 Total Profit/Loss: ₹{Profit_Loss_Home:.2f}")