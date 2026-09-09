#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Логин -> меню приложений (grid-иконка слева) -> SCADA/HMI -> поиск демо-дашборда."""
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
    time.sleep(5)
    print(f"После логина: {page.url}")

    # grid-иконка меню приложений в левой панели
    page.mouse.click(22, 75)
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "case18_app_menu.png"))
    body = page.locator("body").inner_text()
    print("Меню открыто, текст:", body[:200].replace("\n", " | "))

    # клик по SCADA/HMI в меню
    try:
        page.locator("text=SCADA/HMI").first.click()
        time.sleep(6)
        print(f"После клика SCADA/HMI: {page.url}")
        page.screenshot(path=str(OUT_DIR / "case18_scada_app_open.png"))
        # вкладки приложения
        for tab in ["Конфигурация", "Ресурсы", "События", "Визуализация"]:
            try:
                t = page.locator(f"[role='tab']:has-text('{tab}'), text={tab}").first
                print(f"  вкладка {tab}: count={page.locator(f'text={tab}').count()}")
            except Exception:
                pass
    except Exception as e:
        print(f"Клик SCADA/HMI не удался: {e}")
    browser.close()
