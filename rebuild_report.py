import re
import markdown
from pathlib import Path

md_path = Path("tests/BUG_CASES.md")
html_path = Path("bug_cases_report.html")
md_text = md_path.read_text(encoding="utf-8")

# Парсим кейсы из markdown
pattern = re.compile(r'<a id="(case-\d+)"></a>\n## Кейс (\d+)\.\s*(.+?)\n\n(.+?)(?=\n---|\n## |\Z)', re.DOTALL)
cases = []
for m in pattern.finditer(md_text):
    old_id = m.group(1)
    old_num = int(m.group(2))
    title = m.group(3).strip()
    body_md = m.group(4).strip()
    cases.append({
        'old_id': old_id,
        'old_num': old_num,
        'title': title,
        'body_md': body_md,
    })

# Фильтруем: убираем 12 (AggreGate), 14 (/web/* JSON 404), 15 (документация из SPA)
filtered = [c for c in cases if c['old_num'] not in (12, 14, 15)]

# Кейсы без тикета в АГ (реакции АГ нет). Полный список тикетов — в CONTEXT.md
NO_AG_REACTION = {4}

# Категории ошибок (по старой нумерации):
CAT_CUSTOM = "Ошибки кастомизации"
CAT_OEM = "Ошибки OEM"
CAT_PLATFORM = "Ошибки платформы партнёра"
custom_cases = {2, 11, 12, 15, 18, 22}
oem_cases = {1, 3, 9, 10, 25}

def cat_of(old_num):
    if old_num in custom_cases:
        return CAT_CUSTOM
    if old_num in oem_cases:
        return CAT_OEM
    return CAT_PLATFORM

# Задаём порядок по старой нумерации; группа вычисляется по категории
case_order = [2, 3, 4, 6, 7, 9, 1, 5, 8, 10, 11, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
order_and_groups = [(n, cat_of(n)) for n in case_order]
case_map = {c['old_num']: c for c in filtered}
ordered = []
for old_num, group in order_and_groups:
    if old_num in case_map:
        case_map[old_num]['group'] = group
        ordered.append(case_map[old_num])

# Перенумеровываем сквозной нумерацией
for i, c in enumerate(ordered, start=1):
    c['new_num'] = i

# Статусы по кейсам
statuses = {
    1: "Частично исправлено в 6.41.11 (2532): 3 исходных ERROR устранены, осталась deviceImages (ASD-6474)",
    2: "Передан в АГ (ASD-6482, блокер), ожидает реакции",
    3: "Передан в АГ (ASD-6483), ожидает реакции / в т.ч. в 6.41.11",
    4: "Подтверждён коллегами / в trial нет драйвера Modbus / реакции АГ нет",
    5: "Передан в АГ (ASD-6475), ожидает реакции / в trial нет редактора дашбордов",
    6: "Закрыто / не баг (by design)",
    7: "Передан в АГ (ASD-6486, блокер), ожидает реакции / переключение не проводилось",
    8: "Закрыто / не воспроизводится у АГ (ASD-6476, 6.41.10-2512), перепроверка невозможна, незначительный",
    9: "Передан в АГ (ASD-6487, критический), ожидает реакции / требует переустановки",
    10: "Передан в АГ (ASD-6477, критический), ожидает реакции",
    11: "Передан в АГ (ASD-6478), ожидает реакции",
    13: "Передан в АГ (ASD-6479), ожидает реакции",
    16: "Исправлено в 6.41.11-2532 (ASD-6480), проверено: скрытые вкладки доступны через меню «Ещё»",
    17: "Исправлено в 6.41.11-2532 (ASD-6481), проверено: контекст резолвится в учётные записи (users.admin)",
    18: "Исправлено в 6.41.11",
    19: "Не исправлено в 6.41.11",
    20: "Передан в АГ (ASD-6498), ожидает реакции / требует уточнения",
    21: "Исправлено в 6.41.11",
    22: "Частично исправлено в 6.41.11",
    23: "Требует уточнения / АГ: проект вне дистрибутива; передано имя дашборда «АСДУ (SCADA/HMI) v2»",
    24: "Исправлено в 6.41.11 / поведение подтверждено (ASD-6502)",
    25: "Закрыто / дубликат ASD-6496 (ASD-6503)",
    26: "Разрешён и закрыт (ASD-6504), самостоятельно не проверялось",
    27: "Закрыто / by design (ASD-6505); непоследовательность JSON/HTML 404 — см. кейс 14",
    28: "Исправлено в 6.41.11-2553 (по ответу АГ, ASD-6521) / самостоятельно не проверялось",
    29: "Исправлено в 6.41.11-2553 (по ответу АГ, ASD-6523, задача №20649) / самостоятельно не проверялось",
    30: "Ожидает ответа коллег (АГ запросили контексты и сценарий, ASD-6522)",
}

# Извлекаем критичность (поддерживаем старый "Критичность" и новый "Серьёзность")
def get_severity(body_md):
    m = re.search(r'\*\*(?:Критичность|Серьёзность):\*\*\s*(\w+)', body_md)
    return m.group(1) if m else "Medium"

for c in ordered:
    c['severity'] = get_severity(c['body_md'])
    c['status'] = statuses.get(c['old_num'], "Подтверждён")
    if c['old_num'] in NO_AG_REACTION:
        c['status'] += " / реакции АГ нет"
    c['cat'] = cat_of(c['old_num'])

filtered = ordered
for c in filtered:
    # Убираем строки серьёзности и типа из тела, т.к. они уже в meta
    c['body_md'] = re.sub(r'\*\*Критичность:\*\*\s*\w+\s*\n', '', c['body_md'])
    c['body_md'] = re.sub(r'\*\*Тип:\*\*\s*[^\n]+\s*\n', '', c['body_md'])
    c['body_md'] = re.sub(r'\*\*Категория:\*\*\s*[^\n]+\s*\n', '', c['body_md'])
    # Убираем служебные секции "Источник" и "Примечание" полностью
    c['body_md'] = re.sub(r'###\s*(Источник|Примечание)\s*\n(.*?)(?=###|\Z)', '', c['body_md'], flags=re.DOTALL)
    # Убираем служебные строки
    c['body_md'] = re.sub(r'[-*]\s*Автотест фиксирует проблему:.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*Лог-файл:.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*incoming/.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*Тикет\s+`[^`]+`\s*из\s*`[^`]+`\.?', '', c['body_md'])

# Генерируем строки таблицы с группами
groups_order = [CAT_CUSTOM, CAT_OEM, CAT_PLATFORM]
cases_by_group = {g: [] for g in groups_order}
for c in filtered:
    cases_by_group[c['group']].append(c)

table_rows = []
for group in groups_order:
    table_rows.append(f'<tr class="group-row"><td colspan="5"><strong>{group}</strong></td></tr>')
    for c in cases_by_group[group]:
        table_rows.append(
            f'<tr><td>{c["new_num"]}</td><td><a href="#case-{c["new_num"]}">{c["title"]}</a></td>'
            f'<td>{c["severity"]}</td><td>{c["cat"]}</td><td>{c["status"]}</td></tr>'
        )

summary_table = '<table class="summary-table"><thead><tr><th>№</th><th>Кейс</th><th>Критичность</th><th>Категория</th><th>Статус</th></tr></thead><tbody>' + "\n".join(table_rows) + '</tbody></table>'

# Конвертируем тела кейсов в HTML
md = markdown.Markdown(extensions=['fenced_code', 'tables'])

sections_html = {g: [] for g in groups_order}
for c in filtered:
    # Конвертируем body
    body_html = md.convert(c['body_md'])
    md.reset()
    # Подзаголовки секций делаем h4
    body_html = re.sub(r'<h3([^>]*)>', r'<h4\1>', body_html)
    body_html = re.sub(r'</h3>', r'</h4>', body_html)
    body_html = re.sub(r'<h2([^>]*)>', r'<h4\1>', body_html)
    body_html = re.sub(r'</h2>', r'</h4>', body_html)
    body_html = re.sub(r'<h1([^>]*)>', r'<h4\1>', body_html)
    body_html = re.sub(r'</h1>', r'</h4>', body_html)
    # Обертка секции
    section = f'''<section class="case severity-{c["severity"].lower()}" id="case-{c["new_num"]}">
<h3>Кейс {c["new_num"]}. {c["title"]}</h3>
<p class="meta"><span class="severity severity-{c["severity"].lower()}"><strong>Критичность:</strong> {c["severity"]}</span> <span class="type"><strong>Категория:</strong> {c["cat"]}</span> <span class="type"><strong>Статус:</strong> {c["status"]}</span></p>
{body_html}
</section>'''
    sections_html[c['group']].append(section)

# Генерируем левую колонку с навигацией
nav_links = []
for gi, group in enumerate(groups_order):
    nav_links.append(f'<a href="#section-{gi}" class="group-link">{group}</a>')
    for c in cases_by_group[group]:
        nav_links.append(f'<a href="#case-{c["new_num"]}">{c["new_num"]}. {c["title"]}</a>')

nav_links_html = "\n".join(nav_links)
group_sections_html = {g: "\n".join(sections_html[g]) for g in groups_order}

aside_html = f'''<aside>
<h2>Отчёт по багам</h2>
<nav>
{nav_links_html}
</nav>
</aside>'''

main_html = f'''<main>
<header>
<h1>Отчёт по баг-кейсам RatioT SCADA 6.41.09–6.41.11</h1>
<a class="pdf-button" href="RatioT_SCADA_Bug_Cases.pdf" download>Скачать PDF</a>
</header>
<h2>Сводная таблица</h2>
{summary_table}
{''.join(f'<h2 class="section-title" id="section-{gi}">{group}</h2>' + group_sections_html[group] for gi, group in enumerate(groups_order))}
</main>'''

final_html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Отчёт по баг-кейсам RatioT SCADA 6.41.09–6.41.11</title>
<style>
:root {{ --text:#1f2328; --muted:#59636e; --border:#d1d9e0; --bg:#f6f8fa; --accent:#0969da; --danger:#cf222e; --warn:#9a6700; }}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--text); line-height: 1.55; margin: 0; padding: 0; background:#fff; }}
.layout {{ display: flex; max-width: 1240px; margin: 0 auto; align-items: flex-start; }}
aside {{ width: 320px; padding: 20px; position: sticky; top: 0; align-self: flex-start; border-right: 1px solid var(--border); max-height: 100vh; overflow-y: auto; }}
aside h2 {{ font-size: 1.1rem; margin: 0 0 16px; }}
aside nav {{ display: flex; flex-direction: column; gap: 4px; }}
aside a {{ color: var(--text); text-decoration: none; font-size: 0.9rem; line-height: 1.35; padding: 4px 8px; border-radius: 4px; overflow-wrap: break-word; word-break: break-word; hyphens: auto; }}
aside a:hover {{ background: var(--bg); color: var(--accent); }}
aside a.active {{ background: var(--bg); color: var(--accent); font-weight: 600; }}
aside a.group-link {{ font-weight: 700; margin-top: 10px; color: var(--accent); }}
main {{ flex: 1; padding: 32px 24px; max-width: 900px; min-width: 0; }}
header {{ border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }}
header h1 {{ font-size: 1.8rem; margin: 0 0 12px; }}
.pdf-button {{ display: inline-block; padding: 12px 24px; background: var(--accent); color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 1.05rem; }}
.pdf-button:hover {{ background: #0550ae; }}
.summary-table {{ width: 100%; border-collapse: collapse; margin: 16px 0 16px; font-size: 0.95rem; }}
.summary-table th, .summary-table td {{ border: 1px solid var(--border); padding: 6px 8px; text-align: left; vertical-align: top; overflow-wrap: break-word; word-break: break-word; }}
.summary-table th {{ background: var(--bg); font-weight: 600; }}
.summary-table tr {{ page-break-inside: avoid; }}
.summary-table tr:nth-child(even) {{ background: #fafafa; }}
.summary-table tr.group-row {{ background: var(--bg); }}
.summary-table tr.group-row td {{ font-weight: 600; padding-top: 10px; padding-bottom: 10px; }}
.summary-table a {{ color: var(--text); text-decoration: none; }}
.summary-table a:hover {{ text-decoration: underline; color: var(--accent); }}
.section-title {{ margin-top: 24px; padding-bottom: 8px; border-bottom: 2px solid var(--border); font-size: 1.4rem; page-break-after: avoid; }}
.case {{ margin: 28px 0; padding: 18px; border: 1px solid var(--border); border-radius: 8px; background: #fff; }}
.case h3 {{ margin-top: 0; font-size: 1.2rem; color: var(--text); }}
.case h4 {{ font-size: 1rem; color: var(--muted); margin: 16px 0 6px; text-transform: uppercase; letter-spacing: 0.02em; }}
.case .meta {{ margin: 4px 0 12px; color: var(--muted); font-size: 0.95rem; }}
.case .severity {{ font-weight: 600; margin-right: 16px; }}
.severity-critical {{ color: #cf222e; }}
.severity-high {{ color: #cf222e; }}
.severity-medium {{ color: #9a6700; }}
.severity-low {{ color: #59636e; }}
.case p, .case li {{ margin: 6px 0; }}
.case ul, .case ol {{ margin: 6px 0; padding-left: 22px; }}
.case img {{ max-width: 100%; height: auto; border: 1px solid var(--border); border-radius: 4px; margin: 6px 0; }}
.case code {{ background: var(--bg); padding: 2px 4px; border-radius: 3px; font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace; font-size: 0.9em; }}
.case pre {{ background: var(--bg); padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.9em; }}
.case blockquote {{ margin: 8px 0; padding: 8px 14px; border-left: 4px solid var(--accent); background: var(--bg); color: var(--text); }}
.case blockquote p {{ margin: 0; }}
@media print {{
  aside {{ display: none; }}
  .layout {{ display: block; }}
  .pdf-button {{ display: none; }}
  body {{ font-size: 10pt; }}
  .case {{ break-inside: avoid; border: none; padding: 8px 0; }}
  .case img {{ max-height: 60vh; }}
  .summary-table {{ font-size: 8pt; }}
  .summary-table th, .summary-table td {{ padding: 4px 6px; }}
}}
</style>
</head>
<body>
<div class="layout">
{aside_html}
{main_html}
</div>
<script>
  const sections = document.querySelectorAll('section[id], h2[id]');
  const links = document.querySelectorAll('aside nav a[href^="#"]');
  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        links.forEach(link => link.classList.remove('active'));
        const active = document.querySelector('aside nav a[href="#" + entry.target.id]');
        if (active) active.classList.add('active');
      }}
    }});
  }}, {{ rootMargin: '-20% 0px -60% 0px' }});
  sections.forEach(section => observer.observe(section));
</script>
</body>
</html>
'''

html_path.write_text(final_html, encoding="utf-8")
print(f"Сгенерирован {html_path}: {len(filtered)} кейсов")
