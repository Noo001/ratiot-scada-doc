#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: мастер «Добавить устройство» + поле метаданных."""
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
    # Клик по пункту «Добавить устройство» (самый нижний видимый из дампа)
    item = page.locator("text=Добавить устройство").first
    item.click()
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case24_64111_wizard1.png"))
    print(f"url: {page.url}")
    body = page.locator("body").inner_text()
    print("текст:", body[:800].replace("\n", " | "))
    browser.close()
    print("Готово.")
