from pathlib import Path
from PIL import Image

SCREENSHOTS_DIR = Path('tests/screenshots')
MAX_WIDTH = 1000

for img_path in SCREENSHOTS_DIR.glob('*.png'):
    with Image.open(img_path) as im:
        w, h = im.size
        if w > MAX_WIDTH:
            new_h = int(h * MAX_WIDTH / w)
            resized = im.resize((MAX_WIDTH, new_h), Image.Resampling.LANCZOS)
            resized.save(img_path)
            print(f'Resized {img_path.name}: {w}x{h} -> {MAX_WIDTH}x{new_h}')
        else:
            print(f'Skip {img_path.name}: {w}x{h}')
