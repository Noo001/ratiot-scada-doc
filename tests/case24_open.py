#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: открыть свойства существующего local_system через поиск в дереве."""
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

    # Поиск в системном дереве
    search = page.locator("[placeholder*='Поиск в системном дереве']").first
    search.fill("local_system")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(4)
    page.screenshot(path=str(OUT_DIR / "case24_64111_search.png"))

    node = page.locator("text=local_system").first
    if node.count():
        node.dblclick()
        time.sleep(6)
        body = page.locator("body").inner_text()
        print("Свойства открыты:", "Активные переменные" in body)
        page.screenshot(path=str(OUT_DIR / "case24_64111_props3.png"))
    else:
        print("Узел local_system не найден в дереве")
    browser.close()
    print("Готово.")
