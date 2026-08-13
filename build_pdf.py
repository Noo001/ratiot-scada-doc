import re
from pathlib import Path
import markdown

BASE_URL = "https://noo001.github.io/ratiot-scada-doc"

md_path = Path("tests/BUG_CASES.md")
html_path = Path("bug_cases_print.html")

md_text = md_path.read_text(encoding="utf-8")

# Convert markdown to HTML
body_html = markdown.markdown(
    md_text,
    extensions=["fenced_code", "tables"],
)

# Wrap images with links to full-size images on GitHub Pages
img_pattern = re.compile(r'<img alt="([^"]+)" src="(tests/screenshots/[^"]+)" />')

def img_repl(m):
    alt = m.group(1)
    src = m.group(2)
    full_url = f"{BASE_URL}/{src}"
    return f'<a href="{full_url}"><img alt="{alt}" src="{src}" /></a>'

body_html = img_pattern.sub(img_repl, body_html)

# Make relative links absolute
body_html = re.sub(r'<a href="(index\.html|scada/index\.html|ux\.html|bug_cases\.html)"', 
                   lambda m: f'<a href="{BASE_URL}/{m.group(1)}"', body_html)

# Auto-link plain URLs
url_pattern = re.compile(r'(?<![\'"<>])(https?://[^\s<>"\)]+)')
body_html = url_pattern.sub(r'<a href="\1">\1</a>', body_html)

# But avoid double-linking inside existing <a> tags by simple heuristic: re-run and fix if href contains http inside a tag
# Better: use negative lookbehind for </a> -- skipped for simplicity; we will post-process.

html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Баг-кейсы RatioT SCADA</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .content {{ padding: 32px 40px; max-width: 900px; }}
    .content h1 {{ font-size: 2rem; margin-bottom: 8px; }}
    .content h2 {{ margin-top: 36px; padding-bottom: 8px; border-bottom: 1px solid var(--border); page-break-after: avoid; }}
    .content h3 {{ margin-top: 24px; page-break-after: avoid; }}
    .content p {{ margin: 12px 0; }}
    .content ul, .content ol {{ margin: 12px 0; padding-left: 24px; }}
    .content li {{ margin: 6px 0; }}
    .content code {{ background: var(--code); padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; }}
    .content pre {{ background: var(--code); padding: 16px; border-radius: 8px; overflow-x: auto; }}
    .content pre code {{ background: transparent; padding: 0; }}
    .content blockquote {{ border-left: 4px solid var(--accent); margin: 16px 0; padding: 8px 16px; background: var(--accent-light); }}
    .content table {{ border-collapse: collapse; width: 100%; margin: 16px 0; page-break-inside: avoid; }}
    .content th, .content td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; }}
    .content th {{ background: var(--accent-light); }}
    .content img {{ max-width: 100%; height: auto; }}
    a {{ color: #0066cc; text-decoration: underline; }}
    @media print {{
      body {{ -webkit-print-color-adjust: exact; }}
      h2 {{ page-break-after: avoid; }}
      img {{ page-break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="content">
    {body_html}
  </div>
</body>
</html>
"""

html_path.write_text(html, encoding="utf-8")
print(f"Generated {html_path}")
