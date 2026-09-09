#!/usr/bin/env python3
"""Второй этап исследования кейсов 18-24: приложения, демо, шаблоны, справка."""

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
    login_selector = wait_for_login(page)
    print(f"Селектор логина: {login_selector}")
    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    save(page, "explore2_01_after_login")


def expand_tree_item(page, text: str):
    """Раскрывает элемент дерева по тексту, кликая на стрелку/иконку раскрытия."""
    print(f"Раскрываем '{text}'")
    try:
        # Ищем строку дерева с нужным текстом и кликаем на треугольник раскрытия слева
        row = page.locator(f"[role='treeitem']:has-text('{text}')").first
        if row.count() == 0:
            print(f"Элемент '{text}' не найден")
            return False
        # Пробуем кликнуть по иконке раскрытия (обычно это первая ячейка/элемент в строке)
        row.click()
        time.sleep(2)
        # Попробуем нажать стрелку вправо для раскрытия
        page.keyboard.press("ArrowRight")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Ошибка раскрытия '{text}': {e}")
        return False


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

        # 1. Приложения: раскрываем и смотрим, что внутри
        print("Раскрываем Приложения")
        expand_tree_item(page, "Приложения")
        save(page, "explore2_02_applications_expanded")

        # Попробуем кликнуть по "Приложения" как по контейнеру
        try:
            page.locator("text=Приложения").first.click()
            time.sleep(3)
            save(page, "explore2_03_applications_container")
        except Exception as e:
            print(f"Не удалось открыть контейнер Приложения: {e}")

        # 2. Поиск "SCADA" в дереве
        print("Поиск SCADA в дереве")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("SCADA")
            time.sleep(3)
            save(page, "explore2_04_search_scada")
            search.fill("")
            time.sleep(1)
        except Exception as e:
            print(f"Поиск не удался: {e}")

        # 3. Поиск "Демо" в дереве
        print("Поиск Демо в дереве")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Демо")
            time.sleep(3)
            save(page, "explore2_05_search_demo")
            search.fill("")
            time.sleep(1)
        except Exception as e:
            print(f"Поиск не удался: {e}")

        # 4. Раскрываем Инструментальные панели
        print("Раскрываем Инструментальные панели")
        expand_tree_item(page, "Инструментальные панели")
        save(page, "explore2_06_dashboards_expanded")

        # Поиск "задвиж" в дереве
        print("Поиск задвиж в дереве")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("задвиж")
            time.sleep(3)
            save(page, "explore2_07_search_valve")
            search.fill("")
            time.sleep(1)
        except Exception as e:
            print(f"Поиск не удался: {e}")

        # 5. Проверка разных URL справки
        print("Проверяем URL справки")
        for doc_path in [
            "/static/docs/index.htm",
            "/static/docs/introduction.htm",
            "/static/docs/introduction.html",
            "/static/docs/index.html",
            "/static/docs/",
            "/docs/index.html",
            "/docs/introduction.html",
        ]:
            try:
                print(f"Пробуем {doc_path}")
                page.goto(f"{BASE_URL}{doc_path}", timeout=30000)
                time.sleep(3)
                save(page, f"explore2_08_help_{doc_path.replace('/', '_').replace('.', '_')}")
            except Exception as e:
                print(f"Ошибка {doc_path}: {e}")

        # 6. Проверяем URL демо-приложений
        print("Проверяем URL приложений")
        for app_url in [
            "/web/apps",
            "/web/app",
            "/web/application",
            "/web/#apps",
            "/web/#application",
        ]:
            try:
                print(f"Пробуем {app_url}")
                page.goto(f"{BASE_URL}{app_url}", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                save(page, f"explore2_09_app_{app_url.replace('/', '_').replace('#', '')}")
            except Exception as e:
                print(f"Ошибка {app_url}: {e}")

        # 7. Возвращаемся в web/ и ищем переключатель приложений
        print("Ищем переключатель приложений")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        save(page, "explore2_10_web_home")

        # Ищем элементы, похожие на переключатель приложений или домашнюю иконку
        try:
            page.click("[title='Главная']", timeout=3000)
            time.sleep(3)
            save(page, "explore2_11_home_click")
        except Exception as e:
            print(f"Клик по главной не удался: {e}")

        # 8. Проверяем меню пользователя (шестеренка / аватар)
        print("Открываем меню пользователя")
        try:
            page.click("[data-testid='settings-icon']", timeout=3000)
            time.sleep(2)
            save(page, "explore2_12_settings_menu")
        except Exception:
            try:
                page.click("button:has([data-icon])", timeout=3000)
                time.sleep(2)
                save(page, "explore2_12_settings_menu")
            except Exception as e:
                print(f"Меню настроек не открылось: {e}")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "explore2_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Исследование 2 завершено")


if __name__ == "__main__":
    main()
