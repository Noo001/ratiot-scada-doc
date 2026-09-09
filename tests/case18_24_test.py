#!/usr/bin/env python3
"""Финальное тестирование кейсов 18-24 и поиск новых багов."""

import sys
import io
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    save(page, "test_01_after_login")


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

        # Кейс 19: дашборд alerts
        print("Кейс 19: открываем дашборд alerts")
        page.goto(f"{BASE_URL}/users.admin.dashboards.alerts", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        save(page, "test_case19_alerts_dashboard")

        # Проверяем дашборд alertsMonitoring
        print("Открываем alertsMonitoring")
        page.goto(f"{BASE_URL}/users.admin.dashboards.alertsMonitoring", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        save(page, "test_case19_alerts_monitoring")

        # Кейс 18: ищем ссылки на дашборде alertsMonitoring
        print("Кейс 18: ищем ссылки Документация/Онлайн")
        link_targets = []
        for text in ["Документация", "Онлайн", "Documentation", "Online", "Docs", "Web"]:
            try:
                links = page.locator(f"a:has-text('{text}'), button:has-text('{text}')").all()
                for link in links:
                    try:
                        if link.is_visible():
                            href = link.get_attribute("href") or link.get_attribute("data-href") or "(no href)"
                            print(f"Найдена ссылка '{text}': href={href}")
                            link_targets.append((text, href))
                    except Exception:
                        pass
            except Exception as e:
                print(f"Ошибка поиска '{text}': {e}")
        # Сохраняем скриншот текущего дашборда для кейса 18
        save(page, "test_case18_alerts_monitoring_links")

        # Кейс 22: проверяем справку по разным URL
        print("Кейс 22: проверяем URL справки")
        for doc_url in [
            "/web/static/docs/index.htm",
            "/web/static/docs/introduction.htm",
            "/admin/custom/templates/docs/index.htm",
            "/admin/custom/templates/docs/introduction.htm",
            "/static/docs/introduction.htm",
            "/docs/index.htm",
            "/help/index.htm",
        ]:
            try:
                print(f"Пробуем {doc_url}")
                page.goto(f"{BASE_URL}{doc_url}", timeout=30000)
                time.sleep(3)
                save(page, f"test_case22_help_{doc_url.replace('/', '_').replace('.', '_')}")
            except Exception as e:
                print(f"Ошибка {doc_url}: {e}")

        # Кейс 24: создаём устройство
        print("Кейс 24: создаём устройство")
        page.goto(f"{BASE_URL}/web/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        try:
            page.click("text=Устройства", timeout=10000)
            time.sleep(2)
            page.click("text=Создать", timeout=10000)
            time.sleep(3)
            save(page, "test_case24_create_device")
        except Exception as e:
            print(f"Создание устройства не удалось: {e}")
            save(page, "test_case24_create_device_error")

        # Пробуем открыть другие дашборды
        print("Проверяем другие дашборды")
        for dash in ["devices", "globalSearch", "container", "class"]:
            try:
                url = f"{BASE_URL}/users.admin.dashboards.{dash}"
                print(f"Пробуем {url}")
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                save(page, f"test_dashboard_{dash}")
            except Exception as e:
                print(f"Ошибка {dash}: {e}")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "test_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Тестирование завершено")


if __name__ == "__main__":
    main()
