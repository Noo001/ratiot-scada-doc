# -*- coding: utf-8 -*-
"""Клик по каждому пункту рейла: что открывается."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SHOTS = Path(__file__).parent / "screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
    page = ctx.new_page()
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)

    items = page.locator(".ant-menu-item")
    n = items.count()
    print("Пунктов рейла:", n)
    for i in range(n):
        try:
            label = items.nth(i).inner_text().strip()
        except Exception:
            label = ""
        items.nth(i).click()
        time.sleep(6)
        body = page.locator("body").inner_text().replace("\n", " | ")
        print(f"[{i}] label='{label}' url={page.url}")
        print(f"    body: {body[:220]}")
        page.screenshot(path=str(SHOTS / f"rail_{i}.png"))
    browser.close()
