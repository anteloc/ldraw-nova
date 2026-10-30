"""Optional, labeled inspection boards composed from existing full-resolution renders."""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .common import atomic_write, dumps


def compose_mosaic(manifest, output, *, columns=2, panel_width=800, force=False):
    """Compose views without cropping; analysis mode requires declared identical framing."""
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    sidecar = output.with_suffix('.json')
    spec = json.loads(manifest.read_text())
    if not isinstance(spec, dict):
        raise ValueError('Mosaic manifest must be an object')
    panels, mode = spec.get('panels'), spec.get('mode', 'views')
    if mode not in {'views', 'analysis'}:
        raise ValueError('Mosaic mode must be views or analysis')
    if not isinstance(panels, list) or not 2 <= len(panels) <= 9:
        raise ValueError('Choose 2 to 9 panels')
    if not 1 <= columns <= 3 or not 320 <= panel_width <= 1600:
        raise ValueError('Use 1–3 columns and panel width 320–1600')
    if output.suffix.lower() != '.png':
        raise ValueError('Mosaic output must be a PNG')
    if not isinstance(spec.get('title', 'Inspection mosaic'), str):
        raise ValueError('Mosaic title must be text')
    if len(spec.get('title', '')) > 120:
        raise ValueError('Keep the title within 120 characters')
    images, entries, inputs = [], [], {manifest}
    for panel in panels:
        if not isinstance(panel, dict) or not isinstance(panel.get('image'), str):
            raise ValueError('Each panel needs an image path')
        label = panel.get('label')
        if not isinstance(label, str) or not label.strip() or len(label) > 160:
            raise ValueError('Each panel needs a nonempty label of at most 160 characters')
        path = (manifest.parent / panel['image']).resolve()
        inputs.add(path)
        data = path.read_bytes()
        with Image.open(io.BytesIO(data)) as source:
            if source.width * source.height > 24_000_000:
                raise ValueError('Panel exceeds 24 megapixels')
            image = source.convert('RGBA')
        background = Image.new('RGBA', image.size, '#303437')
        background.alpha_composite(image)
        images.append(background.convert('RGB'))
        entries.append(dict(panel= len(entries)+1, label=label, image=str(path),
                            sha256=hashlib.sha256(data).hexdigest(), size=list(image.size),
                            camera=panel.get('camera'), subject=panel.get('subject'),
                            state=panel.get('state')))
    if output in inputs or sidecar in inputs:
        raise ValueError('Mosaic outputs must not overwrite inputs')
    if not force and (output.exists() or sidecar.exists()):
        raise ValueError('Mosaic output exists; use --force')
    if mode == 'analysis':
        first = panels[0]
        if not isinstance(first.get('camera'), dict) or not first['camera'] or not first.get('subject'):
            raise ValueError('Analysis panels need camera metadata and a common subject identifier')
        if any(p.get('camera') != first['camera'] or p.get('subject') != first['subject'] for p in panels):
            raise ValueError('Analysis panels must declare the same camera and subject coordinate frame')
        if any(im.size != images[0].size for im in images):
            raise ValueError('Analysis panels must have identical source image dimensions')
    # Equal image boxes preserve pixel registration for aligned analysis panels.
    height = round(panel_width * 0.75)
    gap, caption, heading = 16, 96, 96
    columns = min(columns, len(panels))
    rows = math.ceil(len(panels) / columns)
    board = Image.new('RGB', (columns*(panel_width+gap)+gap,
                              heading+rows*(height+caption+gap)), '#eef1f4')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=20)
    title_font = ImageFont.load_default(size=26)

    def lines(text, width, selected_font):
        words, result, current = text.split(), [], ''
        for word in words:
            for char in (' ' if current else '') + word:
                if current and draw.textlength(current+char, font=selected_font) > width:
                    result.append(current); current = ''
                current += char
        return result + ([current] if current else [])

    title = spec.get('title', 'Inspection mosaic')
    for n, line in enumerate(lines(title, board.width-2*gap, title_font)[:2]):
        draw.text((gap, 8+n*28), line, font=title_font, fill='#17272c')
    note = ('Aligned by supplied camera metadata; render settings not independently verified.'
            if mode == 'analysis' else 'Views independently framed; not to common scale.')
    draw.text((gap, 68), note, font=ImageFont.load_default(size=14), fill='#394952')
    for i, (im, entry) in enumerate(zip(images, entries)):
        x, y = gap+(i % columns)*(panel_width+gap), heading+(i//columns)*(height+caption+gap)
        fitted = ImageOps.contain(im, (panel_width, height), Image.Resampling.LANCZOS)
        draw.rectangle((x,y,x+panel_width-1,y+height-1), fill='#303437')
        left, top = x+(panel_width-fitted.width)//2, y+(height-fitted.height)//2
        board.paste(fitted, (left,top))
        entry['image_box'] = [left, top, fitted.width, fitted.height]
        label_lines = lines(f'{i+1}. {entry["label"]}', panel_width-12, font)
        if len(label_lines) > 4:
            raise ValueError('Panel label is too long for this width; shorten it or increase panel width')
        for n, line in enumerate(label_lines):
            draw.text((x+6,y+height+6+n*22), line, font=font, fill='#17272c')
    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(suffix='.png', dir=output.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        board.save(temporary, format='PNG')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    report = dict(version=1, output=str(output), mode=mode, title=title, size=list(board.size),
                  columns=columns, panels=entries, manifest=str(manifest),
                  manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  image_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  visual_review='pending', note=note,
                  limitations=['Mosaics do not change source review status; inspect full-resolution originals for small connections.'])
    atomic_write(sidecar, dumps(report)+'\n')
    return report
