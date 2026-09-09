#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 19: проверка вкладки «Исторические тревоги» и поиска 'alerts' в системном дереве."""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()
    page.on("console", lambda m: errors.append(f"[console] {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    # alertsMonitoring -> вкладка «Исторические тревоги»
    errors.clear()
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.alertsMonitoring")
    time.sleep(6)
    try:
        page.locator("[role='tab']:has-text('Исторические тревоги'), text=Исторические тревоги").first.click()
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case19_64111_history_tab.png"))
        print(f"Исторические тревоги: {page.url}, ошибок {len(errors)}")
        for e in errors[:5]:
            print(f"  {e[:180]}")
    except Exception as e:
        print(f"Вкладка не открылась: {e}")

    # поиск alerts в системном дереве
    try:
        search = page.locator("input[placeholder='Поиск в системном дереве']").first
        search.fill("alerts")
        time.sleep(3)
        page.screenshot(path=str(OUT_DIR / "case19_64111_tree_search.png"))
        results = page.locator(".system-tree-context-name, [class*='context-name']").all()
        print(f"Результатов поиска: {len(results)}")
        for r in results[:10]:
            try:
                print(f"  - {r.inner_text()[:60]}")
            except Exception:
                pass
    except Exception as e:
        print(f"Поиск в дереве: {e}")

    browser.close()
    print("Готово.")
