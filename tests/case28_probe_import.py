# -*- coding: utf-8 -*-
"""Кейс 28: диагностика кнопки импорта приложения (тултипы, input[type=file], модальные окна)."""
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
    page.on("filechooser", lambda fc: print("FILECHOOSER EVENT:", fc.element if hasattr(fc, 'element') else fc))
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)

    # тултипы верхних трёх иконок
    for svg_id in ("ic_apply_16", "ic_import_16", "ic_export_16"):
        b = page.locator(f"div.component-system-button:has(svg#{svg_id})").first
        b.hover()
        time.sleep(1.5)
        tips = page.locator(".ant-tooltip:visible")
        t = tips.last.inner_text().strip() if tips.count() else ""
        print(f"{svg_id} tooltip: {t!r}")

    # клик по импорту и наблюдение
    print("--- клик по импорту ---")
    page.locator("div.component-system-button:has(svg#ic_import_16)").first.click()
    for i in range(6):
        time.sleep(2)
        inputs = page.evaluate("""() => Array.from(document.querySelectorAll('input[type=file]')).map(
            e => ({id: e.id, name: e.name, cls: (e.className||'').toString().slice(0,50),
                   accept: e.accept, visible: !!(e.offsetWidth || e.offsetHeight)}))""")
        print(f"t+{(i+1)*2}s inputs:", inputs)
        modals = page.evaluate("""() => Array.from(document.querySelectorAll('[class*=modal], [class*=Modal], [role=dialog]')).filter(
            e => e.offsetWidth || e.offsetHeight).map(e => (e.innerText||'').slice(0,120).replace(/\\n/g,' | '))""")
        print("  модальные окна:", modals)
    page.screenshot(path=str(OUT / "case28_64112_40_import_diag.png"), full_page=True)
    print("BODY:", page.locator("body").inner_text()[:500].replace("\n", " | "))
    browser.close()
