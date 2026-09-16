# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521): финальный сценарий — упаковать в ZIP, удалить ресурс, обновить из ZIP,
проверить «Результат обновления» и возврат ресурса, удалить приложение test."""
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
PACKAGED = DL / "case28_test_app_packaged.zip"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def body_peek(page, n=1000):
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


def close_error(page):
    for _ in range(3):
        if "Копировать текст ошибки" not in page.locator("body").inner_text():
            return
        b = page.locator("button:visible", has_text="Закрыть")
        if b.count():
            b.last.click()
            time.sleep(1)


def menu_item_coords(page, item_text):
    res = page.evaluate("""(txt) => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === txt && e.getBoundingClientRect().width);
      if (!els.length) return null;
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""", item_text)
    return res


def open_actions_menu(page):
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("td:has-text('test')").first.click()
    time.sleep(3)
    return "ДЕЙСТВИЯ" in page.locator("body").inner_text()


def open_editor_resources(page):
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(6)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000},
                              accept_downloads=True)
    page = ctx.new_page()
    hook(page)
    login(page)

    # --- Шаг 3: Упаковать -> Скачать как ZIP-архив ---
    print("=== ШАГ 3: упаковать и выгрузить ZIP ===")
    errors_all.clear()
    ok = open_actions_menu(page)
    print("Меню ДЕЙСТВИЯ:", ok)
    res = menu_item_coords(page, "Упаковать")
    page.mouse.click(*res)
    time.sleep(4)
    page.locator(".ant-select:visible").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Скачать как ZIP-архив").first.click()
    time.sleep(2)
    page.screenshot(path=str(OUT / "case28_64112_70_pack_zip.png"), full_page=True)
    try:
        with page.expect_download(timeout=60000) as dl_info:
            page.locator("button:visible", has_text="OK").last.click()
        dl = dl_info.value
        shutil.copy(dl.path(), PACKAGED)
        print("Скачан архив:", dl.suggested_filename, "->", PACKAGED, "размер:", PACKAGED.stat().st_size)
    except Exception as e:
        print("Ошибка скачивания:", str(e)[:200])
        page.screenshot(path=str(OUT / "case28_64112_70_pack_err.png"), full_page=True)
    close_error(page)

    # --- Шаг 4: удалить ресурс, сохранить ---
    print("=== ШАГ 4: удалить ресурсы ===")
    errors_all.clear()
    open_editor_resources(page)
    body = page.locator("body").inner_text()
    print("Ресурс на месте до удаления:", "users.admin.dashboards.devices" in body or "Устройства" in body)
    row = page.locator(".ant-table-row:visible").last
    row.locator("input.ant-checkbox-input").first.check(force=True)
    time.sleep(1)
    page.locator("div.component-system-button:has(svg#ic_bin_24)").first.click()
    time.sleep(3)
    page.locator("div.component-system-button:has(svg#ic_apply_16)").first.click()
    time.sleep(8)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    body = page.locator("body").inner_text()
    print("Ресурсы после удаления (No Data):", "No Data" in body)
    page.screenshot(path=str(OUT / "case28_64112_71_after_delete.png"), full_page=True)
    print("JS-ошибок (шаг 4):", len(errors_all))
    close_error(page)

    # --- Шаг 5: Обновить из ZIP ---
    print("=== ШАГ 5: обновить приложение из архива ===")
    errors_all.clear()
    ok = open_actions_menu(page)
    print("Меню ДЕЙСТВИЯ:", ok)
    res = menu_item_coords(page, "Обновить")
    page.mouse.click(*res)
    time.sleep(4)
    page.locator(".ant-select:visible").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Загрузить как ZIP-архив").first.click()
    time.sleep(3)
    inputs = page.evaluate("""() => Array.from(document.querySelectorAll('input[type=file]')).map(
        (e, i) => ({i, accept: e.accept}))""")
    print("inputs:", inputs)
    target = [x for x in inputs if x["accept"] == ""]
    if target:
        page.locator("input[type=file]").nth(target[0]["i"]).set_input_files(str(PACKAGED))
        print("Файл установлен")
    time.sleep(2)
    page.screenshot(path=str(OUT / "case28_64112_72_file_set.png"), full_page=True)
    page.locator("button:visible", has_text="OK").last.click()
    time.sleep(20)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_73_update_result.png"), full_page=True)
    body = page.locator("body").inner_text()
    has_window = "Результат обновления" in body
    print("Окно «Результат обновления» открылось:", has_window)
    body_peek(page, 1500)
    print("JS-ошибок (шаг 5):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    close_error(page)
    # закрыть окно результата, если открылось
    if has_window:
        b = page.locator("button:visible", has_text="OK")
        if b.count():
            b.last.click()
            time.sleep(6)

    # --- Шаг 6: ресурс вернулся ---
    print("=== ШАГ 6: проверка возврата ресурса ===")
    open_editor_resources(page)
    page.screenshot(path=str(OUT / "case28_64112_74_resources_final.png"), full_page=True)
    body = page.locator("body").inner_text()
    returned = ("users.admin.dashboards.devices" in body) or ("Устройства" in body)
    print("Ресурс «Устройства» вернулся:", returned)
    body_peek(page, 500)

    # --- Очистка: удалить приложение test ---
    print("=== ОЧИСТКА: удалить приложение test ===")
    ok = open_actions_menu(page)
    print("Меню ДЕЙСТВИЯ:", ok)
    res = menu_item_coords(page, "Удалить")
    page.mouse.click(*res)
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_75_delete_confirm.png"), full_page=True)
    body = page.locator("body").inner_text()
    # подтверждение удаления
    for txt in ("Да", "Удалить", "OK"):
        b = page.locator("button:visible", has_text=txt)
        if b.count():
            print("Подтверждаю удаление кнопкой:", txt)
            b.last.click()
            time.sleep(8)
            break
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    body = page.locator("body").inner_text()
    print("Приложение test удалено:", "test" not in body.split("Создать")[0])
    page.screenshot(path=str(OUT / "case28_64112_76_after_cleanup.png"), full_page=True)
    print("JS-ошибок (всего):", len(errors_all))
    browser.close()
