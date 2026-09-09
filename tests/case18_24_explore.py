#!/usr/bin/env python3
"""Исследование и тестирование кейсов 18-24 в веб-интерфейсе RatioT SCADA."""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

console_errors = []
page_errors = []


def save(page, name: str):
    path = SCREENSHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"Screenshot: {path}")
    return path


def log_console(msg):
    text = f"[{msg.type}] {msg.text}"
    console_errors.append(text)
    if msg.type in ("error", "warning"):
        print(text)


def log_page_error(err):
    page_errors.append(str(err))
    print(f"PAGE ERROR: {err}")


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
    save(page, "explore_01_login")

    login_selector = wait_for_login(page)
    print(f"Селектор логина: {login_selector}")

    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    save(page, "explore_02_after_login")


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
        page.on("console", log_console)
        page.on("pageerror", log_page_error)

        login(page)

        # Кейс 18: демо-приложение, ссылки Документация/Онлайн
        print("Кейс 18: открываем демо-приложение")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)
        save(page, "explore_03_demo_home")

        # Попробуем найти ссылки "Документация" и "Онлайн"
        for text in ["Документация", "Онлайн"]:
            try:
                link = page.locator(f"text={text}").first
                if link.is_visible():
                    print(f"Найдена ссылка '{text}', кликаем")
                    link.click()
                    time.sleep(3)
                    save(page, f"explore_04_case18_{text.lower()}")
                    # Вернёмся
                    page.goto(f"{BASE_URL}/web/")
                    page.wait_for_load_state("networkidle", timeout=60000)
                    time.sleep(3)
                else:
                    print(f"Ссылка '{text}' не видна")
            except Exception as e:
                print(f"Не удалось кликнуть '{text}': {e}")

        # Кейс 19: раздел Тревоги
        print("Кейс 19: открываем раздел Тревоги")
        try:
            page.click("text=Тревоги", timeout=5000)
            time.sleep(5)
            save(page, "explore_05_case19_alarms")
        except Exception as e:
            print(f"Не удалось открыть Тревоги: {e}")
            save(page, "explore_05_case19_alarms_error")

        # Кейс 20: шаблоны задвижек
        print("Кейс 20: шаблоны задвижек")
        page.goto(f"{BASE_URL}/web/")
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Инструментальные панели", timeout=5000)
            time.sleep(2)
            page.click("text=Группы инструментальных панелей", timeout=5000)
            time.sleep(2)
            page.click("text=Шаблон задвижка", timeout=5000)
            time.sleep(3)
            save(page, "explore_06_case20_valve_template")
        except Exception as e:
            print(f"Не удалось открыть шаблон задвижки: {e}")
            save(page, "explore_06_case20_valve_template_error")

        # Кейс 21: редактирование демо-проекта
        print("Кейс 21: редактирование демо-проекта")
        for dash_path in [
            "/web/dashboards/users.admin.dashboards.ioField",
            "/web/dashboards/users.admin.dashboards.milkStorage",
            "/web/#dashboards:users.admin.dashboards.ioField",
            "/web/#dashboards:users.admin.dashboards.milkStorage",
        ]:
            try:
                print(f"Пробуем URL: {dash_path}")
                page.goto(f"{BASE_URL}{dash_path}", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(8)
                save(page, f"explore_07_case21_{dash_path.replace('/', '_').replace('#', '')}")
            except Exception as e:
                print(f"Ошибка открытия {dash_path}: {e}")

        # Кейс 22: справка и демо "Дом"
        print("Кейс 22: справка и демо Дом")
        page.goto(f"{BASE_URL}/static/docs/index.htm", timeout=60000)
        time.sleep(3)
        save(page, "explore_08_case22_help")

        page.goto(f"{BASE_URL}/web/")
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Дом", timeout=5000)
            time.sleep(3)
            save(page, "explore_09_case22_demo_home")
        except Exception as e:
            print(f"Не удалось открыть демо Дом: {e}")
            save(page, "explore_09_case22_demo_home_error")

        # Кейс 24: метаданные устройства
        print("Кейс 24: метаданные устройства")
        page.goto(f"{BASE_URL}/web/")
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Устройства", timeout=5000)
            time.sleep(2)
            # Попробуем открыть первое устройство
            rows = page.locator("[role='row']").all()
            if rows and len(rows) > 1:
                rows[1].click()
                time.sleep(2)
                save(page, "explore_10_case24_device_props")
            else:
                print("Устройства не найдены")
                save(page, "explore_10_case24_device_props_empty")
        except Exception as e:
            print(f"Не удалось открыть устройство: {e}")
            save(page, "explore_10_case24_device_props_error")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "explore_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Исследование завершено")


if __name__ == "__main__":
    main()
