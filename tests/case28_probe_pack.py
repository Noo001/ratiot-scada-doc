# -*- coding: utf-8 -*-
"""Кейс 28: «Упаковать» — выбор типа операции для скачивания ZIP."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
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
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000},
                              accept_downloads=True)
    page = ctx.new_page()
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("td:has-text('test')").first.click()
    time.sleep(3)
    res = page.evaluate("""() => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === 'Упаковать' && e.getBoundingClientRect().width);
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""")
    page.mouse.click(*res)
    time.sleep(4)

    # варианты «Тип операции»
    page.locator(".ant-select:visible").first.click()
    time.sleep(2)
    opts = page.locator(".ant-select-item-option:visible")
    print("Вариантов:", opts.count())
    for i in range(opts.count()):
        print("  -", opts.nth(i).inner_text().strip()[:80])
    page.screenshot(path=str(OUT / "case28_64112_62_pack_optype.png"), full_page=True)
    browser.close()
