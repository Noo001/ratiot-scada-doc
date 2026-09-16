# -*- coding: utf-8 -*-
"""Кейс 2: фиксация текущей лицензии сервера RatioT SCADA 6.41.12-2562.

Путь пользователя: логин → дашборд «Администрирование» → плитка
«Информация о сервере» → вкладка «Лицензионная информация» → раскрыть
«Группы плагинов» (обе страницы вложенной таблицы).
Только чтение/навигация: никаких изменений конфигурации и ресурсов.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
ADMIN = f"{BASE}/users.admin.dashboards.administration"

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


def section(body, start, n=2500):
    i = body.find(start)
    return body[i:i + n] if i >= 0 else f"<не найдено: {start}>"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    hook(page)
    login(page)
    print("URL после логина:", page.url)
    page.screenshot(path=str(OUT / "case2lic_01_after_login.png"))

    page.goto(ADMIN, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)

    page.locator("text=Информация о сервере").first.click()
    time.sleep(8)
    page.screenshot(path=str(OUT / "case2lic_02_server_info.png"))
    print("URL информации о сервере:", page.url)

    page.locator("text=Лицензионная информация").first.click()
    time.sleep(5)
    page.screenshot(path=str(OUT / "case2lic_03_license_tab.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("--- ЛИЦЕНЗИЯ (форма) ---")
    print(section(body, "Дата выпуска", 1400))

    page.locator("text=Записей").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case2lic_04_plugins_page1.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("--- ГРУППЫ ПЛАГИНОВ, стр. 1 ---")
    print(section(body, "Описание", 3200))

    try:
        page.locator(".ant-pagination-item-2").first.click(timeout=5000)
    except Exception:
        page.mouse.click(492, 894)
    time.sleep(4)
    page.screenshot(path=str(OUT / "case2lic_05_plugins_page2.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("--- ГРУППЫ ПЛАГИНОВ, стр. 2 ---")
    print(section(body, "Описание", 1200))

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:5]:
        print("  -", e[:160])
    browser.close()
