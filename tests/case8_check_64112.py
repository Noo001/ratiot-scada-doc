# -*- coding: utf-8 -*-
"""Кейс 8 (ASD-6485): HTML-сниппет сдвигает layout дашборда; после обновления сбрасывается. Проверка на 6.41.12-2562."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"
DASH = "Test_case8_dash"
DASH_URL = f"{BASE}/web/dashboards/users.admin.dashboards.{DASH}"
EDIT_URL = DASH_URL + "?mode=EDIT"

HTML_CODE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body { margin: 0; padding: 20px; background: #ffeecc; font-family: Arial, sans-serif; }
h2 { color: #336699; margin: 0 0 10px 0; }
p { color: #444444; }
</style>
</head>
<body>
<h2>Test snippet CASE8</h2>
<p>HTML snippet content</p>
</body>
</html>
"""

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def login(page):
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)


def wait_editor(page, timeout=150000):
    page.wait_for_selector(".dashboard-panel-content", state="visible", timeout=timeout)
    time.sleep(6)


def dirty(page):
    """True если во вкладке есть '*' (нет сохранённых изменений)."""
    try:
        title = page.locator("xpath=//div[contains(@class,'dock-tab') and contains(.,'Test_case8_dash')]").first.inner_text()
    except Exception:
        title = ""
    if not title:
        try:
            title = page.title()
        except Exception:
            title = ""
    return "*" in title


def drop_component(page, name, tx, ty, marker_re, tries=10):
    for t in range(tries):
        tx = tx if t % 2 == 0 else tx + 250
        try:
            src = page.locator(".component-on-palette", has_text=name).first
            dst = page.locator(".dashboard-panel-content").first
            src.drag_to(dst, target_position={"x": tx, "y": ty}, force=True, timeout=10000)
        except Exception:
            pass
        time.sleep(3.5)
        if page.locator(f"text=/{marker_re}/").count() > 0:
            return True
    return False


def open_component_props(page, marker_re):
    hdr = page.locator(f"text=/{marker_re}/").first
    hb = hdr.bounding_box()
    page.mouse.click(hb["x"] + hb["width"] + 14, hb["y"] + hb["height"] / 2)
    time.sleep(4)


def find_y(page, text):
    loc = page.get_by_text(text, exact=False).first
    if loc.count() == 0:
        return None
    try:
        bb = loc.bounding_box()
        return None if bb is None else round(bb["y"], 1)
    except Exception:
        return None


def save_dashboard(page):
    page.keyboard.press("Control+s")
    time.sleep(6)
    return True


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    hook(page)
    login(page)

    # ---------- 0. Создаём тестовый дашборд, если его нет ----------
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.wait_for(state="visible", timeout=60000)
    search.click(); search.fill(""); time.sleep(1); search.fill(DASH); time.sleep(3)
    page.keyboard.press("Enter"); time.sleep(6)
    exists = page.locator(".system-tree-context-name", has_text=DASH).count() > 0
    print("Дашборд существует:", exists)
    if not exists:
        search.click(); search.fill(""); time.sleep(1); search.fill("Инструментальные панели"); time.sleep(3)
        page.keyboard.press("Enter"); time.sleep(6)
        node = page.locator(".system-tree-context-name", has_text="Инструментальные панели").first
        node.click(button="right")
        time.sleep(3)
        page.mouse.click(283, 305)  # пункт «Создать»
        time.sleep(6)
        page.mouse.click(994, 178)  # поле Имя
        time.sleep(1)
        page.keyboard.type(DASH, delay=30)
        time.sleep(1)
        page.mouse.click(1509, 950)  # OK
        time.sleep(14)
        print("Дашборд создан, URL:", page.url)

    # ---------- 1. Редактор: сниппет сверху, подпись под ним ----------
    page.goto(EDIT_URL, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    wait_editor(page)
    page.screenshot(path=str(OUT / "case8_01_editor_empty.png"), full_page=False)

    ok_snip = drop_component(page, "HTML сниппет", 300, 120, r"htmlSni")
    print("Сниппет добавлен:", ok_snip)
    page.screenshot(path=str(OUT / "case8_02_snippet_dropped.png"), full_page=False)

    open_component_props(page, r"htmlSni")
    page.screenshot(path=str(OUT / "case8_03_snippet_props.png"), full_page=False)
    ta = page.locator("textarea:visible").last
    ta.click(force=True)
    time.sleep(1)
    page.keyboard.insert_text(HTML_CODE)
    time.sleep(2)
    page.screenshot(path=str(OUT / "case8_04_snippet_html.png"), full_page=False)
    page.mouse.click(1577, 68)  # закрыть панель свойств
    time.sleep(3)

    ok_label = drop_component(page, "Подпись", 620, 420, r"label\d")
    print("Подпись добавлена:", ok_label)
    time.sleep(2)
    page.screenshot(path=str(OUT / "case8_05_editor_both.png"), full_page=False)

    saved = save_dashboard(page)
    print("Сохранено:", saved)
    page.screenshot(path=str(OUT / "case8_06_editor_saved.png"), full_page=False)

    y_snip_design = find_y(page, "htmlSnippet0")
    y_lbl_design = find_y(page, "label0")
    print(f"Дизайн: snippet y={y_snip_design}, label y={y_lbl_design}")

    # ---------- 2. Визуализация (первый заход) ----------
    errors_all.clear()
    page.goto(DASH_URL, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(12)
    page.screenshot(path=str(OUT / "case8_07_view_first.png"), full_page=False)
    y_snip_v1 = find_y(page, "Test snippet CASE8")
    y_lbl_v1 = find_y(page, "label0")
    print(f"Визуализация (1-й заход): snippet y={y_snip_v1}, label y={y_lbl_v1}")
    print("JS-ошибок в визуализации:", len(errors_all))
    for e in errors_all[:5]:
        print("  -", e[:180])

    # ---------- 3. F5 ----------
    page.reload()
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(12)
    page.screenshot(path=str(OUT / "case8_08_view_after_f5.png"), full_page=False)
    y_snip_v2 = find_y(page, "Test snippet CASE8")
    y_lbl_v2 = find_y(page, "label0")
    print(f"Визуализация (после F5): snippet y={y_snip_v2}, label y={y_lbl_v2}")

    # ---------- 4. Снова редактор ----------
    page.goto(EDIT_URL, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    wait_editor(page)
    page.screenshot(path=str(OUT / "case8_09_editor_reopened.png"), full_page=False)
    y_snip_e2 = find_y(page, "htmlSnippet0")
    y_lbl_e2 = find_y(page, "label0")
    print(f"Редактор (повторно): snippet y={y_snip_e2}, label y={y_lbl_e2}")

    # ---------- Сводка ----------
    def delta(yl, ys):
        return None if yl is None or ys is None else round(yl - ys, 1)
    print("\n===== СВОДКА КЕЙС 8 =====")
    print(f"Дизайн:                delta(label-snippet) = {delta(y_lbl_design, y_snip_design)} px")
    print(f"Визуализация:          delta = {delta(y_lbl_v1, y_snip_v1)} px")
    print(f"Визуализация после F5: delta = {delta(y_lbl_v2, y_snip_v2)} px")
    print(f"Редактор повторно:     delta = {delta(y_lbl_e2, y_snip_e2)} px")

    # ---------- 5. Удаление тестового дашборда ----------
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.wait_for(state="visible", timeout=60000)
    search.click(); search.fill(""); time.sleep(1); search.fill(DASH); time.sleep(3)
    page.keyboard.press("Enter"); time.sleep(6)
    page.locator(".system-tree-context-name", has_text=DASH).first.click(button="right")
    time.sleep(3)
    page.screenshot(path=str(OUT / "case8_10_delete_menu.png"), full_page=False)
    deleted = False
    try:
        page.get_by_text("Удалить", exact=True).first.click(force=True)
        time.sleep(4)
        page.screenshot(path=str(OUT / "case8_11_delete_confirm.png"), full_page=False)
        for b in ("button:has-text('Да')", "button:has-text('OK')", "button:has-text('Удалить')"):
            if page.locator(b).count() > 0:
                page.locator(b).last.click(force=True)
                time.sleep(8)
                deleted = True
                break
    except Exception as e:
        print("Ошибка удаления:", str(e)[:150])
    print("Дашборд удалён:", deleted)
    page.screenshot(path=str(OUT / "case8_12_after_cleanup.png"), full_page=False)

    print("\nJS-ошибок (всего):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
