# -*- coding: utf-8 -*-
"""Кейс 26 (ASD-6504): проверка отсутствия JS-ошибок getListenerCode при навигации по дереву на 6.41.12."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
TREE_URL = f"{BASE_URL}/web/dashboards/users.admin.dashboards.scadaApplication"
SHOTS = Path(__file__).parent / "screenshots"

console_msgs = []


def on_console(msg):
    text = f"[{msg.type}] {msg.text}"
    console_msgs.append(text)
    if msg.type == "error":
        print("CONSOLE ERROR:", text[:200])


def login(page):
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
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
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
    page = ctx.new_page()
    page.on("console", on_console)

    print("Логин...")
    login(page)
    console_msgs.clear()

    print("Открываем системное дерево...")
    page.goto(TREE_URL, timeout=120000)
    page.wait_for_load_state("networkidle", timeout=120000)
    time.sleep(10)

    print("Поиск «Устройства» в дереве...")
    search = page.locator("input[placeholder*='Поиск в системном дереве' i]").first
    search.fill("Устройства")
    time.sleep(3)
    page.keyboard.press("Enter")
    time.sleep(5)
    page.screenshot(path=str(SHOTS / "case26_search.png"))

    print("Клик по результату...")
    res = page.locator("text=Устройства").first
    res.click()
    time.sleep(10)
    page.screenshot(path=str(SHOTS / "case26_opened.png"), full_page=True)

    errors = [m for m in console_msgs if m.startswith("[error]")]
    gl = [m for m in errors if "getListenerCode" in m]
    print(f"\nВсего JS-ошибок: {len(errors)}")
    print(f"Ошибок getListenerCode: {len(gl)}")
    for e in gl[:5]:
        print(" ", e[:200])
    print("\nИТОГ:", "НЕ ИСПРАВЛЕНО" if gl else "ИСПРАВЛЕНО (ошибок getListenerCode нет)")
    browser.close()
