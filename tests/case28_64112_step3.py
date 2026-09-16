# -*- coding: utf-8 -*-
"""Кейс 28, этап 3в: дашборд приложения test — дамп кнопок/иконок с title."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"

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

    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    print("URL:", page.url)
    page.screenshot(path=str(OUT / "case28_64112_19_app_dash.png"), full_page=True)

    # дамп всех элементов с title / aria-label в шапке приложения
    els = page.locator("[title]:visible, [aria-label]:visible")
    print("Элементов с title/aria-label:", els.count())
    for i in range(els.count()):
        try:
            t = els.nth(i).get_attribute("title") or els.nth(i).get_attribute("aria-label")
            tag = els.nth(i).evaluate("e => e.tagName")
            cls = (els.nth(i).get_attribute("class") or "")[:60]
            print(f"  [{i}] <{tag}> title={t!r} class={cls!r}")
        except Exception:
            pass

    # все видимые кнопки
    btns = page.locator("button:visible")
    print("Видимых кнопок:", btns.count())
    for i in range(min(btns.count(), 25)):
        try:
            print(f"  b[{i}] {btns.nth(i).inner_text().strip()[:60]!r}")
        except Exception:
            pass

    # вкладка «Ресурсы»
    page.locator(".ant-tabs-tab:visible, [role='tab']:visible", has_text="Ресурсы").first.click()
    time.sleep(5)
    page.screenshot(path=str(OUT / "case28_64112_20_resources_tab.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("Панель «Устройства» в ресурсах:", "Устройства" in body)
    print("BODY:", body[:800].replace("\n", " | "))

    # дамп иконок под вкладками (title)
    icons = page.locator("[class*='icon']:visible, button:visible")
    for i in range(min(icons.count(), 40)):
        try:
            t = icons.nth(i).get_attribute("title")
            if t:
                print(f"  icon[{i}] title={t!r}")
        except Exception:
            pass

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
