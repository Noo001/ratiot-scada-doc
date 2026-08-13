import re
from pathlib import Path

md_path = Path('tests/BUG_CASES.md')
text = md_path.read_text(encoding='utf-8')

def repl(m):
    path = m.group(1)
    desc = m.group(2)
    return f'- ![{desc}]({path}) — {desc}'

# Match: - `tests/screenshots/xxx.png` — description
pattern = re.compile(r'^- `(tests/screenshots/[^`]+)` — (.+)$', re.MULTILINE)
text = pattern.sub(repl, text)

md_path.write_text(text, encoding='utf-8')
print('done')
