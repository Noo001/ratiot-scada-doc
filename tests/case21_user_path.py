#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 21 (ASD-6499) на 6.41.11: редактирование демо-проекта пользовательским путём.
Логин -> Центр управления -> поиск демо-проекта -> открытие -> кнопка редактирования."""

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

    # 1. Стартовая страница (Центр управления)
    page.screenshot(path=str(OUT_DIR / "case21_u_01_start.png"))
    log(f"Старт: {page.url}")

    # 2. Ищем всё со словом «Демо» на странице
    demo_links = page.locator("text=/Демо|demo/i")
    n = demo_links.count()
    log(f"Элементов с «Демо/demo» на старте: {n}")
    for i in range(min(n, 20)):
        try:
            el = demo_links.nth(i)
            txt = el.inner_text().strip().replace("\n", " ")[:60]
            log(f"  [{i}] {txt} | visible={el.is_visible()}")
        except Exception:
            pass

    # 3. Попробовать кликнуть на ссылку «Каталог демо-проектов», если есть
    try:
        cat = page.locator("text=Каталог демо").first
        if cat.is_visible():
            cat.click()
            time.sleep(4)
            page.screenshot(path=str(OUT_DIR / "case21_u_02_demo_catalog.png"))
            log(f"Каталог демо: {page.url}")
    except Exception as e:
        log(f"Каталог демо не найден: {e}")

    # 4. Ищем milkStorage / ioField
    for i in range(demo_links.count()):
        try:
            el = demo_links.nth(i)
            if el.is_visible() and ("milk" in el.inner_text().lower() or "milkstorage" in el.inner_text().lower()):
                el.click()
                time.sleep(4)
                page.screenshot(path=str(OUT_DIR / "case21_u_03_milkstorage.png"))
                log(f"Открыт milkStorage: {page.url}")
                break
        except Exception:
            pass

    # 5. Ищем кнопку редактирования на странице дашборда
    time.sleep(3)
    btns = page.locator("[title*='едактир'], [aria-label*='едактир'], button:has-text('Редакт'), [class*='edit']")
    log(f"Кандидатов в кнопку редактирования: {btns.count()}")
    for i in range(min(btns.count(), 10)):
        try:
            b = btns.nth(i)
            log(f"  btn[{i}] title={b.get_attribute('title')} aria={b.get_attribute('aria-label')} visible={b.is_visible()}")
        except Exception:
            pass

    errors.clear()
    try:
        edit_btn = page.locator("[title*='Редакт'], button:has-text('Редактировать'), [aria-label*='Редакт']").first
        if edit_btn.is_visible():
            edit_btn.click()
            time.sleep(8)
            page.screenshot(path=str(OUT_DIR / "case21_u_04_edit_mode.png"))
            log(f"После клика «Редактировать»: {page.url}")
            log(f"Ошибок JS: {len(errors)}")
            for e in errors[:10]:
                log(f"  {e[:220]}")
        else:
            log("Кнопка редактирования не видна — смотри скриншот страницы")
    except Exception as e:
        log(f"Клик по «Редактировать» не удался: {e}")

    summary["errors"] = list(errors)
    (OUT_DIR / "case21_user_path_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
