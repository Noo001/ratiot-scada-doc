#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: открыть свойства local_system, проверить подсказку и список поля «Активные переменные/функции/события»."""
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

    # Раскрыть «Устройства»
    dev = page.locator("text=Устройства").first
    box = dev.bounding_box()
    page.mouse.click(box["x"] - 15, box["y"] + box["height"] / 2)
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case24_64111_tree.png"))

    # Двойной клик по local_system
    node = page.locator("text=local_system").first
    node.dblclick()
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case24_64111_props.png"))

    body = page.locator("body").inner_text()
    print("Свойства открыты:", "Активные переменные" in body)

    # Hover на подсказку [?] поля «Активные переменные/функции/события»
    label = page.locator("text=Активные переменные/функции/").first
    lb = label.bounding_box()
    print(f"Метка: {lb}")
    # Знак [?] обычно сразу после текста метки
    page.mouse.move(lb["x"] + lb["width"] + 8, lb["y"] + lb["height"] / 2)
    time.sleep(2.5)
    page.screenshot(path=str(OUT_DIR / "case24_64111_tooltip.png"))
    # Дамп tooltip
    tips = page.locator("[role='tooltip'], [class*='tooltip'], [class*='hint']").all()
    for t in tips:
        try:
            if t.is_visible():
                print("TOOLTIP:", t.inner_text().strip()[:300])
        except Exception:
            pass

    # Раскрыть список значений поля
    label.click()
    time.sleep(1)
    page.keyboard.press("Escape")
    # Клик по селекту справа от метки
    row = page.locator("div", has_text="Активные переменные/функции/").last
    sel = page.locator("text=Все").last
    sb = sel.bounding_box()
    print(f"Селект: {sb}")
    page.mouse.click(sb["x"] + sb["width"] / 2, sb["y"] + sb["height"] / 2)
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_values.png"))
    opts = page.locator("[class*='select'] [class*='option'], [role='option']").all()
    for o in opts:
        try:
            if o.is_visible():
                t = o.inner_text().strip()
                if t:
                    print("ОПЦИЯ:", t[:80])
        except Exception:
            pass
    browser.close()
    print("Готово.")
