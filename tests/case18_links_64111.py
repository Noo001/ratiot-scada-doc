#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 18 (ASD-6496) на 6.41.11: ссылки «Документация»/«Онлайн» в демо -> куда ведут.
Пользовательский путь: Центр управления -> Каталог демо-проектов -> Открыть."""

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

BAD = ("aggregate", "tibbo")
GOOD = ("ratiot", "bufflab", "ratio-t")

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

    summary = {"steps": []}

    def log(msg):
        summary["steps"].append(msg)
        print(msg)

    # Центр управления -> Каталог демо-проектов
    page.locator("text=Каталог демо").first.click()
    time.sleep(4)

    results = {}

    # Проходим по всем демо из дерева и жмём «Открыть»
    demo_names = [
        "Линия бутилирования",
        "Фильтровальная станция",
        "Хранилище пастеризованного молока",
        "Магистральный газопровод",
        "Интеллектуальная энергосистема",
    ]
    for name in demo_names:
        try:
            page.locator(f"text={name}").first.click()
            time.sleep(2)
            open_btn = page.locator("button:has-text('Открыть')").locator("visible=true").first
            if not open_btn.is_visible():
                log(f"{name}: кнопки «Открыть» нет")
                continue
            errors_open = []
            with page.expect_popup(timeout=8000) as popup_info:
                try:
                    open_btn.click()
                except Exception:
                    pass
            try:
                demo_page = popup_info.value
                demo_page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                # попапа нет — возможно, открылось в той же вкладке
                demo_page = page
                time.sleep(5)
            time.sleep(5)
            shot = OUT_DIR / f"case18_64111_{name.split()[0]}.png"
            demo_page.screenshot(path=str(shot))

            links = []
            for frame in demo_page.frames:
                try:
                    for a in frame.locator("a[href]").all():
                        href = a.get_attribute("href")
                        txt = ""
                        try:
                            txt = a.inner_text().strip().replace("\n", " ")[:50]
                        except Exception:
                            pass
                        if href and ("http" in href or "docs" in href):
                            links.append({"text": txt, "href": href})
                except Exception:
                    pass
            results[name] = {"url": demo_page.url, "links": links}
            log(f"--- {name}: {demo_page.url}")
            for l in links:
                flag = ""
                low = l["href"].lower()
                if any(b in low for b in BAD):
                    flag = "  <== AGGREGATE"
                elif any(g in low for g in GOOD):
                    flag = "  <== RATIOT/BUFFLAB"
                log(f"  [{l['text']}] {l['href'][:110]}{flag}")

            demo_page.close() if demo_page != page else None
            time.sleep(2)
        except Exception as e:
            log(f"{name}: ошибка — {e}")

    summary["results"] = results
    (OUT_DIR / "case18_64111_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
