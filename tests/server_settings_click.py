#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка пользовательского пути: кнопка 'Настроить сервер' на главной."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1400, "height": 1000}, ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://localhost:8443/web/login")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin")
    page.locator("button[type='submit'], button:has-text('Войти')").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # inject console collector
    page.evaluate("""
        window.__errors = [];
        const origError = console.error;
        console.error = function(...args) { window.__errors.push(args.map(a => String(a)).join(' ')); origError.apply(console, args); };
        window.addEventListener('error', e => window.__errors.push(e.message + ' at ' + e.filename + ':' + e.lineno));
        window.addEventListener('unhandledrejection', e => window.__errors.push(String(e.reason || 'null reason')));
    """)

    page.screenshot(path=str(OUT_DIR / "settings_before_click.png"))

    # клик по кнопке Настроить сервер
    page.locator("text=Настроить сервер").first.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    page.screenshot(path=str(OUT_DIR / "settings_after_click.png"))

    # собрать URL и console errors
    current_url = page.url
    errors = page.evaluate("() => window.__errors")

    summary = {"url": current_url, "errors": errors or []}
    (OUT_DIR / "settings_click_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    browser.close()
