#!/usr/bin/env python3
"""Уточнение кейса 4: что реально видит саморегистрированный пользователь."""

import asyncio
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
TEST_USER = {
    "username": "testuser02",
    "password": "TestPassword123!",
}

SCREENSHOTS = {
    "login_as_new": "tests/screenshots/05_login_as_new.png",
    "dashboard_header": "tests/screenshots/06_dashboard.png",
    "tree_expanded": "tests/screenshots/04_tree_expanded.png",
    "admin_access_denied": "tests/screenshots/04_admin_access_denied.png",
}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--ignore-certificate-errors", "--ignore-urlfetcher-cert-requests"],
        )
        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        page.set_default_timeout(15000)

        # Логин
        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_selector("input", state="visible")
        inputs = await page.locator("input").all()
        await inputs[0].fill(TEST_USER["username"])
        await inputs[1].fill(TEST_USER["password"])
        await page.locator("button:has-text('Войти')").first.click()
        await page.wait_for_timeout(6000)
        await page.screenshot(path=SCREENSHOTS["login_as_new"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['login_as_new']}")

        # Дашборд с заголовком
        await page.wait_for_timeout(2000)
        await page.screenshot(path=SCREENSHOTS["dashboard_header"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['dashboard_header']}")

        # Попытка найти users.admin в дереве
        admin_nodes = await page.locator("text=users.admin").all()
        print(f"[INFO] Найдено узлов users.admin в дереве: {len(admin_nodes)}")
        admin_node = None
        if admin_nodes:
            admin_node = admin_nodes[0]

        # Раскрываем дерево: найдём все элементы с expander
        expanders = await page.locator("[class*='expand'], [class*='toggle'], .tree-node__toggle, .ag-tree-toggle").all()
        print(f"[INFO] Найдено элементов раскрытия дерева: {len(expanders)}")
        # Просто кликнем по первым нескольким visible элементам дерева слева
        for i, el in enumerate(expanders[:10]):
            try:
                await el.click(force=True)
                await page.wait_for_timeout(500)
            except Exception as e:
                print(f"[WARN] Не удалось кликнуть expander {i}: {e}")

        await page.wait_for_timeout(2000)
        await page.screenshot(path=SCREENSHOTS["tree_expanded"], full_page=True)
        print(f"[OK] Скриншот: {SCREENSHOTS['tree_expanded']}")

        # Если users.admin найден, попробуем кликнуть
        if admin_node:
            try:
                await admin_node.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=SCREENSHOTS["admin_access_denied"], full_page=False)
                print(f"[OK] Скриншот: {SCREENSHOTS['admin_access_denied']}")
            except Exception as e:
                print(f"[WARN] Не удалось кликнуть users.admin: {e}")
        else:
            print("[INFO] users.admin не найден в дереве для testuser02")

        # Выводим заголовок страницы
        title = await page.title()
        print(f"[INFO] Title: {title}")

        # Попробуем получить текст заголовка интерфейса
        header_locators = [
            "header",
            "[class*='header']",
            "[class*='app-bar']",
            "[class*='toolbar']",
        ]
        for sel in header_locators:
            text = await page.locator(sel).first.text_content(timeout=2000).catch(lambda: None)
            if text:
                print(f"[INFO] Header ({sel}): {text[:200]}")
                break

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
