"""Publish structural recipes and mechanism studies in one Technic atlas."""
from pathlib import Path
import html
import json

from ldraw_tools.common import atomic_write, dumps
from ldraw_tools.manuals import current_manual, sha


def write_catalog(outdir, rows):
    outdir = Path(outdir)
    entries = []
    for original in rows:
        row = dict(original)
        if row.get('kind') == 'mechanism':
            row.pop('visual_review', None)
            row['visual_review_status'] = 'pending'
            folder = outdir / Path(row['manual']).parent
            try:
                _, manual = current_manual(folder)
                review = json.loads((folder / 'visual-review.json').read_text())
                images = {p for s in manual['sections'] for step in s['steps']
                          for p in step['images'].values()}
                images.update(manual['final_images'])
                if (manual['source_checks_passed'] and manual['bom_matches'] is True
                        and review.get('status') == 'visually_reviewed'
                        and review.get('manual_sha256') == sha(folder / 'manual.json')
                        and set(review.get('viewed_images', [])) == images
                        and review.get('note', '').strip()):
                    row['visual_review_status'] = 'visually_reviewed'
                    row['visual_review'] = str(Path(row['manual']).parent / 'visual-review.json')
            except (OSError, ValueError, KeyError):
                pass
        entries.append(row)
    atomic_write(outdir / 'catalog.json', dumps(dict(
        version=1, scope='technic-construction', examples=entries, details=[])) + '\n')
    cards = []
    escape = html.escape
    for row in entries:
        image = (f'<img src="{escape(row["preview"])}" alt="{escape(row["title"])}" loading="lazy">'
                 if row.get('preview') else '')
        destination = row.get('manual', row['guide'])
        kind = 'Mechanism study' if row.get('kind') == 'mechanism' else 'Fixed structure'
        cards.append(f'<article><p class="kind">{kind}</p><a href="{escape(destination)}">'
                     f'{image}<h2>{escape(row["title"])}</h2></a><p>{escape(row["lesson"])}</p>'
                     f'<p>{row["physical_placements"]} parts · '
                     f'<a href="{escape(row["guide"])}">Construction and adaptation guide</a></p></article>')
    atomic_write(outdir / 'index.html', '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Technic construction atlas</title>
<style>body{font:16px/1.5 system-ui;max-width:1200px;margin:36px auto;padding:0 24px;color:#263540;background:#f6f8fa}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}article{padding:20px;background:white;border:1px solid #dce2e7;border-radius:8px}img{width:100%;border-radius:5px}a{color:#165e9e}h2{font-size:20px}.kind{font-size:13px;text-transform:uppercase;color:#59646e}</style>
<h1>Technic construction atlas</h1><p>Frames, supports and useful mechanisms to study and adapt.
Read each guide's mounting interfaces and parent dependencies before reuse.
Mechanism operation is intended; analytical verification is deferred.</p>
<p><a href="README.md">Atlas guide</a> · <a href="mechanism-selections.json">Mechanism sources</a></p>
<main>''' + ''.join(cards) + '</main></html>\n')
    return entries
