# -*- coding: utf-8 -*-
"""Кейс 28: клик по иконке ⭳ у поля «Архив» — поиск filechooser."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
ARCHIVE = DL / "case28_test_app.zip"
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
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    login(page)
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)
    page.locator("td:has-text('test')").first.click()
    time.sleep(3)
    res = page.evaluate("""() => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === 'Обновить' && e.getBoundingClientRect().width);
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""")
    page.mouse.click(*res)
    time.sleep(4)
    page.locator(".ant-select:visible", has_text="Загрузить из папки сервера").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Загрузить как ZIP-архив").first.click()
    time.sleep(3)

    # иконка справа от поля «Архив»
    icon = page.evaluate("""() => {
      const lbl = Array.from(document.querySelectorAll('*')).find(
        e => e.children.length === 0 && e.textContent.trim() === 'Архив' && e.getBoundingClientRect().width);
      if (!lbl) return null;
      const row = lbl.closest('div[class*=row], div[class*=field], tr') || lbl.parentElement;
      const icons = row.querySelectorAll('svg[id], [class*=upload], [class*=download]');
      const out = [];
      icons.forEach(s => { const r = s.getBoundingClientRect(); if (r.width) out.push({id: s.id || s.className.baseVal || s.className, x: Math.round(r.x), y: Math.round(r.y)}); });
      return out;
    }""")
    print("Иконки у поля «Архив»:", icon)

    # клик по первой иконке с ожиданием filechooser
    try:
        with page.expect_event("filechooser", timeout=10000) as fc_info:
            if icon:
                page.mouse.click(icon[0]["x"] + 5, icon[0]["y"] + 5)
        chooser = fc_info.value
        print("FILECHOOSER! accept:", chooser.page.locator("input[type=file]").evaluate_all(
            "els => els.map(e => e.accept)"))
        chooser.set_files(str(ARCHIVE))
        print("Файл передан")
        time.sleep(3)
        page.screenshot(path=str(OUT / "case28_64112_56_file_set.png"), full_page=True)
        body = page.locator("body").inner_text()
        print("BODY:", body[:400].replace("\n", " | "))
    except Exception as e:
        print("Нет filechooser:", str(e)[:100])
    # fallback: input[type=file] с пустым accept (загрузчик архива)
    inputs = page.evaluate("""() => Array.from(document.querySelectorAll('input[type=file]')).map(
        (e, i) => ({i, accept: e.accept, name: e.name, id: e.id}))""")
    print("inputs:", inputs)
    target = [x for x in inputs if x["accept"] == ""]
    if target:
        page.locator("input[type=file]").nth(target[0]["i"]).set_input_files(str(ARCHIVE))
        print("Файл установлен в input №", target[0]["i"])
        time.sleep(3)
        page.screenshot(path=str(OUT / "case28_64112_56_file_set.png"), full_page=True)
        body = page.locator("body").inner_text()
        print("BODY:", body[:400].replace("\n", " | "))
