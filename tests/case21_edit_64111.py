#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 21 (ASD-6499) на 6.41.11: режим редактирования демо-проектов.
Сбор ошибок через page.on, чтобы не теряться при переходах."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1600, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    def on_console(msg):
        if msg.type == "error":
            errors.append(f"[console] {msg.text}")

    def on_pageerror(err):
        errors.append(f"[pageerror] {err}")

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    summary = {}

    for name in ("ioField", "milkStorage"):
        errors.clear()
        url = f"https://localhost:8443/web/dashboards/users.admin.dashboards.{name}/edit"
        page.goto(url)
        time.sleep(8)
        shot = OUT_DIR / f"case21_edit_{name}.png"
        page.screenshot(path=str(shot))
        summary[name] = {"url": page.url, "errors": list(errors)}
        print(f"--- {name}: {page.url}")
        for e in errors[:10]:
            print(f"  {e[:220]}")

    (OUT_DIR / "case21_edit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
