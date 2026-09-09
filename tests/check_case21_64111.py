#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка кейса 21 (ASD-6499) на 6.41.11: бесконечная загрузка и JS-ошибка демо-проектов."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

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

    # сборщик ошибок
    page.evaluate("""
        window.__errors = [];
        const origError = console.error;
        console.error = function(...args) { window.__errors.push(args.map(a => String(a)).join(' ')); origError.apply(console, args); };
        window.addEventListener('error', e => window.__errors.push(e.message));
        window.addEventListener('unhandledrejection', e => window.__errors.push(String(e.reason || 'null')));
    """)

    summary = {"steps": []}

    def log(msg):
        summary["steps"].append(msg)
        print(msg)

    # 1. Открыть системное дерево через иконку слева, затем поиск
    page.goto("https://localhost:8443/web/dashboards")
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case21_01_dashboards.png"))
    log(f"URL дашбордов: {page.url}")

    # клик по иконке дерева в левой панели (первая иконка)
    try:
        page.locator(".anticon-appstore, [class*='appstore'], aside svg, .left-panel svg, .sidebar svg").first.click()
        time.sleep(2)
        page.screenshot(path=str(OUT_DIR / "case21_01b_tree.png"))
    except Exception as e:
        log(f"Не удалось открыть дерево: {e}")

    # 2. Поиск в дереве ioField / milkStorage
    try:
        search = page.locator("input[placeholder='Поиск в системном дереве']").first
        search.fill("ioField")
        time.sleep(1.5)
        page.screenshot(path=str(OUT_DIR / "case21_02_search_iofield.png"))
        result = page.locator(".system-tree-context-name").filter(has_text="ioField").first
        if result.is_visible():
            result.click()
            time.sleep(3)
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(OUT_DIR / "case21_03_iofield_view.png"))
            log(f"Открыт ioField: {page.url}")
    except Exception as e:
        log(f"Ошибка открытия ioField: {e}")

    # 3. Открыть в режиме редактирования
    try:
        page.evaluate("() => window.__errors = []")
        page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.ioField/edit")
        page.wait_for_load_state("networkidle")
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case21_04_iofield_edit.png"))
        errors = page.evaluate("() => window.__errors")
        summary["edit_errors"] = errors
        summary["edit_url"] = page.url
        log(f"Редактор ioField: {page.url}, ошибок JS: {len(errors)}")
        for e in errors[:10]:
            log(f"  - {e[:200]}")
    except Exception as e:
        log(f"Ошибка открытия редактора: {e}")

    # 4. milkStorage
    try:
        page.evaluate("() => window.__errors = []")
        page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.milkStorage/edit")
        page.wait_for_load_state("networkidle")
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case21_05_milkstorage_edit.png"))
        errors = page.evaluate("() => window.__errors")
        summary["milk_errors"] = errors
        log(f"Редактор milkStorage: {page.url}, ошибок JS: {len(errors)}")
        for e in errors[:10]:
            log(f"  - {e[:200]}")
    except Exception as e:
        log(f"Ошибка milkStorage: {e}")

    (OUT_DIR / "case21_64111_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    browser.close()
    print("Готово.")
