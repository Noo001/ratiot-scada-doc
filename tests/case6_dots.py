#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: меню действий «...» у узла «SCADA/HMI - Теги»."""
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

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.alertsMonitoring")
    time.sleep(6)

    search = page.locator("input[placeholder='Поиск в системном дереве']").first
    search.fill("теги")
    time.sleep(3)

    # наводим на строку «SCADA/HMI - Теги (4)» и жмём «...»
    el = page.locator(".system-tree-context-name", has_text="SCADA/HMI - Теги").first
    row = el.locator("xpath=..")
    row.hover()
    time.sleep(1)
    # «...» — последний svg/button в строке
    dots = row.locator("svg, button").last
    dots.click()
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case6_64111_dots_menu.png"))

    # выводим пункты меню
    menu_items = page.locator("[role='menuitem'], .ant-dropdown-menu-item, li[role='menuitem']")
    print(f"Пунктов меню: {menu_items.count()}")
    for i in range(menu_items.count()):
        try:
            print(f"  - {menu_items.nth(i).inner_text()[:50]}")
        except Exception:
            pass
    browser.close()
    print("Готово.")
