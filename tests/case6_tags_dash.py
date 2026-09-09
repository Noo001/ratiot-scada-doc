#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: дашборд дерева тегов — создание тега, просмотр доступных источников."""
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
    time.sleep(3)

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case6_64111_tags_dashboard.png"))
    body = page.locator("body").inner_text()
    print("текст дашборда:", body[:500].replace("\n", " | "))

    # кнопки
    for t in ("Создать", "Добавить", "+", "Создать тег", "Добавить тег"):
        c = page.locator(f"button:has-text('{t}')").locator("visible=true").count()
        if c:
            print(f"кнопка «{t}»: {c}")
    page.screenshot(path=str(OUT_DIR / "case6_64111_tags_dash_full.png"))
    browser.close()
    print("Готово.")
