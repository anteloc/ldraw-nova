"""One contact sheet per look: parallel LeoCAD views, cropped onto a neutral background.

    ./ldraw-agent look MODEL.mpd                      # home, front, right and top in one PNG
    ./ldraw-agent look MODEL.mpd --problems           # floating parts magenta, colliding parts red
    ./ldraw-agent look MODEL.mpd --focus roof-left    # close-up around one plan id
    ./ldraw-agent look MODEL.mpd --highlight a b      # recolour chosen plan ids magenta

Transparent renders hide white parts on white pages, so every view is composited
onto a mid-grey background and labelled. Views (the model's front faces -Z):

| view  | camera            | image right | image up |
|-------|-------------------|-------------|----------|
| front | on the -Z side    | +X          | up (-Y)  |
| right | on the +X side    | +Z          | up (-Y)  |
| top   | above             | +X          | +Z, so the front is at the bottom |
| home  | above front-right | -           | -        |
"""
from __future__ import annotations

import math
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw

from . import check as checker
from .common import atomic_write, normalized
from .document import selected_source
from .external import cad_source
from .validation import validate_file

BACKGROUND = (178, 184, 194)
MAGENTA, RED = 26, 4
DIRECTIONS = {"home": (1, -1, -1), "front": (0, 0, -1), "back": (0, 0, 1), "left": (-1, 0, 0),
              "right": (1, 0, 0), "top": (0, -1, 0), "bottom": (0, 1, 0)}


def _camera(center, radius, view, fov=30):
    direction = np.array(DIRECTIONS[view], dtype=float)
    distance = radius / math.sin(math.radians(fov / 2)) * 1.15
    camera = center + direction / np.linalg.norm(direction) * distance
    up = (0, 0, 1) if view == "top" else (0, 0, -1) if view == "bottom" else (0, -1, 0)
    return ["--fov", str(fov), "--camera-position-ldraw", *map(lambda v: f"{v:.3f}", (*camera, *center)), *map(str, up)]


def _recoloured(path, targets, temp):
    """Copy of the MPD with chosen (section, line) placements recoloured."""
    if not targets:
        return Path(path)
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    section = None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("0 FILE "):
            section = normalized(stripped[7:].strip())
        colour = targets.get((section, number)) or targets.get((None, number))
        if colour is not None and stripped.startswith("1 "):
            fields = line.split(None, 2)
            lines[number - 1] = f"1 {colour} {fields[2]}"
    out = Path(temp) / Path(path).name
    atomic_write(out, "\r\n".join(lines) + "\r\n")
    return out


def _sheet(images, labels, output, columns, cell):
    tiles = []
    for image_path, label in zip(images, labels):
        raw = Image.open(image_path).convert("RGBA")
        box = raw.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        tile = Image.new("RGB", raw.size, BACKGROUND)
        tile.paste(raw, mask=raw.getchannel("A"))
        if box:
            pad = 16
            tile = tile.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(tile.width, box[2] + pad), min(tile.height, box[3] + pad)))
        tile.thumbnail((cell, cell))
        canvas = Image.new("RGB", (cell, cell), BACKGROUND)
        canvas.paste(tile, ((cell - tile.width) // 2, (cell - tile.height) // 2))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 9 + 7 * len(label), 18), fill=(40, 44, 52))
        draw.text((5, 4), label, fill=(255, 255, 255))
        tiles.append(canvas)
    rows = math.ceil(len(tiles) / columns)
    sheet = Image.new("RGB", (columns * cell + (columns - 1) * 4, rows * cell + (rows - 1) * 4), (90, 96, 108))
    for k, tile in enumerate(tiles):
        sheet.paste(tile, ((k % columns) * (cell + 4), (k // columns) * (cell + 4)))
    sheet.save(output)


def look(path, parts, library, outdir=None, *, views=("home", "front", "right", "top"), focus=None, highlight=(),
         problems=False, section=None, colour=None, cell=640, timeout=120):
    started = time.perf_counter()
    path = Path(path)
    outdir = Path(outdir) if outdir else path.parent / "look"
    outdir.mkdir(parents=True, exist_ok=True)
    unknown = [v for v in views if v not in DIRECTIONS]
    if unknown:
        raise ValueError(f"Unknown view(s) {unknown}; choose from {', '.join(DIRECTIONS)}")
    model, diagnostics = validate_file(path, parts, assembly=False)
    if model is None:
        raise ValueError("Cannot parse the model: " + "; ".join(d["message"] for d in diagnostics[:3]))
    rows, _, _ = checker.placed_rows(model, path, parts, library)
    by_label = {row["label"]: row for row in rows}
    targets, notes = {}, []
    for label in highlight:
        if label not in by_label:
            raise ValueError(f"No plan id {label!r}; ids look like {next(iter(by_label), '?')}")
        targets[(normalized(by_label[label]["section"]), by_label[label]["line"])] = MAGENTA
    if problems:
        report = checker.check_model(path, parts, library, limit=100000)
        for group in report.get("floating_groups", []):
            for item in group["parts"]:
                targets[(normalized(item["section"]), item["line"])] = MAGENTA
        for item in report.get("collisions", []):
            for side in ("a", "b"):
                targets[(normalized(item[side]["section"]), item[side]["line"])] = RED
        notes.append(f"{report.get('floating_count', 0)} floating (magenta), {report.get('collision_count', 0)} collisions (red)")
    if focus is not None:
        if focus not in by_label:
            raise ValueError(f"No plan id {focus!r}; ids look like {next(iter(by_label), '?')}")
        lo, hi = checker.world_box(by_label[focus])
        center, radius = (lo + hi) / 2, max(float(np.linalg.norm(hi - lo)) * 1.5, 40.0)
    else:
        boxes = [checker.world_box(row) for row in rows]
        lo, hi = np.min([b[0] for b in boxes], axis=0), np.max([b[1] for b in boxes], axis=0)
        center, radius = (lo + hi) / 2, max(float(np.linalg.norm(hi - lo)) / 2, 20.0)
    with TemporaryDirectory(prefix=".look-", dir=outdir) as temp:
        source = _recoloured(path, targets, temp)
        if section is not None:
            text, _ = selected_source(source, section, colour)
            source = Path(temp) / "section.mpd"
            atomic_write(source, text)
        cad_path, cad_library, _ = cad_source(source, library, temp)

        def render(view):
            target = Path(temp) / f"{view}.png"
            command = ["leocad", "-l", str(cad_library), "-i", str(target), "-w", str(cell + 200), "-h", str(cell + 100),
                       "--aa-samples", "4", "--shading", "full", "--line-width", "1", "--no-highlight", "--no-fade-steps",
                       str(Path(cad_path).resolve()), *_camera(center, radius, view)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            if result.returncode or not target.exists():
                raise ValueError(f"LeoCAD failed for {view}: {result.stderr[-300:]}")
            return target
        with ThreadPoolExecutor(max_workers=min(4, len(views))) as pool:
            images = list(pool.map(render, views))
        name = "look" + (f"-{re.sub(r'[^A-Za-z0-9_-]+', '_', focus)}" if focus else "") + ("-problems" if problems else "") + ".png"
        output = outdir / name
        _sheet(images, [v + (f" · {focus}" if focus else "") for v in views], output, 2 if len(views) > 1 else 1, cell)
    return dict(sheet=str(output), views=list(views), focus=focus, highlighted=len(targets), notes=notes,
                seconds=round(time.perf_counter() - started, 1))
