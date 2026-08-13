#!/usr/bin/env python3
"""Кейс 8: импорт/экспорт Modbus регистров."""

import asyncio
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://localhost:8443"
ADMIN = {"username": "admin", "password": "admin"}

SCREENSHOTS = {
    "devices": "tests/screenshots/case8_devices.png",
    "modbus_empty": "tests/screenshots/case8_modbus_empty.png",
    "modbus_registers": "tests/screenshots/case8_modbus_registers.png",
    "export_dialog": "tests/screenshots/case8_export_dialog.png",
    "csv_encoding": "tests/screenshots/case8_csv_encoding.png",
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

        # Переходим к устройствам через системное дерево
        await page.goto(f"{BASE_URL}/web/")
        await page.wait_for_timeout(4000)

        # Раскрываем раздел "Устройства"
        device_nodes = await page.locator("text=Устройства").all()
        for node in device_nodes:
            try:
                if await node.is_visible():
                    await node.click()
                    await page.wait_for_timeout(1500)
                    break
            except Exception:
                pass

        await page.screenshot(path=SCREENSHOTS["devices"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['devices']}")

        # Пробуем найти существующий modbus
        # Создаём новое устройство
        create_btns = await page.locator("button:has-text('Создать')").all()
        print(f"[INFO] Найдено кнопок Создать: {len(create_btns)}")
        if create_btns:
            await create_btns[0].click()
            await page.wait_for_timeout(3000)
            # Открываем выпадающий список драйверов
            await page.locator("text=Выберите драйвер").first.click()
            await page.wait_for_timeout(2000)
            # Ищем Modbus в выпадающем списке
            modbus_items = await page.locator("text=Modbus, text=modbus").all()
            print(f"[INFO] Найдено Modbus в диалоге: {len(modbus_items)}")
            if modbus_items:
                await modbus_items[0].click()
                await page.wait_for_timeout(3000)
        else:
            print("[WARN] Кнопка Создать не найдена")

        await page.screenshot(path=SCREENSHOTS["modbus_empty"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['modbus_empty']}")

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
