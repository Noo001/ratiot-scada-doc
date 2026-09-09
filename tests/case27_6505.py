#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 27 (ASD-6505): прямые URL /web/context/* в 6.41.11 + пользовательский путь."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

URLS = [
    ("server", "https://localhost:8443/web/context/users.admin.server.properties"),
    ("license", "https://localhost:8443/web/context/users.admin.licenseInfo"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    # 1) Без авторизации
    for name, url in URLS:
        page.goto(url)
        time.sleep(4)
        page.screenshot(path=str(OUT_DIR / f"case27_64111_{name}_anon.png"))
        print(f"[anon] {name}: final={page.url}")
        print("  body:", page.locator("body").inner_text()[:220].replace("\n", " | "))

    # 2) Логин, затем те же URL в той же сессии
    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    for name, url in URLS:
        page.goto(url)
        time.sleep(5)
        page.screenshot(path=str(OUT_DIR / f"case27_64111_{name}_auth.png"))
        print(f"[auth] {name}: final={page.url}")
        print("  body:", page.locator("body").inner_text()[:220].replace("\n", " | "))

    # 3) Пользовательский путь: Информация о сервере
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)
    search = page.locator("[placeholder*='Поиск в системном дереве']").first
    search.fill("Информация о сервере")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(4)
    page.screenshot(path=str(OUT_DIR / "case27_64111_server_search.png"))
    node = page.locator("text=Информация о сервере").first
    print("Узел найден:", node.count() > 0)
    if node.count() > 0:
        node.click()
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case27_64111_server_info.png"))
        # Вкладка «Лицензионная информация»
        lic = page.locator("text=Лицензионная информация").first
        print("Вкладка лицензии:", lic.count() > 0)
        if lic.count() > 0:
            lic.click()
            time.sleep(4)
            page.screenshot(path=str(OUT_DIR / "case27_64111_license_tab.png"))
    browser.close()
    print("Готово.")
