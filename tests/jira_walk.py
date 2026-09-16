# -*- coding: utf-8 -*-
"""Обход тикетов Jira через реальный Firefox с профилем пользователя (headed)."""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

PROFILE = r"C:\Users\Andrey\AppData\Roaming\Mozilla\Firefox\Profiles\muinccr9.default-release"
OUT = Path(__file__).parent / "screenshots" / "jira"
OUT.mkdir(parents=True, exist_ok=True)

TICKETS = """ASD-6392 ASD-6406 ASD-6418 ASD-6455 ASD-6474 ASD-6475 ASD-6476 ASD-6477 ASD-6478 ASD-6479
ASD-6480 ASD-6481 ASD-6482 ASD-6483 ASD-6484 ASD-6485 ASD-6486 ASD-6487 ASD-6496 ASD-6497
ASD-6498 ASD-6499 ASD-6500 ASD-6501 ASD-6502 ASD-6503 ASD-6504 ASD-6505 ASD-6521 ASD-6522 ASD-6523""".split()

opts = Options()
opts.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
opts.profile = PROFILE

driver = webdriver.Firefox(options=opts)
try:
    driver.set_window_size(1700, 1000)
    # прогрев: список запросов
    driver.get("https://tibbotech.atlassian.net/servicedesk/customer/user/requests?reporter=all&statuses=open")
    time.sleep(15)
    print("warmup url:", driver.current_url)
    driver.save_screenshot(str(OUT / "warmup.png"))

    for t in TICKETS:
        url = f"https://tibbotech.atlassian.net/servicedesk/customer/portal/1/{t}"
        try:
            driver.get(url)
            time.sleep(10)
            body = driver.find_element("tag name", "body").text
            (OUT / f"{t}.txt").write_text(f"URL: {driver.current_url}\n\n{body}", encoding="utf-8")
            driver.save_screenshot(str(OUT / f"{t}.png"))
            print(t, "ok, url:", driver.current_url, "len:", len(body))
        except Exception as e:
            print(t, "ERROR:", type(e).__name__, str(e)[:120])
finally:
    driver.quit()
    print("done")
