# -*- coding: utf-8 -*-
"""Кейсы 13 (ASD-6479) и 10 (ASD-6477) через системное дерево."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
TREE_URL = f"{BASE_URL}/web/dashboards/users.admin.dashboards.scadaApplication"
SHOTS = Path(__file__).parent / "screenshots"


def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
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
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
    page = ctx.new_page()

    print("Логин...")
    login(page)
    print("Открываем системное дерево:", TREE_URL)
    page.goto(TREE_URL, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    page.screenshot(path=str(SHOTS / "case13_tree.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("BODY дерева:")
    print(body[:1200])

    # --- Кейс 13 ---
    print("\n=== КЕЙС 13: «Драйверы/Драйвера и расширения» ===")
    for name in ["Драйверы и расширения", "Драйвера и расширения"]:
        loc = page.locator(f"text={name}")
        if loc.count() > 0:
            print(f"Найден узел: «{name}» ({loc.count()})")
            loc.first.hover()
            time.sleep(2)
            page.screenshot(path=str(SHOTS / "case13_tooltip.png"))
            loc.first.click()
            time.sleep(8)
            page.screenshot(path=str(SHOTS / "case13_opened.png"), full_page=True)
            body2 = page.locator("body").inner_text()
            print("BODY после клика:")
            print(body2[:2000])
            markers = ["Устройства", "Группы устройств", "Пользователи", "Приложения", "Модели"]
            print("Маркеры корня дерева:", [m for m in markers if m in body2])
            break
    else:
        print("Узел «Драйверы/Драйвера и расширения» НЕ найден в дереве!")

    # --- Кейс 10: поиск «Магазин» ---
    print("\n=== КЕЙС 10: поиск «Магазин» ===")
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    print("Поле «Поиск в системном дереве» найдено:", search.count() > 0)
    if search.count() > 0:
        search.fill("Магазин")
        time.sleep(2)
        page.keyboard.press("Enter")
        time.sleep(8)
        page.screenshot(path=str(SHOTS / "case10_search.png"), full_page=True)
        body3 = page.locator("body").inner_text()
        print("BODY после поиска:")
        print(body3[:1500])
        print("Вхождений «Магазин»:", body3.count("Магазин"))

    browser.close()
