#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Клик по заголовку раздела в системном дереве (system-tree-context-header)."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

SECTIONS = [
    ("devices", "Устройства"),
    ("groups", "Группы устройств"),
    ("users", "Пользователи"),
    ("applications", "Приложения"),
    ("models", "Модели"),
    ("plugins", "Драйвера и расширения"),
    ("security", "Безопасность"),
    ("queries", "Запросы"),
    ("classes", "Классы"),
]

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
    for ctx_path, label in SECTIONS:
        page.evaluate("""
            window.__errors = [];
            const origError = console.error;
            console.error = function(...args) { window.__errors.push(args.map(a => String(a)).join(' ')); origError.apply(console, args); };
            window.addEventListener('error', e => window.__errors.push(e.message));
            window.addEventListener('unhandledrejection', e => window.__errors.push(String(e.reason || 'null')));
        """)
        # click header by data-context-path
        page.evaluate(f"""
            (ctxPath) => {{
                const node = document.querySelector('.system-tree-context[data-context-path="' + ctxPath + '"] .system-tree-context-header');
                if (node) {{
                    const dbl = new MouseEvent('dblclick', {{ bubbles: true, cancelable: true }});
                    node.dispatchEvent(dbl);
                }}
                return node ? node.className : 'not found';
            }}
        """, ctx_path)
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(OUT_DIR / f"header_{ctx_path}.png"))
        summary[label] = {"url": page.url, "errors": page.evaluate("() => window.__errors")}

    (OUT_DIR / "header_click_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    browser.close()
