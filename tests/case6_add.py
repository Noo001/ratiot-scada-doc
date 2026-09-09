#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: попытка создать тег в дереве тегов — поиск кнопки добавления."""
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

    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)

    # наводим на правый верхний угол таблицы (иконка около поиска тегов)
    page.mouse.move(1525, 160)
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case6_64111_corner_hover.png"))

    # перечислим все кнопки и иконки в области дашборда
    btns = page.locator("main button, [class*='dashboard'] button, [role='button']")
    print(f"Кнопок на дашборде: {btns.count()}")
    for i in range(btns.count()):
        try:
            b = btns.nth(i)
            t = b.inner_text().strip()[:30]
            ti = b.get_attribute("title") or ""
            vis = b.is_visible()
            if vis:
                print(f"  [{i}] text='{t}' title='{ti}'")
        except Exception:
            pass

    # Попробуем режим редактирования
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags?mode=EDIT")
    time.sleep(8)
    page.screenshot(path=str(OUT_DIR / "case6_64111_edit.png"))
    print(f"edit url: {page.url}")
    browser.close()
    print("Готово.")
