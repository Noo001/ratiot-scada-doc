"""Кейсы 14 и 11: поведение на несуществующей странице /web/* после логина.

Кейс 14: раньше вместо интерфейса открывался JSON с ошибкой.
Кейс 11: вёрстка страницы 404.
"""
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
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(5)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox",
        "--disable-dev-shm-usage", "--disable-web-security",
    ])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 900})
    page = ctx.new_page()

    console_msgs = []
    page.on("console", lambda m: console_msgs.append(f"[{m.type}] {m.text}"))

    print("Логин...")
    login(page)
    print(f"После логина URL: {page.url}")
    page.screenshot(path=str(SCREENSHOTS / "case14_00_after_login.png"))

    bad_url = f"{BASE_URL}/web/nonexistent12345"
    print(f"\nПереход на несуществующую страницу: {bad_url}")
    page.goto(bad_url, timeout=60000)
    page.wait_for_load_state("load", timeout=60000)
    time.sleep(5)

    body = page.locator("body").inner_text()
    print(f"URL после перехода: {page.url}")
    print(f"Первые 500 символов body:\n{body[:500]}")
    looks_json = body.strip().startswith("{")
    print(f"Похоже на JSON-ошибку: {looks_json}")

    page.screenshot(path=str(SCREENSHOTS / "case14_11_404.png"), full_page=True)
    print("Скриншот: tests/screenshots/case14_11_404.png")

    errs = [m for m in console_msgs if m.startswith("[error]")]
    print(f"\nJS-ошибок в консоли: {len(errs)}")
    for e in errs[:5]:
        print(e)

    browser.close()
    print("\nИТОГ: JSON-ошибка" if looks_json else "\nИТОГ: интерфейс (не JSON)")
