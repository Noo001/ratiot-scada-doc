# -*- coding: utf-8 -*-
"""Кейс 16 (ASD-6480): функциональная проверка меню «Ещё» у вкладок на 6.41.11-2532."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"

def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--headless=new", "--disable-gpu", "--no-sandbox",
            "--disable-dev-shm-usage", "--disable-web-security",
        ])
        context = browser.new_context(ignore_https_errors=True,
                                      viewport={"width": 1280, "height": 720})
        page = context.new_page()
        login(page)
        page.click("text=Просмотр информации о сервере", timeout=10000)
        time.sleep(3)

        more = page.locator(".ant-tabs-nav-more").first
        print("Кнопка «Ещё» visible:", more.is_visible())
        box = more.bounding_box()
        print("Кнопка «Ещё» box:", box)
        more.click()
        time.sleep(1)
        page.screenshot(path=str(SCREENSHOTS / "case16_more_dropdown.png"))

        # Пробуем открыть скрытую вкладку через выпадающее меню
        for item in ["Производительность", "Потоки", "Статистика событий"]:
            try:
                page.click(f".ant-tabs-dropdown-menu-item:has-text(\"{item}\")", timeout=3000)
                print(f"Открыта вкладка через «Ещё»: {item}")
                time.sleep(2)
                page.screenshot(path=str(SCREENSHOTS / f"case16_tab_{item}.png"))
                break
            except Exception as e:
                print(f"Не удалось кликнуть {item}: {type(e).__name__}")
        browser.close()

if __name__ == "__main__":
    main()
