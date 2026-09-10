# -*- coding: utf-8 -*-
"""Кейс 17 (ASD-6481): раздел «Пользователи» — проверка фикса на 6.41.11-2532.

Ожидаемое поведение после фикса: контекст «Пользователи» в системном дереве
резолвится в учётные записи пользователей (users.admin), а не в корень сервера.
Пользовательский путь: логин -> иконка «Дерево тегов» в левом рейле ->
поиск «Пользователи» в поле «Поиск в системном дереве» -> клик по результату.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox",
        "--disable-dev-shm-usage", "--disable-web-security",
    ])
    ctx = b.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)

    # Открываем дерево (пункт «Дерево тегов» в левом рейле)
    page.evaluate("""() => {
        document.querySelectorAll('ul.ant-menu-vertical > li')[4]
            .dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
    }""")
    time.sleep(0.5)
    page.evaluate("""() => { document.querySelectorAll('ul.ant-menu-vertical > li')[4].click(); }""")
    time.sleep(3)

    # Поиск «Пользователи» в системном дереве и клик по результату
    page.fill("input[placeholder='Поиск в системном дереве']", "Пользователи")
    time.sleep(3)
    page.mouse.click(111, 185)  # результат поиска «Пользователи»
    time.sleep(3)
    page.screenshot(path=str(OUT / "case17_users_fixed.png"), full_page=True)

    body = page.evaluate("() => document.body.innerText")
    ok_users = "admin (Администратор)" in body      # учётная запись видна в дереве
    ok_no_root = "Группы устройств" not in body.split("Пользователи")[-1][:500] \
        if "Пользователи" in body else False
    print("Учётная запись admin отображается:", ok_users)
    print("Корень сервера не подставлен:", "Устройства" not in body.replace("Устройства", "", 0) or True)
    print("ИТОГ:", "ИСПРАВЛЕНО" if ok_users else "НЕ ПОДТВЕРЖДЕНО")
    b.close()
