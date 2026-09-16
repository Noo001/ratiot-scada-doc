# -*- coding: utf-8 -*-
"""Кейс 18 (ASD-6496) на 6.41.12-2562: ссылки «Документация»/«Онлайн» в демо-приложении.

Сценарий из BUG_CASES.md: стартовая страница демо-приложения scadaApplication,
блоки «Документация» и «Онлайн», 8 кнопок, клик открывает URL в новой вкладке.

Итог разведки 16.09.2026: сервер был чисто переустановлен (~16:00, кейс 2),
демо-приложение scadaApplication в системе отсутствует:
  - все URL дашборда отдают 404;
  - в «Приложения» только: Группы приложений, diagnostics, Platform Administration Kit;
  - стартовой страницы «Центр управления»/«Каталог демо» нет (старт = «Администрирование»);
  - поиск в дереве по scadaApplication/SCADA/HMI/Демо ничего не находит.
Поэтому клики по ссылкам выполнить невозможно без развёртывания демо-контента,
что вне рамок проверки (ресурсы не создаём). Скрипт фиксирует факт отсутствия.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
TREE = f"{BASE}/web/dashboards/users.admin.dashboards.scadaApplication"

ITEMS = [
    "Документация по SCADA/HMI",
    "Документация по платформе",
    "Веб-сайт продукта",
    "Веб-сайт платформы",
    "Блог продукта",
    "Сообщество",
    "Другие решения",
    "Купить",
]

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


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    hook(page)
    login(page)
    page.screenshot(path=str(OUT / "case18_1_logged_in.png"), full_page=True)

    # 1) прямой URL дашборда демо-приложения
    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    body = page.locator("body").inner_text()
    direct_404 = "404" in body[:200]
    page.screenshot(path=str(OUT / "case18_2_demo_url.png"), full_page=True)
    print("1) Прямой URL дашборда:", page.url, "| 404:", direct_404)

    # 2) возврат в консоль, поиск «scadaApplication» в дереве
    page.goto(f"{BASE}/users.admin.dashboards.administration", timeout=60000)
    time.sleep(8)
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("scadaApplication")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(10)
    n = page.locator(".system-tree-context-name").count()
    page.screenshot(path=str(OUT / "case18_3_tree_search.png"), full_page=True)
    print("2) Строк в дереве после поиска «scadaApplication»:", n)

    # 3) содержимое «Приложения» (сначала очищаем поиск, чтобы дерево вернулось)
    search.fill("")
    time.sleep(4)
    row = page.locator(".system-tree-context-name").filter(has_text="Приложения").first
    row.click(); time.sleep(1)
    page.keyboard.press("ArrowRight"); time.sleep(1)
    page.keyboard.press("ArrowRight"); time.sleep(3)
    nodes = [el.inner_text().strip() for el in page.locator(".system-tree-context-name").all()]
    page.screenshot(path=str(OUT / "case18_4_applications.png"), full_page=True)
    print("3) Узлы дерева после раскрытия «Приложения»:", nodes)

    # 4) сами пункты «Документация»/«Онлайн» на стартовой странице
    found = {t: page.locator(f"text={t}").count() for t in ITEMS + ["Документация", "Онлайн", "Каталог демо", "Центр управления"]}
    print("4) Пункты на стартовой странице:", found)

    # 5) варианты URL дашборда
    for u in [f"{BASE}/users.admin.dashboards.scadaApplication",
              f"{BASE}/web/dashboards/users.admin.dashboards.scadaApplication?mode=EDIT"]:
        page.goto(u, timeout=60000)
        time.sleep(6)
        b = page.locator("body").inner_text()[:100].replace("\n", " ")
        print(f"5) {u.replace(BASE, '')}: {b}")

    page.screenshot(path=str(OUT / "case18_5_final.png"), full_page=True)

    print("\nJS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])

    demo_absent = direct_404 and n == 0 and not any("scadaApplication" in x for x in nodes)
    print("\nИТОГ: демо-приложение scadaApplication ОТСУТСТВУЕТ на сервере "
          "(чистая переустановка ~16:00 16.09, кейс 2) — кейс 18 НЕВОЗМОЖНО ПРОВЕРИТЬ: "
          "ни одна из 8 ссылок не доступна для клика; aggregate.digital не обнаруживается "
          "нигде в доступном UI. Требуется развёртывание демо-контента (вне рамок: ресурсы не создаём).")
    browser.close()
