#!/usr/bin/env python3
"""UI-автоматизация RatioT SCADA Web UI через Playwright.

Сценарий:
1. Открыть страницу входа.
2. Сделать скриншот.
3. Нажать "Зарегистрироваться".
4. Заполнить форму регистрации.
5. Сделать скриншоты результата.
6. Войти созданным пользователем.
7. Сделать скриншот дашборда.
"""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = {
    "login": "tests/screenshots/01_login.png",
    "register_form": "tests/screenshots/02_register_form.png",
    "register_filled": "tests/screenshots/03_register_filled.png",
    "register_success": "tests/screenshots/04_register_success.png",
    "login_as_new": "tests/screenshots/05_login_as_new.png",
    "dashboard": "tests/screenshots/06_dashboard.png",
}

# Тестовый пользователь
TEST_USER = {
    "username": "testuser02",
    "password": "TestPassword123!",
    "confirm": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
}


async def logout(page):
    """Выход из системы через прямой URL."""
    try:
        await page.goto(f"{BASE_URL}/logout")
        await page.wait_for_timeout(2000)
        print("[OK] Выполнен выход через /logout")
        return True
    except Exception as e:
        print(f"[WARN] Не удалось выйти: {e}")
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # интерактивный режим: окно видно
            args=["--ignore-certificate-errors", "--ignore-urlfetcher-cert-requests"],
        )
        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        page.set_default_timeout(15000)

        # 1. Страница входа
        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_selector("input", state="visible")
        await page.screenshot(path=SCREENSHOTS["login"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['login']}")

        # 2. Переход к регистрации
        register_btn = page.locator("button:has-text('Зарегистрироваться')").first
        await register_btn.click()
        await page.wait_for_timeout(1500)
        await page.screenshot(path=SCREENSHOTS["register_form"], full_page=True)
        print(f"[OK] Скриншот: {SCREENSHOTS['register_form']}")

        # Получаем все input на странице
        all_inputs = await page.locator("input").all()
        print(f"[INFO] Найдено input: {len(all_inputs)}")

        # Заполняем обязательные поля по индексам (на основе скриншота):
        # 0: username, 1: first name, 2: last name, 3: password, 4: confirm password
        await all_inputs[0].fill(TEST_USER["username"])
        await all_inputs[1].fill(TEST_USER["first_name"])
        await all_inputs[2].fill(TEST_USER["last_name"])
        await all_inputs[3].fill(TEST_USER["password"])
        await all_inputs[4].fill(TEST_USER["confirm"])

        await page.screenshot(path=SCREENSHOTS["register_filled"], full_page=True)
        print(f"[OK] Скриншот: {SCREENSHOTS['register_filled']}")

        # Нажимаем кнопку регистрации
        submit = page.locator("button:has-text('Зарегистрироваться')").first
        await submit.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        await submit.click()
        await page.wait_for_timeout(5000)
        await page.screenshot(path=SCREENSHOTS["register_success"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['register_success']}")

        # 3. Разлогиниваемся (если регистрация сразу авторизовала)
        await logout(page)

        # 4. Вход созданным пользователем
        await page.goto(f"{BASE_URL}/web/login")
        await page.wait_for_selector("input[type='password']", state="visible")
        login_inputs = await page.locator("input").all()
        if len(login_inputs) >= 2:
            await login_inputs[0].fill(TEST_USER["username"])
            await login_inputs[1].fill(TEST_USER["password"])
            await page.locator("button:has-text('Войти')").first.click()
            await page.wait_for_timeout(5000)
            await page.screenshot(path=SCREENSHOTS["login_as_new"], full_page=False)
            print(f"[OK] Скриншот: {SCREENSHOTS['login_as_new']}")
        else:
            print("[WARN] На странице входа меньше 2 input — возможно, уже авторизованы")

        # 5. Дашборд (ждём отрисовки SPA)
        await page.wait_for_timeout(5000)
        await page.screenshot(path=SCREENSHOTS["dashboard"], full_page=False)
        print(f"[OK] Скриншот: {SCREENSHOTS['dashboard']}")

        await browser.close()
        print("[DONE] UI-автоматизация завершена")


if __name__ == "__main__":
    asyncio.run(main())
