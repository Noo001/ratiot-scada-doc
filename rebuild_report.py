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

# Задаём порядок и группы по старой нумерации:
order_and_groups = [
    (2, "Сообщённые Агрегейту"),
    (3, "Сообщённые Агрегейту"),
    (4, "Сообщённые Агрегейту"),
    (6, "Сообщённые Агрегейту"),
    (7, "Сообщённые Агрегейту"),
    (9, "Сообщённые Агрегейту"),
    (1, "Новые баги"),
    (5, "Новые баги"),
    (8, "Новые баги"),
    (10, "Новые баги"),
    (11, "Новые баги"),
    (13, "Новые баги"),
    (16, "Новые баги"),
    (17, "Новые баги"),
]
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
    1: "Подтверждён",
    2: "Подтверждён",
    3: "Подтверждён",
    4: "Подтверждён коллегами / в trial нет драйвера Modbus",
    5: "Подтверждён коллегами / в trial нет редактора дашбордов",
    6: "Подтверждён коллегами / в trial нет раздела",
    7: "Подтверждён коллегами / настройка доступна, переключение не проводилось",
    8: "Подтверждён коллегами / в trial нет редактора дашбордов",
    9: "Подтверждён коллегами / требует переустановки",
    10: "Подтверждён",
    11: "Подтверждён",
    13: "Подтверждён",
    16: "Подтверждён",
    17: "Подтверждён",
}

# Извлекаем серьёзность
def get_severity(body_md):
    m = re.search(r'\*\*Серьёзность:\*\*\s*(\w+)', body_md)
    return m.group(1) if m else "Medium"

for c in ordered:
    c['severity'] = get_severity(c['body_md'])
    c['status'] = statuses.get(c['old_num'], "Подтверждён")

filtered = ordered
for c in filtered:
    # Убираем строки серьёзности и типа из тела, т.к. они уже в meta
    c['body_md'] = re.sub(r'\*\*Серьёзность:\*\*\s*\w+\s*\n', '', c['body_md'])
    c['body_md'] = re.sub(r'\*\*Тип:\*\*\s*[^\n]+\s*\n', '', c['body_md'])
    # Убираем служебные секции "Источник" и "Примечание" полностью
    c['body_md'] = re.sub(r'###\s*(Источник|Примечание)\s*\n(.*?)(?=###|\Z)', '', c['body_md'], flags=re.DOTALL)
    # Убираем служебные строки
    c['body_md'] = re.sub(r'[-*]\s*Автотест фиксирует проблему:.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*Лог-файл:.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*incoming/.*', '', c['body_md'])
    c['body_md'] = re.sub(r'[-*]\s*Тикет\s+`[^`]+`\s*из\s*`[^`]+`\.?', '', c['body_md'])

# Генерируем строки таблицы с группами
groups_order = [
    "Сообщённые Агрегейту",
    "Новые баги",
]
cases_by_group = {g: [] for g in groups_order}
for c in filtered:
    cases_by_group[c['group']].append(c)

table_rows = []
for group in groups_order:
    table_rows.append(f'<tr class="group-row"><td colspan="4"><strong>{group}</strong></td></tr>')
    for c in cases_by_group[group]:
        table_rows.append(
            f'<tr><td>{c["new_num"]}</td><td><a href="#case-{c["new_num"]}">{c["title"]}</a></td>'
            f'<td>{c["severity"]}</td><td>{c["status"]}</td></tr>'
        )

summary_table = '<table class="summary-table"><thead><tr><th>№</th><th>Кейс</th><th>Серьёзность</th><th>Статус</th></tr></thead><tbody>' + "\n".join(table_rows) + '</tbody></table>'

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
<p class="meta"><span class="severity severity-{c["severity"].lower()}"><strong>Серьёзность:</strong> {c["severity"]}</span> <span class="type"><strong>Статус:</strong> {c["status"]}</span></p>
{body_html}
</section>'''
    sections_html[c['group']].append(section)

# Генерируем левую колонку с навигацией
nav_links = []
g1 = groups_order[0]
g2 = groups_order[1]
nav_links.append(f'<a href="#section-предъявленные" class="group-link">{g1}</a>')
for c in cases_by_group[g1]:
    nav_links.append(f'<a href="#case-{c["new_num"]}">{c["new_num"]}. {c["title"]}</a>')
nav_links.append(f'<a href="#section-новые" class="group-link">{g2}</a>')
for c in cases_by_group[g2]:
    nav_links.append(f'<a href="#case-{c["new_num"]}">{c["new_num"]}. {c["title"]}</a>')

nav_links_html = "\n".join(nav_links)
g1_sections_html = "\n".join(sections_html[g1])
g2_sections_html = "\n".join(sections_html[g2])

aside_html = f'''<aside>
<h2>Отчёт по багам</h2>
<nav>
{nav_links_html}
</nav>
</aside>'''

main_html = f'''<main>
<header>
<h1>Отчёт по баг-кейсам RatioT SCADA 6.41.09</h1>
<a class="pdf-button" href="RatioT_SCADA_Bug_Cases.pdf" download>Скачать PDF</a>
</header>
<h2>Сводная таблица</h2>
{summary_table}
<h2 class="section-title" id="section-предъявленные">{g1}</h2>
{g1_sections_html}
<h2 class="section-title" id="section-новые">{g2}</h2>
{g2_sections_html}
</main>'''

final_html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Отчёт по баг-кейсам RatioT SCADA</title>
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
