# Контекст проекта: RatioT SCADA

## Предустановки ассистента

- Имя: **Кимико**
- Род: женский
- Язык работы: **только русский**
- Язык мышления и рассуждений: **только русский**
- Рабочая папка документации: `C:/repos/doc`
- Принцип: не врать. Если не знаю — сказать. Если не уверена — сказать. Если ошиблась — исправить.
- **Жёсткое требование пользователя:** мыслить, рассуждать и общаться **только на русском**. Это обязательное правило, нарушать нельзя.

## Структура рабочих папок

```
C:/repos/doc/
├── .github/workflows/         # CI/CD для GitHub Pages
├── .gitlab-ci.yml             # CI/CD для GitLab (Pages / ВМ)
├── index.html                 # Главная страница портала
├── style.css                  # Общие стили
├── ux.html                    # Редирект на scada/ux.html
├── scada/                     # База знаний по RatioT SCADA
│   ├── index.html
│   ├── ux.html
│   └── style.css
├── product/                   # Продукт, экосистема, лицензирование, бизнес-процессы
│   └── index.html
├── bug_cases.html             # Баг-кейсы
├── bug_cases_print.html       # Версия для печати
├── bug_cases_report.html      # Отчёт по багам для руководителя
├── RatioT_SCADA_Bug_Cases.pdf # PDF-версия отчёта по багам
├── build_bug_cases.py         # Генерация bug_cases.html из tests/BUG_CASES.md
├── build_pdf.py               # Сборка PDF (старая версия)
├── generate_pdf.py            # Генерация PDF через Playwright
├── rebuild_report.py          # Перегенерация bug_cases_report.html
├── extract_*.py               # Скрипты извлечения текста из PDF/HTML
├── robots.txt                 # Запрет индексации поисковиками
├── tests/                     # Автотесты, отчёты, кейсы
└── sources/                   # Локальные исходные материалы (не в git)
```

> **Примечание:** папка `sources/` добавлена в `.gitignore` и хранится только локально. В репозиторий попадает результат обработки — статьи, выжимки и HTML-страницы.

## Цель

Протестировать программу RatioT SCADA 6.41.09, выявить несоответствия, ошибки и зависания в UI/UX, оформить тест-кейсы, а затем поддерживать краткую выжимку документации в едином репозитории на основе актуальной документации внутри самой программы.

## Установка RatioT SCADA

- Путь: `C:\Program Files\RatioTScada`
- Версия: `RatioT Server 6.41.09-2456`
- Web UI: `https://localhost:8443/web`
- HTTP-вариант: `http://localhost:8080/web` (если включён незащищённый доступ)
- REST API: `https://localhost:8443/rest/...`
- Встроенная документация: `C:\Program Files\RatioTScada\admin\custom\templates\docs\`
- Учётные данные для тестов: `admin / admin`, тестовый пользователь `testuser / TestPassword123!`

## Текущее состояние проекта

- В папке `sources/incoming/` находятся два PDF-файла:
  - `Руководство по развертыванию RatioT SCADA.pdf`
  - `Руководство по эксплуатации RatioT SCADA.pdf`
- Извлечённые тексты сохранены в `sources/extracted/`.
- Создан портал документации с базой знаний, баг-кейсами и отчётом для руководителя.
- Репозиторий размещается в GitLab; GitHub используется как временное зеркало для GitHub Pages.

## Что уже сделано

1. Найдена установка и запущен сервер.
2. Извлечена и проанализирована актуальная HTML-документация из `admin/custom/templates/docs/`.
3. Проведены базовые HTTP/REST проверки.
4. Сделаны headless-скриншоты страницы входа и других экранов.
5. Обновлена выжимка документации (`index.html`, `scada/index.html`, `scada/ux.html`).
6. Оформлены тест-кейсы в `tests/BUG_CASES.md` и опубликованы как `bug_cases.html`.
7. Сформирован сводный отчёт `bug_cases_report.html` с группировкой по статусу предъявления Объединению.
8. Построен PDF-отчёт `RatioT_SCADA_Bug_Cases.pdf`.
9. Скачан и распарсен changelog базовой платформы AggreGate (`sources/incoming/changelog.html` → `sources/extracted/changelog/changelog_parsed.tsv`).
10. Выполнено сравнение changelog с 17 баг-кейсами RatioT; отчёт сохранён в `sources/extracted/changelog/changelog_bug_cases_report.md`.
11. Скрипты для повторного парсинга и сопоставления размещены в `tools/parse_changelog.pl` и `tools/match_changelog_cases.pl`.
12. Извлечена встроенная справка RatioT SCADA 6.41.10 (1996 htm-файлов).
13. Справка сконвертирована в Markdown: `sources/extracted/scada-docs-6.41.10-md/` (1996 md-файлов + `index.md`).
14. Сделано сопоставление разделов справки с 17 баг-кейсами: `sources/extracted/scada-docs-6.41.10-md/case_matches.md`.
15. Создана HTML-страница `scada/docs-6.41.10.html` (карта справки 6.41.10 по 17 баг-кейсам с выдержками) и генератор `tools/build_scada_64110_page.pl`. Страница связана из `scada/index.html` и `scada/ux.html`.

## Ключевые инструменты

- `tests/test_ui_ux.py` — автоматические smoke-тесты HTTP/REST/UI.
- `tests/TEST_REPORT.md` — отчёт по найденным проблемам.
- `tests/BUG_CASES.md` — оформленные баг-кейсы и скриншоты.
- `rebuild_report.py` + `generate_pdf.py` — генерация HTML/PDF отчёта (Playwright + Chromium).
- `build_bug_cases.py`, `build_pdf.py`, `extract_*.py` — вспомогательные скрипты.
- Playwright — для UI-автоматизации.

## Извлечённые данные по RatioT SCADA

### Общая характеристика

- **RatioT SCADA** — SCADA/HMI-платформа, серверная часть работает на Java.
- Серверное ПО устанавливается как служба/демон на Windows (7/10/11/Server 2016/2019) и Linux.
- Клиентская часть — Web UI на React; запускается в браузерах Google Chrome / Mozilla Firefox.
- Есть отдельный инструмент **Net Admin** на порту **6440**.

### Компоненты и технологический стек

| Компонент | Описание |
|-----------|----------|
| JVM | Java 17; настройки через `*.vmoptions` (`-Xms/-Xmx`, прокси, язык) |
| БД конфигураций / исторические данные | Apache Cassandra (NoSQL), встроенная; опционально — RDBMS: MySQL, PostgreSQL, Oracle, MS SQL Server, Firebird |
| Встроенные БД | H2 / Cassandra для хранения |
| API | Собственный бинарный/API-протокол на порту **6460** |
| Web UI | HTTP **8080** / HTTPS **8443** (`/web`) |
| Net Admin | порт **6440** |
| SNMP | **162/UDP** |
| Мониторинг потоков | NetFlow **2055**, sFlow **6343**, Syslog **514** |
| Дополнительно | FTP/SSH/TFTP, BACnet **47808**, DNS, LDAP/AD, RADIUS, SMTP/POP3/IMAP, Heartbeat **7800** |

### Установка и развёртывание

- Дистрибутивы:
  - Windows: `RatioT_SCADA_full_6.34.07_windows-x64.exe`
  - Linux: `RatioT_SCADA_full_6.34.07_unix-x64.sh`
- Режимы установки:
  - GUI (`installer -c`)
  - Тихая (`installer -q -varfile response.varfile`)
  - Вручную через `response.varfile`
  - Docker-образ (Dockerfile с `xvfb-run --auto-servernum ./ag_server -r`)
- Целевой каталог по умолчанию:
  - Linux: `/opt/RatioT SCADA`
  - Windows: `C:\Program Files\RatioT SCADA`
- Лицензирование: `activation.txt` → получение `server.license`, активация через Net Admin.

### Управление сервером

- Linux:
  - systemd: `systemctl enable|restart|status %LS_BINARY%.service`
  - init-скрипт: `service %LS_BINARY%_service start|stop|restart|status`
  - консоль: `%LS_BINARY%_console`
- Windows: служба + консоль `%LS_BINARY%_console.exe`.

### Ключевые сущности системы

- **Проект (.prs)** — основная единица конфигурации SCADA.
- **Server / LinkServer** — ядро сбора данных, обработки тегов, хранения.
- **Модель (Model)** — логическое представление объекта/устройства.
- **Устройство (Device)** — источник данных (RTU/PLC/контроллер).
- **Тег / переменная** — значение из устройства или виртуальное.
- **Историк (Historian)** — хранение временных рядов.
- **Dashboard / HMI** — визуализация: формы, SVG-графика, таблицы, диаграммы.
- **События и алармы** — журналирование, SLA, уведомления (e-mail/SMS).
- **Пользователи и роли** — аутентификация, права доступа.
- **SQL-запросы** — встроенная возможность выполнять запросы к данным системы и внешним БД.
- **Скрипты / выражения** — поддержка Java, R, Python; DSL для binding вида `{users.admin.devices...}`.

### Поддерживаемые протоколы и источники данных

- Modbus (TCP/UDP/RTU/ASCII/Serial)
- OPC (DA) / OPC UA
- IEC-104 / IEC-104 Server
- DNP3
- MQTT
- SNMP
- HTTP/HTTPS
- BACnet
- CoAP
- DLMS/COSEM
- Ethernet/IP
- Kafka
- M-Bus
- NMEA 0183
- Omron FINS
- Siemens S7
- SIP
- SMPP
- SOAP
- SQL-подключения (JDBC)
- VMware
- WebSphere MQ
- WMI
- XMPP
- CORBA
- CWMP
- FTP/SSH/TFTP/SMB/CIFS
- Asterisk
- IPMI
- JMX
- Message stream
- RADIUS / LDAP / Active Directory

### Структура руководств

- **Руководство по эксплуатации:** ~2849 страниц, ~114 600 строк извлечённого текста.
  - Включает: введение, установку и администрирование, описание модели данных, протоколов, UI/HMI, скриптов, DevOps, резервное копирование, безопасность, API, примеры.
- **Руководство по развёртыванию:** 98 страниц, ~2600 строк.
  - Основные разделы: требования, установка, лицензирование, запуск, архитектура SCADA/HMI, базовые примеры dashboard, события/SLA, резервное копирование, обновление/удаление.

### Внешние источники по платформе AggreGate

- **Changelog AggreGate (рус.):** `https://aggregate.digital/ru/changelog.html`
  - Официальный лог изменений базовой платформы AggreGate, на которой работает RatioT SCADA.
  - Используется для перекрёстной проверки: исправлены ли зафиксированные в `tests/BUG_CASES.md` проблемы в новых версиях ядра.

## GitLab-проект для документации

- Проект: `https://gitlab.dkc.ru/ratiot/doc` (переименован из `ratiot/ratiot-scada-doc`).
- **Дистрибутивы RatioT SCADA:** `https://drive.google.com/drive/folders/1oetjGm66MAspkpMmon9lTHDiiOtep2Mu`
- Текущая роль пользователя: **Maintainer/Owner**.
- Репозиторий содержит портал документации:
  - `index.html` — главная страница с плитками проектов.
  - `style.css` — общие стили.
  - `scada/index.html` — база знаний по RatioT SCADA.
  - `scada/ux.html` — руководство пользователя по интерфейсу.
  - `.gitlab-ci.yml` — pipeline для публикации.
- **Деплой:** сейчас используется GitLab Pages; в будущем планируется публикация на собственную виртуальную машину с веб-сервером.

## GitHub-зеркало

- Репозиторий: `https://github.com/Noo001/ratiot-scada-doc`
- Workflow: `.github/workflows/pages.yml`
- URL Pages: `https://noo001.github.io/ratiot-scada-doc/`
- Назначение: временный хостинг через GitHub Pages, пока в контуре не будет готова виртуальная машина для деплоя из GitLab.

## CI/CD

- **GitHub Pages:** `.github/workflows/pages.yml` — публикует сайт при push в `main`.
- **GitHub PDF:** `.github/workflows/generate-pdf.yml` — перегенерирует отчёт по багам вручную.
- **GitLab:** `.gitlab-ci.yml` — job `pages` для GitLab Pages (временно) или деплоя на ВМ.

## Доработки отчёта по багам

- Левая колонка с навигацией по группам и кейсам в `bug_cases_report.html`.
- Подсветка активного пункта при скролле через `IntersectionObserver`.
- Адаптация длинных ссылок/таблиц (`overflow-wrap`, `word-break`, `min-width: 0`).
- «Серьёзность» переименована в «Критичность» в отчёте и в `tests/BUG_CASES.md`.
- Кейс «Ошибки создания ресурсов при первом запуске сервера» переведён на **Low**.
- HTML и PDF генерируются через `rebuild_report.py` + `generate_pdf.py`.

## Безопасность Web UI

- Web UI: HTTPS `8443`, HTTP `8080` (не рекомендуется наружу), Net Admin `6440` (только LAN/VPN).
- Стандартная учётка `admin / admin` — сменить сразу.
- Поддерживается управление пользователями/ролями, LDAP/AD, RADIUS, OAuth 2.0/OpenID Connect.
- SCADA наружу лучше не выставлять напрямую; использовать VPN/firewall и ограничить права.

## Требуется для продолжения работы

1. **Проверка отчёта по changelog:**
   - Файл `sources/extracted/changelog/changelog_bug_cases_report.md` требует ручной проверки найденных совпадений.
   - По платформенным кейсам (4, 5, 7, 8, 14, 15) нужно подтвердить, относятся ли пункты changelog к нашим багам.
2. **Обновление bug_cases_report.html:**
   - По запросу пользователя — перенести результаты сравнения changelog и справки 6.41.10 в `bug_cases_report.html`.
3. **Документация по новым файлам из `sources/incoming/`:**
   - После разархивации новых архивов в `sources/incoming/` нужно создать связные разделы базы знаний.
4. **GitLab и GitHub:**
   - GitHub Pages уже защищены паролем «111» и публикуют актуальную базу знаний.
   - GitLab (`origin`) требует SSH-ключа для синхронизации; ключ `~/.ssh/ratiot_scada_doc_deploy` используется для GitHub.

## Открытые вопросы

- Какая конечная цель проекта? (документация, генератор документации, портал, другое)
- Кто конечные пользователи?
- Есть ли сроки?
- Кто ещё в команде?
- Где будет располагаться папка с кодом?
- Есть ли доступ к другой машине с админскими правами для распаковки дистрибутива RatioT SCADA?
- Какие пункты из отчёта changelog действительно относятся к нашим багам и должны быть отражены в `bug_cases_report.html`?

## Правила ведения файла

- Это живой документ. Обновляется по мере поступления информации.
- В него записываются только проверенные и важные тезисы.
- Все договорённости фиксируются здесь.
