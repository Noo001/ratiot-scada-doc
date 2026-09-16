# -*- coding: utf-8 -*-
"""Кейс 28: какая из двух kebab-кнопок открывает меню ДЕЙСТВИЯ."""
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
    row = page.locator("tr:has-text('test')").first
    row.hover()
    time.sleep(1)
    row.locator("td.kebab-row-cell .kebab-btn").nth(1).click()
    time.sleep(3)
    body = page.locator("body").inner_text()
    print("После клика по 2-й kebab-кнопке:")
    print("  URL:", page.url)
    print("  ДЕЙСТВИЯ в body:", "ДЕЙСТВИЯ" in body)
    page.screenshot(path=str(OUT / "case28_64112_45_kebab2.png"), full_page=True)
    if "ДЕЙСТВИЯ" in body:
        items = page.locator(".ant-dropdown-menu-item:visible")
        print("  Пунктов меню:", items.count())
        for i in range(items.count()):
            print("   -", items.nth(i).inner_text().strip()[:50])
    browser.close()
