from html.parser import HTMLParser
import re

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

with open('tmp_self_reg.htm', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()
parser = TextExtractor()
parser.feed(html)
text = ' '.join(parser.text)
text = re.sub(r'\s+', ' ', text)
with open('tmp_self_reg_full.txt', 'w', encoding='utf-8') as f:
    f.write(text[:8000])
print('written')
