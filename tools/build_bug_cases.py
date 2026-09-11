#!/usr/bin/env python3
"""Генерация bug_cases.html из tests/BUG_CASES.md (Python-версия).

Кейсы группируются в три главы по полю **Категория:** из markdown:
1. Ошибки кастомизации, 2. Ошибки OEM, 3. Ошибки платформы партнёра.
"""

import re
from pathlib import Path
import markdown

MD = Path("tests/BUG_CASES.md")
OUT = Path("bug_cases.html")

md_text = MD.read_text(encoding="utf-8")

# Удаляем standalone anchors
md_text = re.sub(r'^<a\s+id="(case-\d+|summary)"></a>\n+', '', md_text, flags=re.MULTILINE)

# Разбиваем markdown на преамбулу, кейсы и итог
head_re = re.compile(r'^##\s+(Кейс\s+(\d+)\.\s+.+?|Итог)\s*$', re.MULTILINE)
heads = list(head_re.finditer(md_text))
preamble_md = md_text[:heads[0].start()]
summary_block = None
cases = []
for i, m in enumerate(heads):
    end = heads[i + 1].start() if i + 1 < len(heads) else len(md_text)
    block = md_text[m.end():end]
    if m.group(2):
        title_short = re.sub(r'^Кейс\s+\d+\.\s*', '', m.group(1).strip())
        cases.append({'num': int(m.group(2)), 'title': title_short, 'body': block})
    else:
        summary_block = block

# Категория кейса берётся из поля **Категория:** N. Название; без поля — платформа
CAT_DEFAULT = (3, 'Ошибки платформы партнёра')
for c in cases:
    m = re.search(r'^\*\*Категория:\*\*\s*(\d+)\.\s*(.+?)\s*$', c['body'], re.MULTILINE)
    c['cat'], c['cat_name'] = (int(m.group(1)), m.group(2).strip()) if m else CAT_DEFAULT
    c['body'] = re.sub(r'^\*\*Категория:\*\*[^\n]*\n', '', c['body'], flags=re.MULTILINE)

# Группируем кейсы по категориям (порядок глав — по номеру категории)
chapters = {}
for c in cases:
    chapters.setdefault(c['cat'], {'name': c['cat_name'], 'cases': []})['cases'].append(c)

# Убираем оглавление из преамбулы (есть боковая навигация)
preamble_md = re.sub(r'^##\s+Оглавление\s*$\n.*?(?=^---\s*$|\Z)', '', preamble_md,
                     count=1, flags=re.MULTILINE | re.DOTALL)

md = markdown.Markdown(extensions=['fenced_code', 'tables'])

# Конвертируем преамбулу и нормализуем h1
preamble_html = md.convert(preamble_md)
md.reset()
preamble_html = re.sub(r'<h1[^>]*>\s*</h1>', '<h1 id="top">Баг-кейсы RatioT SCADA</h1>', preamble_html, count=1)
preamble_html = re.sub(r'<h1[^>]*>Баг-кейсы RatioT SCADA\s*6\.41\.09\s*</h1>',
                       '<h1 id="top">Баг-кейсы RatioT SCADA 6.41.09</h1>', preamble_html, count=1)

# Собираем тело: главы с кейсами + итог
sections = [preamble_html]
toc = []
for cat in sorted(chapters):
    ch = chapters[cat]
    sections.append(f'<h2 class="chapter" id="cat-{cat}">Глава {cat}. {ch["name"]}</h2>')
    toc.append(f'        <a href="#cat-{cat}" class="chapter-link">Глава {cat}. {ch["name"]}</a>')
    for c in ch['cases']:
        body_html = md.convert(c['body'])
        md.reset()
        sections.append(f'<h2 id="case-{c["num"]}">Кейс {c["num"]}. {c["title"]}</h2>\n{body_html}')
        toc.append(f'        <a href="#case-{c["num"]}" class="case-link">{c["num"]}. {c["title"]}</a>')

if summary_block is not None:
    summary_html = md.convert('## Итог\n' + summary_block)
    md.reset()
    summary_html = re.sub(r'<h2>Итог</h2>', '<h2 id="summary">Итог</h2>', summary_html)
    sections.append(summary_html)
toc.append('        <a href="#summary" class="chapter-link">Итог</a>')

body_html = '\n'.join(sections)
toc_html = "\n".join(toc)

html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta name="robots" content="noindex, nofollow">
  <script>
    (function () {{
      if (localStorage.getItem('ratiot-doc-auth') !== 'ok') {{
        var pwd = prompt('Доступ к документации. Введите пароль:');
        if (pwd !== '111') {{
          document.documentElement.innerHTML = '<body style="font-family:sans-serif;padding:40px;text-align:center;"><h1>Доступ запрещён</h1><p>Неверный пароль.</p></body>';
          throw new Error('Access denied');
        }}
        localStorage.setItem('ratiot-doc-auth', 'ok');
      }}
    }})();
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Баг-кейсы RatioT SCADA</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .content {{ padding: 32px 40px; max-width: 900px; }}
    .content h1 {{ font-size: 2rem; margin-bottom: 8px; }}
    .content h2 {{ margin-top: 36px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
    .content h2.chapter {{ font-size: 1.6rem; margin-top: 52px; color: var(--accent); border-bottom: 2px solid var(--border); }}
    .content h3 {{ margin-top: 24px; }}
    .content p {{ margin: 12px 0; }}
    .content ul, .content ol {{ margin: 12px 0; padding-left: 24px; }}
    .content li {{ margin: 6px 0; }}
    .content code {{ background: var(--code); padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; }}
    .content pre {{ background: var(--code); padding: 16px; border-radius: 8px; overflow-x: auto; }}
    .content pre code {{ background: transparent; padding: 0; }}
    .content blockquote {{ border-left: 4px solid var(--accent); margin: 16px 0; padding: 8px 16px; background: var(--accent-light); }}
    .content table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    .content th, .content td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; }}
    .content th {{ background: var(--accent-light); }}
    .back {{ display: inline-block; margin-bottom: 20px; color: var(--accent); text-decoration: none; }}
    .back:hover {{ text-decoration: underline; }}
    nav a.chapter-link {{ font-weight: 700; margin-top: 14px; color: var(--accent); }}
    nav a.case-link {{ padding-left: 22px; font-size: .9rem; }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>RatioT SCADA</h1>
      <div class="subtitle">Баг-кейсы и тестирование</div>
      <nav>
        <a href="index.html">← На главную</a>
        <a href="scada/index.html">Документация SCADA</a>
        <a href="ux.html">UX-заметки</a>
{toc_html}
      </nav>
    </aside>
    <main class="content">
      <a class="back" href="index.html">← На главную</a>
{body_html}
    </main>
  </div>

  <script>
    const sections = document.querySelectorAll('h2[id], h1[id]');
    const links = document.querySelectorAll('nav a[href^="#"]');
    if (links.length) {{
      const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
          if (entry.isIntersecting) {{
            links.forEach(link => link.classList.remove('active'));
            const active = document.querySelector('nav a[href="#' + entry.target.id + '"]');
            if (active) active.classList.add('active');
          }}
        }});
      }}, {{ rootMargin: '-20% 0px -60% 0px' }});
      sections.forEach(section => observer.observe(section));
    }}
  </script>
</body>
</html>
'''

OUT.write_text(html, encoding='utf-8')
print(f"Generated {OUT}: {len(cases)} кейсов в {len(chapters)} главах")
