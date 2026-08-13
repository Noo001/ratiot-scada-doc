#!/usr/bin/env python3
"""Скриншоты для кейса 2: токен в URL не авторизует."""

import asyncio
import json
import ssl
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = "https://localhost:8443"
OUT_DIR = Path(__file__).parent / "screenshots"


def get_token():
    payload = json.dumps({"username": "admin", "password": "admin"}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/rest/auth",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
        return data["token"]


async def main():
    token = get_token()
    dashboard_url = f"{BASE_URL}/web/dashboards/users.admin.dashboards.default?token={token}"

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

        # Обычная страница логина
        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_selector("input", state="visible")
        await page.screenshot(path=str(OUT_DIR / "02_token_url_login.png"))
        print("[OK] screenshot: 02_token_url_login.png")

        # Открываем URL с токеном
        await page.goto(dashboard_url)
        await page.wait_for_timeout(5000)
        await page.screenshot(path=str(OUT_DIR / "02_token_url_dashboard.png"))
        print("[OK] screenshot: 02_token_url_dashboard.png")

        await browser.close()


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    asyncio.run(main())
