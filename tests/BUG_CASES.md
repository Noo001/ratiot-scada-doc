# Баг-кейсы RatioT SCADA 6.41.09

**Дата тестирования:** 13.08.2026  
**Версия:** RatioT Server 6.41.09-2456  
**Контур:** локальная установка `C:\Program Files\RatioTScada`  
**Учётные данные для тестов:** `admin / admin`, тестовый пользователь `testuser02 / TestPassword123!`

---

## Кейс 1. Ошибки создания ресурсов при первом запуске сервера

**Серьёзность:** Medium  
**Тип:** Ошибка инициализации

### Описание
При первом запуске `RatioT_server_console.exe` сервер стартует, но в журнале фиксируются 3 ERROR. Часть встроенных моделей и отчётов не инициализируется.

### Воспроизведение
1. Установить RatioT SCADA 6.41.09 на чистую Windows.
2. Запустить `C:\Program Files\RatioTScada\RatioT_server_console.exe`.
3. Дождаться строки `Starting web server`.
4. Открыть `C:\Program Files\RatioTScada\logs\server.log`.
5. Найти строки с `ERROR ag.context`.

### Ожидаемый результат
Первый запуск завершается без ERROR/FATAL.

### Фактический результат
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

### Скриншоты
- Лог-файл: см. `C:\Program Files\RatioTScada\logs\server.log`
- Автотест фиксирует проблему: `tests/test_ui_ux.py` → `test_log_errors()`

---

## Кейс 2. Токен в URL не авторизует пользователя в Web UI

**Серьёзность:** Medium  
**Тип:** UX / deep linking

### Описание
Передача JWT-токена в URL дашборда (`/web/dashboards/...?token=<token>`) не авторизует пользователя. SPA перенаправляет на форму логина.

### Воспроизведение
1. Получить токен:
   ```bash
   curl -k -X POST -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}' \
     https://localhost:8443/rest/auth
   ```
2. Открыть в браузере:
   ```
   https://localhost:8443/web/dashboards/users.admin.dashboards.default?token=<token>
   ```
3. Убедиться, что открылась страница логина.

### Ожидаемый результат
Токен принимается, пользователь попадает в дашборд.

### Фактический результат
Открывается форма логина.

### Скриншоты
- `screenshot_login.png` — страница входа вместо дашборда
- `screenshot_dashboard.png` — та же страница входа при открытии URL с токеном

---

## Кейс 3. Противоречивая документация внутри программы

**Серьёзность:** Low  
**Тип:** Документация / терминология

### Описание
Файл `admin/custom/templates/docs/cl_dashboard.htm` утверждает, что инструментальные панели можно использовать только в десктопном RatioT Client, в то время как остальная документация позиционирует панели как часть Web UI.

### Воспроизведение
1. Открыть в браузере:
   - `https://localhost:8443/static/docs/cl_dashboard.htm`
   - `https://localhost:8443/static/docs/ls_wui_dashboards.htm`
2. Сравнить первые абзацы.

### Ожидаемый результат
Единая терминология: Web UI — основной способ работы с панелями; RatioT Client — устаревший/альтернативный вариант.

### Фактический результат
Пользователь может запутаться, где реально работают дашборды.

---

## Кейс 4. Саморегистрация создаёт пользователя с доступом к Admin Panel

**Серьёзность:** High  
**Тип:** Безопасность / RBAC

### Описание
При включённой саморегистрации (`usersSelfRegistration = true`) новый пользователь, зарегистрированный через Web UI, сразу попадает в Admin Panel с полным системным деревом. Нет явного разделения ролей/ограничений.

### Учётные данные для воспроизведения
- Логин: `testuser02`
- Пароль: `TestPassword123!`

### Воспроизведение
1. Открыть `https://localhost:8443/web/login`.
2. Нажать **Зарегистрироваться**.
3. Заполнить обязательные поля:
   - Имя пользователя: `testuser02`
   - Имя: `Test`
   - Фамилия: `User`
   - Пароль: `TestPassword123!`
   - Повторите пароль: `TestPassword123!`
4. Нажать **Зарегистрироваться**.
5. После успешной регистрации откроется Admin Panel со всеми разделами (Системное дерево, Пользователи, Приложения, Инструментальные панели, Тревоги и т.д.).

### Ожидаемый результат
Новый пользователь получает минимальные права (operator/viewer), без доступа к Admin Panel и управлению пользователями.

### Фактический результат
Новый пользователь сразу видит Admin Panel.

### Скриншоты
- `tests/screenshots/02_register_form.png` — форма регистрации
- `tests/screenshots/03_register_filled.png` — заполненная форма
- `tests/screenshots/04_register_success.png` — сразу после регистрации открывается Admin Panel
- `tests/screenshots/05_login_as_new.png` — вход под `testuser02`, открывается Admin Panel
- `tests/screenshots/06_dashboard.png` — подтверждение, что новый пользователь видит админ-интерфейс

---

## Кейс 5. Консольный вывод Playwright повреждён (кодировка)

**Серьёзность:** Low  
**Тип:** Окружение / локализация

### Описание
При запуске `tests/ui_automation.py` в Git Bash русские сообщения в stdout отображаются как `��������`. Это не влияет на функциональность, но затрудняет отладку.

### Воспроизведение
1. Запустить `python tests/ui_automation.py` из Git Bash.
2. Обратить внимание на русский текст в консоли.

### Ожидаемый результат
Корректный вывод UTF-8.

### Фактический результат
Кракозябры из-за несоответствия кодировки терминала.

---

## Итог

| Кейс | Серьёзность | Статус |
|---|---|---|
| 1. Ошибки старта | Medium | Подтверждён |
| 2. Токен в URL не авторизует | Medium | Подтверждён |
| 3. Противоречивая документация | Low | Подтверждён |
| 4. Саморегистрация даёт админ-доступ | High | Подтверждён |
| 5. Кодировка консоли | Low | Подтверждён |
