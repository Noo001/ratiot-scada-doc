#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Диагностика: что на странице каталога демо после выбора демо."""
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

    page.locator("text=Каталог демо").first.click()
    time.sleep(4)
    page.locator("text=Линия бутилирования").first.click()
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case18_diag_selected.png"))

    btns = page.locator("button")
    print(f"Всего кнопок: {btns.count()}")
    for i in range(btns.count()):
        b = btns.nth(i)
        try:
            t = b.inner_text().strip().replace("\n", " ")[:40]
            vis = b.is_visible()
            if t:
                print(f"  btn[{i}] '{t}' visible={vis}")
        except Exception:
            pass

    # ищем по частичному тексту
    for sel in ["text=Открыть", "text=тьть", "button:has-text(\"ткрыть\")", "[class*='open']"]:
        loc = page.locator(sel)
        print(f"селектор {sel!r}: count={loc.count()}")
    browser.close()
