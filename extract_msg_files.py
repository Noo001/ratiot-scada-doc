import extract_msg
import os
from pathlib import Path
import sys

OUT_DIR = Path('incoming_extracted/msg')
OUT_DIR.mkdir(parents=True, exist_ok=True)

msg_files = [f for f in Path('incoming').glob('*.msg')]
text_out = open(OUT_DIR / 'texts.txt', 'w', encoding='utf-8')

for f in msg_files:
    print(f'Processing {f}')
    text_out.write(f'\n=== {f.name} ===\n')
    try:
        msg = extract_msg.Message(str(f))
        text_out.write(f'Subject: {msg.subject}\n')
        text_out.write(f'From: {msg.sender}\n')
        text_out.write(f'To: {msg.to}\n')
        text_out.write(f'Date: {msg.date}\n')
        body = msg.body or ''
        text_out.write('--- Body ---\n')
        text_out.write(body)
        text_out.write('\n')
        # Save attachments
        attach_dir = OUT_DIR / f.stem
        attach_dir.mkdir(exist_ok=True)
        for att in msg.attachments:
            try:
                os.chdir(attach_dir)
                att.save()
                text_out.write(f'[attachment] {attach_dir / att.longFilename}\n')
            except Exception as e:
                text_out.write(f'[attachment error] {e}\n')
            finally:
                os.chdir(OUT_DIR)
        msg.close()
    except Exception as e:
        text_out.write(f'[error] {e}\n')

text_out.close()
print('done')
