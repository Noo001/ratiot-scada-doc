# -*- coding: utf-8 -*-
"""Чтение тикета Jira через Firefox-профиль пользователя (копия)."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = "C:/Users/Andrey/AppData/Local/Temp/ff_profile_win"
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)

url = sys.argv[1] if len(sys.argv) > 1 else "https://tibbotech.atlassian.net/servicedesk/customer/portal/1/ASD-6480"
name = sys.argv[2] if len(sys.argv) > 2 else "jira_test"

with sync_playwright() as p:
    ctx = p.firefox.launch_persistent_context(
        PROFILE, headless=True,
        viewport={"width": 1600, "height": 1000},
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    print("Открываем:", url)
    page.goto(url, timeout=90000)
    page.wait_for_load_state("load", timeout=90000)
    time.sleep(12)
    print("URL после загрузки:", page.url)
    text = page.locator("body").inner_text()
    print("=== TEXT START ===")
    print(text[:4000])
    print("=== TEXT END ===")
    page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)
    print("Скриншот:", SHOTS / f"{name}.png")
    ctx.close()
