# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521): финальный сценарий, часть 2.

Текущее состояние: приложение test создано, ресурс «Устройства» добавлен.
Шаги: упаковать (скачать ZIP из окна «Результат экспорта») -> проверить ZIP ->
удалить ресурс -> обновить из ZIP -> проверить «Результат обновления» и возврат ресурса ->
удалить приложение.
"""
import time
import shutil
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
DL = Path(__file__).parent / "downloads"
PACKAGED = DL / "case28_test_app_packaged.zip"
BASE = "https://localhost:8443"
CC = f"{BASE}/web/dashboards/users.admin.dashboards.scadaControlCenter"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def body_peek(page, n=900):
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


def close_error(page):
    for _ in range(3):
        if "Копировать текст ошибки" not in page.locator("body").inner_text():
            return
        b = page.locator("button:visible", has_text="Закрыть")
        if b.count():
            b.last.click()
            time.sleep(1)


def goto_cc(page):
    page.goto(CC, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(8)


def menu_item_coords(page, item_text):
    res = page.evaluate("""(txt) => {
      const els = Array.from(document.querySelectorAll('*')).filter(
        e => e.children.length === 0 && e.textContent.trim() === txt && e.getBoundingClientRect().width);
      if (!els.length) return null;
      const r = els[0].getBoundingClientRect();
      return [Math.round(r.x + 5), Math.round(r.y + 5)];
    }""", item_text)
    return res


def open_actions_menu(page, name="test"):
    goto_cc(page)
    page.locator(f"td:has-text('{name}')").first.click()
    time.sleep(3)
    return "ДЕЙСТВИЯ" in page.locator("body").inner_text()


def open_editor_resources(page, name="test"):
    goto_cc(page)
    page.locator(f"tr:has-text('{name}') .system-tree-context-name").first.click()
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    page.locator(".ant-tabs-tab:visible", has_text="Ресурсы").first.click()
    time.sleep(4)


def select_zip_upload(page):
    page.locator(".ant-select:visible").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Загрузить как ZIP-архив").first.click()
    time.sleep(3)


def create_app(page, name="test"):
    goto_cc(page)
    if page.locator(f"tr:has-text('{name}')").count():
        print("Приложение уже есть")
        return
    page.locator("button:has-text('Создать')").first.click()
    time.sleep(3)
    inputs = page.locator("input:visible")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        ph = inp.get_attribute("placeholder") or ""
        box = inp.bounding_box()
        if "Фильтр" in ph or not box or box["x"] > 1200:
            continue
        inp.fill(name)
        break
    time.sleep(1)
    page.locator("button:has-text('OK')").last.click()
    time.sleep(12)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    close_error(page)
    print("Приложение создано, URL:", page.url)


def add_resource_via_tree(page, dash_name="Устройства"):
    """Дашборд приложения: «Добавить ресурс» -> Инструментальные панели -> панель -> OK -> OK."""
    page.locator("button:visible", has_text="Добавить ресурс").first.click()
    time.sleep(4)
    nodes = page.get_by_text("Инструментальные панели", exact=True).locator(
        "xpath=ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' system-tree-context ')][1]")
    node = nodes.filter(has=page.locator("label.agg-checkbox")).first
    node.locator(".system-tree-context-expand").first.click()
    time.sleep(3)
    child_node = node.locator(
        "xpath=./div[contains(@class,'system-tree-context-children')]/div[contains(@class,'system-tree-context')]"
    ).filter(has=page.get_by_text(dash_name, exact=True)).first
    child_node.locator("input.ant-checkbox-input").first.check(force=True)
    time.sleep(1)
    page.locator("button:has-text('OK')").last.click()
    time.sleep(5)
    body = page.locator("body").inner_text()
    if "Результат добавления" in body:
        page.screenshot(path=str(OUT / "case28_64112_82_add_result.png"), full_page=True)
        page.locator("button:has-text('OK')").last.click()
        time.sleep(8)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000},
                              accept_downloads=True)
    page = ctx.new_page()
    hook(page)
    login(page)

    # подготовка: приложение test с ресурсом «Устройства»
    print("=== ПОДГОТОВКА: создать test + добавить ресурс ===")
    create_app(page)
    open_editor_resources(page)
    body = page.locator("body").inner_text()
    if "Устройства" not in body:
        goto_cc(page)
        row = page.locator("tr:has-text('test')").first
        row.hover()
        time.sleep(1)
        row.locator(".kebab-btn").first.click()   # «Открыть» -> дашборд приложения
        time.sleep(10)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        add_resource_via_tree(page)
        print("Ресурс добавлен")
    else:
        print("Ресурс уже есть")

    # --- Шаг 3: упаковать -> ZIP ---
    print("=== ШАГ 3: упаковать -> ZIP ===")
    errors_all.clear()
    ok = open_actions_menu(page)
    print("Меню ДЕЙСТВИЯ:", ok)
    res = menu_item_coords(page, "Упаковать")
    page.mouse.click(*res)
    time.sleep(4)
    page.locator(".ant-select:visible").first.click()
    time.sleep(2)
    page.locator(".ant-select-item-option:visible", has_text="Скачать как ZIP-архив").first.click()
    time.sleep(2)
    page.locator("button:visible", has_text="OK").last.click()
    time.sleep(15)
    body = page.locator("body").inner_text()
    print("Окно «Результат экспорта»:", "Результат экспорта" in body)
    page.screenshot(path=str(OUT / "case28_64112_91_export_result.png"), full_page=True)

    # клик по иконке скачивания в строке application.zip
    packed = False
    try:
        icon = page.evaluate("""() => {
          const cells = Array.from(document.querySelectorAll('*')).filter(
            e => e.children.length === 0 && e.textContent.trim().startsWith('application.zip') && e.getBoundingClientRect().width);
          if (!cells.length) return null;
          const row = cells[0].closest('tr') || cells[0].parentElement.parentElement;
          const svgs = row.querySelectorAll('svg[id]');
          let best = null;
          svgs.forEach(s => {
            if ((s.id || '').includes('export') || (s.id || '').includes('download') || (s.id || '').includes('import')) {
              const r = s.getBoundingClientRect();
              if (r.width) best = [Math.round(r.x + 5), Math.round(r.y + 5)];
            }
          });
          return best;
        }""")
        print("Иконка скачивания:", icon)
        with page.expect_download(timeout=60000) as dl_info:
            if icon:
                page.mouse.click(*icon)
            else:
                # клик правее текста application.zip (иконка ⭳)
                cell = page.locator("text=application.zip").first
                box = cell.bounding_box()
                page.mouse.click(box["x"] + box["width"] + 30, box["y"] + box["height"] / 2)
        dl = dl_info.value
        shutil.copy(dl.path(), PACKAGED)
        print("Скачан архив:", dl.suggested_filename, "размер:", PACKAGED.stat().st_size)
        packed = True
    except Exception as e:
        print("Ошибка скачивания:", str(e)[:200])
        page.screenshot(path=str(OUT / "case28_64112_92_download_err.png"), full_page=True)
    close_error(page)

    if packed:
        # проверка ZIP
        try:
            with zipfile.ZipFile(PACKAGED) as z:
                names = z.namelist()
            print("ZIP валиден, записей:", len(names))
            print("  application.properties в корне:", any(n.endswith("application.properties") for n in names))
            print("  примеры:", names[:6])
        except Exception as e:
            print("ZIP невалиден:", str(e)[:150])

        # закрыть окно результата экспорта
        b = page.locator("button:visible", has_text="OK")
        if b.count() and "Результат экспорта" in page.locator("body").inner_text():
            b.last.click()
            time.sleep(4)

        # --- Шаг 4: удалить ресурс, сохранить ---
        print("=== ШАГ 4: удалить ресурсы ===")
        errors_all.clear()
        open_editor_resources(page)
        row = page.locator(".ant-table-row:visible").last
        row.locator("input.ant-checkbox-input").first.check(force=True)
        time.sleep(1)
        page.locator("div.component-system-button:has(svg#ic_bin_24)").first.click()
        time.sleep(3)
        page.locator("div.component-system-button:has(svg#ic_apply_16)").first.click()
        time.sleep(8)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        body = page.locator("body").inner_text()
        print("Ресурсы после удаления (No Data):", "No Data" in body)
        page.screenshot(path=str(OUT / "case28_64112_93_after_delete.png"), full_page=True)
        close_error(page)

        # --- Шаг 5: обновить из ZIP ---
        print("=== ШАГ 5: обновить из ZIP ===")
        errors_all.clear()
        ok = open_actions_menu(page)
        print("Меню ДЕЙСТВИЯ:", ok)
        res = menu_item_coords(page, "Обновить")
        page.mouse.click(*res)
        time.sleep(4)
        select_zip_upload(page)
        inputs = page.evaluate("""() => Array.from(document.querySelectorAll('input[type=file]')).map(
            (e, i) => ({i, accept: e.accept}))""")
        target = [x for x in inputs if x["accept"] == ""]
        if target:
            page.locator("input[type=file]").nth(target[0]["i"]).set_input_files(str(PACKAGED))
            print("Файл установлен в input №", target[0]["i"])
        time.sleep(2)
        page.screenshot(path=str(OUT / "case28_64112_94_file_set.png"), full_page=True)
        page.locator("button:visible", has_text="OK").last.click()
        time.sleep(25)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)
        page.screenshot(path=str(OUT / "case28_64112_95_update_result.png"), full_page=True)
        body = page.locator("body").inner_text()
        has_window = "Результат обновления" in body
        print("Окно «Результат обновления» открылось:", has_window)
        if has_window:
            seg = body.split("Результат обновления")[1][:700]
            no_data = "No Data" in seg
            print("Окно результата пустое (No Data):", no_data)
            print("Фрагмент результата:", seg.replace("\n", " | ")[:600])
        body_peek(page, 600)
        print("JS-ошибок (шаг 5):", len(errors_all))
        for e in errors_all[:8]:
            print("  -", e[:200])
        close_error(page)
        if has_window:
            b = page.locator("button:visible", has_text="OK")
            if b.count():
                b.last.click()
                time.sleep(6)

        # --- Шаг 6: ресурс вернулся ---
        print("=== ШАГ 6: проверка возврата ресурса ===")
        open_editor_resources(page)
        page.screenshot(path=str(OUT / "case28_64112_96_resources_final.png"), full_page=True)
        body = page.locator("body").inner_text()
        print("Ресурс «Устройства» вернулся:", "Устройства" in body)

    # очистка
    print("=== ОЧИСТКА: удалить приложение test ===")
    ok = open_actions_menu(page)
    if ok:
        res = menu_item_coords(page, "Удалить")
        page.mouse.click(*res)
        time.sleep(4)
        for txt in ("Да", "Удалить", "OK"):
            b = page.locator("button:visible", has_text=txt)
            if b.count():
                print("Подтверждаю кнопкой:", txt)
                b.last.click()
                time.sleep(8)
                break
        close_error(page)
        goto_cc(page)
        print("Приложение test удалено:", page.locator("tr:has-text('test')").count() == 0)
    page.screenshot(path=str(OUT / "case28_64112_97_after_cleanup.png"), full_page=True)
    print("JS-ошибок (всего):", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
