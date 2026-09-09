#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: выбор драйвера в мастере."""
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

    page.locator("text=Устройства").first.click(button="right")
    time.sleep(2)
    page.locator("text=Добавить устройство").first.click()
    time.sleep(4)

    # Раскрыть список драйверов
    sel = page.locator("text=Выберите драйвер").first
    sel.click()
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_drivers.png"))

    # Дамп опций выпадающего списка
    opts = page.locator("[role='option'], [role='listbox'] [class*='item'], [class*='select'] [class*='option']").all()
    print(f"Опций: {len(opts)}")
    for i, o in enumerate(opts[:60]):
        try:
            if o.is_visible():
                t = o.inner_text().strip().replace("\n", " / ")
                if t:
                    print(f"  [{i}] {t[:70]}")
        except Exception:
            pass
    browser.close()
    print("Готово.")
