# -*- coding: utf-8 -*-
"""Кейсы 13 (ASD-6479) и 10 (ASD-6477): раздел «Драйвера и расширения» и магазин приложений."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)


def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--headless=new", "--disable-gpu", "--no-sandbox",
            "--disable-dev-shm-usage", "--disable-web-security",
        ])
        ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
        page = ctx.new_page()

        print("Логин...")
        login(page)
        print("URL:", page.url)
        page.screenshot(path=str(SHOTS / "case13_00_main.png"))

        # Открываем системное дерево (Управление ресурсами)
        print("\nОткрываем «Управление ресурсами»...")
        try:
            page.click("text=Управление ресурсами", timeout=10000)
        except Exception as e:
            print("Клик по ссылке не удался:", type(e).__name__)
        time.sleep(8)
        page.screenshot(path=str(SHOTS / "case13_005_tree.png"), full_page=True)
        body_tree = page.locator("body").inner_text()
        print("BODY после открытия дерева (первые 1500 символов):")
        print(body_tree[:1500])

        # --- Кейс 13: раздел «Драйвера и расширения» ---
        print("\n=== КЕЙС 13: Драйвера и расширения ===")
        node = page.locator("text=Драйверы и расширения").first
        alt = page.locator("text=Драйвера и расширения").first
        target = node if node.count() > 0 else alt
        print("Найден узел «Драйверы и расширения»:", node.count() > 0)
        print("Найден узел «Драйвера и расширения»:", alt.count() > 0)

        if node.count() == 0 and alt.count() == 0:
            # выведем, что вообще есть в дереве
            tree_text = page.locator("body").inner_text()
            print("BODY (первые 2000 символов):")
            print(tree_text[:2000])
        else:
            el = node if node.count() > 0 else alt
            el.hover()
            time.sleep(2)
            page.screenshot(path=str(SHOTS / "case13_01_tooltip.png"))
            el.click()
            time.sleep(8)
            page.screenshot(path=str(SHOTS / "case13_02_opened.png"), full_page=True)
            body = page.locator("body").inner_text()
            print("BODY после открытия (первые 2500 символов):")
            print(body[:2500])
            markers_root = ["Устройства", "Группы устройств", "Пользователи", "Приложения", "Модели"]
            found = [m for m in markers_root if m in body]
            print("Маркеры корня дерева найдены:", found)

        # --- Кейс 10: поиск «Магазин» в системном дереве ---
        print("\n=== КЕЙС 10: Магазин приложений ===")
        search = page.locator("input[placeholder*='Поиск в системном дереве' i], input[placeholder*='Поиск' i]").first
        print("Поле поиска дерева найдено:", search.count() > 0)
        if search.count() > 0:
            search.fill("Магазин")
            time.sleep(3)
            page.keyboard.press("Enter")
            time.sleep(6)
            page.screenshot(path=str(SHOTS / "case10_01_search.png"), full_page=True)
            body = page.locator("body").inner_text()
            print("BODY после поиска «Магазин» (первые 2000 символов):")
            print(body[:2000])
            print("Слово «Магазин» встречается:", body.count("Магазин"))

        browser.close()


if __name__ == "__main__":
    main()
