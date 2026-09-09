#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 27 (ASD-6505): открыть Server Information — даблклик / контекстное меню корневого узла."""
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

    # Двойной клик по корневому узлу
    page.locator("text=RatioT Server v6.41.11").first.dblclick()
    time.sleep(6)
    body = page.locator("body").inner_text()
    print("После dblclick, Server Information:", "Статус сервера" in body or "Название сервера" in body)
    page.screenshot(path=str(OUT_DIR / "case27_64111_dblclick.png"))

    if "Название сервера" not in body:
        # Контекстное меню корневого узла
        page.locator("text=RatioT Server v6.41.11").first.click(button="right")
        time.sleep(2)
        page.screenshot(path=str(OUT_DIR / "case27_64111_rootmenu.png"))
        seen = set()
        for it in page.locator("[class*='select'] [class*='option'], [role='menuitem'], [class*='contextmenu'] *, [class*='dropdown-menu'] *").all():
            try:
                if it.is_visible():
                    t = it.inner_text().strip().replace("\n", " / ")
                    if t and t not in seen and len(t) < 60:
                        seen.add(t)
                        print("ПУНКТ:", t)
            except Exception:
                pass
        # клик по пункту про информацию/свойства сервера
        for it in page.locator("[class*='select'] [class*='option'], [role='menuitem'], [class*='contextmenu'] *, [class*='dropdown-menu'] *").all():
            try:
                if it.is_visible() and ("Информация" in it.inner_text() or "Свойства" in it.inner_text()):
                    it.click()
                    print("Клик по:", it.inner_text().strip()[:50])
                    break
            except Exception:
                pass
        time.sleep(6)
        page.screenshot(path=str(OUT_DIR / "case27_64111_rootmenu_click.png"))
        body = page.locator("body").inner_text()
        print("После клика, Название сервера:", "Название сервера" in body)

    lic = page.locator("text=Лицензионная информация").first
    print("Вкладка лицензии:", lic.count() > 0)
    if lic.count() > 0:
        lic.click()
        time.sleep(4)
        page.screenshot(path=str(OUT_DIR / "case27_64111_license_tab.png"))
        i = body.find("Лицензионная информация")
        print("лицензия:", page.locator("body").inner_text()[i:i+250].replace("\n", " | "))
    browser.close()
    print("Готово.")
