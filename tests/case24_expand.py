#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: раскрыть «Устройства» через экспандер и проверить дочерние узлы."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)

    dev = page.locator("text=Устройства").first
    box = dev.bounding_box()
    # Клик по треугольнику-экспандеру слева от текста
    page.mouse.click(box["x"] - 12, box["y"] + box["height"] / 2)
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case24_64111_devices_expanded.png"))

    # Весь текст левой панели
    left = page.locator("text=Устройства").first
    # Дамп body вокруг узлов
    body = page.locator("body").inner_text()
    idx = body.find("Устройства")
    print(body[max(0, idx - 50):idx + 400].replace("\n", " | "))
    browser.close()
    print("Готово.")
