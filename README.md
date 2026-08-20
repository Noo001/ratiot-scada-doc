# Документация RatioT

Этот репозиторий — единый проект портала документации для продуктов RatioT. Сейчас в нём размещена документация по **RatioT SCADA 6.41.09**, включая базу знаний, баг-кейсы и отчёты по тестированию.

## Где смотреть сайт

- **GitHub Pages (временный хостинг):** `https://noo001.github.io/ratiot-scada-doc/`
- **GitLab:** проект `ratiot/doc`. После появления виртуальной машины в контуре сайт будет опубликован на ней.
- **Дистрибутивы RatioT SCADA:** `https://drive.google.com/drive/folders/1oetjGm66MAspkpMmon9lTHDiiOtep2Mu`

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
├── product/
│   └── index.html           # Продукт, экосистема, лицензирование, бизнес-процессы
├── bug_cases.html           # Баг-кейсы
├── bug_cases_print.html     # Версия для печати
├── bug_cases_report.html    # Сводный отчёт по багам
├── RatioT_SCADA_Bug_Cases.pdf
├── build_bug_cases.py       # Генерация bug_cases.html из tests/BUG_CASES.md
├── build_pdf.py             # Сборка PDF (старая версия)
├── generate_pdf.py          # Генерация PDF через Playwright
├── rebuild_report.py        # Перегенерация bug_cases_report.html
├── extract_*.py             # Скрипты извлечения текста из PDF/HTML
├── robots.txt               # Запрет индексации поисковиками
├── tests/                   # Автотесты, отчёты, Markdown-источники
└── sources/                 # Локальные исходные материалы (не в git)
```

> **Примечание:** папка `sources/` добавлена в `.gitignore` и хранится только локально. В репозиторий попадает результат обработки — статьи, выжимки и HTML-страницы.

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
