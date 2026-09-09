#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 18 (ASD-6496): клик по каждой кнопке Документация/Онлайн -> фиксируем URL."""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

BUTTONS = [
    "Документация по SCADA/HMI",
    "Документация по платформе",
    "Веб-сайт продукта",
    "Веб-сайт платформы",
    "Блог продукта",
    "Сообщество",
    "Другие решения",
    "Купить",
]

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
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaControlCenter")
    time.sleep(6)

    results = []
    for text in BUTTONS:
        entry = {"text": text}
        try:
            # ждём возможного popup
            popup = None
            try:
                with page.expect_popup(timeout=4000) as popup_info:
                    page.locator(f"button:has-text('{text}')").first.click()
                popup = popup_info.value
            except Exception:
                page.locator(f"button:has-text('{text}')").first.click()

            time.sleep(5)
            target = popup or page
            entry["url"] = target.url
            safe = text.replace(" ", "_").replace("/", "-")[:30]
            target.screenshot(path=str(OUT_DIR / f"case18_click_{safe}.png"))
            if popup:
                popup.close()
            else:
                # вернуться на стартовую
                page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaControlCenter")
                time.sleep(5)
        except Exception as e:
            entry["error"] = str(e)[:200]
        results.append(entry)
        print(json.dumps(entry, ensure_ascii=False))

    (OUT_DIR / "case18_64111_clicks.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
