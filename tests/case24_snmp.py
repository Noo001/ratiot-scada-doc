#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: мастер SNMP — создание устройства."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

def dump(page, tag):
    body = page.locator("body").inner_text()
    print(f"--- {tag} ---")
    print(body[:1200].replace("\n", " | "))
    print()

def click_option(page, text):
    for sel in ["[class*='select'] [class*='option']", "[role='option']", "[role='listbox'] [class*='item']"]:
        for o in page.locator(sel).all():
            try:
                if o.is_visible() and text in o.inner_text():
                    o.click()
                    return True
            except Exception:
                pass
    return False

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

    page.locator("text=Выберите драйвер").first.click()
    time.sleep(1.5)
    ok = click_option(page, "SNMP")
    print(f"SNMP выбран: {ok}")
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case24_64111_wizard_snmp.png"))
    page.locator("button:has-text('OK')").last.click()
    time.sleep(4)
    dump(page, "после OK (SNMP)")
    page.screenshot(path=str(OUT_DIR / "case24_64111_wizard_snmp_step2.png"))
    browser.close()
    print("Готово.")
