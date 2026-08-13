import zipfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

OUT_DIR = Path('incoming_extracted')
OUT_DIR.mkdir(exist_ok=True)

docx_files = [
    'incoming/Баги с импортом и экспортом Modbus регистров в форматах csv и xml.docx',
    'incoming/Тикеты в АГ от ДИР.docx',
    'incoming/отчет о проблеме с html.docx',
]

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

text_out = open(OUT_DIR / 'texts.txt', 'w', encoding='utf-8')

for f in docx_files:
    if not os.path.exists(f):
        continue
    text_out.write(f'\n=== {f} ===\n')
    with zipfile.ZipFile(f) as z:
        xml = z.read('word/document.xml')
        root = ET.fromstring(xml)
        texts = []
        for p in root.findall('.//w:p', ns):
            para = ''.join(t.text or '' for t in p.findall('.//w:t', ns))
            if para.strip():
                texts.append(para)
        text_out.write('\n'.join(texts[:300]) + '\n')

        # extract images
        base = Path(f).stem
        img_dir = OUT_DIR / base
        img_dir.mkdir(exist_ok=True)
        for name in z.namelist():
            if name.startswith('word/media/'):
                data = z.read(name)
                ext = Path(name).suffix
                out_name = img_dir / f'{Path(name).name}'
                out_name.write_bytes(data)
                text_out.write(f'[image] {out_name}\n')

text_out.close()
print('done')
