#!/usr/bin/env python3
"""Подбор URL для открытия свойств устройства."""

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
    save(page, "case24_url_01_login")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security"],
        )
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 900})
        page = context.new_page()
        login(page)

        urls = [
            "/web/#users.admin.devices.dataCenterManagementDevice1",
            "/web/#context:users.admin.devices.dataCenterManagementDevice1",
            "/web/#context/users.admin.devices.dataCenterManagementDevice1",
            "/context/users.admin.devices.dataCenterManagementDevice1",
            "/users.admin.devices.dataCenterManagementDevice1/properties",
            "/web/#devices:users.admin.devices.dataCenterManagementDevice1",
        ]
        for i, url in enumerate(urls):
            try:
                print(f"Пробуем {url}")
                page.goto(f"{BASE_URL}{url}", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(5)
                save(page, f"case24_url_{i}_{url.replace('/', '_').replace('#', '')}")
            except Exception as e:
                print(f"Ошибка {url}: {e}")

        browser.close()


if __name__ == "__main__":
    main()
