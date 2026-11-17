"""Generate ldraw_tools/data/technic-gears.json: gear facts and mesh geometries.

    .venv/bin/python scripts/technic_gears.py

Tooth counts and types come from the part descriptions. How two gears stand
when they mesh is not assumed: parallel pairs are checked against the pitch
rule, and perpendicular, worm and rack arrangements are counted in the official
sets (data/models-annotated) and kept when they recur.
"""
from __future__ import annotations

import collections
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import DATA, atomic_write, get_parts, models_path, shadow_paths  # noqa: E402
from ldraw_tools.document import parse_source, physical_context  # noqa: E402
from ldraw_tools.technic import canonical, registry  # noqa: E402

TABLE = DATA / 'technic-gears.json'
MODULE = 1.25


def gear_type(description):
    text = description.lstrip('~=_ ')
    if 'Gear Rack' in text:
        return 'rack'
    if not re.match(r'Technic (Gear|Worm|Turntable|Differential)', text):
        return None
    for name, word in (('worm', 'Worm'), ('turntable', 'Turntable'), ('differential', 'Differential'),
                       ('double_bevel', 'Double Bevel'), ('bevel', 'Bevel'), ('crown', 'Crown'), ('knob', 'Knob')):
        if word in text:
            return name
    return 'spur'


def gear_entry(code, description, entry, bounds):
    kind = gear_type(description)
    if kind is None:
        return None
    teeth = re.search(r'(\d+) Tooth', description)
    teeth = int(teeth.group(1)) if teeth else None
    row = dict(description=description.lstrip('~=_ '), type=kind)
    if teeth:
        row['teeth'] = teeth
    if kind == 'worm':
        row['radius'] = 10.0
    elif kind == 'knob':
        row['radius'] = 20.0
    elif kind != 'rack' and teeth:
        row['radius'] = MODULE * teeth
    holes = [p for p in (entry or {}).get('ports', []) if p['kind'] == 'axle_hole'] or \
            [p for p in (entry or {}).get('ports', []) if p['kind'] == 'pin_hole']
    if kind != 'rack':
        if not holes or 'radius' not in row:
            return None
        centres = np.array([p['at'] for p in holes], float)
        middle = (np.array(bounds['min']) + np.array(bounds['max'])) / 2 if bounds else centres.mean(axis=0)
        axis = np.array(holes[0]['axis'], float)
        offsets = centres - middle
        radial = np.linalg.norm(offsets - np.outer(offsets @ axis, axis), axis=1)
        on_axis = [p for p, r in zip(holes, radial) if r < 1.0]
        if not on_axis:
            return None
        along = [float(np.array(p['at'], float) @ axis) for p in on_axis]
        low = min(a - p['length'] / 2 for a, p in zip(along, on_axis))
        high = max(a + p['length'] / 2 for a, p in zip(along, on_axis))
        base = np.array(on_axis[0]['at'], float)
        centre = base + axis * ((low + high) / 2 - float(base @ axis))
        row.update(axis=[round(float(v), 6) + 0.0 for v in axis], centre=[round(float(v), 3) + 0.0 for v in centre],
                   width=round(high - low, 3), ports=[p['id'] for p in on_axis])
    return row


def library_descriptions(parts):
    rows = {}
    for line in Path(parts.path).read_text(errors='replace').splitlines():
        match = re.match(r'(\S+)\.dat\s+(.*)', line.strip(), re.I)
        if match:
            rows[match.group(1).casefold()] = match.group(2)
    return rows


def gears(parts):
    listed = library_descriptions(parts)
    entries = registry()['parts']
    table = {}
    for code, description in sorted(listed.items()):
        if description.startswith('~Moved') or gear_type(description) is None:
            continue
        key = canonical(code)
        bounds = None
        try:
            box = parts.geometry(code).bounds
            bounds = dict(min=[box.min.x, box.min.y, box.min.z], max=[box.max.x, box.max.y, box.max.z]) if box else None
        except Exception:
            continue
        row = gear_entry(code, description, entries.get(key), bounds)
        if row:
            if row['type'] == 'rack':
                row['bounds'] = dict(min=[round(v, 3) for v in bounds['min']], max=[round(v, 3) for v in bounds['max']])
            table[code] = row
    return table


def mine(parts, table, seconds=240):
    """Count how gears stand to each other in the official sets."""
    listed = library_descriptions(parts)
    parallel = collections.Counter()
    perpendicular = collections.Counter()
    worm = collections.Counter()
    rack = collections.defaultdict(collections.Counter)
    started, models = time.time(), 0
    for path in sorted(models_path().glob('*.mpd'), key=lambda p: p.stat().st_size):
        if time.time() - started > seconds:
            break
        text = path.read_text(errors='replace')
        if text.count('2780.dat') < 20 or not re.search(r'Tooth|3647|3648|32270|32269|94925|4716|3743', text):
            continue
        try:
            model, _ = physical_context(parse_source(path), parts)
            found = []
            for occurrence in model.iter_occurrences(include_steps=False):
                code = occurrence.part_code.casefold()
                row = table.get(code) or table.get(canonical(code))
                if not row:
                    continue
                matrix = np.array(occurrence.matrix.rows, float)
                if abs(np.linalg.det(matrix) - 1) > 1e-3:
                    continue
                position = np.array([occurrence.position.x, occurrence.position.y, occurrence.position.z], float)
                if row['type'] == 'rack':
                    found.append((code, row, position, matrix))
                else:
                    found.append((code, row, position + matrix @ np.array(row['centre']), matrix @ np.array(row['axis'])))
        except Exception:
            continue
        models += 1
        for i, (code_a, a, centre_a, axis_a) in enumerate(found):
            for code_b, b, centre_b, axis_b in found[i + 1:]:
                if a['type'] == 'rack' and b['type'] == 'rack':
                    continue
                if a['type'] == 'rack' or b['type'] == 'rack':
                    (rcode, r, rpos, rmat), (g, gcentre, gaxis) = ((code_a, a, centre_a, axis_a), (b, centre_b, axis_b)) \
                        if a['type'] == 'rack' else ((code_b, b, centre_b, axis_b), (a, centre_a, axis_a))
                    if g['type'] == 'worm' or 'teeth' not in g:
                        continue
                    local = rmat.T @ (gcentre - rpos)
                    low, high = np.array(r['bounds']['min']), np.array(r['bounds']['max'])
                    if np.any(local < low - 60) or np.any(local > high + 60):
                        continue
                    local_axis = rmat.T @ gaxis
                    direction = int(np.argmax(np.abs(local_axis)))
                    if abs(local_axis[direction]) < 0.999:
                        continue
                    length = int(np.argmax(high - low))
                    if direction == length:
                        continue
                    other = [k for k in range(3) if k not in (direction, length)][0]
                    rack[rcode][(g['teeth'], direction, other, round(float(local[other]), 1))] += 1
                    continue
                delta = centre_b - centre_a
                if np.linalg.norm(delta) > 140:
                    continue
                dot = abs(float(axis_a @ axis_b))
                first, second = sorted([(a['type'], a.get('teeth', 0)), (b['type'], b.get('teeth', 0))])
                swap = (a['type'], a.get('teeth', 0)) != first
                if dot > 0.999:
                    if 'worm' in (a['type'], b['type']):
                        continue
                    axial = abs(float(delta @ axis_a))
                    radial = float(np.linalg.norm(delta - (delta @ axis_a) * axis_a))
                    if axial <= (a['width'] + b['width']) / 2 - 1:
                        parallel[first, second, round(radial - a['radius'] - b['radius'], 1)] += 1
                elif dot < 0.001:
                    normal = np.cross(axis_a, axis_b)
                    normal /= np.linalg.norm(normal)
                    skew = abs(float(delta @ normal))
                    off_a, off_b = abs(float(delta @ axis_a)), abs(float(delta @ axis_b))
                    if swap:
                        off_a, off_b = off_b, off_a
                    if 'worm' in (a['type'], b['type']):
                        worm[first, second, round(off_a, 1), round(off_b, 1), round(skew, 1)] += 1
                    elif skew < 1 and max(off_a, off_b) <= 75:
                        perpendicular[first, second, round(off_a, 1), round(off_b, 1)] += 1
    return dict(models=models, parallel=parallel, perpendicular=perpendicular, worm=worm, rack=rack)


def main():
    parts = get_parts(shadows=shadow_paths())
    table = gears(parts)
    mined = mine(parts, table)
    exact = sum(n for (a, b, d), n in mined['parallel'].items() if abs(d) <= 0.6)
    near = sum(n for (a, b, d), n in mined['parallel'].items() if abs(d) <= 3)
    # A perpendicular arrangement is kept when it recurs and each gear stands off the other's axis.
    perpendicular = [dict(a=list(a), b=list(b), offset_a=oa, offset_b=ob, count=n)
                     for (a, b, oa, ob), n in sorted(mined['perpendicular'].items(), key=lambda kv: -kv[1])
                     if n >= 5 and oa >= 5 and ob >= 5 and oa <= 1.25 * b[1] + 12 and ob <= 1.25 * a[1] + 12]
    worms = [dict(a=list(a), b=list(b), offset_a=oa, offset_b=ob, skew=s, count=n)
             for (a, b, oa, ob, s), n in sorted(mined['worm'].items(), key=lambda kv: -kv[1]) if n >= 5]
    # A rack's pitch line follows from its most common pinion: the pinion's axis
    # stands one pitch radius off it.
    racks = {}
    for code, counts in mined['rack'].items():
        (teeth, axis, normal, offset), count = counts.most_common(1)[0]
        if count >= 5:
            sign = -1.0 if offset < 0 else 1.0
            racks[code] = dict(pinion_axis='xyz'[axis], normal='xyz'[normal], side=sign,
                               pitch=round(offset - sign * MODULE * teeth, 3),
                               evidence=dict(teeth=teeth, offset=offset, count=count))
            table[code].update(racks[code])
    result = dict(version=1, units='LDU', generator='scripts/technic_gears.py',
                  rule='Parallel gears mesh when their axes are 1.25 * (teeth_a + teeth_b) LDU apart.',
                  evidence=dict(models=mined['models'], parallel_pairs_within_3_ldu=near, parallel_pairs_exact=exact),
                  gears=table, perpendicular=perpendicular, worm=worms)
    atomic_write(TABLE, json.dumps(result, indent=1) + '\n')
    print(json.dumps(dict(gears=len(table), types=collections.Counter(g['type'] for g in table.values()),
                          evidence=result['evidence'], perpendicular=len(perpendicular), worm=len(worms), racks=len(racks)), default=dict))
    for row in perpendicular[:16]:
        print('  perp', row)
    for row in worms[:8]:
        print('  worm', row)
    for code, row in racks.items():
        print('  rack', code, table[code]['description'], row)


if __name__ == '__main__':
    main()
