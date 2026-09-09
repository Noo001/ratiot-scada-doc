#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скриншот кейса 26: поиск в системном дереве не открывает раздел."""

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

    # пользовательский путь: поиск в дереве
    search = page.locator("input[placeholder='Поиск в системном дереве']").first
    search.fill("")
    search.fill("Устройства")
    time.sleep(1.5)

    # клик по первому результату в дереве
    result = page.locator(".system-tree-context-name").filter(has_text="Устройства").first
    result.click()
    time.sleep(2)
    page.wait_for_load_state("networkidle")

    page.screenshot(path=str(OUT_DIR / "case26_tree_search_no_open.png"))
    browser.close()
    print("Скриншот сохранён: case26_tree_search_no_open.png")
