# -*- coding: utf-8 -*-
"""Кейс 16 (ASD-6480): проверка обрезания вкладок «Информации о сервере» на 6.41.11-2532."""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    sel = "input[placeholder*='Имя пользователя' i]"
    page.fill(sel, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--headless=new", "--disable-gpu", "--no-sandbox",
            "--disable-dev-shm-usage", "--disable-web-security",
        ])
        context = browser.new_context(ignore_https_errors=True,
                                      viewport={"width": 1280, "height": 720})
        page = context.new_page()
        login(page)

        print("Открываем Информацию о сервере")
        page.screenshot(path=str(SCREENSHOTS / "case16_after_login.png"), full_page=True)
        navs = page.evaluate("""() => Array.from(document.querySelectorAll('a, span, div'))
            .map(e => (e.textContent || '').trim())
            .filter(t => t.includes('Информация') || t.includes('Сервер'))
            .slice(0, 20)""")
        print("Найденные элементы:", json.dumps(navs, ensure_ascii=False))
        page.click("text=Просмотр информации о сервере", timeout=10000)
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS / "case16_server_info_64111.png"), full_page=True)

        # Ищем вкладки: Bootstrap nav-tabs / role=tab в правой панели
        info = page.evaluate("""() => {
            const tabs = Array.from(document.querySelectorAll('[role="tab"], .nav-tabs > li, .nav-tabs > a, .nav-link'));
            const seen = new Set();
            const items = [];
            for (const t of tabs) {
                const r = t.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) continue;
                const key = Math.round(r.x) + ':' + Math.round(r.y) + ':' + t.textContent.trim().slice(0, 40);
                if (seen.has(key)) continue;
                seen.add(key);
                items.push({
                    text: t.textContent.trim().slice(0, 60),
                    x: Math.round(r.x), y: Math.round(r.y),
                    w: Math.round(r.width), h: Math.round(r.height),
                    right: Math.round(r.right),
                });
            }
            // Контейнер вкладок — ближайший общий предок первой строки
            let container = null;
            if (tabs.length) {
                let el = tabs[0];
                while (el && el !== document.body) {
                    const cs = getComputedStyle(el);
                    if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll' || cs.overflowX === 'hidden') ) { container = el; break; }
                    el = el.parentElement;
                }
            }
            const cw = container ? {
                cls: container.className.slice(0, 80),
                clientWidth: container.clientWidth,
                scrollWidth: container.scrollWidth,
                overflowX: getComputedStyle(container).overflowX,
            } : null;
            // Есть ли выпадающее меню "Ещё" / стрелки прокрутки
            const more = Array.from(document.querySelectorAll('.dropdown-menu, [class*="scroll"] button, [class*="arrow"]'))
                .map(e => e.className.slice(0, 60)).slice(0, 10);
            return { n_tabs: items.length, tabs: items.slice(0, 25), container: cw, more };
        }""")
        print(json.dumps(info, ensure_ascii=False, indent=1))
        (SCREENSHOTS / "case16_tabs_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        browser.close()

if __name__ == "__main__":
    main()
