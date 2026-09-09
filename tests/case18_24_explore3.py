#!/usr/bin/env python3
"""Третий этап: открытие SCADA/HMI приложения и тестирование кейсов 18-22."""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

console_errors = []
page_errors = []


def save(page, name: str, full_page=True):
    path = SCREENSHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page)
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
    save(page, "explore3_01_after_login")


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

        # Открываем контейнер Приложения
        print("Открываем Приложения")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        page.click("text=Приложения", timeout=10000)
        time.sleep(3)
        save(page, "explore3_02_applications")

        # Кликаем SCADA/HMI
        print("Открываем SCADA/HMI")
        page.click("text=SCADA/HMI", timeout=10000)
        time.sleep(5)
        save(page, "explore3_03_scada_hmi_app")

        # Даём время на загрузку приложения и сохраняем текущий URL
        current_url = page.url
        print(f"URL после открытия SCADA/HMI: {current_url}")

        # Пробуем найти ссылки "Документация" и "Онлайн"
        print("Ищем ссылки Документация и Онлайн")
        for text in ["Документация", "Онлайн", "Documentation", "Online"]:
            try:
                links = page.locator(f"text={text}").all()
                for link in links:
                    if link.is_visible():
                        print(f"Найдена ссылка '{text}', кликаем")
                        link.click()
                        time.sleep(4)
                        save(page, f"explore3_04_case18_{text.lower()}_clicked")
                        page.goto(current_url, timeout=60000)
                        page.wait_for_load_state("networkidle", timeout=60000)
                        time.sleep(3)
                        break
            except Exception as e:
                print(f"Ошибка при клике '{text}': {e}")

        # Поиск "Тревоги" в дереве приложения
        print("Ищем Тревоги")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Тревоги")
            time.sleep(3)
            save(page, "explore3_05_search_alarms")
            search.fill("")
            time.sleep(1)
        except Exception as e:
            print(f"Поиск не удался: {e}")

        # Поиск "dashboard" / "дашборд" / "home"
        for term in ["dashboard", "дашборд", "Главная", "Home", "Дом"]:
            try:
                print(f"Поиск '{term}'")
                search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
                search.fill(term)
                time.sleep(2)
                save(page, f"explore3_06_search_{term.lower()}")
                search.fill("")
                time.sleep(1)
            except Exception as e:
                print(f"Поиск '{term}' не удался: {e}")

        # Раскрываем дерево, ищем дашборды
        print("Раскрываем элементы дерева")
        try:
            # Пробуем кликнуть на стрелки раскрытия
            toggles = page.locator("[role='treeitem'] [aria-expanded='false']").all()
            print(f"Найдено {len(toggles)} свернутых элементов дерева")
            for i, toggle in enumerate(toggles[:10]):
                try:
                    toggle.click()
                    time.sleep(1)
                except Exception:
                    pass
            save(page, "explore3_07_tree_expanded")
        except Exception as e:
            print(f"Ошибка раскрытия дерева: {e}")

        # Пробуем открыть любой дашборд по ссылке
        print("Ищем дашборды в дереве")
        try:
            dashboard_links = page.locator("text=Dashboard").all()
            print(f"Найдено Dashboard: {len(dashboard_links)}")
            for i, link in enumerate(dashboard_links[:3]):
                try:
                    if link.is_visible():
                        link.click()
                        time.sleep(5)
                        save(page, f"explore3_08_dashboard_{i}")
                except Exception as e:
                    print(f"Ошибка открытия дашборда {i}: {e}")
        except Exception as e:
            print(f"Ошибка поиска дашбордов: {e}")

        # Проверяем URL приложения для редактирования демо
        print("Пробуем URL редактирования демо")
        for path in [
            "/web/app/scada",
            "/web/application/scada",
            "/web/apps/scada",
        ]:
            try:
                page.goto(f"{BASE_URL}{path}", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                save(page, f"explore3_09_app_url_{path.replace('/', '_')}")
            except Exception as e:
                print(f"Ошибка URL {path}: {e}")

        # Возвращаемся в SCADA/HMI приложение
        print("Возвращаемся в SCADA/HMI")
        page.goto(current_url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        save(page, "explore3_10_back_to_scada")

        # Пробуем открыть дашборд через древовидный поиск
        print("Открываем дашборд Тревоги")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Тревоги")
            time.sleep(3)
            results = page.locator("[role='treeitem']").all()
            for result in results:
                if "Тревоги" in result.text_content():
                    result.click()
                    time.sleep(5)
                    save(page, "explore3_11_alarms_dashboard")
                    break
        except Exception as e:
            print(f"Не удалось открыть дашборд тревог: {e}")

        # Поиск шаблонов
        print("Поиск шаблонов")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Шаблон")
            time.sleep(3)
            save(page, "explore3_12_search_templates")
        except Exception as e:
            print(f"Поиск шаблонов не удался: {e}")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "explore3_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Исследование 3 завершено")


if __name__ == "__main__":
    main()
