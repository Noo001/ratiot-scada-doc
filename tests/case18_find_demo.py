#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Найти стартовый демо-дашборд с блоками Документация/Онлайн (кейс 18)."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

CANDIDATES = [
    "scadaDemo", "scadaDemos", "demo", "demoHome", "home", "scadaHome",
    "welcome", "start", "scada", "main", "dashboard", "homePage",
]

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

    for name in CANDIDATES:
        url = f"https://localhost:8443/web/dashboards/users.admin.dashboards.{name}"
        try:
            page.goto(url, timeout=20000)
            time.sleep(4)
            txt = page.locator("body").inner_text()[:200].replace("\n", " ")
            found = []
            for t in ["Документация", "Онлайн", "404"]:
                if page.locator(f"text={t}").count() > 0:
                    found.append(t)
            print(f"{name}: url={page.url.split('/')[-1]} markers={found} body='{txt[:120]}'")
            if "Документация" in found:
                page.screenshot(path=str(OUT_DIR / f"case18_found_{name}.png"))
        except Exception as e:
            print(f"{name}: ошибка {e}")
    browser.close()
