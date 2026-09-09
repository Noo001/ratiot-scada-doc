#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 1 (ASD-6474): скриншот фрагмента server.log с ERROR ag.context (deviceImages)."""
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
    found = page.evaluate("window.find(\"Error creating resource 'users.admin.models.deviceImages'\")")
    print("Найдено:", found)
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case1_64111_error.png"))
    browser.close()
    print("Готово.")
