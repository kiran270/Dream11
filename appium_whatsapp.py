from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

# Desired Capabilities
desired_caps = {
    "platformName": "Android",
    "deviceName": "Android Device",  # Or your specific device name shown in `adb devices`
    "appPackage": "com.whatsapp",
    "appActivity": "com.whatsapp.HomeActivity",
    "automationName": "UiAutomator2",
    "noReset": True  # So it doesn't log you out
}

# Create options instance
options = UiAutomator2Options().load_capabilities(desired_caps)

# Start driver
driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)

# Wait for WhatsApp to open
time.sleep(5)

# Example: Go back to home
driver.press_keycode(3)  # Android keycode for Home button

driver.quit()
