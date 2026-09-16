# -*- coding: utf-8 -*-
"""Кейс 28: открыть меню ДЕЙСТВИЯ кликом по td строки test (как в case28_7)."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"


def login(page):
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)

    for sel in ["td:has-text('test')", "tr:has-text('test')"]:
        page.goto(CC, timeout=120000)
        page.wait_for_load_state("networkidle", timeout=120000)
        time.sleep(6)
        page.locator(sel).first.click()
        time.sleep(3)
        body = page.locator("body").inner_text()
        print(f"Селектор {sel!r}: ДЕЙСТВИЯ={'ДЕЙСТВИЯ' in body}, URL={page.url.split('/')[-1]}")
        if "ДЕЙСТВИЯ" in body:
            page.screenshot(path=str(OUT / "case28_64112_46_actions.png"), full_page=True)
            items = page.locator(".ant-dropdown-menu-item:visible")
            for i in range(items.count()):
                print("   -", items.nth(i).inner_text().strip()[:50])
            break
    browser.close()
