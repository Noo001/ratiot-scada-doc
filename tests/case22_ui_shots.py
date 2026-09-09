#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Снять скриншоты разделов «Обзор UI компонентов» (кнопка Открыть там может отсутствовать — открываем по клику на элемент)."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots") / "case22_demos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ITEMS = ["Контейнеры", "Отображение данных", "Ввод данных", "Навигация", "Графики"]

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
    page.screenshot(path=str(OUT_DIR / "ui_tree.png"))

    for name in ITEMS:
        try:
            page.locator(f"text={name}").first.click()
            time.sleep(3)
            page.screenshot(path=str(OUT_DIR / f"ui_select_{name.replace(' ', '_')[:25]}.png"))
            # есть ли кнопка Открыть?
            open_btns = page.locator("button:has-text('Открыть')").locator("visible=true")
            if open_btns.count() > 0:
                popup = None
                try:
                    with page.expect_popup(timeout=4000) as pi:
                        open_btns.first.click()
                    popup = pi.value
                except Exception:
                    open_btns.first.click()
                time.sleep(7)
                target = popup or page
                safe = name.replace(" ", "_")[:25]
                target.screenshot(path=str(OUT_DIR / f"ui_{safe}.png"))
                print(f"{name}: открыто {target.url}")
                if popup:
                    popup.close()
                    time.sleep(2)
                else:
                    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaDemos?tab=ui")
                    time.sleep(4)
            else:
                print(f"{name}: кнопки Открыть нет, скриншот выбора сохранён")
        except Exception as e:
            print(f"{name}: ошибка {str(e)[:120]}")
    browser.close()
    print("Готово.")
