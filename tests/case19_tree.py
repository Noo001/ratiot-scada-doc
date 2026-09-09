#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 19: вкладка «Исторические тревоги» и открытие «Тревоги» из поиска дерева."""
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

    errors.clear()
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.alertsMonitoring")
    time.sleep(6)
    try:
        page.get_by_text("Исторические тревоги", exact=True).first.click()
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case19_64111_history_tab.png"))
        print(f"Исторические тревоги: {page.url}, ошибок {len(errors)}")
        for e in errors[:5]:
            print(f"  {e[:180]}")
    except Exception as e:
        print(f"Вкладка не открылась: {str(e)[:150]}")

    # все результаты поиска 'alerts'
    try:
        search = page.locator("input[placeholder='Поиск в системном дереве']").first
        search.fill("alerts")
        time.sleep(3)
        items = page.locator(".system-tree-context-name").all()
        print(f"Всего результатов: {len(items)}")
        for i, r in enumerate(items):
            try:
                t = r.inner_text().strip()
                print(f"  [{i}] {t[:60]}")
            except Exception:
                pass
        # клик по первому элементу с текстом «Тревоги» (не Активные/Исторические)
        for i, r in enumerate(items):
            try:
                t = r.inner_text().strip()
                if t == "Тревоги":
                    r.click()
                    time.sleep(6)
                    page.screenshot(path=str(OUT_DIR / "case19_64111_tree_alerts_click.png"))
                    print(f"Клик по «Тревоги» [{i}]: {page.url}, ошибок {len(errors)}")
                    for e in errors[:5]:
                        print(f"  {e[:180]}")
                    break
            except Exception:
                pass
    except Exception as e:
        print(f"Поиск: {str(e)[:150]}")

    browser.close()
    print("Готово.")
