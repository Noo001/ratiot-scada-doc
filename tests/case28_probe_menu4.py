# -*- coding: utf-8 -*-
"""Кейс 28: дамп HTML пункта «Обновить» в меню ДЕЙСТВИЯ."""
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
    print("Меню открыто:", "ДЕЙСТВИЯ" in page.locator("body").inner_text())

    # все видимые элементы, содержащие точный текст «Обновить»
    res = page.evaluate("""() => {
      const out = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
      let n;
      while (n = walker.nextNode()) {
        if (n.children.length === 0 && n.textContent.trim() === 'Обновить') {
          const r = n.getBoundingClientRect();
          if (r.width === 0) continue;
          out.push({tag: n.tagName, cls: (n.className||'').toString().slice(0,80),
                    x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width),
                    parentCls: (n.parentElement.className||'').toString().slice(0,80)});
        }
      }
      return out;
    }""")
    print("Пунктов «Обновить» (листовые, видимые):", res)
    if res:
        x, y = res[0]["x"] + 5, res[0]["y"] + 5
        print("Кликаю по координатам:", x, y)
        page.mouse.click(x, y)
        time.sleep(5)
        page.screenshot(path=str(OUT / "case28_64112_47_after_update_click.png"), full_page=True)
        print("BODY:", page.locator("body").inner_text()[:600].replace("\n", " | "))
        inputs = page.evaluate("() => Array.from(document.querySelectorAll('input[type=file]')).map(e => e.accept)")
        print("inputs:", inputs)
    browser.close()
