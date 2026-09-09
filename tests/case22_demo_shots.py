#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Снять скриншоты всех демо-решений и разделов «Обзор UI компонентов»."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots") / "case22_demos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEMOS = [
    "Линия бутилирования",
    "Фильтровальная станция",
    "Хранилище пастеризованного молока",
    "Магистральный газопровод",
    "Интеллектуальная энергосистема",
    "Контейнеры",
    "Отображение данных",
    "Ввод данных",
    "Навигация",
    "Графики",
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
    time.sleep(4)

    page.locator("text=Каталог демо").first.click()
    time.sleep(4)

    for name in DEMOS:
        try:
            page.locator(f"text={name}").first.click()
            time.sleep(2)
            open_btn = page.locator("button:has-text('Открыть')").locator("visible=true").first
            if not open_btn.is_visible():
                print(f"{name}: нет кнопки Открыть")
                continue
            popup = None
            try:
                with page.expect_popup(timeout=4000) as pi:
                    open_btn.click()
                popup = pi.value
            except Exception:
                open_btn.click()
            time.sleep(7)
            target = popup or page
            safe = name.replace(" ", "_")[:30]
            target.screenshot(path=str(OUT_DIR / f"demo_{safe}.png"))
            print(f"{name}: {target.url}")
            if popup:
                popup.close()
                time.sleep(2)
            else:
                page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaDemos?tab=ui")
                time.sleep(4)
        except Exception as e:
            print(f"{name}: ошибка {str(e)[:120]}")
    browser.close()
    print("Готово.")
