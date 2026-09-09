#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: контекстное меню устройства local_system → Свойства."""
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

    search = page.locator("[placeholder*='Поиск в системном дереве']").first
    search.fill("local_system")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(3)

    # Первый узел local_system (под «Устройства»)
    node = page.locator("text=local_system").first
    node.click(button="right")
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_devmenu.png"))

    # Дамп пунктов меню
    items = page.locator("[class*='select'] [class*='option'], [role='menuitem'], [class*='contextmenu'] *, [class*='dropdown-menu'] *").all()
    seen = set()
    for it in items:
        try:
            if it.is_visible():
                t = it.inner_text().strip().replace("\n", " / ")
                if t and t not in seen and len(t) < 60:
                    seen.add(t)
                    print("ПУНКТ:", t)
        except Exception:
            pass

    # Клик по пункту «Свойства»
    for it in items:
        try:
            if it.is_visible() and "Свойства" in it.inner_text():
                it.click()
                print("Клик по: Свойства")
                break
        except Exception:
            pass
    time.sleep(6)
    body = page.locator("body").inner_text()
    print("Свойства открыты:", "Активные переменные" in body)
    page.screenshot(path=str(OUT_DIR / "case24_64111_props4.png"))
    browser.close()
    print("Готово.")
