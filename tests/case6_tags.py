#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: открыть «Теги» из дерева, создать тег, посмотреть выбор источника."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
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

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.alertsMonitoring")
    time.sleep(6)

    search = page.locator("input[placeholder='Поиск в системном дереве']").first
    search.fill("теги")
    time.sleep(3)

    # клик по листовому узлу «Теги» (точное совпадение)
    popup = None
    try:
        with page.expect_popup(timeout=5000) as pi:
            page.locator(".system-tree-context-name", has_text="Теги").first.click()
        popup = pi.value
    except Exception:
        try:
            page.locator(".system-tree-context-name", has_text="Теги").first.click()
        except Exception as e:
            print(f"Клик не удался: {str(e)[:150]}")
    time.sleep(6)
    target = popup or page
    print(f"После клика: {target.url}")
    target.screenshot(path=str(OUT_DIR / "case6_64111_tags_open.png"))

    # ищем кнопки создания
    time.sleep(2)
    for btn_text in ("Создать", "Добавить"):
        b = target.locator(f"button:has-text('{btn_text}')").locator("visible=true")
        print(f"кнопок «{btn_text}»: {b.count()}")
    body = target.locator("body").inner_text()
    print("текст:", body[:300].replace("\n", " | "))
    target.screenshot(path=str(OUT_DIR / "case6_64111_tags_page.png"))
    browser.close()
    print("Готово.")
