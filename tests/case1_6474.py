#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 1 (ASD-6474): скриншот server.log 6.41.11 с фрагментом ERROR ag.context."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = context.new_page()
    page.goto("file:///C:/Program Files/RatioTScada/logs/server.log")
    time.sleep(3)
    # ищем строку с ERROR ag.context
    hit = page.locator("text=Error creating resource 'users.admin.models.deviceImages'").first
    if hit.count():
        hit.scroll_into_view_if_needed()
        time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case1_64111_log.png"))
    print("Скриншот сохранён")
    browser.close()
    print("Готово.")
