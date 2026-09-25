"""Tile part-board or review PNGs into one labelled contact sheet."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

board = Path(sys.argv[1]); out = Path(sys.argv[2]); cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
meta = json.loads((board / 'board.json').read_text())
meta = {'cards': meta} if isinstance(meta, list) else meta
cards = meta.get('cards') or meta.get('parts') or []
imgs = []
for i, card in enumerate(cards):
    d = board / f'{i:02d}'
    p = d / 'home.png'
    if not p.exists():
        continue
    im = Image.open(p).convert('RGB')
    bbox = Image.eval(im, lambda v: 255 - v).getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((300, 260))
    label = str(card.get('ref') or card.get('part') or card.get('code') or i)
    size = card.get('size_ldu') or ''
    imgs.append((im, f'{label} {size}'))
w, h = 320, 300
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * h), 'white')
draw = ImageDraw.Draw(sheet)
for i, (im, label) in enumerate(imgs):
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im, (x + (w - im.width) // 2, y + 5))
    draw.text((x + 5, y + h - 30), label[:60], fill='black')
sheet.save(out)
print(out, len(imgs))
