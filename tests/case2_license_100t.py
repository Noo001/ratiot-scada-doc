# -*- coding: utf-8 -*-
"""Кейс 2: проверка режима 100 тегов после чистой установки (6.41.12)."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)

    # Меню пользователя: иконка в правом верхнем углу
    clicked = False
    for sel in [".ant-avatar", "img[alt*='admin' i]", "[class*='user' i][class*='menu' i]",
                "button:has-text('admin')", "[class*='header' i] [class*='avatar' i]"]:
        loc = page.locator(sel)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=5000)
                clicked = True
                print("Клик по:", sel)
                break
            except Exception:
                continue
    time.sleep(4)
    page.screenshot(path=str(OUT / "case2_100t_usermenu.png"))
    body = page.locator("body").inner_text()
    if "лицензи" in body.lower():
        try:
            page.click("text=/лицензи/i", timeout=8000)
            time.sleep(8)
        except Exception as e:
            print("клик по пункту лицензии не сработал:", e)
    page.screenshot(path=str(OUT / "case2_100t_license.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("BODY (после):")
    print(body[:2500])
    browser.close()
