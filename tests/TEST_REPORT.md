# Отчёт по тестированию RatioT SCADA 6.41.09

**Дата:** 13.08.2026  
**Версия ПО:** RatioT Server 6.41.09-2456  
**Путь установки:** `C:\Program Files\RatioTScada`  
**Репозиторий документации:** `C:\repos\ratiot-scada-doc`  
**Тестируемый контур:** локальная Windows-установка, Web UI на `https://localhost:8443/web`

---

## 1. Что тестировали

| Область | Метод |
|---|---|
| Доступность Web UI | HTTP/HTTPS запросы, headless-скриншоты |
| Вход в систему (UI) | Скриншоты страницы `/web/login` |
| Внутренний дашборд | Прямые URL + токен авторизации |
| REST API | `POST /rest/auth`, `GET /rest/v1/contexts/...` |
| Статические ресурсы | Загрузка JS/CSS |
| Журнал сервера | Анализ `logs/server.log` |
| Актуальность документации | Сравнение HTML-доков из `admin/custom/templates/docs/` с выжимкой в репозитории |

---

## 2. Найденные ошибки

### 2.1. Ошибки при старте сервера

При первом запуске `RatioT_server_console.exe` сервер стартовал, но в `logs/server.log` зафиксированы 3 ERROR:

```
13.08.2026 12:47:25,471 ERROR ag.context
  Error creating resource 'users.admin.models.avatarManagement':
  Cannot invoke "...Context.callFunction(...)" because "container" is null

13.08.2026 12:47:25,733 ERROR ag.context
  Error creating resource 'users.admin.reports.maintenance':
  Контекст недоступен: users.admin.reports

13.08.2026 12:47:26,509 ERROR ag.context
  Error creating resource 'users.admin.models.workflowModel':
  Cannot invoke "...Context.callFunction(...)" because "container" is null
```

**Влияние:** часть встроенных моделей/отчётов не инициализировалась. Нужно проверить, не мешает ли это работе Web UI Builder и шаблонов по умолчанию.

**Воспроизведение:**
1. Установить RatioT SCADA 6.41.09 на чистую Windows.
2. Запустить `RatioT_server_console.exe`.
3. Дождаться строки `Starting web server`.
4. Открыть `logs/server.log` и поискать `ERROR ag.context`.

**Ожидаемое поведение:** первый запуск без ERROR/FATAL.

---

### 2.2. Несоответствие в документации внутри программы

Файл `admin/custom/templates/docs/cl_dashboard.htm` утверждает:

> «Инструментальные панели можно открывать и использовать только в программном обеспечении для настольных компьютеров **RatioT Client**».

В то же время `ls_wui_dashboards.htm` и `sh_creating_hmis.htm` описывают создание/использование панелей **в Web UI**.

**Влияние:** путаница у пользователя — инструментальные панели часть Web UI или только десктопа?.

**Воспроизведение:**
1. Открыть `https://localhost:8443/static/docs/cl_dashboard.htm`.
2. Прочитать первый абзац.
3. Открыть `https://localhost:8443/static/docs/ls_wui_dashboards.htm` и сравнить.

**Ожидаемое поведение:** единая терминология (Web UI = основной способ работы с панелями; RatioT Client — устаревший/альтернативный вариант).

---

### 2.3. Невозможно войти в Web UI по токену из URL

Передача `?token=<JWT>` в URL дашборда (`/web/dashboards/...`) не авторизует пользователя — SPA перенаправляет на форму логина.

**Влияние:** нельзя делать прямые ссылки на защищённые дашборды с предварительной авторизацией (deep links).

**Воспроизведение:**
1. `POST /rest/auth` с `{"username":"admin","password":"admin"}` → получить токен.
2. Открыть `https://localhost:8443/web/dashboards/users.admin.dashboards.default?token=<token>`.
3. Убедиться, что открылась страница логина, а не дашборд.

**Ожидаемое поведение:** токен принимается и пользователь попадает в дашборд.

---

## 3. Успешные проверки

| Проверка | Результат |
|---|---|
| Web UI открывается по `https://localhost:8443/web` | OK |
| Страница логина отрисовывается (логотип DKC, поля "Имя пользователя", "Пароль", кнопки "Войти"/"Зарегистрироваться") | OK |
| `POST /rest/auth` возвращает JWT-токен | OK |
| `GET /rest/v1/contexts/users.admin` с токеном возвращает 200 | OK |
| Загрузка JS/CSS работает быстро (< 100 мс) | OK |
| Встроенная документация доступна по `/static/docs/index.htm` | OK |

---

## 4. Рекомендации по доработке тестирования

1. Добавить UI-автоматизацию (Puppeteer/Playwright) для проверки сценария: логин → открытие Default Dashboard → открытие Конструктора Web UI.
2. Протестировать создание Device Server/Device через Net Admin (порт 6440).
3. Проверить, появляются ли ошибки `users.admin.models.avatarManagement`/`workflowModel` при открытии Web UI Builder.
4. Проверить производительность при большом количестве тегов/исторических данных.

---

## 5. Артефакты

- `tests/test_ui_ux.py` — автоматические smoke-тесты.
- `tests/screenshots/01_login.png` — страница входа.
