#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: открыть контекст «Теги» — dblclick / hover-действия."""
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

    el = page.locator(".system-tree-context-name", has_text="Теги").first
    # hover и смотрим, какие кнопки появятся в строке
    row = el.locator("xpath=..")
    row.hover()
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case6_64111_hover.png"))

    # иконки/кнопки в строке
    btns = row.locator("button, [role='button'], svg")
    print(f"Элементов-действий в строке: {btns.count()}")
    for i in range(btns.count()):
        try:
            b = btns.nth(i)
            print(f"  [{i}] {b.get_attribute('class','')[:60]} title={b.get_attribute('title')} aria={b.get_attribute('aria-label')}")
        except Exception:
            pass

    # двойной клик
    try:
        el.dblclick()
        time.sleep(5)
        print(f"После dblclick: {page.url}")
        page.screenshot(path=str(OUT_DIR / "case6_64111_dblclick.png"))
    except Exception as e:
        print(f"dblclick: {str(e)[:120]}")

    browser.close()
    print("Готово.")
