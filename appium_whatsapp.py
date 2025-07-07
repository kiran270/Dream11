from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Desired Capabilities
desired_caps = {
    "platformName": "Android",
    "deviceName": "Android",
    "automationName": "UiAutomator2",
    "appPackage": "com.app.dream11Pro",
    "appActivity": "com.app.dream11.dream11.ReactHomeActivity",
    "noReset": True,
    "ignoreHiddenApiPolicyError": True
}

# Start the Appium driver
options = UiAutomator2Options().load_capabilities(desired_caps)
driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 30)

print("✅ Dream11 app launched.")

# Wait and click the first match card (adjust XPath as per your UI)
print(driver.page_source)
# match_card = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[contains(@text, "ICW-W")]')))
# match_card.click()
# print("✅ Match selected.")

# # Click on Create Team
# create_team_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@text="Create Team"]')))
# create_team_btn.click()
# print("✅ Create Team screen opened.")

# # Select 1 WK
# for _ in range(1):
#     try:
#         wk = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[contains(@text, "WK")]/following-sibling::android.view.ViewGroup')))
#         wk.click()
#         print("✅ WK selected")
#     except:
#         print("❌ No WK found")

# # Select 4 BAT
# for i in range(4):
#     try:
#         bat = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[contains(@text, "BAT")]/following-sibling::android.view.ViewGroup')))
#         bat.click()
#         print(f"✅ BAT {i+1} selected")
#     except:
#         print(f"❌ BAT {i+1} not found")

# # Select 3 ALL
# for i in range(3):
#     try:
#         allr = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[contains(@text, "ALL")]/following-sibling::android.view.ViewGroup')))
#         allr.click()
#         print(f"✅ ALL {i+1} selected")
#     except:
#         print(f"❌ ALL {i+1} not found")

# # Select 3 BOWL
# for i in range(3):
#     try:
#         bowl = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[contains(@text, "BOWL")]/following-sibling::android.view.ViewGroup')))
#         bowl.click()
#         print(f"✅ BOWL {i+1} selected")
#     except:
#         print(f"❌ BOWL {i+1} not found")

# # Click Continue
# try:
#     continue_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[contains(@text, "Continue")]')))
#     continue_btn.click()
#     print("✅ Team creation continued")
# except:
#     print("❌ Continue button not found")

# # Finish
driver.quit()
print("✅ Script finished.")