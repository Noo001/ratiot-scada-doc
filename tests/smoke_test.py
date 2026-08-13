"""Смоук-тест веб-интерфейса RatioT SCADA."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://localhost:8443"
SCREENSHOTS = Path(__file__).parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

console_errors = []
page_errors = []


def save(page, name: str):
    path = SCREENSHOTS / f"smoke_{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"Screenshot: {path}")
    return path


def log_console(msg):
    text = f"[{msg.type}] {msg.text}"
    loc = msg.location
    if loc and loc.get("url"):
        text += f" (url: {loc['url']})"
    console_errors.append(text)
    if msg.type in ("error", "warning"):
        print(text)


def log_page_error(err):
    page_errors.append(str(err))
    print(f"PAGE ERROR: {err}")


def wait_for_login(page):
    for _ in range(60):
        try:
            if page.locator("input[placeholder*='Имя пользователя' i]").count() > 0:
                return "input[placeholder*='Имя пользователя' i]"
            if page.locator("input[type='text']").count() > 0:
                return "input[type='text']"
        except Exception:
            pass
        time.sleep(1)
    return None


def login(page):
    print("Открываем логин")
    page.goto(f"{BASE_URL}/web/login", timeout=120000)
    page.wait_for_load_state("load", timeout=120000)
    time.sleep(5)
    save(page, "01_login_page")

    print("Ждем форму логина")
    login_selector = wait_for_login(page)
    print(f"Селектор: {login_selector}")

    print("Вводим учетные данные")
    page.fill(login_selector, "admin")
    page.fill("input[type='password']", "admin")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=60000)
    time.sleep(3)
    save(page, "02_after_login")


def navigate_and_shoot(page, menu_text: str, name: str, wait: int = 2):
    print(f"Открываем: {menu_text}")
    try:
        page.click(f"text={menu_text}", timeout=5000)
        time.sleep(wait)
        save(page, name)
    except Exception as e:
        print(f"Не удалось открыть {menu_text}: {e}")
        save(page, f"{name}_error")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ],
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.on("console", log_console)
        page.on("pageerror", log_page_error)

        login(page)

        navigate_and_shoot(page, "Информация о сервере", "03_server_info")

        # Открываем раздел Пользователи
        navigate_and_shoot(page, "Пользователи", "05_users")

        # Открываем Драйвера и расширения (именно так написано в дереве)
        navigate_and_shoot(page, "Драйвера и расширения", "06_drivers")

        # Поиск по слову Магазин
        print("Поиск 'Магазин'")
        try:
            search = page.locator("input[placeholder*='Поиск в системном дереве' i]")
            search.fill("Магазин")
            time.sleep(2)
            save(page, "07_store_search")
        except Exception as e:
            print(f"Поиск не удался: {e}")
            save(page, "07_store_search_error")

        print("Открываем встроенную документацию")
        page.goto(f"{BASE_URL}/static/docs/index.htm", timeout=30000)
        time.sleep(3)
        save(page, "09_docs")

        print("Лицензионная информация")
        page.goto(f"{BASE_URL}/system/license", timeout=30000)
        time.sleep(2)
        save(page, "10_license")

        print("Проверяем 404 /web/")
        page.goto(f"{BASE_URL}/web/thispagedoesnotexist", timeout=30000)
        time.sleep(1)
        save(page, "11_404_web")

        print("Проверяем 404 /static/docs/")
        page.goto(f"{BASE_URL}/static/docs/nonexistent.htm", timeout=30000)
        time.sleep(1)
        save(page, "12_404_docs")

        browser.close()

        # Сохраняем ошибки
        (SCREENSHOTS / "smoke_errors.txt").write_text(
            "CONSOLE ERRORS:\n" + "\n".join(console_errors) + "\n\nPAGE ERRORS:\n" + "\n".join(page_errors),
            encoding="utf-8",
        )
        print("Смоук-тест завершён")


if __name__ == "__main__":
    main()
