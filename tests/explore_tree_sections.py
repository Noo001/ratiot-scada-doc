#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исследование разделов системного дерева через поиск (пользовательский путь)."""

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

SECTIONS = [
    "Устройства",
    "Группы устройств",
    "Пользователи",
    "Приложения",
    "Модели",
    "Инструментальные панели",
    "Тревоги",
    "Фильтры событий",
    "Классы",
    "Запросы",
    "Планировщик",
    "Процессы",
    "Машинное обучение",
    "Корреляторы событий",
    "UI компоненты",
    "Скрипты",
    "Отчёты",
    "Автозапуск",
    "Драйвера и расширения",
    "Управление процессами",
    "Виджеты",
    "Безопасность",
]


def safe_filename(text: str) -> str:
    return re.sub(r"[^\w\-_.]", "_", text).strip("_")[:80]


def collect_errors(page):
    return page.evaluate("""
        () => {
            if (window.__testConsoleErrors) return window.__testConsoleErrors;
            return [];
        }
    """) or []


def main():
    summary = {}
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

        page.evaluate("""
            window.__testConsoleErrors = [];
            const origError = console.error;
            console.error = function(...args) {
                window.__testConsoleErrors.push(args.map(a => String(a)).join(' '));
                origError.apply(console, args);
            };
            window.addEventListener('error', e => window.__testConsoleErrors.push(e.message));
            window.addEventListener('unhandledrejection', e => window.__testConsoleErrors.push(String(e.reason || 'null')));
        """)

        for label in SECTIONS:
            try:
                search = page.locator("input[placeholder='Поиск в системном дереве']").first
                search.fill("")
                search.click()
                search.fill(label)
                time.sleep(1.2)

                # ищем любой видимый элемент в дереве с нужным текстом
                result = page.locator(".ag-tree-node-content").filter(has_text=re.compile(re.escape(label))).first
                if result.is_visible():
                    result.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(1.5)
                else:
                    # попробуем раскрыть родителя, если раздел вложен
                    parent = page.locator(".ag-tree-node-content").filter(has_text=re.compile(re.escape("RatioT Server"))).first
                    if parent.is_visible():
                        parent.click()
                        time.sleep(0.5)

                fname = safe_filename(label)
                page.screenshot(path=str(OUT_DIR / f"tree_section_{fname}.png"))
                summary[label] = {
                    "url": page.url,
                    "errors": collect_errors(page),
                }
            except Exception as e:
                summary[label] = {"error": str(e)}

        browser.close()

    summary_path = OUT_DIR / "tree_sections_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово. Сводка: {summary_path}")


if __name__ == "__main__":
    main()
