# -*- coding: utf-8 -*-
"""Кейс 21 (ASD-6499) на 6.41.12-2562: редактирование демо-проектов ioField и milkStorage."""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "screenshots"
BASE = "https://localhost:8443"

errors_all = []


def on_page_error(err):
    errors_all.append(str(err))


def on_console(msg):
    if msg.type == "error":
        errors_all.append(msg.text)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    page.on("pageerror", on_page_error)
    page.on("console", on_console)

    page.goto(f"{BASE}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)

    summary = {}
    for name in ["ioField", "milkStorage"]:
        errors_all.clear()
        url = f"{BASE}/web/dashboards/users.admin.dashboards.{name}/edit"
        print(f"\nОткрываем редактор: {url}")
        page.goto(url, timeout=120000)
        page.wait_for_load_state("networkidle", timeout=120000)
        time.sleep(15)
        page.screenshot(path=str(OUT / f"case21_64112_{name}_edit.png"), full_page=True)
        errors = list(errors_all)
        spinners = page.locator(".ant-spin-spinning").count()
        body = page.locator("body").inner_text()
        getctx = [e for e in errors if "getContextManager" in e]
        init_err = [e for e in errors if "init dashboard" in e.lower() or "Ошибка инициализации" in e]
        print(f"  URL: {page.url}")
        print(f"  JS-ошибок: {len(errors)}, getContextManager: {len(getctx)}, init dashboard: {len(init_err)}")
        for e in errors[:5]:
            print("   -", e[:200])
        print(f"  Видимых спиннеров: {spinners}")
        print(f"  BODY (300 символов): {body[:300]!r}")
        summary[name] = {"errors": errors[:10], "spinners": spinners, "url": page.url}

    (OUT / "case21_64112_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    browser.close()
    bad = {k: v for k, v in summary.items()
           if v["errors"] or v["spinners"] > 0 or "getContextManager" in json.dumps(v)}
    print("\nИТОГ:", "НЕ ИСПРАВЛЕНО: " + ", ".join(bad) if bad else "ИСПРАВЛЕНО (ошибок и спиннеров нет)")
