#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 18: извлечь ссылки блоков Документация/Онлайн, включая onclick и js-обработчики."""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")

ITEMS = [
    "Документация по SCADA/HMI",
    "Документация по платформе",
    "Веб-сайт продукта",
    "Веб-сайт платформы",
    "Блог продукта",
    "Сообщество",
    "Другие решения",
    "Купить",
    "Открыть медиа библиотеку",
    "Каталог демо-проектов",
    "Настроить сервер",
    "Управление ресурсами",
    "Информация о лицензии",
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

    result = page.evaluate("""(items) => {
        const out = [];
        for (const text of items) {
            const els = Array.from(document.querySelectorAll('a, [role="link"], li, span, div'));
            const el = els.find(e => e.childElementCount <= 3 && (e.textContent || '').trim().startsWith(text));
            if (!el) { out.push({text, found: false}); continue; }
            let cur = el;
            let info = {text, found: true, tag: el.tagName, href: el.getAttribute('href'), onclick: el.getAttribute('onclick')};
            // ищем ближайший предок-ссылку
            for (let i = 0; i < 5 && cur; i++) {
                if (cur.tagName === 'A' && cur.getAttribute('href')) { info.href = cur.getAttribute('href'); break; }
                cur = cur.parentElement;
            }
            info.outer = el.outerHTML.slice(0, 300);
            out.push(info);
        }
        return out;
    }""", ITEMS)

    for r in result:
        print(json.dumps(r, ensure_ascii=False))

    (OUT_DIR / "case18_64111_items.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    browser.close()
    print("Готово.")
