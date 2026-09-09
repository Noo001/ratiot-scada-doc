#!/usr/bin/env python3
"""Пробуем открыть свойства устройства разными способами."""

import sys
import io
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)


def save(page, name: str, full_page=True):
    path = SCREENSHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page)
    print(f"Screenshot: {path}")


def wait_for_login(page):
    for _ in range(60):
        try:
            if page.locator("input[placeholder*='Имя пользователя' i]").count() > 0:
                return "input[placeholder*='Имя пользователя' i]"
            if page.locator("input[type='text']").count() > 0:
                return "input[type='text']"
        except Exception:
            pass
        time.sleep(1)
    return None


def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(3)
    login_selector = wait_for_login(page)
    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    save(page, "case24_click_01_login")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security"],
        )
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 900})
        page = context.new_page()
        login(page)

        page.goto(f"{BASE_URL}/users.admin.dashboards.devices", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)
        save(page, "case24_click_02_devices")

        # Кликаем по описанию устройства
        print("Клик по описанию устройства")
        try:
            link = page.locator("text=Data Center Management Device 1").first
            link.click()
            time.sleep(5)
            save(page, "case24_click_03_desc_click")
        except Exception as e:
            print(f"Клик по описанию не удался: {e}")
            save(page, "case24_click_03_desc_error")

        # Возвращаемся
        page.goto(f"{BASE_URL}/users.admin.dashboards.devices", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)

        # Кликаем по контексту устройства (ссылка users.admin.devices.dataCenterManagementDevice1)
        print("Клик по контексту устройства")
        try:
            link = page.locator("a:has-text('dataCenterManagementDevice1')").first
            link.click()
            time.sleep(5)
            save(page, "case24_click_04_context_click")
        except Exception as e:
            print(f"Клик по контексту не удался: {e}")
            save(page, "case24_click_04_context_error")

        # Возвращаемся и пробуем кнопку "Добавить устройство" / меню
        page.goto(f"{BASE_URL}/users.admin.dashboards.devices", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)

        # Ищем иконку на строке устройства
        print("Ищем иконки действий на строке")
        try:
            # Попробуем найти кнопку/иконку в строке таблицы
            rows = page.locator("[role='row']").all()
            print(f"Найдено строк: {len(rows)}")
            for i, row in enumerate(rows[:5]):
                print(f"Строка {i}: {row.text_content()[:100]}")
        except Exception as e:
            print(f"Ошибка: {e}")

        browser.close()


if __name__ == "__main__":
    main()
