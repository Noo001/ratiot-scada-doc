#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24 (ASD-6502): создать устройство, открыть Метаданные, проверить поле «Активные переменные»."""
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

    # открываем системное дерево: дашборд тегов даёт дерево с корнем Устройства
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)

    # «Устройства» -> меню действий «...»
    dev = page.locator("text=Устройства").first
    row = dev.locator("xpath=..")
    row.hover()
    time.sleep(1)
    row.locator("svg, button").last.click()
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_devices_menu.png"))
    menu_items = page.locator("[role='menuitem'], .ant-dropdown-menu-item")
    print(f"Пунктов меню «Устройства»: {menu_items.count()}")
    for i in range(menu_items.count()):
        try:
            print(f"  - {menu_items.nth(i).inner_text()[:50]}")
        except Exception:
            pass
    browser.close()
    print("Готово.")
