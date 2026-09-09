#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 21 (ASD-6499) на 6.41.11: «Хранилище пастеризованного молока» -> «Изменить».
Пользовательский путь через Демо библиотеку."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()
    page.on("console", lambda m: errors.append(f"[console] {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    summary = {"steps": []}

    def log(msg):
        summary["steps"].append(msg)
        print(msg)

    # 1. Центр управления -> «Каталог демо-проектов»
    page.locator("text=Каталог демо").first.click()
    time.sleep(4)

    # 2. Выбрать «Хранилище пастеризованного молока»
    errors.clear()
    item = page.locator("text=Хранилище пастеризованного молока").first
    item.click()
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case21_u_10_milk_selected.png"))
    log(f"Выбрано демо: {page.url}, ошибок JS: {len(errors)}")

    # 3. Нажать «Изменить»
    page.locator("button:has-text('Изменить')").first.click()
    time.sleep(10)
    page.screenshot(path=str(OUT_DIR / "case21_u_11_milk_edit.png"))
    log(f"Режим «Изменить»: {page.url}")
    log(f"Ошибок JS после открытия редактора: {len(errors)}")
    for e in errors[:15]:
        log(f"  {e[:250]}")

    # 4. Проверить, нет ли бесконечных спиннеров: снять повторный скриншот через 10 с
    time.sleep(10)
    page.screenshot(path=str(OUT_DIR / "case21_u_12_milk_edit_after10s.png"))
    log(f"Повторный скриншот через 10 с, ошибок JS всего: {len(errors)}")

    summary["errors"] = list(errors)
    (OUT_DIR / "case21_edit_user_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
