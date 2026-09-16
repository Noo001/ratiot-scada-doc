# -*- coding: utf-8 -*-
"""Кейс 6 (ASD-6476): дерево тегов — выбор абсолютной модели в качестве источника. Проверка на 6.41.12-2562.

Итог проверки: экран «Дерево тегов» на данном контуре недоступен (Free-лицензия «Network Manager Free License»,
узел отсутствует в системном дереве, прямые URL 404), устройств и моделей с тегами нет — диалог выбора источника
лично воспроизвести нельзя (та же ограниченность, что и на trial в 6.41.11). Скрипт фиксирует факты и убирает
тестовую абсолютную модель, созданную во время разведки.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
MODEL = "_____case6_______"  # тестовая модель, созданная при разведке (кириллица не ввелась headless-клавиатурой)

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def login(page):
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)


def tree_search(page, query, shot):
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.wait_for(state="visible", timeout=60000)
    search.click()
    search.fill("")
    time.sleep(1)
    search.fill(query)
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(6)
    page.screenshot(path=str(OUT / shot), full_page=False)
    names = [n.strip() for n in page.locator(".system-tree-context-name").all_inner_texts() if n.strip()]
    print(f"Поиск «{query}»:", names[:20])
    return names


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    hook(page)
    login(page)
    page.screenshot(path=str(OUT / "case6_00_home.png"), full_page=False)

    # 1. Лицензия (Мониторинг)
    page.mouse.click(22, 127)  # иконка «Мониторинг» на левой панели
    time.sleep(8)
    page.screenshot(path=str(OUT / "case6_01_license.png"), full_page=False)
    body = page.locator("body").inner_text()
    lic = "Free License" in body or "Trial" in body
    print("Бесплатная/trial лицензия:", lic)

    # 2. Поиск дерева тегов в системном дереве
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    r1 = tree_search(page, "тег", "case6_02_search_tag.png")
    r2 = tree_search(page, "Дерево", "case6_03_search_tree.png")
    tag_tree_found = any("дерево тегов" in n.lower() for n in r1 + r2)
    print("Узел «Дерево тегов» найден:", tag_tree_found)

    # 3. Прямые URL дашборда дерева тегов (оба паттерна)
    for url, shot in [
        (f"{BASE}/web/dashboards/users.admin.dashboards.tags", "case6_04_url_old.png"),
        (f"{BASE}/users.admin.dashboards.tags", "case6_05_url_new.png"),
    ]:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(4)
        body = page.locator("body").inner_text()[:60].replace("\n", " | ")
        page.screenshot(path=str(OUT / shot), full_page=False)
        print(f"{url} :: {body}")

    # 4. Контейнеры пустые: устройств нет, моделей с тегами нет
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    names = tree_search(page, "Устройства", "case6_06_devices.png")
    print("Есть ли устройства:", names)

    # 5. Удаление тестовой модели, созданной при разведке
    tree_search(page, "case6", "case6_07_model_found.png")
    node = page.locator(".system-tree-context-name", has_text="case6").first
    if node.count() > 0:
        node.click(button="right")
        time.sleep(3)
        page.screenshot(path=str(OUT / "case6_08_model_ctx.png"), full_page=False)
        try:
            page.get_by_text("Удалить", exact=True).first.click(force=True)
            time.sleep(4)
            page.screenshot(path=str(OUT / "case6_09_delete_confirm.png"), full_page=False)
            for b in ("button:has-text('Да')", "button:has-text('OK')", "button:has-text('Удалить')"):
                if page.locator(b).count() > 0:
                    page.locator(b).last.click(force=True)
                    time.sleep(8)
                    break
            print("Тестовая модель удалена")
        except Exception as e:
            print("Не удалось удалить модель:", str(e)[:150])
    tree_search(page, "case6", "case6_10_after_cleanup.png")

    print("\nJS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
    print("\nИТОГ КЕЙС 6: проверка не завершена — экран «Дерево тегов» недоступен в Free-лицензии,")
    print("диалог выбора источника лично воспроизвести нельзя (как и на trial 6.41.11).")
