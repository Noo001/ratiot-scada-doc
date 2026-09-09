#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 19 (ASD-6497): дашборды тревог на 6.41.11 — просмотр и путь через иконку колокольчика."""
import json
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

    summary = {}

    # 1. Прямой просмотр обоих дашбордов
    for name in ("alerts", "alertsMonitoring"):
        errors.clear()
        page.goto(f"https://localhost:8443/web/dashboards/users.admin.dashboards.{name}")
        time.sleep(8)
        page.screenshot(path=str(OUT_DIR / f"case19_64111_{name}.png"))
        summary[name] = {"url": page.url, "errors": list(errors)}
        print(f"--- {name}: {page.url}, ошибок {len(errors)}")
        for e in errors[:5]:
            print(f"  {e[:180]}")

    # 2. Пользовательский путь: иконка колокольчика в левой панели
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaControlCenter")
    time.sleep(5)
    errors.clear()
    page.mouse.click(22, 351)  # колокол на вертикальной панели
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case19_64111_bell_click.png"))
    summary["bell"] = {"url": page.url, "errors": list(errors)}
    print(f"--- bell: {page.url}, ошибок {len(errors)}")

    (OUT_DIR / "case19_64111_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
