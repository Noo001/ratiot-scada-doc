#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 18 (ASD-6496): собрать href ссылок «Документация»/«Онлайн» на стартовой странице."""
import json
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

    # центр управления (стартовая страница)
    page.goto("https://localhost:8443/web/dashboards/users.admin.dashboards.scadaControlCenter")
    time.sleep(6)
    page.screenshot(path=str(OUT_DIR / "case18_64111_start.png"))

    links = []
    for a in page.locator("a[href]").all():
        try:
            href = a.get_attribute("href")
            txt = a.inner_text().strip().replace("\n", " ")[:60]
            if href and txt:
                links.append({"text": txt, "href": href})
        except Exception:
            pass

    result = {"links": links}
    print(f"Всего ссылок с текстом: {len(links)}")
    for l in links:
        print(f"  [{l['text']}] -> {l['href']}")

    (OUT_DIR / "case18_64111_links.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
