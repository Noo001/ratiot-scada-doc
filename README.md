# Документация RatioT

Этот репозиторий содержит портал документации для проектов RatioT. Сейчас в нём размещена выжимка документации по **RatioT SCADA 6.41.09**.

## Где смотреть сайт

Сайт публикуется через **GitHub Pages**:

```text
https://noo001.github.io/ratiot-scada-doc/
```

После включения GitHub Pages в настройках репозитория сайт будет доступен по ссылке выше.

## Структура репозитория

```
.
├── .github/
│   └── workflows/
│       └── pages.yml     # Конфигурация GitHub Pages
├── index.html            # Главная страница с плитками проектов
├── style.css             # Общие стили
└── scada/
    ├── index.html        # База знаний по RatioT SCADA
    └── ux.html           # Руководство пользователя по интерфейсу
```

## Как вносить изменения

1. Редактируй файлы в локальной копии.
2. Закоммить и запушь в `main`:

```bash
cd /c/repos/github-ratiot-scada-doc
git add .
git commit -m "описание изменений"
git push origin main
```

После пуша GitHub Actions автоматически опубликует новую версию сайта. Проверить статус можно во вкладке **Actions**.

## Как запускать локально (для проверки перед пушем)

Можно открыть `index.html` прямо в браузере, но некоторые браузеры блокируют локальные ресурсы (CSS, переходы между страницами). Лучше запустить минимальный сервер:

### Через Python

```bash
cd /c/repos/github-ratiot-scada-doc
python -m http.server 8765
```

### Через Node.js

```bash
cd /c/repos/github-ratiot-scada-doc
npx http-server -p 8765
```

После этого сайт доступен по адресу:

```text
http://localhost:8765/
```

## Как добавить новый проект

1. Создай папку с документацией проекта, например `newproject/`.
2. Добавь туда `index.html` и другие файлы.
3. В `index.html` на главной странице добавь новую плитку в блок `.projects-grid`:

```html
<a href="newproject/" class="project-card">
  <div class="project-icon">NP</div>
  <div class="project-info">
    <h2>Название проекта</h2>
    <p>Краткое описание</p>
  </div>
</a>
```

4. Запушь изменения. GitHub Actions само опубликует новую версию.

## Тестирование и актуализация

Документация актуализирована по встроенной HTML-документации, поставляемой вместе с RatioT Server 6.41.09 (`admin/custom/templates/docs/`).

- `tests/test_ui_ux.py` — автоматические smoke-тесты Web UI и REST API.
- `tests/TEST_REPORT.md` — отчёт о найденных ошибках и несоответствиях.
- `screenshot_login.png` — скриншот страницы входа.

## CI/CD

Публикация через GitHub Actions:

- **Workflow:** `.github/workflows/pages.yml`
- **Триггер:** push в `main`
- **Результат:** сайт на GitHub Pages

Если сайт не обновляется после пуша, проверь вкладку **Actions → Deploy to GitHub Pages**.

## Контакты и вопросы

- Репозиторий: `https://github.com/Noo001/ratiot-scada-doc`
- Локальная рабочая копия: `C:/repos/github-ratiot-scada-doc`
