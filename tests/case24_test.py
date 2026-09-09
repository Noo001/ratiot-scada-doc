#!/usr/bin/env python3
"""Тестирование кейса 24: метаданные устройства."""

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
    return path


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
    print("Открываем логин")
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(3)
    login_selector = wait_for_login(page)
    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    save(page, "case24_01_after_login")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ],
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        login(page)

        # Используем поиск в системном дереве для нахождения устройства
        print("Ищем устройство через поиск")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
        search.fill("dataCenterManagementDevice1")
        time.sleep(3)
        save(page, "case24_02_search_device")
        # Кликаем по найденному устройству в дереве
        print("Открываем устройство в дереве")
        try:
            page.click("text=dataCenterManagementDevice1", timeout=10000)
            time.sleep(5)
            save(page, "case24_03_device_tree_opened")
        except Exception as e:
            print(f"Не удалось открыть устройство: {e}")
            save(page, "case24_03_device_tree_error")

        # Ищем вкладки
        print("Ищем вкладки")
        tabs = page.locator("[role='tab']").all()
        print(f"Найдено вкладок: {len(tabs)}")
        for tab in tabs:
            try:
                text = tab.text_content()
                print(f"Вкладка: {text}")
            except Exception:
                pass

        # Ищем "Активные переменные/функции/события"
        print("Ищем активные переменные")
        page_content = page.content()
        if "Активные" in page_content:
            print("Текст 'Активные' найден в HTML")
        if "Метаданные" in page_content:
            print("Текст 'Метаданные' найден в HTML")
        if "activeVariables" in page_content:
            print("Текст 'activeVariables' найден в HTML")

        # Сохраняем скриншот свойств устройства
        save(page, "case24_04_device_props_final")

        # Пробуем найти поле через evaluate
        print("Поиск полей через JS")
        labels = page.evaluate("""() => {
            const result = [];
            document.querySelectorAll('label, span, div').forEach(el => {
                const text = el.textContent || '';
                if (text.includes('Активные') || text.includes('Метаданные') || text.includes('activeVariables')) {
                    result.push(text.trim().substring(0, 100));
                }
            });
            return result;
        }""")
        print(f"Найденные метки: {labels}")

        browser.close()
        print("Тестирование кейса 24 завершено")


if __name__ == "__main__":
    main()
