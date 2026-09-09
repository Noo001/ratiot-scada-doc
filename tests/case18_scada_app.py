#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Открыть приложение SCADA/HMI и найти демо-дашборд (кейс 18)."""
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
    time.sleep(3)
    print(f"После логина: {page.url}")

    # Прямые URL приложения
    for url in [
        "https://localhost:8443/web/applications/users.admin.applications.scada",
        "https://localhost:8443/web/users.admin.applications.scada",
    ]:
        try:
            page.goto(url, timeout=20000)
            time.sleep(4)
            txt = page.locator("body").inner_text()[:150].replace("\n", " ")
            print(f"{url.split('/web/')[1]}: body='{txt[:100]}'")
            if "404" not in txt:
                page.screenshot(path=str(OUT_DIR / "case18_scada_app.png"))
                # вкладка Ресурсы
                try:
                    page.locator("text=Ресурсы").first.click()
                    time.sleep(4)
                    page.screenshot(path=str(OUT_DIR / "case18_scada_resources.png"))
                    print("Ресурсы открыты")
                    # поиск демо
                    body = page.locator("body").inner_text()
                    for line in body.split("\n"):
                        if "емо" in line:
                            print(f"  строка: {line[:80]}")
                except Exception as e:
                    print(f"Ресурсы: {e}")
                break
        except Exception as e:
            print(f"{url}: ошибка {e}")
    browser.close()
