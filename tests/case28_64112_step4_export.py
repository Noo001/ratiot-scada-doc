# -*- coding: utf-8 -*-
"""Кейс 28, шаг 3: упаковать/выгрузить приложение test как ZIP."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
DL.mkdir(exist_ok=True)
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
    page.locator(".ant-tabs-tab:visible, [role='tab']:visible", has_text="Ресурсы").first.click()
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
    page.screenshot(path=str(OUT / "case28_64112_21_before_export.png"), full_page=True)

    # тултипы верхних иконок: наводим по очереди
    header_icons = page.locator("button:visible")
    print("Кнопок видно:", header_icons.count())
    # иконки приложения — первая группа (☑ ⭳ ⭱) слева под вкладками Конфигурация
    # найдём их через svg внутри button
    for i in range(header_icons.count()):
        try:
            b = header_icons.nth(i)
            b.hover()
            time.sleep(1)
            tip = page.locator(".ant-tooltip:visible").last
            t = tip.inner_text().strip() if tip.count() else ""
            print(f"  b[{i}] tooltip={t[:60]!r}")
        except Exception as e:
            print(f"  b[{i}] err {e}")

    page.screenshot(path=str(OUT / "case28_64112_22_tooltips.png"), full_page=True)

    # экспорт приложения: верхняя иконка ic_export_16 (⭳)
    errors_all.clear()
    export_btn = page.locator("div.component-system-button:has(svg#ic_export_16)").first
    try:
        with page.expect_download(timeout=45000) as dl_info:
            export_btn.click()
        dl = dl_info.value
        path = dl.path()
        print("Скачан файл:", dl.suggested_filename, "->", path)
        dst = DL / "case28_test_app.zip"
        import shutil
        shutil.copy(path, dst)
        print("Сохранён как:", dst, "размер:", dst.stat().st_size)
        page.screenshot(path=str(OUT / "case28_64112_23_after_export.png"), full_page=True)
    except Exception as e:
        print("Download не произошёл:", str(e)[:300])
        page.screenshot(path=str(OUT / "case28_64112_23_export_dialog.png"), full_page=True)
        body_peek(page)

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
