#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 24: подсказка [?] поля + переключение в «Только выбранные» + вкладка «Метаданные»."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

def open_props(page):
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.tags")
    time.sleep(6)
    search = page.locator("[placeholder*='Поиск в системном дереве']").first
    search.fill("local_system")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(3)
    page.locator("text=local_system").first.click(button="right")
    time.sleep(2)
    page.locator("text=Редактировать свойства аккаунта устройства").first.click()
    time.sleep(6)

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

    open_props(page)
    print("Свойства:", "Активные переменные" in page.locator("body").inner_text())

    # Hover точно на [?] поля (значок сразу после текста «события»)
    label = page.locator("text=Активные переменные/функции/").first
    lb = label.bounding_box()
    qx, qy = lb["x"] + lb["width"] + 8, lb["y"] + lb["height"] - 8
    print(f"Hover на ({qx:.0f}, {qy:.0f})")
    page.mouse.move(qx - 40, qy)  # подведём постепенно
    time.sleep(0.5)
    page.mouse.move(qx, qy)
    time.sleep(3.5)
    page.screenshot(path=str(OUT_DIR / "case24_64111_tooltip2.png"))
    found = False
    for t in page.locator("[role='tooltip']").all():
        try:
            txt = t.inner_text().strip()
            if txt and txt not in ("Объекты", "Теги"):
                print("TOOLTIP:", txt[:500])
                found = True
        except Exception:
            pass
    if not found:
        print("TOOLTIP: (пусто)")

    # Выбрать «Только выбранные»
    page.mouse.click(1024, lb["y"] + lb["height"] / 2)
    time.sleep(1.5)
    page.locator("[class*='select'] [class*='option'], [role='option']").filter(has_text="Только выбранные").first.click()
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "case24_64111_only_selected.png"))
    page.locator("button:has-text('OK')").last.click()
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case24_64111_after_ok.png"))
    body = page.locator("body").inner_text()
    print("После OK, ошибки нет:", "Error" not in body and "Ошибка" not in body)

    # Вкладка «Метаданные»
    open_props(page)
    page.locator("text=Метаданные").first.click()
    time.sleep(5)
    page.screenshot(path=str(OUT_DIR / "case24_64111_metadata_tab.png"))
    body = page.locator("body").inner_text()
    idx = body.find("Метаданные")
    print("Вкладка метаданных:", body[idx:idx+600].replace("\n", " | "))
    browser.close()
    print("Готово.")
