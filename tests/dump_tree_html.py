#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Дамп HTML системного дерева для подбора локаторов."""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

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

    # найти первые 5 элементов дерева
    html = page.evaluate("""
        () => {
            const tree = document.querySelector('.ag-tree, [role=\"tree\"], .system-tree, .navigation-tree');
            const items = Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.includes('Устройства')).slice(0,5);
            return {
                treeClass: tree ? tree.className : null,
                treeTag: tree ? tree.tagName : null,
                items: items.map(el => ({
                    tag: el.tagName,
                    class: el.className,
                    text: el.textContent.trim().slice(0,60)
                }))
            };
        }
    """)
    import json
    print(json.dumps(html, ensure_ascii=False, indent=2))
    browser.close()
