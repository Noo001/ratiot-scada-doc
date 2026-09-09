#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: проверить, появилось ли устройство в дереве."""
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

    # Раскрыть узел «Устройства»
    dev = page.locator("text=Устройства").first
    dev.click()
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case24_64111_devices.png"))

    # Собрать видимые строки дерева
    rows = page.locator("[class*='tree'] [class*='node'], [class*='Tree'] [class*='row'], [role='treeitem']").all()
    print(f"Строк дерева: {len(rows)}")
    for r in rows[:40]:
        try:
            if r.is_visible():
                t = r.inner_text().strip().replace("\n", " / ")
                if t:
                    print(f"  - {t[:80]}")
        except Exception:
            pass
    browser.close()
    print("Готово.")
