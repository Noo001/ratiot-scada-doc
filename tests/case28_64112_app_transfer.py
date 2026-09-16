# -*- coding: utf-8 -*-
"""Кейс 28 (ASD-6521): перенос приложения «test» по алгоритму вендора на 6.41.12-2562."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"

errors_all = []


def hook(page):
    page.on("pageerror", lambda e: errors_all.append(str(e)))
    page.on("console", lambda m: errors_all.append(m.text) if m.type == "error" else None)


def body_peek(page, n=1200):
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


def close_error_dialogs(page):
    """Закрыть всплывшие диалоги ошибок «Error / UI процедура» (они поверх остального)."""
    for _ in range(5):
        body = page.locator("body").inner_text()
        if "UI процедура" not in body:
            break
        ok = page.locator("button:has-text('OK')")
        for i in reversed(range(ok.count())):
            try:
                ok.nth(i).click(timeout=2000)
                time.sleep(1)
                break
            except Exception:
                pass


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    hook(page)
    login(page)

    # --- Шаг 1: создать приложение test ---
    errors_all.clear()
    page.locator("button:has-text('Создать')").first.click()
    time.sleep(3)
    close_error_dialogs(page)

    inputs = page.locator("input:visible")
    print("Видимых input:", inputs.count())
    # печатаем placeholder каждого, чтобы выбрать верный
    for i in range(inputs.count()):
        try:
            print(f"  input[{i}] placeholder={inputs.nth(i).get_attribute('placeholder')!r}")
        except Exception as e:
            print(f"  input[{i}] err {e}")

    # Имя = видимый input с пустым placeholder внутри диалога (исключаем глобальный поиск и фильтр)
    name_filled = False
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        ph = inp.get_attribute("placeholder") or ""
        box = inp.bounding_box()
        if "Фильтр" in ph or not box or box["x"] > 1200:
            continue
        inp.fill("test")
        name_filled = True
        print(f"Заполнил input[{i}] (placeholder={ph!r}) значением 'test'")
        break
    assert name_filled, "не нашёл поле Имя"

    time.sleep(1)
    page.screenshot(path=str(OUT / "case28_64112_02_create_filled.png"), full_page=True)
    # Кнопка OK именно диалога (синяя, широкая)
    ok_btns = page.locator("button:has-text('OK')")
    for i in range(ok_btns.count()):
        b = ok_btns.nth(i)
        box = b.bounding_box()
        if box and box["width"] > 60:
            b.click()
            print("Кликнул OK кнопку №", i)
            break
    time.sleep(10)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    close_error_dialogs(page)
    page.screenshot(path=str(OUT / "case28_64112_03_after_create.png"), full_page=True)
    print("URL после создания:", page.url)
    body_peek(page, 800)

    # Проверить список приложений на главной
    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)
    body = body_peek(page, 800)
    print("Приложение test в списке:", "test" in body)
    page.screenshot(path=str(OUT / "case28_64112_04_main_with_test.png"), full_page=True)

    print("JS-ошибок:", len(errors_all))
    for e in errors_all[:8]:
        print("  -", e[:200])
    browser.close()
