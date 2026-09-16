# -*- coding: utf-8 -*-
"""Кейс 21: контекстное меню IO Field + просмотр milkStorage на 6.41.12."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
TREE = f"{BASE}/web/dashboards/users.admin.dashboards.scadaApplication"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


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
    hook(page)
    login(page)
    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)

    # IO Field — правый клик
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("IO Field")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(5)
    res = page.locator(".system-tree-context-name").filter(has_text="IO Field")
    print("Результатов IO Field:", res.count())
    res.first.click(button="right")
    time.sleep(3)
    page.screenshot(path=str(OUT / "case21_ctx_menu.png"))
    body = page.locator("body").inner_text()
    # ищем пункт редактирования в меню
    for item in ["Редактировать", "Правка", "Изменить"]:
        loc = page.locator(f"text={item}")
        print(f"Пункт «{item}» в контекстном меню:", loc.count())
    # закрыть меню
    page.keyboard.press("Escape")
    time.sleep(1)

    # milkStorage — поиск и открытие
    errors_all.clear()
    search.fill("")
    search.fill("Хранилище пастеризованного молока")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(5)
    res2 = page.locator(".system-tree-context-name").filter(has_text="Хранилище пастеризованного молока")
    if res2.count() == 0:
        res2 = page.locator("text=Хранилище пастеризованного молока")
    print("Результатов «Хранилище…»:", res2.count())
    if res2.count() > 0:
        res2.first.click()
        time.sleep(18)
        page.screenshot(path=str(OUT / "case21_64112_milkstorage_view.png"), full_page=True)
        print("URL:", page.url)
        print("JS-ошибок:", len(errors_all))
        for e in errors_all[:6]:
            print("  -", e[:180])
        print("Спиннеров:", page.locator(".ant-spin-spinning").count())

    browser.close()
