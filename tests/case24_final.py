#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: открыть «Редактировать свойства аккаунта устройства» + проверка поля метаданных."""
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

    node = page.locator("text=local_system").first
    node.click(button="right")
    time.sleep(2)
    page.locator("text=Редактировать свойства аккаунта устройства").first.click()
    time.sleep(6)

    body = page.locator("body").inner_text()
    print("Свойства открыты:", "Активные переменные" in body)
    page.screenshot(path=str(OUT_DIR / "case24_64111_props5.png"))

    # Hover на [?] у поля «Активные переменные/функции/события»
    label = page.locator("text=Активные переменные/функции/").first
    lb = label.bounding_box()
    page.mouse.move(lb["x"] + lb["width"] + 10, lb["y"] + lb["height"] / 2)
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case24_64111_tooltip.png"))
    for t in page.locator("[role='tooltip'], [class*='tooltip']").all():
        try:
            if t.is_visible():
                print("TOOLTIP:", t.inner_text().strip()[:400])
        except Exception:
            pass

    # Раскрыть список значений поля
    page.mouse.click(1024, lb["y"] + lb["height"] / 2)
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_values.png"))
    for o in page.locator("[class*='select'] [class*='option'], [role='option']").all():
        try:
            if o.is_visible():
                t = o.inner_text().strip()
                if t:
                    print("ОПЦИЯ:", t[:80])
        except Exception:
            pass
    browser.close()
    print("Готово.")
