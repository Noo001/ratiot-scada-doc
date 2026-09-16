# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521), шаги 4-6: удалить ресурсы, сохранить, обновить из архива, проверить результат."""
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


def body_peek(page, n=800):
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


def open_test_editor(page):
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
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
    open_test_editor(page)
    page.screenshot(path=str(OUT / "case28_64112_30_before_delete.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("До удаления, ресурс «Устройства» на месте:", "Устройства" in body)

    # --- Шаг 4: удалить все ресурсы ---
    errors_all.clear()
    row = page.locator(".ant-table-row:visible", has_text="Устройства").first
    print("Строк ресурсов:", page.locator(".ant-table-row:visible").count())
    row.locator("input.ant-checkbox-input").first.check(force=True)
    time.sleep(1)
    page.locator("div.component-system-button:has(svg#ic_bin_24)").first.click()
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_31_after_bin.png"), full_page=True)
    # подтверждение удаления, если появилось
    body = page.locator("body").inner_text()
    if "Удалить" in body and ("подтверд" in body.lower() or "Вы уверены" in body or "Да" in body):
        yes = page.locator("button:visible", has_text="Да")
        if yes.count():
            yes.first.click()
            time.sleep(3)
    # сохранить (ic_apply_16)
    page.locator("div.component-system-button:has(svg#ic_apply_16)").first.click()
    time.sleep(8)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_32_after_save.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("После удаления+сохранения, «Устройства» в ресурсах:", "Устройства" in body)
    print("JS-ошибок (шаг 4):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])

    # --- Шаг 5: обновить приложение из архива ---
    errors_all.clear()
    import_btn = page.locator("div.component-system-button:has(svg#ic_import_16)").first
    try:
        fc = page.wait_for_event("filechooser", timeout=15000)
        import_btn.click()
        chooser = fc.value
        chooser.set_files(str(ARCHIVE))
        print("Файл передан в диалог выбора:", ARCHIVE)
    except Exception as e:
        print("filechooser не сработал:", str(e)[:200])
        # fallback: скрытый input[type=file]
        inputs = page.locator("input[type=file]")
        print("input[type=file] на странице:", inputs.count())
        if inputs.count():
            inputs.first.set_input_files(str(ARCHIVE))
    time.sleep(12)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.screenshot(path=str(OUT / "case28_64112_33_after_import.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("Окно «Результат обновления» открылось:", "Результат обновления" in body)
    body_peek(page, 1200)
    print("JS-ошибок (шаг 5):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])

    # подтвердить результат обновления, если есть кнопка
    for txt in ("OK", "Применить", "Сохранить"):
        b = page.locator("button:visible", has_text=txt)
        if b.count() and "Результат обновления" in page.locator("body").inner_text():
            b.first.click()
            time.sleep(6)
            break

    # --- Шаг 6: проверить, что ресурс вернулся ---
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)
    page.screenshot(path=str(OUT / "case28_64112_34_after_update.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("После обновления, «Устройства» в ресурсах:", "Устройства" in body)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)
    page.screenshot(path=str(OUT / "case28_64112_35_resources_after_update.png"), full_page=True)
    body = page.locator("body").inner_text()
    print("Вкладка Ресурсы, «Устройства» на месте:", "Устройства" in body)
    print("JS-ошибок (шаг 6):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
