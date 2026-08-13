#!/usr/bin/env python3
"""Кейс 11: NoSQL-хранилище событий."""

import asyncio
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
ADMIN = {"username": "admin", "password": "admin"}

SCREENSHOTS = {
    "settings": "tests/screenshots/case11_settings.png",
    "storage": "tests/screenshots/case11_storage.png",
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

        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_selector("input", state="visible")
        inputs = await page.locator("input").all()
        await inputs[0].fill(ADMIN["username"])
        await inputs[1].fill(ADMIN["password"])
        await page.locator("button:has-text('Войти')").first.click()
        await page.wait_for_timeout(6000)

        await page.goto(f"{BASE_URL}/web/")
        await page.wait_for_timeout(3000)

        # Открываем "Настроить сервер"
        config_btns = await page.locator("button:has-text('Настроить сервер'), button:has-text('Configure server')").all()
        print(f"[INFO] Найдено кнопок настройки сервера: {len(config_btns)}")
        if config_btns:
            await config_btns[0].click()
            await page.wait_for_timeout(3000)

        await page.screenshot(path=SCREENSHOTS["settings"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['settings']}")

        # Ищем вкладку "Хранилище"
        storage_items = await page.locator("[role='tab']:has-text('Хранилище'), [role='tab']:has-text('Storage')").all()
        print(f"[INFO] Найдено вкладок Хранилище: {len(storage_items)}")
        if not storage_items:
            storage_items = await page.locator("text=Хранилище").all()
            print(f"[INFO] Найдено элементов Хранилище: {len(storage_items)}")
        if storage_items:
            for item in storage_items:
                try:
                    if await item.is_visible():
                        await item.click()
                        await page.wait_for_timeout(3000)
                        break
                except Exception:
                    pass

        await page.screenshot(path=SCREENSHOTS["storage"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['storage']}")

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
