#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Клик по разделам дерева через JS-evaluate."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

SECTIONS = ["Устройства", "Пользователи", "Приложения", "Драйвера и расширения", "Безопасность"]

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

    summary = {}
    for label in SECTIONS:
        page.evaluate("""
            window.__errors = [];
            const origError = console.error;
            console.error = function(...args) { window.__errors.push(args.map(a => String(a)).join(' ')); origError.apply(console, args); };
            window.addEventListener('error', e => window.__errors.push(e.message));
            window.addEventListener('unhandledrejection', e => window.__errors.push(String(e.reason || 'null')));
        """)
        # click element containing label in system tree
        ok = page.evaluate("""
            (label) => {
                const tree = document.querySelector('.system-tree');
                if (!tree) return {ok: false, reason: 'no tree'};
                const walker = document.createTreeWalker(tree, NodeFilter.SHOW_ELEMENT);
                let el;
                while (el = walker.nextNode()) {
                    if (el.textContent.trim() === label || el.textContent.trim().startsWith(label)) {
                        el.click();
                        return {ok: true, clicked: el.tagName + '.' + el.className};
                    }
                }
                return {ok: false, reason: 'not found'};
            }
        """, label)
        print(label, ok)
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(OUT_DIR / f"jsclick_{label}.png"))
        summary[label] = {"url": page.url, "ok": ok, "errors": page.evaluate("() => window.__errors")}

    (OUT_DIR / "jsclick_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    browser.close()
