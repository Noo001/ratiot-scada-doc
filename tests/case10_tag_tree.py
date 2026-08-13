#!/usr/bin/env python3
"""Кейс 10: дерево тегов — абсолютная модель как источник."""

import asyncio
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
ADMIN = {"username": "admin", "password": "admin"}

SCREENSHOTS = {
    "tag_tree": "tests/screenshots/case10_tag_tree.png",
    "source_dialog": "tests/screenshots/case10_source_dialog.png",
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

        # Переходим в дерево тегов
        await page.goto(f"{BASE_URL}/web/")
        await page.wait_for_timeout(3000)

        # Ищем "Дерево тегов", "Tag tree" или "tags" через поиск в дереве
        search_input = page.locator("[placeholder*='Поиск в системном дереве']").first
        await search_input.fill("тег")
        await page.wait_for_timeout(2000)

        tag_items = await page.locator("text=тег, text=tag").all()
        print(f"[INFO] Найдено элементов 'Дерево тегов': {len(tag_items)}")
        if tag_items:
            for item in tag_items:
                try:
                    if await item.is_visible():
                        await item.click()
                        await page.wait_for_timeout(3000)
                        break
                except Exception:
                    pass
        else:
            print("[WARN] Дерево тегов не найдено")

        await page.screenshot(path=SCREENSHOTS["tag_tree"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['tag_tree']}")

        # Пробуем найти кнопку/ссылку "Источник"
        source_items = await page.locator("text=Источник, text=Source").all()
        print(f"[INFO] Найдено элементов 'Источник': {len(source_items)}")
        if source_items:
            for item in source_items:
                try:
                    if await item.is_visible():
                        await item.click()
                        await page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass

        await page.screenshot(path=SCREENSHOTS["source_dialog"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['source_dialog']}")

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
