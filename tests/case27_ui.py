#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 27 (ASD-6505): пользовательский путь — Server Information → Лицензионная информация."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)

    # Клик по корневому узлу сервера в дереве
    page.locator("text=RatioT Server v6.41.11").first.click()
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case27_64111_server_info.png"))
    print("body:", page.locator("body").inner_text()[:200].replace("\n", " | "))

    lic = page.locator("text=Лицензионная информация").first
    print("Вкладка лицензии:", lic.count() > 0)
    if lic.count() > 0:
        lic.click()
        time.sleep(4)
        page.screenshot(path=str(OUT_DIR / "case27_64111_license_tab.png"))
        body = page.locator("body").inner_text()
        i = body.find("Лицензионная информация")
        print("лицензия:", body[i:i+250].replace("\n", " | "))
    browser.close()
    print("Готово.")
