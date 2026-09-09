#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исследование разделов системного дерева и настроек сервера для поиска новых багов."""

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE = "https://localhost:8443"
LOGIN = "https://localhost:8443/web/login"
OUT_DIR = Path(__file__).with_name("screenshots")
OUT_DIR.mkdir(exist_ok=True)

SECTIONS = [
    ("Устройства", "Устройства"),
    ("Группы устройств", "Группы устройств"),
    ("Пользователи", "Пользователи"),
    ("Приложения", "Приложения"),
    ("Модели", "Модели"),
    ("Инструментальные панели", "Инструментальные панели"),
    ("Тревоги", "Тревоги"),
    ("Фильтры событий", "Фильтры событий"),
    ("Классы", "Классы"),
    ("Запросы", "Запросы"),
    ("Планировщик", "Планировщик"),
    ("Процессы", "Процессы"),
    ("Машинное обучение", "Машинное обучение"),
    ("Корреляторы событий", "Корреляторы событий"),
    ("UI компоненты", "UI компоненты"),
    ("Скрипты", "Скрипты"),
    ("Отчёты", "Отчёты"),
    ("Автозапуск", "Автозапуск"),
    ("Драйвера и расширения", "Драйвера и расширения"),
    ("Управление процессами", "Управление процессами"),
    ("Виджеты", "Виджеты"),
    ("Безопасность", "Безопасность"),
]


def safe_filename(text: str) -> str:
    return re.sub(r"[^\w\-_.]", "_", text).strip("_")[:80]


def save_console_errors(page, errors_path: Path):
    logs = page.evaluate("""
        () => {
            if (window.__testConsoleErrors) return window.__testConsoleErrors;
            return [];
        }
    """)
    logs = logs or []
    severe = [l for l in logs if l.get("type") in ("error", "severe")]
    if severe:
        errors_path.write_text(json.dumps(severe, ensure_ascii=False, indent=2), encoding="utf-8")
    return severe


def main():
    errors_summary = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1400, "height": 1000}, ignore_https_errors=True)
        page = context.new_page()

        page.goto(LOGIN)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # login
        page.locator("input[placeholder='Имя пользователя'], input[name='username'], input[type='text']").first.fill("admin")
        page.locator("input[type='password']").first.fill("admin")
        page.locator("button[type='submit'], button:has-text('Войти')").first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # inject console error collector
        page.evaluate("""
            window.__testConsoleErrors = [];
            const origError = console.error;
            console.error = function(...args) {
                window.__testConsoleErrors.push({type: 'error', message: args.map(a => String(a)).join(' ')});
                origError.apply(console, args);
            };
            window.addEventListener('error', e => {
                window.__testConsoleErrors.push({type: 'error', message: e.message, filename: e.filename, lineno: e.lineno});
            });
            window.addEventListener('unhandledrejection', e => {
                window.__testConsoleErrors.push({type: 'error', message: String(e.reason)});
            });
        """)

        # главная
        main_path = OUT_DIR / "new_main.png"
        page.screenshot(path=str(main_path))
        errors_summary["main"] = save_console_errors(page, OUT_DIR / "new_main_errors.json")

        # Информация о сервере через верхнюю плитку
        try:
            page.locator("text=Информация о сервере").first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page.screenshot(path=str(OUT_DIR / "new_server_info.png"))
            errors_summary["server_info"] = save_console_errors(page, OUT_DIR / "new_server_info_errors.json")
        except PlaywrightTimeout:
            pass

        # Настроить сервер
        try:
            page.goto(f"{BASE}/web/context/users.admin.server.properties")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page.screenshot(path=str(OUT_DIR / "new_server_settings.png"))
            errors_summary["server_settings"] = save_console_errors(page, OUT_DIR / "new_server_settings_errors.json")
        except PlaywrightTimeout:
            pass

        # Разделы системного дерева через поиск
        for search_name, label in SECTIONS:
            try:
                search = page.locator("input[placeholder='Поиск в системном дереве']").first
                search.fill("")
                search.fill(search_name)
                time.sleep(1)
                # first result in tree
                result = page.locator(".ag-tree-node-content:visible, [role='treeitem']:visible").filter(has_text=search_name).first
                if result.is_visible():
                    result.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(1.5)
                    fname = safe_filename(label)
                    page.screenshot(path=str(OUT_DIR / f"new_section_{fname}.png"))
                    errors_summary[label] = save_console_errors(page, OUT_DIR / f"new_section_{fname}_errors.json")
            except Exception as e:
                errors_summary[label] = [{"type": "error", "message": str(e)}]

        # Лицензионная информация
        try:
            page.goto(f"{BASE}/web/context/users.admin.licenseInfo")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page.screenshot(path=str(OUT_DIR / "new_license_info.png"))
            errors_summary["license_info"] = save_console_errors(page, OUT_DIR / "new_license_info_errors.json")
        except Exception as e:
            errors_summary["license_info"] = [{"type": "error", "message": str(e)}]

        browser.close()

    summary_path = OUT_DIR / "new_bugs_summary.json"
    summary_path.write_text(json.dumps(errors_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово. Скриншоты в {OUT_DIR}, сводка: {summary_path}")


if __name__ == "__main__":
    main()
