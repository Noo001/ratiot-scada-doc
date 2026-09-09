#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: мастер «Локальная Система» → свойства → подсказка и список поля «Активные переменные/функции/события»."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

def click_option(page, text):
    for sel in ["[class*='select'] [class*='option']", "[role='option']", "[role='listbox'] [class*='item']"]:
        for o in page.locator(sel).all():
            try:
                if o.is_visible() and text in o.inner_text():
                    o.click()
                    return True
            except Exception:
                pass
    return False

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

    page.locator("text=Устройства").first.click(button="right")
    time.sleep(2)
    page.locator("text=Добавить устройство").first.click()
    time.sleep(4)
    page.locator("text=Выберите драйвер").first.click()
    time.sleep(1.5)
    click_option(page, "Локальная Система")
    time.sleep(1)
    page.locator("button:has-text('OK')").last.click()
    time.sleep(8)

    body = page.locator("body").inner_text()
    print("Свойства открыты:", "Активные переменные" in body)
    page.screenshot(path=str(OUT_DIR / "case24_64111_props2.png"))

    # Hover на подсказку [?] рядом с меткой поля
    label = page.locator("text=Активные переменные/функции/").first
    lb = label.bounding_box()
    print(f"Метка: x={lb['x']:.0f} y={lb['y']:.0f} w={lb['width']:.0f} h={lb['height']:.0f}")
    page.mouse.move(lb["x"] + lb["width"] + 10, lb["y"] + lb["height"] / 2)
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case24_64111_tooltip.png"))
    for t in page.locator("[role='tooltip'], [class*='tooltip'], [class*='hint']").all():
        try:
            if t.is_visible():
                print("TOOLTIP:", t.inner_text().strip()[:400])
        except Exception:
            pass

    # Клик по селекту значения (строка той же высоты, что метка, правая колонка)
    page.mouse.click(1024, lb["y"] + lb["height"] / 2)
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case24_64111_values.png"))
    for o in page.locator("[class*='select'] [class*='option'], [role='option']").all():
        try:
            if o.is_visible():
                t = o.inner_text().strip()
                if t:
                    print("ОПЦИЯ:", t[:80])
        except Exception:
            pass
    browser.close()
    print("Готово.")
