#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 6: перетащить узел из дерева в таблицу тегов и открыть выбор источника."""
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

    # раскроем «Устройства»
    dev = page.locator("text=Устройства").first
    dev.click()
    time.sleep(3)
    page.screenshot(path=str(OUT_DIR / "case6_64111_devices.png"))

    # ищем дочерний узел устройства
    body = page.locator("body").inner_text()
    print("после раскрытия:", body[:300].replace("\n", " | "))

    # drag-and-drop первого дочернего узла в таблицу
    try:
        src = page.locator(".system-tree-context-name").nth(2)
        print("источник:", src.inner_text()[:50])
        box = src.bounding_box()
        tgt = page.locator("text=No Data").first.bounding_box()
        if box and tgt:
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.down()
            page.mouse.move(tgt["x"] + 200, tgt["y"], steps=15)
            time.sleep(1)
            page.mouse.up()
            time.sleep(4)
            page.screenshot(path=str(OUT_DIR / "case6_64111_dnd.png"))
            print("после dnd:", page.locator("body").inner_text()[:300].replace("\n", " | "))
    except Exception as e:
        print(f"dnd не удался: {str(e)[:200]}")

    browser.close()
    print("Готово.")
