#!/usr/bin/env python3
"""Создаёт скриншот фрагмента server.log для кейса 1."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

LOG_PATH = Path("C:/Program Files/RatioTScada/logs/server.log")
OUT_PATH = Path("tests/screenshots/case1_server_log_errors.png")

# Найдём первые 3 блока ERROR ag.context (читаем только первые 2000 строк)
lines = []
error_count = 0
stack_after = 0
try:
    with LOG_PATH.open(encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            if idx >= 2000:
                break
            if "ERROR ag.context" in line:
                if error_count >= 3:
                    break
                lines.append(line.rstrip()[:120])
                error_count += 1
                stack_after = 3  # берём не более 3 строк стектрейса после ошибки
            elif stack_after > 0 and line.startswith("\t"):
                lines.append(line.rstrip()[:120])
                stack_after -= 1
            elif stack_after > 0:
                stack_after = 0
except Exception as e:
    lines = [f"ERROR reading log: {e}"]

if not lines:
    lines = ["ERROR: не удалось найти строки ERROR ag.context в server.log"]

text = "\n".join(lines)

# Шрифт
font_size = 16
try:
    font = ImageFont.truetype("consola.ttf", font_size)
except Exception:
    try:
        font = ImageFont.truetype("Consolas.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

# Размеры
padding = 20
max_width = 1000
draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
lines_wrapped = list(text.splitlines())

bbox = draw.textbbox((0, 0), "\n".join(lines_wrapped), font=font, spacing=4)
img_w = min(max_width, bbox[2] - bbox[0] + padding * 2)
img_h = bbox[3] - bbox[1] + padding * 2 + 40  # + title

img = Image.new("RGB", (img_w, img_h), color="#1e1e1e")
d = ImageDraw.Draw(img)

d.text((padding, 10), "server.log — ERROR ag.context (первый запуск)", fill="#d4d4d4", font=font)
d.text((padding, 50), "\n".join(lines_wrapped), fill="#d4d4d4", font=font, spacing=4)

img.save(OUT_PATH)
print(f"OK {OUT_PATH}")
