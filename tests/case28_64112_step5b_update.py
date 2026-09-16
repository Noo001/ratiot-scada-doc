# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521), шаг 5 (правильный): «Обновить» приложение из архива через меню ДЕЙСТВИЯ."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
ARCHIVE = DL / "case28_test_app.zip"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def body_peek(page, n=900):
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


def open_row_menu(page, row_text, cc_url):
    for attempt in range(5):
        row = page.locator(f"tr:has-text('{row_text}')").first
        if not row.is_visible():
            page.goto(cc_url, timeout=120000)
            page.wait_for_load_state("networkidle", timeout=120000)
            time.sleep(8)
            row = page.locator(f"tr:has-text('{row_text}')").first
        page.locator(f"td:has-text('{row_text}')").first.click()
        time.sleep(2)
        if "ДЕЙСТВИЯ" in page.locator("body").inner_text():
            return True
        print(f"  меню не открылось, попытка {attempt + 1}")
    return False


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000},
                              accept_downloads=True)
    page = ctx.new_page()
    hook(page)
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    ok = open_row_menu(page, "test", CC)
    print("Меню ДЕЙСТВИЯ открыто:", ok)
    page.screenshot(path=str(OUT / "case28_64112_41_actions_menu.png"), full_page=True)

    errors_all.clear()
    # пункт «Обновить» — ищем по тексту внутри видимого меню
    upd = page.get_by_text("Обновить", exact=True)
    print("Элементов «Обновить»:", upd.count())
    clicked = False
    try:
        fc = page.wait_for_event("filechooser", timeout=8000)
        upd.last.click()
        chooser = fc.value
        chooser.set_files(str(ARCHIVE))
        print("Файл передан через filechooser:", ARCHIVE)
        clicked = True
    except Exception as e:
        print("filechooser не возник:", str(e)[:120])
    if not clicked:
        time.sleep(4)
        page.screenshot(path=str(OUT / "case28_64112_42_update_dialog.png"), full_page=True)
        body_peek(page, 1200)
        # возможно, открылось окно с кнопкой выбора файла
        inputs = page.locator("input[type=file]")
        print("input[type=file]:", inputs.count())
        btns = page.locator("button:visible")
        for i in range(btns.count()):
            print(f"  кнопка[{i}]: {btns.nth(i).inner_text().strip()[:60]!r}")
    time.sleep(12)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_42_update_result.png"), full_page=True)
    body = page.locator("body").inner_text()
    has_window = "Результат обновления" in body
    print("Окно «Результат обновления» открылось:", has_window)
    body_peek(page, 1500)
    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])

    # если окно с результатом — подтвердить (OK/Закрыть)
    if has_window:
        for txt in ("OK", "Закрыть", "Применить"):
            b = page.locator("button:visible", has_text=txt)
            if b.count():
                print("Нажимаю:", txt)
                b.first.click()
                time.sleep(6)
                break
        page.screenshot(path=str(OUT / "case28_64112_43_after_confirm.png"), full_page=True)

    # проверка: ресурс вернулся
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(6)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_44_resources_final.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("Ресурс «Устройства» вернулся:", "Устройства" in body)
    body_peek(page, 500)
    print("JS-ошибок (всего):", len(errors_all))
    browser.close()
