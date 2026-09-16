# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521), этап 2в: открыть приложение test из Control Center и добавить ресурс."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def body_peek(page, n=1500):
    txt = page.locator("body").inner_text()
    print("BODY:", txt[:n].replace("\n", " | "))
    return txt


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

    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    page.screenshot(path=str(OUT / "case28_64112_09_cc.png"), full_page=True)
    body = body_peek(page, 700)
    print("test в таблице:", "test" in body)

    # строка test -> kebab-кнопка -> меню ДЕЙСТВИЯ -> «Открыть»
    row = page.locator("tr:has-text('test')").first
    row.hover()
    time.sleep(1)
    row.locator(".kebab-btn").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_10_test_menu.png"), full_page=True)
    body = page.locator("body").inner_text()
    if "ДЕЙСТВИЯ" in body:
        page.locator(".ant-dropdown-menu-item:visible", has_text="Открыть").first.click()
        time.sleep(12)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_10_test_open.png"), full_page=True)
    print("URL:", page.url)
    body_peek(page, 500)

    # «Добавить ресурс»
    errors_all.clear()
    page.locator("button:has-text('Добавить ресурс')").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_11_add_resource.png"), full_page=True)

    # раскрыть «Инструментальные панели» (exact text -> ancestor .system-tree-context -> expander)
    nodes = page.get_by_text("Инструментальные панели", exact=True).locator(
        "xpath=ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' system-tree-context ')][1]")
    print("Узлов:", nodes.count())
    node = nodes.filter(has=page.locator("label.agg-checkbox")).first  # только узел в диалоге (с чекбоксом)
    print("Узел диалога найден:", node.count())
    node.locator(".system-tree-context-expand").first.click()
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_12_dash_expanded.png"), full_page=True)

    # дочерние узлы панелей
    children = node.locator(
        "xpath=./div[contains(@class,'system-tree-context-children')]/div[contains(@class,'system-tree-context')]"
        "//div[contains(@class,'system-tree-context-name')]")
    print("Дочерних панелей:", children.count())
    picked = None
    for i in range(min(children.count(), 20)):
        t = children.nth(i).inner_text().strip()
        print(f"  [{i}] {t[:60]}")
        if picked is None and t and not t.startswith("Группы"):
            picked = t
    print("Выбираю:", picked)

    # отметить чекбокс выбранной панели
    child_node = node.locator(
        "xpath=./div[contains(@class,'system-tree-context-children')]/div[contains(@class,'system-tree-context')]"
    ).filter(has=page.get_by_text(picked, exact=True)).first
    child_node.locator("input.ant-checkbox-input").first.check(force=True)
    time.sleep(1)
    page.screenshot(path=str(OUT / "case28_64112_13_checked.png"), full_page=True)

    # OK -> окно «Результат добавления» -> снова OK
    page.locator("button:has-text('OK')").last.click()
    time.sleep(5)
    page.screenshot(path=str(OUT / "case28_64112_13b_add_result.png"), full_page=True)
    body = page.locator("body").inner_text()
    if "Результат добавления" in body:
        print("Окно «Результат добавления» открылось, подтверждаю")
        page.locator("button:has-text('OK')").last.click()
        time.sleep(8)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_14_after_add.png"), full_page=True)
    print("URL:", page.url)
    body = body_peek(page, 700)
    print("Ресурс добавлен (Глобальный поиск в body):", "Глобальный поиск" in body)

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
