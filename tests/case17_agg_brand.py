#!/usr/bin/env python3
"""Кейс 17: артефакты бренда AggreGate в Web UI."""

import asyncio
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from playwright.async_api import async_playwright

BASE_URL = "https://localhost:8443"
ADMIN = {"username": "admin", "password": "admin"}
OUT_DIR = Path("tests/screenshots")
OUT_DIR.mkdir(exist_ok=True)


async def screenshot(page, name: str):
    path = OUT_DIR / name
    await page.screenshot(path=str(path), full_page=False)
    print(f"[OK] {path}")
    return path


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

        # 1. Страница логина
        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_load_state("networkidle")
        await screenshot(page, "case17_login.png")

        # 2. Логин
        inputs = await page.locator("input").all()
        await inputs[0].fill(ADMIN["username"])
        await inputs[1].fill(ADMIN["password"])
        await page.locator("button:has-text('Войти')").first.click()
        await page.wait_for_timeout(6000)
        await screenshot(page, "case17_after_login.png")

        await browser.close()
        print("[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
