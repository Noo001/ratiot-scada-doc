# -*- coding: utf-8 -*-
"""Кейс 5 (финальный прогон, v2):
A. Сохранённый набор колонок в редакторе (проверка, что сохранилось [Время, Событие]).
B. Живой виджет: набор колонок до события.
C. Генерация события: вход admin во втором контексте -> событие входа пользователя.
D. Набор колонок живого виджета после события.
E. Перезагрузка страницы -> набор колонок (persistence).
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
TREE = f"{BASE}/web/dashboards/users.admin.dashboards.scadaApplication"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def login(page):
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    if page.locator("input[placeholder*='Имя пользователя' i]").count() > 0:
        page.fill("input[placeholder*='Имя пользователя' i]", "admin")
        page.fill("input[type='password']", "admin")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(8)


def live_columns(page):
    return page.evaluate("""() => {
        const cont = document.querySelector('.container-scrolling.eventLog');
        const scope = cont || document;
        return [...scope.querySelectorAll('th')].map(t => t.innerText.trim()).filter(Boolean);
    }""")


def live_events(page):
    """Тексты строк событий (только с содержимым)."""
    return page.evaluate("""() => {
        const cont = document.querySelector('.container-scrolling.eventLog');
        const scope = cont || document;
        return [...scope.querySelectorAll('tbody tr')].map(r => r.innerText.replace(/\\s+/g, ' ').trim()).filter(t => t && t.includes('2026')).slice(0, 3);
    }""")


def expand_live_widget(page):
    page.locator(".dock-tab-title:has-text('Журнал событий')").first.click()
    time.sleep(3)
    page.mouse.click(1094, page.viewport_size["height"] - 22)
    time.sleep(4)


def popup_columns(page):
    return page.evaluate("""() => {
        const popups = [...document.querySelectorAll('.ant-dropdown-menu, [class*=dropdown] [role=menu]')].filter(m => m.offsetParent !== null);
        const popup = popups.find(m => m.innerText.includes('Сброс') || m.innerText.includes('OK'));
        if (!popup) return null;
        return [...popup.querySelectorAll('li, label')].map(li => {
            const cb = li.querySelector('input[type=checkbox]');
            return {text: li.innerText.trim().slice(0, 30), checked: cb ? cb.checked : null};
        }).filter(x => x.text);
    }""")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1700, "height": 1500})
    page = ctx.new_page()
    hook(page)
    login(page)
    errors_all.clear()

    # === A. сохранённая конфигурация в редакторе ===
    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("scadaApplication")
    time.sleep(4)
    page.keyboard.press("Enter")
    time.sleep(5)
    leaves = page.locator(".system-tree-context-name", has_text="Приложение")
    box = leaves.first.bounding_box()
    page.mouse.click(box["x"] + 30, box["y"] + box["height"] / 2, button="right")
    time.sleep(2.5)
    page.locator("[class*=context-menu] [class*=action]:has-text(\"Редактировать\")").first.click()
    time.sleep(20)
    page.locator("text=Журнал событий").filter(visible=True).nth(0).click()
    time.sleep(8)
    page.screenshot(path=str(OUT / "case5_step70_editor.png"), full_page=True)
    # триггер: точная иконка «колонки» справа в тулбаре виджета
    trig = page.evaluate("""() => {
        const cont = document.querySelector('.toolbar-container');
        const els = [...document.querySelectorAll('svg, button, [class*=trigger], [class*=dropdown]')].filter(e => e.offsetParent !== null);
        const out = [];
        document.querySelectorAll('*').forEach(e => {
            const b = e.getBoundingClientRect();
            if (b.y > 100 && b.y < 140 && b.x > 1600 && b.width > 5 && b.width < 40) {
                out.push({tag: e.tagName, x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2),
                          cls: String(e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className).slice(0,50)});
            }
        });
        return out.slice(0, 10);
    }""")
    print("элементы триггера:", json.dumps(trig, ensure_ascii=False))
    page.mouse.click(1670, 120)
    time.sleep(2.5)
    cols_editor = popup_columns(page)
    print("A. СОХРАНЁННЫЙ набор колонок (редактор):", json.dumps(cols_editor, ensure_ascii=False))
    page.screenshot(path=str(OUT / "case5_step71_editor_popup.png"), full_page=True)
    page.keyboard.press("Escape")

    # === B. живой виджет: до события ===
    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(12)
    expand_live_widget(page)
    cols_before = live_columns(page)
    ev_before = live_events(page)
    print("B. ЖИВОЙ набор ДО события:", cols_before)
    print("   события (до):", json.dumps(ev_before, ensure_ascii=False))
    page.screenshot(path=str(OUT / "case5_step72_live_before.png"), full_page=True)

    # === C. генерация события: вход admin во втором контексте ===
    ctx2 = browser.new_context(ignore_https_errors=True, viewport={"width": 1200, "height": 900})
    p2 = ctx2.new_page()
    hook(p2)
    print("C. логинимся вторым контекстом (генерация события входа)...")
    login(p2)
    p2.close()
    ctx2.close()

    # === D. ждём появления события и сравниваем колонки ===
    time.sleep(5)
    got = False
    for i in range(18):  # до ~3 минут
        ev_now = live_events(page)
        cols_now = live_columns(page)
        print(f"   [{i}] {json.dumps(ev_now[:1], ensure_ascii=False)[:90]} cols={cols_now}")
        if ev_now != ev_before and any("Вход" in e or "вход" in e or "2026" in e for e in ev_now):
            got = True
            print(">>> СОБЫТИЕ ПОСТУПИЛО")
            time.sleep(3)
            cols_after = live_columns(page)
            print("D. ЖИВОЙ набор ПОСЛЕ события:", cols_after)
            print("   события (после):", json.dumps(ev_now, ensure_ascii=False))
            page.screenshot(path=str(OUT / "case5_step73_live_after_event.png"), full_page=True)
            break
        time.sleep(10)
    if not got:
        print("D. событие не детектировано штатно; фиксируем текущее состояние")
        cols_after = live_columns(page)
        print("D. ЖИВОЙ набор (текущий):", cols_after)
        page.screenshot(path=str(OUT / "case5_step73_live_after_event.png"), full_page=True)

    # === E. перезагрузка ===
    page.goto(TREE, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(12)
    expand_live_widget(page)
    cols_reload = live_columns(page)
    print("E. ЖИВОЙ набор ПОСЛЕ ПЕРЕЗАГРУЗКИ:", cols_reload)
    page.screenshot(path=str(OUT / "case5_step74_live_reload.png"), full_page=True)

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:10]:
        print("  -", e[:250])
    browser.close()
