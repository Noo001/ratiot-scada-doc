#!/usr/bin/env python3
"""Кейс 15: отсутствие локального магазина приложений в веб-клиенте."""

import asyncio
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
ADMIN = {"username": "admin", "password": "admin"}

SCREENSHOTS = {
    "tree_search_store": "tests/screenshots/store_tree_search.png",
    "docs_store": "tests/screenshots/store_docs.png",
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
        await inputs[0].fill(ADMIN["username"])
        await inputs[1].fill(ADMIN["password"])
        await page.locator("button:has-text('Войти')").first.click()
        await page.wait_for_timeout(6000)

        # Поиск "Магазин" в системном дереве
        search = await page.locator("[placeholder*='Поиск'], input[placeholder*='поиск']").all()
        if search:
            await search[0].fill("Магазин")
            await page.wait_for_timeout(2000)
        await page.screenshot(path=SCREENSHOTS["tree_search_store"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['tree_search_store']}")

        # Открыть документацию по магазину (в новой вкладке, чтобы избежать SPA-роутинга)
        doc_page = await context.new_page()
        await doc_page.goto(f"{BASE_URL}/static/docs/ls_store.htm", wait_until="networkidle")
        await doc_page.wait_for_timeout(3000)
        await doc_page.screenshot(path=SCREENSHOTS["docs_store"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['docs_store']}")
        await doc_page.close()

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
