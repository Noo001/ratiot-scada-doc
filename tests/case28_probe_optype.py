# -*- coding: utf-8 -*-
"""Кейс 28: диалог «Выберите папку приложения» — варианты типа операции и иконки шапки."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
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
      if (!els.length) return null;
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""")
    print("Координаты «Обновить»:", res)
    if res:
        page.mouse.click(*res)
        time.sleep(4)

    # варианты «Тип операции»
    page.locator(".ant-select:visible", has_text="Загрузить из папки сервера").first.click()
    time.sleep(2)
    opts = page.locator(".ant-select-item-option:visible, .ant-select-dropdown li:visible")
    print("Вариантов типа операции:", opts.count())
    for i in range(opts.count()):
        print("  -", opts.nth(i).inner_text().strip()[:80])
    page.screenshot(path=str(OUT / "case28_64112_48_optype.png"), full_page=True)

    # иконки шапки диалога (тултипы)
    page.keyboard.press("Escape")
    time.sleep(1)
    dlg = page.locator("text=Выберите папку приложения").first
    header = dlg.locator("xpath=ancestor::div[contains(@class,'window') or contains(@class,'dialog') or position()=1][1]")
    svgs = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('svg[id]').forEach(s => {
        const r = s.getBoundingClientRect();
        if (r.width && r.top > 250 && r.top < 360 && r.left > 350 && r.left < 900) {
          let p = s.parentElement;
          out.push({id: s.id, x: Math.round(r.x), y: Math.round(r.y),
                    pCls: (p.className||'').toString().slice(0,60)});
        }
      });
      return out;
    }""")
    print("Иконки шапки диалога:", svgs)
    for it in svgs:
        page.mouse.move(it["x"] + 5, it["y"] + 5)
        time.sleep(1.2)
        tips = page.locator(".ant-tooltip:visible, [class*=tooltip]:visible")
        t = tips.last.inner_text().strip() if tips.count() else ""
        print(f"  {it['id']} tooltip: {t[:60]!r}")
    browser.close()
