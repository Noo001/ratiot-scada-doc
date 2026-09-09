#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6 (ASD-6485): дерево тегов — что доступно как источник."""
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

    # открываем дашборд с системным деревом слева
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.alertsMonitoring")
    time.sleep(6)

    # поиск «теги» в системном дереве
    search = page.locator("input[placeholder='Поиск в системном дереве']").first
    search.fill("теги")
    time.sleep(3)
    items = page.locator(".system-tree-context-name").all()
    print(f"Результатов: {len(items)}")
    targets = []
    for i, r in enumerate(items):
        try:
            t = r.inner_text().strip()
        except Exception:
            continue
        if any(k in t.lower() for k in ("тег", "tag")):
            targets.append((i, t))
            print(f"  [{i}] {t[:70]}")
    page.screenshot(path=str(OUT_DIR / "case6_64111_search.png"))

    # открываем первый подходящий узел (дерево тегов)
    clicked = False
    for i, t in targets:
        try:
            items[i].click()
            time.sleep(5)
            print(f"Клик по [{i}] «{t[:40]}»: {page.url}")
            page.screenshot(path=str(OUT_DIR / "case6_64111_open.png"))
            clicked = True
            break
        except Exception as e:
            print(f"  клик [{i}] не удался: {str(e)[:100]}")

    if clicked:
        # ищем кнопку создания тега
        time.sleep(2)
        body = page.locator("body").inner_text()
        print("--- текст страницы (фрагмент):", body[:400].replace("\n", " | "))
        for btn_text in ("Создать", "Добавить", "Создать тег"):
            b = page.locator(f"button:has-text('{btn_text}')").locator("visible=true")
            print(f"кнопок «{btn_text}»: {b.count()}")
        page.screenshot(path=str(OUT_DIR / "case6_64111_page.png"))

    browser.close()
    print("Готово.")
