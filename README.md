# Документация RatioT

Этот репозиторий — единый проект портала документации для продуктов RatioT. Сейчас в нём размещена документация по **RatioT SCADA 6.41.09**, включая базу знаний, баг-кейсы и отчёты по тестированию.

## Где смотреть сайт

- **GitHub Pages (временный хостинг):** `https://noo001.github.io/ratiot-scada-doc/`
- **GitLab:** проект `ratiot/doc`. После появления виртуальной машины в контуре сайт будет опубликован на ней.

## Структура репозитория

```
.
├── .github/workflows/        # GitHub Actions: Pages + генерация PDF
├── .gitlab-ci.yml           # GitLab CI/CD
├── index.html               # Главная страница с плитками
├── style.css                # Общие стили
├── ux.html                  # Редирект на scada/ux.html
├── scada/
│   ├── index.html           # База знаний по RatioT SCADA
│   ├── ux.html              # Руководство пользователя по интерфейсу
│   └── style.css            # Стили раздела
├── bug_cases.html           # Баг-кейсы
├── bug_cases_print.html     # Версия для печати
├── bug_cases_report.html    # Сводный отчёт по багам
├── RatioT_SCADA_Bug_Cases.pdf
├── tests/                   # Автотесты, отчёты, Markdown-источники
├── sources/                 # Исходные материалы
│   ├── incoming/            # PDF-руководства
│   ├── extracted/           # Извлечённые тексты
│   ├── site/                # Локальная копия сайта
│   └── wiki/                # Архив Markdown Wiki
└── build/rebuild-скрипты    # build_bug_cases.py, rebuild_report.py и др.
```

## Как вносить изменения

1. Редактируй файлы в локальной копии `C:/repos/doc`.
2. Закоммить и запушь в `main`:

```bash
cd /c/repos/doc
git add .
git commit -m "описание изменений"
git push origin main
```

После пуша:
- GitHub Actions автоматически опубликует новую версию на GitHub Pages.
- GitLab CI запустит pipeline для публикации (сейчас GitLab Pages, позже — деплой на ВМ).

## Как запускать локально

Можно открыть `index.html` прямо в браузере, но некоторые браузеры блокируют локальные ресурсы. Лучше запустить минимальный сервер:

```bash
cd /c/repos/doc
python -m http.server 8765
```

или

```bash
perl sources/server.pl
```

После этого сайт доступен по адресу `http://localhost:8765/`.

## Как добавить новый проект

1. Создай папку с документацией проекта, например `newproject/`.
2. Добавь туда `index.html` и другие файлы.
3. В корневом `index.html` добавь новую плитку в блок `.tiles`.
4. Если используется GitLab Pages, убедись, что папка копируется в артефакт `public` в `.gitlab-ci.yml`.
5. Запушь изменения.

## CI/CD

- **GitHub Pages:** `.github/workflows/pages.yml` — публикует сайт при push в `main`.
- **Генерация PDF:** `.github/workflows/generate-pdf.yml` — перегенерирует `RatioT_SCADA_Bug_Cases.pdf` по запросу.
- **GitLab:** `.gitlab-ci.yml` — job `pages` (временно) или деплой на ВМ.

## Контакты и вопросы

- GitLab: `https://gitlab.dkc.ru/ratiot/doc`
- GitHub: `https://github.com/Noo001/ratiot-scada-doc`
- Локальная рабочая копия: `C:/repos/doc`
