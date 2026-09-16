# -*- coding: utf-8 -*-
"""Кейс 2: проверка режима 100 тегов (попытка 2 — меню пользователя по координатам)."""
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
    page.mouse.click(1540, 23)
    time.sleep(4)
    page.screenshot(path=str(OUT / "case2_100t_menu2.png"))
    body = page.locator("body").inner_text()
    print("Есть 'лицензи' в body:", "лицензи" in body.lower())
    # выведем текст выпадашки
    for sel in [".ant-dropdown", "[role='menu']", "[class*='dropdown' i]"]:
        n = page.locator(sel)
        if n.count():
            try:
                print(f"--- {sel}:", n.first.inner_text()[:400])
            except Exception:
                pass
    try:
        page.click("text=Информация о лицензии", timeout=8000)
        time.sleep(8)
        page.screenshot(path=str(OUT / "case2_100t_license2.png"), full_page=True)
        print("--- BODY после клика:")
        print(page.locator("body").inner_text()[:2500])
    except Exception as e:
        print("Клик не сработал:", str(e)[:200])
    browser.close()
