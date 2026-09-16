# -*- coding: utf-8 -*-
"""Кейс 21 на 6.41.12: пользовательский путь — дерево → ioField → кнопка редактирования."""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
TREE = f"{BASE}/web/dashboards/users.admin.dashboards.scadaApplication"

errors_all = []


def on_page_error(err):
    errors_all.append(str(err))


def on_console(msg):
    if msg.type == "error":
        errors_all.append(msg.text)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    page.on("pageerror", on_page_error)
    page.on("console", on_console)

    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)

    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)

    print("Поиск «ioField» в дереве...")
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("ioField")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(6)
    page.screenshot(path=str(OUT / "case21_64112_tree_search.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("BODY после поиска (800 символов):")
    print(body[:800])

    # клик по результату
    res = page.locator(".system-tree-context-name").filter(has_text="IO Field")
    if res.count() == 0:
        res = page.locator("text=IO Field")
    print("Результатов ioField:", res.count())
    if res.count() > 0:
        errors_all.clear()
        try:
            with ctx.expect_page(timeout=10000) as new_page_info:
                res.first.click()
            dash = new_page_info.value
            dash.wait_for_load_state("networkidle", timeout=120000)
            time.sleep(15)
            dash.on("pageerror", on_page_error)
            dash.on("console", on_console)
            page2 = dash
        except Exception:
            page2 = page
            time.sleep(12)
        page2.screenshot(path=str(OUT / "case21_64112_iofield_view.png"), full_page=True)
        print("URL:", page2.url)
        print("BODY после клика (600 символов):")
        print(page2.locator("body").inner_text()[:600])
        # ищем кнопку редактирования
        edit_btns = page2.locator("button[title*='едактир' i], [aria-label*='edit' i], .anticon-edit")
        print("Кнопок редактирования найдено:", edit_btns.count())
        if edit_btns.count() > 0:
            errors_all.clear()
            edit_btns.first.click()
            time.sleep(15)
            page2.screenshot(path=str(OUT / "case21_64112_iofield_editmode.png"), full_page=True)
            print("URL после редактирования:", page2.url)
            print("JS-ошибок:", len(errors_all))
            for e in errors_all[:6]:
                print("  -", e[:180])
            print("Спиннеров:", page2.locator(".ant-spin-spinning").count())
            print("BODY (400):", page2.locator("body").inner_text()[:400])

    browser.close()
