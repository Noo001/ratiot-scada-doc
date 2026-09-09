#!/usr/bin/env python3
"""Четвёртый этап: открытие дашбордов SCADA/HMI, поиск ссылок, тревог, шаблонов."""

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
    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    save(page, "explore4_01_after_login")


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

        # Открываем SCADA/HMI приложение через Визуализацию
        print("Открываем дашборд administration")
        for dash_url in [
            f"{BASE_URL}/users.admin.dashboards.administration",
            f"{BASE_URL}/web/users.admin.dashboards.administration",
            f"{BASE_URL}/web/#dashboards:users.admin.dashboards.administration",
        ]:
            try:
                print(f"Пробуем {dash_url}")
                page.goto(dash_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(8)
                save(page, f"explore4_02_dash_admin_{dash_url.replace(BASE_URL, '').replace('/', '_').replace('#', '')}")
            except Exception as e:
                print(f"Ошибка {dash_url}: {e}")

        # Пробуем нажать Визуализация на странице приложения
        print("Открываем свойства SCADA/HMI и Визуализацию")
        page.goto(f"{BASE_URL}/users.admin.applications.scada", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        save(page, "explore4_03_scada_props")

        try:
            page.click("text=Визуализация", timeout=10000)
            time.sleep(5)
            save(page, "explore4_04_scada_visualization")
        except Exception as e:
            print(f"Визуализация не открылась: {e}")

        # Пробуем перейти в дашборд administration из visualization
        print("Переходим к дашборду administration")
        page.goto(f"{BASE_URL}/users.admin.dashboards.administration", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(8)
        save(page, "explore4_05_dash_admin_direct")

        # Ищем ссылки Документация/Онлайн на дашборде
        print("Ищем ссылки Документация/Онлайн")
        for text in ["Документация", "Онлайн", "Documentation", "Online", "Docs"]:
            try:
                links = page.locator(f"text={text}").all()
                for link in links:
                    if link.is_visible():
                        print(f"Найдена ссылка '{text}', кликаем")
                        link.click()
                        time.sleep(5)
                        save(page, f"explore4_06_case18_{text.lower()}_clicked")
                        # Возвращаемся
                        page.goto(f"{BASE_URL}/users.admin.dashboards.administration", timeout=60000)
                        page.wait_for_load_state("networkidle", timeout=60000)
                        time.sleep(5)
                        break
            except Exception as e:
                print(f"Ошибка '{text}': {e}")

        # Пробуем открыть дашборд Тревоги
        print("Открываем дашборд alerts")
        for dash_url in [
            f"{BASE_URL}/users.admin.dashboards.alerts",
            f"{BASE_URL}/users.admin.dashboards.alertsMonitoring",
        ]:
            try:
                print(f"Пробуем {dash_url}")
                page.goto(dash_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(8)
                save(page, f"explore4_07_{dash_url.split('/')[-1]}")
            except Exception as e:
                print(f"Ошибка {dash_url}: {e}")

        # Пробуем редактировать дашборд
        print("Редактируем дашборд administration")
        page.goto(f"{BASE_URL}/users.admin.dashboards.administration", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(5)
        try:
            edit_btn = page.locator("button:has-text('Редактировать'), button[title='Редактировать'], [aria-label='Редактировать']").first
            if edit_btn.is_visible():
                edit_btn.click()
                time.sleep(8)
                save(page, "explore4_08_dash_admin_edit")
        except Exception as e:
            print(f"Редактирование недоступно: {e}")
            save(page, "explore4_08_dash_admin_edit_error")

        # Пробуем URL редактирования дашборда
        print("Пробуем URL редактирования")
        for edit_url in [
            f"{BASE_URL}/users.admin.dashboards.administration/edit",
            f"{BASE_URL}/web/users.admin.dashboards.administration/edit",
        ]:
            try:
                print(f"Пробуем {edit_url}")
                page.goto(edit_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(8)
                save(page, f"explore4_09_edit_{edit_url.split('/')[-2]}")
            except Exception as e:
                print(f"Ошибка {edit_url}: {e}")

        # Открываем SCADA/HMI приложение и ищем демо-дашборды
        print("Ищем демо-дашборды в приложении")
        page.goto(f"{BASE_URL}/users.admin.applications.scada", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Ресурсы", timeout=5000)
            time.sleep(3)
            save(page, "explore4_10_scada_resources")
        except Exception as e:
            print(f"Ресурсы не открылись: {e}")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "explore4_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Исследование 4 завершено")


if __name__ == "__main__":
    main()
