# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521), шаг 5: «Обновить» -> «Загрузить как ZIP-архив» -> Результат обновления."""
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


def body_peek(page, n=1200):
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


def click_menu_item_by_coords(page, item_text):
    """Кликнуть пункт открытого меню ДЕЙСТВИЯ по координатам листового элемента с точным текстом."""
    res = page.evaluate("""(txt) => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === txt && e.getBoundingClientRect().width);
      if (!els.length) return null;
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""", item_text)
    print(f"Координаты пункта {item_text!r}:", res)
    if res:
        page.mouse.click(*res)
        return True
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

    # меню ДЕЙСТВИЯ -> «Обновить»
    page.locator("td:has-text('test')").first.click()
    time.sleep(3)
    print("Меню открыто:", "ДЕЙСТВИЯ" in page.locator("body").inner_text())
    errors_all.clear()
    click_menu_item_by_coords(page, "Обновить")
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_50_update_dialog.png"), full_page=True)

    # тип операции: «Загрузить как ZIP-архив»
    page.locator(".ant-select:visible", has_text="Загрузить из папки сервера").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Загрузить как ZIP-архив").first.click()
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_51_zip_selected.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("После выбора ZIP:", body[:400].replace("\n", " | "))
    inputs = page.evaluate("() => Array.from(document.querySelectorAll('input[type=file]')).map(e => e.accept)")
    print("inputs file accept:", inputs)

    # выбор файла: input[type=file] с пустым accept (зрузчик архива в поле «Архив»)
    picked = False
    inputs = page.evaluate("""() => Array.from(document.querySelectorAll('input[type=file]')).map(
        (e, i) => ({i, accept: e.accept}))""")
    print("inputs file accept:", inputs)
    target = [x for x in inputs if x["accept"] == ""]
    if target:
        page.locator("input[type=file]").nth(target[0]["i"]).set_input_files(str(ARCHIVE))
        picked = True
    print("Файл выбран:", picked)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_52_file_picked.png"), full_page=True)

    # OK в диалоге обновления
    ok = page.locator("button:visible", has_text="OK")
    print("Кнопок OK:", ok.count())
    ok.last.click()
    time.sleep(15)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_53_update_result.png"), full_page=True)
    body = page.locator("body").inner_text()
    has_window = "Результат обновления" in body
    print("Окно «Результат обновления» открылось:", has_window)
    body_peek(page, 1500)
    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])

    # закрыть окно результата
    if has_window:
        for txt in ("OK", "Закрыть"):
            b = page.locator("button:visible", has_text=txt)
            if b.count():
                b.last.click()
                time.sleep(6)
                break
        page.screenshot(path=str(OUT / "case28_64112_54_result_closed.png"), full_page=True)

    # шаг 6: ресурс вернулся?
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(6)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_55_resources_final.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("Ресурс «Устройства» вернулся:", "Устройства" in body)
    print("JS-ошибок (всего):", len(errors_all))
    browser.close()
