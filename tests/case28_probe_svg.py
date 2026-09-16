# -*- coding: utf-8 -*-
"""Кейс 28: дамп svg-иконок редактора приложения (id, родитель)."""
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
    page.locator("tr:has-text('test') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)

    info = page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('svg[id]').forEach(s => {
        const r = s.getBoundingClientRect();
        if (r.width === 0 || r.top < 180 || r.top > 420 || r.left > 1100) return;
        let p = s.parentElement;
        out.push({id: s.id, x: Math.round(r.x), y: Math.round(r.y),
                  parentTag: p ? p.tagName : '', parentClass: p ? (p.className||'').toString().slice(0,60) : '',
                  click: p ? (p.onclick ? 'yes' : '') : ''});
      });
      return out;
    }""")
    for it in info:
        print(it)
    browser.close()
