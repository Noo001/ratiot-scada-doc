#!/usr/bin/env python3
"""Тестирование кейсов 20 и 24: шаблоны и метаданные устройства."""

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
    save(page, "test20_24_01_after_login")


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

        # Кейс 20: шаблоны
        print("Кейс 20: открываем Инструментальные панели")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Инструментальные панели", timeout=10000)
            time.sleep(3)
            save(page, "test20_02_dashboards_group")
        except Exception as e:
            print(f"Не удалось открыть Инструментальные панели: {e}")

        print("Кейс 20: открываем Группы инструментальных панелей")
        try:
            page.click("text=Группы инструментальных панелей", timeout=10000)
            time.sleep(3)
            save(page, "test20_03_dashboards_groups")
        except Exception as e:
            print(f"Не удалось открыть Группы: {e}")

        print("Кейс 20: ищем шаблоны")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Шаблон")
            time.sleep(3)
            save(page, "test20_04_search_template")
            search.fill("")
            time.sleep(1)
        except Exception as e:
            print(f"Поиск не удался: {e}")

        # Пробуем открыть URL шаблонов
        for tpl in ["valve", "pump", "Шаблон задвижка", "Шаблон насос"]:
            try:
                url = f"{BASE_URL}/web/#dashboards:users.admin.dashboards_groups.{tpl}"
                print(f"Пробуем {url}")
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                save(page, f"test20_05_url_{tpl}")
            except Exception as e:
                print(f"Ошибка {tpl}: {e}")

        # Кейс 24: метаданные устройства
        print("Кейс 24: открываем устройство")
        page.goto(f"{BASE_URL}/users.admin.devices.dataCenterManagementDevice1", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)
        save(page, "test24_06_device_props")

        # Ищем вкладку/поле "Активные переменные/функции/события"
        print("Кейс 24: ищем настройку активных переменных")
        try:
            # Пробуем найти текст "Активные" на странице
            active_links = page.locator("text=Активные").all()
            print(f"Найдено элементов с текстом 'Активные': {len(active_links)}")
            for link in active_links:
                try:
                    if link.is_visible():
                        print(f"Кликаем 'Активные': {link.text_content()}")
                        link.click()
                        time.sleep(3)
                        save(page, "test24_07_active_click")
                        break
                except Exception:
                    pass
        except Exception as e:
            print(f"Ошибка поиска 'Активные': {e}")

        # Пробуем найти вкладку Метаданные
        print("Кейс 24: ищем вкладку Метаданные")
        try:
            meta_links = page.locator("text=Метаданные").all()
            print(f"Найдено элементов с текстом 'Метаданные': {len(meta_links)}")
            for link in meta_links:
                try:
                    if link.is_visible():
                        print(f"Кликаем 'Метаданные': {link.text_content()}")
                        link.click()
                        time.sleep(3)
                        save(page, "test24_08_metadata_tab")
                        break
                except Exception:
                    pass
        except Exception as e:
            print(f"Ошибка поиска 'Метаданные': {e}")

        browser.close()
        print("Тестирование кейсов 20, 24 завершено")


if __name__ == "__main__":
    main()
