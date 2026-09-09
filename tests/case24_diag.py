#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: диагностика контекстного меню «Устройства»."""
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

    dev = page.locator("text=Устройства").first
    box = dev.bounding_box()
    print(f"Устройства bbox: {box}")
    dev.click(button="right")
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_diag.png"))

    # Дамп всех потенциально меню-элементов с координатами
    items = page.locator("[role='menuitem'], [class*='contextmenu'] *, [class*='context-menu'] *, .ant-dropdown-menu-item, [class*='popup'] [class*='item']").all()
    print(f"Найдено элементов: {len(items)}")
    for i, it in enumerate(items[:40]):
        try:
            if it.is_visible():
                b = it.bounding_box()
                t = it.inner_text().strip().replace("\n", " / ")
                if t and b:
                    print(f"  [{i}] ({b['x']:.0f},{b['y']:.0f}) {b['width']:.0f}x{b['height']:.0f}: {t[:70]}")
        except Exception:
            pass
    browser.close()
    print("Готово.")
