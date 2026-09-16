# -*- coding: utf-8 -*-
"""Кейс 28: раскрыть «Инструментальные панели» и выбрать панель."""
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
    row.locator(".kebab-btn").first.click()
    time.sleep(3)
    body = page.locator("body").inner_text()
    if "ДЕЙСТВИЯ" in body:
        page.locator(".ant-dropdown-menu-item:visible", has_text="Открыть").first.click()
        time.sleep(10)
    page.locator("button:has-text('Добавить ресурс')").first.click()
    time.sleep(4)

    # узел «Инструментальные панели» — клик по expand-icon в его строке
    name_el = page.locator(".system-tree-context-name:visible", has_text="Инструментальные панели").first
    node = name_el.locator("xpath=ancestor::*[self::div or self::li][contains(@class,'tree') or contains(@class,'node')][1]")
    print("узлов-кандидатов:", node.count())
    # ищем expand-icon рядом
    expander = name_el.locator("xpath=preceding::*[contains(@class,'expand-icon')][1]")
    print("экспандеров:", expander.count())
    if expander.count():
        name_el.click()
        time.sleep(3)
        page.screenshot(path=str(OUT / "case28_64112_12_dash_expanded.png"), full_page=True)
        names = page.locator(".system-tree-context-name:visible")
        print("Имен в дереве после раскрытия:", names.count())
        for i in range(min(names.count(), 60)):
            t = names.nth(i).inner_text().strip()
            print(f"  [{i}] {t[:60]}")
    # HTML строки узла в диалоге (второе вхождение имени)
    name_el2 = page.locator(".system-tree-context-name:visible", has_text="Инструментальные панели").nth(1)
    row_html = name_el2.evaluate("e => { let r = e.parentElement; while (r && r.innerText.length < 40) r = r.parentElement; return r ? r.outerHTML.slice(0, 2500) : 'nf'; }")
    print("HTML строки узла:")
    print(row_html)
    browser.close()
