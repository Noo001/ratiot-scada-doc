# Документация RatioT

Этот репозиторий содержит портал документации для проектов RatioT. Сейчас в нём размещена документация по **RatioT SCADA**.

## Где смотреть сайт

Сайт публикуется через **GitLab Pages** из проекта `ratiot/doc`:

```
https://gitlab.dkc.ru/ratiot/doc/-/pages
https://gitlab.dkc.ru/pages/ratiot/doc/
```

> Точный URL можно посмотреть в GitLab: проект `ratiot/doc` → слева **Deploy → Pages** или **Settings → Pages**.

## Структура репозитория

```
.
├── .gitlab-ci.yml      # Конфигурация GitLab Pages
├── index.html          # Главная страница с плитками проектов
├── style.css           # Общие стили
└── scada/
    ├── index.html      # База знаний по RatioT SCADA
    └── ux.html         # Руководство пользователя по интерфейсу
```

## Как вносить изменения

1. Редактируй файлы в локальной копии `C:/repos/ratiot-scada-doc-publish`.
2. Закоммить и запушь в `main`:

```bash
cd /c/repos/ratiot-scada-doc-publish
git add .
git commit -m "описание изменений"
git push origin main
```

Если SSH-ключ настроен отдельно:

```bash
GIT_SSH_COMMAND="ssh -i /c/Users/andrey.efremtsev/.ssh/ratiot_scada_doc_deploy -o StrictHostKeyChecking=no" git push origin main
```

После пуша GitLab автоматически запустит pipeline `pages` и опубликует новую версию сайта. Проверить статус можно в проекте `ratiot/doc` → **Build → Pipelines**.

## Как запускать локально (для проверки перед пушем)

Можно открыть `index.html` прямо в браузере, но некоторые браузеры блокируют локальные ресурсы (CSS, переходы между страницами). Лучше запустить минимальный сервер:

### Через Python (если установлен)

```bash
cd /c/repos/ratiot-scada-doc-publish
python -m http.server 8765
```

### Через Perl (если есть `server.pl` из старого проекта)

```bash
cd /c/repos/ratiot-scada-doc-publish
perl server.pl
```

После этого сайт доступен по адресу:

```
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

4. Убедись, что папка проекта копируется в артефакт `public` в `.gitlab-ci.yml`:

```yaml
script:
  - mkdir public
  - cp index.html style.css public/
  - cp -r scada public/
  - cp -r newproject public/
```

5. Запушь изменения.

## CI/CD

Pipeline использует job `pages`:

- **Stage:** `deploy`
- **Runner:** `tvr-v-rdep` (тег `shell`)
- **Executor:** shell
- **Артефакт:** папка `public` со всеми файлами сайта

Если pipeline не берёт задачу, проверь, что в `.gitlab-ci.yml` указан тег, соответствующий доступному раннеру:

```yaml
tags:
  - shell
```

## Контакты и вопросы

- Проект в GitLab: `https://gitlab.dkc.ru/ratiot/doc`
- Локальная рабочая копия: `C:/repos/ratiot-scada-doc-publish`
- Контекст и заметки: `C:/repos/scada-doc/KIMIKO_CONTEXT.md`
