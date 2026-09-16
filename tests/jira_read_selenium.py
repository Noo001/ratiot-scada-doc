# -*- coding: utf-8 -*-
"""Чтение тикета Jira через реальный Firefox (Selenium) с копией профиля."""
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

PROFILE = "C:/Users/Andrey/AppData/Local/Temp/ff_profile"
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)

url = sys.argv[1] if len(sys.argv) > 1 else "https://tibbotech.atlassian.net/servicedesk/customer/portal/1/ASD-6480"
name = sys.argv[2] if len(sys.argv) > 2 else "jira_test"

opts = Options()
opts.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
opts.add_argument("-headless")
opts.profile = PROFILE

driver = webdriver.Firefox(options=opts)
try:
    print("Открываем:", url)
    driver.get(url)
    time.sleep(15)
    print("URL после загрузки:", driver.current_url)
    text = driver.find_element("tag name", "body").text
    print("=== TEXT START ===")
    print(text[:4000])
    print("=== TEXT END ===")
    driver.save_full_page_screenshot(str(SHOTS / f"{name}.png"))
    print("Скриншот:", SHOTS / f"{name}.png")
finally:
    driver.quit()
