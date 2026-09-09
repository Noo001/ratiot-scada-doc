#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скриншот кейса 27: прямые ссылки на настройки сервера и лицензию возвращают JSON 404."""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

URLS = [
    ("https://localhost:8443/web/context/users.admin.server.properties", "case27_server_settings_url.png"),
    ("https://localhost:8443/web/context/users.admin.licenseInfo", "case27_license_info_url.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1400, "height": 800}, ignore_https_errors=True)
    page = context.new_page()

    for url, filename in URLS:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.screenshot(path=str(OUT_DIR / filename))

    browser.close()
    print("Скриншоты сохранены.")
