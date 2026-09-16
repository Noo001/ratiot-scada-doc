# -*- coding: utf-8 -*-
"""Кейс 28: сохранить ресурс и упаковать приложение в ZIP (пункт «Упаковать»)."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"


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
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000},
                              accept_downloads=True)
    page = ctx.new_page()
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)

    # если ресурса нет — добавить строку с путём
    body = page.locator("body").inner_text()
    if "users.admin.dashboards.devices" not in body:
        page.locator("div.component-system-button:has(svg#ic_add_16)").first.click()
        time.sleep(4)
        row = page.locator(".ant-table-row:visible").last
        inp = row.locator("input[type=text]:visible, input:not([type]):visible").first
        inp.click()
        inp.fill("users.admin.dashboards.devices")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(3)

    # сохранить (☑ Сохранить свойства)
    page.locator("div.component-system-button:has(svg#ic_apply_16)").first.click()
    time.sleep(8)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    body = page.locator("body").inner_text()
    print("После сохранения, ресурс в списке:", "users.admin.dashboards.devices" in body or "Устройства" in body)
    page.screenshot(path=str(OUT / "case28_64112_60_saved.png"), full_page=True)

    # «Упаковать» через меню ДЕЙСТВИЯ на главной
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("td:has-text('test')").first.click()
    time.sleep(3)
    res = page.evaluate("""() => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === 'Упаковать' && e.getBoundingClientRect().width);
      if (!els.length) return null;
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""")
    print("Координаты «Упаковать»:", res)
    try:
        with page.expect_download(timeout=45000) as dl_info:
            page.mouse.click(*res)
        dl = dl_info.value
        print("Скачан:", dl.suggested_filename)
        import shutil
        dst = DL / "case28_test_app_packaged.zip"
        shutil.copy(dl.path(), dst)
        print("Сохранён:", dst, "размер:", dst.stat().st_size)
    except Exception as e:
        print("Download не был:", str(e)[:150])
        time.sleep(3)
        page.screenshot(path=str(OUT / "case28_64112_61_pack_err.png"), full_page=True)
        print("BODY:", page.locator("body").inner_text()[:400].replace("\n", " | "))
    browser.close()
