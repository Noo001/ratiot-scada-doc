# -*- coding: utf-8 -*-
"""Кейс 28: повторно добавить ресурс «Устройства» в приложение test (вкладка Ресурсы -> ⊕)."""
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
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)

    # ⊕ добавить строку
    page.locator("div.component-system-button:has(svg#ic_add_16)").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_58_add_row.png"), full_page=True)

    # клик по полю «Ресурс» новой строки -> выбор контекста
    row = page.locator(".ant-table-row:visible").last
    inp = row.locator("input[type=text]:visible, input:not([type]):visible").first
    inp.click()
    inp.fill("users.admin.dashboards.devices")
    time.sleep(2)
    page.keyboard.press("Enter")
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_59_typed.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("BODY после ввода пути:", body[:600].replace("\n", " | "))
    browser.close()
