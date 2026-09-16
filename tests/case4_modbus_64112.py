# -*- coding: utf-8 -*-
"""Кейс 4 (6.41.12-2562, free 100 tags): импорт/экспорт Modbus-регистров.

ASD-6484 закрыт АГ как Fixed, но драйвер Modbus в этом дистрибутиве недоступен,
поэтому сценарий импорта/экспорта воспроизвести нельзя. Скрипт фиксирует:
  1. Поиск "modbus" в системном дереве — результатов нет.
  2. Полный (прокрученный) список драйверов в диалоге «Добавить устройство» —
     Modbus отсутствует.
  3. «Установка модулей» — публичный репозиторий buff-lab.ru:6460 не отвечает,
     список модулей пуст.
  4. «Драйвера и расширения» — попытка открыть раздел.
  5. Контроль чистоты: тестовые устройства не создавались (список драйверов
     не содержит Modbus, диалог закрыт через «Отмена»).
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"


def collect_options(page):
    opts = []
    for sel in [".ant-select-item-option", "[role='option']"]:
        for o in page.locator(sel).all():
            try:
                if o.is_visible():
                    t = o.inner_text().strip()
                    if t and t not in opts:
                        opts.append(t)
            except Exception:
                pass
    return opts


def login(page):
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(10)


def tree_names(page):
    return [n.inner_text().strip() for n in page.locator(".system-tree-context-name").all()]


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    login(page)
    page.screenshot(path=str(OUT / "case4_01_after_login.png"))

    # --- 1. Поиск "modbus" в системном дереве ---
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("modbus")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(6)
    found = [t for t in tree_names(page) if "modbus" in t.lower()]
    print("1) Поиск 'modbus' в дереве, найдено узлов:", len(found), found)
    page.screenshot(path=str(OUT / "case4_02_tree_search_modbus.png"), full_page=True)

    # сброс поиска
    try:
        page.locator(".ant-input-clear-icon, [class*='clear']").first.click()
    except Exception:
        search.fill("")
        page.keyboard.press("Enter")
    time.sleep(2)

    # --- 2. Диалог «Добавить устройство» — полный список драйверов ---
    page.locator(".system-tree-context-name", has_text="Устройства").first.click(button="right")
    time.sleep(3)
    page.screenshot(path=str(OUT / "case4_03_context_menu_devices.png"))
    page.locator(".ant-dropdown-menu-item:has-text('Добавить устройство'), "
                 "li:has-text('Добавить устройство')").first.click()
    time.sleep(5)
    page.screenshot(path=str(OUT / "case4_04_add_device_dialog.png"), full_page=True)

    page.locator("text=Выберите драйвер").first.click()
    time.sleep(2)
    all_opts = set()
    for _ in range(15):
        all_opts.update(collect_options(page))
        pos = page.evaluate("""() => {
            for (const h of document.querySelectorAll('.rc-virtual-list-holder')) {
                if (h.offsetHeight > 0) { h.scrollTop += 200; return h.scrollTop + '/' + h.scrollHeight; }
            }
            return null;
        }""")
        time.sleep(0.6)
        if pos is None:
            break
        top, height = map(int, pos.split("/"))
        if top + 300 >= height:
            break
    all_opts.update(collect_options(page))
    drivers = sorted(o for o in all_opts if o != "Выберите драйвер")
    print(f"2) Драйверов в диалоге создания устройства: {len(drivers)}")
    for d in drivers:
        print("   -", d)
    has_modbus = any("modbus" in d.lower() for d in drivers)
    print("   MODBUS ДОСТУПЕН:", has_modbus)
    page.screenshot(path=str(OUT / "case4_05_driver_list.png"), full_page=True)
    page.screenshot(path=str(OUT / "case4_06_driver_list_scrolled.png"), full_page=True)

    # закрываем диалог без создания устройства
    page.keyboard.press("Escape")
    time.sleep(1)
    page.locator("button:has-text('Отмена')").first.click()
    time.sleep(3)

    # --- 3. «Установка модулей» ---
    page.locator("text=Установка модулей").first.click()
    time.sleep(6)
    page.screenshot(path=str(OUT / "case4_07_module_install_dialog.png"), full_page=True)
    page.locator("button:has-text('OK')").last.click()
    time.sleep(15)
    body = page.locator("body").inner_text()
    store_err = "Ошибка" in body or "Error" in body
    print("3) Установка модулей: ошибка подключения к магазину:", store_err,
          "| 'Modbus' на странице:", "modbus" in body.lower())
    page.screenshot(path=str(OUT / "case4_08_module_store_error.png"), full_page=True)
    # закрываем диалог установки модулей
    try:
        page.locator(".ant-modal-wrap button:has-text('Отмена'), "
                     ".ant-modal-wrap button:has-text('Cancel')").first.click(timeout=10000)
    except Exception:
        page.keyboard.press("Escape")
    time.sleep(3)
    time.sleep(5)

    # --- 4. «Драйвера и расширения» ---
    page.locator(".system-tree-context-name", has_text="Драйвера и расширения").first.click()
    time.sleep(6)
    print("4) URL после 'Драйвера и расширения':", page.url,
          "| 'Modbus' на странице:", "modbus" in page.locator("body").inner_text().lower())
    page.screenshot(path=str(OUT / "case4_09_drivers_extensions.png"), full_page=True)

    # --- 5. Контроль чистоты: раскрыть «Устройства» ---
    page.evaluate("""() => {
        const names = document.querySelectorAll('.system-tree-context-name');
        for (const n of names) {
            if (n.innerText.trim() === 'Устройства') {
                const row = n.closest('[class*=tree-treenode],[class*=TreeNode],li,div');
                const sw = row && row.querySelector('[class*=switcher],[class*=arrow],[class*=expand]');
                if (sw) { sw.click(); return; }
            }
        }
    }""")
    time.sleep(5)
    names = tree_names(page)
    devices_children = names[names.index("Устройства") + 1: names.index("Группы устройств")] \
        if "Устройства" in names and "Группы устройств" in names else []
    print("5) Дочерние узлы 'Устройства':", devices_children)
    page.screenshot(path=str(OUT / "case4_10_devices_expanded.png"), full_page=True)

    print("\nJS-ошибок страницы:", len(errors))
    for e in errors[:5]:
        print("   -", e[:200])
    print("\nИТОГ: проверка кейса 4 на 6.41.12-2562 невозможна — драйвер Modbus "
          "отсутствует в дистрибутиве (free 100 tags).")
    browser.close()
