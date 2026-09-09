#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка версии установленной RatioT SCADA через веб-интерфейс."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1400, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # открыть «Информация о сервере»
    page.locator("text=Информация о сервере").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)

    # получить версию из таблицы
    version = page.evaluate("""
        () => {
            const rows = Array.from(document.querySelectorAll('tr'));
            for (const row of rows) {
                const cells = Array.from(row.querySelectorAll('td'));
                if (cells.length >= 2 && cells[0].textContent.includes('Версия сервера')) {
                    return cells[1].textContent.trim();
                }
            }
            return null;
        }
    """)

    page.screenshot(path=str(OUT_DIR / "version_check.png"))
    result = {"version": version, "url": page.url}
    (OUT_DIR / "version_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    browser.close()
