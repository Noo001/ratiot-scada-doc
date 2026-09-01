#!/usr/bin/env python3
"""Генерация bug_cases.html из tests/BUG_CASES.md (Python-версия)."""

import re
from pathlib import Path
import markdown

MD = Path("tests/BUG_CASES.md")
OUT = Path("bug_cases.html")

md_text = MD.read_text(encoding="utf-8")

# Удаляем standalone anchors
md_text = re.sub(r'^<a\s+id="(case-\d+|summary)"></a>\n+', '', md_text, flags=re.MULTILINE)

# Извлекаем пункты оглавления
nav_items = []
for m in re.finditer(r'^##\s+(Кейс\s+(\d+)\.\s+.+?|Итог)\s*$', md_text, flags=re.MULTILINE):
    title = m.group(1).strip()
    case_num = m.group(2)
    anchor = f"case-{case_num}" if case_num else "summary"
    nav_items.append((anchor, title))

toc_html = "\n".join(f'        <a href="#{anchor}">{title}</a>' for anchor, title in nav_items)

# Добавляем pandoc-атрибуты к заголовкам (библиотека markdown их не обработает, поэтому позже вытащим вручную)
md_text = re.sub(r'^##\s+(Кейс\s+(\d+)\.\s+.+?)$', r'## \1 {#case-\2}', md_text, flags=re.MULTILINE)
md_text = re.sub(r'^##\s+(Итог)\s*$', r'## \1 {#summary}', md_text, flags=re.MULTILINE)

# Конвертируем markdown в html
md = markdown.Markdown(extensions=['fenced_code', 'tables'])
body_html = md.convert(md_text)

# Присваиваем id заголовкам кейсов и итогу (pandoc-атрибуты остались в тексте заголовков)
body_html = re.sub(
    r'<h2>Кейс\s+(\d+)\.\s+(.+?)\s+\{#case-\d+\}</h2>',
    r'<h2 id="case-\1">Кейс \1. \2</h2>',
    body_html
)
body_html = re.sub(r'<h2>Итог\s+\{#summary\}</h2>', '<h2 id="summary">Итог</h2>', body_html)

# Нормализуем h1
body_html = re.sub(r'<h1[^>]*>\s*<\/h1>', '<h1 id="top">Баг-кейсы RatioT SCADA</h1>', body_html, count=1)
body_html = re.sub(r'<h1[^>]*>Баг-кейсы RatioT SCADA\s+6\.41\.09\s*<\/h1>', '<h1 id="top">Баг-кейсы RatioT SCADA 6.41.09</h1>', body_html)

# Удаляем оглавление
body_html = re.sub(r'<h2\s+id="оглавление"[^>]*>Оглавление<\/h2>\s*<ul>.*?<\/ul>', '', body_html, flags=re.DOTALL)

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
print(f"Generated {OUT}")
