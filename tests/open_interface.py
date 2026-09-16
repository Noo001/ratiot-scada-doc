# -*- coding: utf-8 -*-
"""Вход в веб-интерфейс RatioT SCADA открытым браузером (headed), окно остаётся открытым."""
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
    page = ctx.new_page()

    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    time.sleep(12)
    print("URL после логина:", page.url)
    print("Заголовок:", page.title())

    # Держим браузер открытым 2 часа
    print("Браузер открыт. Окно можно использовать.")
    time.sleep(7200)
