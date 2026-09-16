# -*- coding: utf-8 -*-
"""Кейс 2: вкладка «Сервер лицензий» в конфигурации сервера."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)
    page.mouse.click(1524, 23)  # шестерёнка
    time.sleep(5)
    page.click("text=Сервер лицензий", timeout=10000)
    time.sleep(8)
    page.screenshot(path=str(OUT / "case2_100t_license_server.png"), full_page=True)
    print(page.locator("body").inner_text()[:3000])
    browser.close()
