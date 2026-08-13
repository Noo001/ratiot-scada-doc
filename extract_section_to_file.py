from html.parser import HTMLParser
import re
import sys

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style'):
            self.skip -= 1
    def handle_data(self, data):
        if self.skip == 0:
            self.text.append(data)

path = sys.argv[1]
keyword = sys.argv[2].lower()
out_path = sys.argv[3]
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

idx = html.lower().find(keyword)
if idx == -1:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Keyword '{sys.argv[2]}' not found\n")
    sys.exit(1)

start = max(0, idx - 200)
end = min(len(html), idx + 3000)
fragment = html[start:end]
parser = TextExtractor()
parser.feed(fragment)
text = ' '.join(parser.text)
text = re.sub(r'\s+', ' ', text)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(text[:4000])
print(f"Written to {out_path}")
