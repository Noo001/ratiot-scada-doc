# -*- coding: utf-8 -*-
"""Разведка: подсказки иконок левого рейла после логина."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SHOTS = Path(__file__).parent / "screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-web-security"])
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 950})
    page = ctx.new_page()
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    page.fill("input[placeholder*='Имя пользователя' i]", "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(8)

    # иконки рейла — ищем все img/svg в левой колонке
    icons = page.locator(".ant-layout-sider img, .ant-layout-sider svg, .ant-layout-sider .anticon, .ant-menu-item").all()
    print("Элементов в рейле:", len(icons))
    # Проще: hover по координатам колонки x=22
    for y in range(80, 480, 44):
        page.mouse.move(22, y)
        time.sleep(1.2)
        tips = page.locator(".ant-tooltip:visible, [class*='tooltip']:visible, [role='tooltip']").all_inner_texts()
        tips = [t.strip() for t in tips if t.strip()]
        print(f"y={y}: {tips}")
    page.screenshot(path=str(SHOTS / "rail_probe.png"))
    browser.close()
