#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 27 (ASD-6505): «Показать информацию о сервере» → вкладка «Лицензионная информация»."""
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

    page.locator("text=RatioT Server v6.41.11").first.click(button="right")
    time.sleep(2)
    page.locator("text=Показать информацию о сервере").first.click()
    time.sleep(7)
    body = page.locator("body").inner_text()
    print("Название сервера:", "Название сервера" in body)
    page.screenshot(path=str(OUT_DIR / "case27_64111_server_info.png"))

    lic = page.locator("text=Лицензионная информация").first
    print("Вкладка лицензии:", lic.count() > 0)
    if lic.count() > 0:
        lic.click()
        time.sleep(4)
        page.screenshot(path=str(OUT_DIR / "case27_64111_license_tab.png"))
        b = page.locator("body").inner_text()
        i = b.find("Лицензионная информация")
        print("лицензия:", b[i:i+300].replace("\n", " | "))
    browser.close()
    print("Готово.")
