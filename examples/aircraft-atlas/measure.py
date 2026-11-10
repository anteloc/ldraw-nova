"""Measure the proportions of source aircraft sections for the aircraft guide.

The numbers describe the annotated sources as drawn: part extents in LDU, part counts, the share of
Technic-prefixed parts, stud directions, and where the tyres, engines and propellers sit. They are
analysis only; nothing here admits a source or proves fit. Run from the repository root:

    .venv/bin/python examples/aircraft-atlas/measure.py --markdown
    .venv/bin/python examples/aircraft-atlas/measure.py --key 10226-sopwith-camel --forward -X
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from ldraw import inspect_model  # noqa: E402
from ldraw_tools.common import atomic_write, dumps, get_parts, models_path  # noqa: E402
from ldraw_tools.discovery import confined  # noqa: E402
from ldraw_tools.document import parse_source, physical_context  # noqa: E402

AXES = {'+X': np.array([1, 0, 0]), '-X': np.array([-1, 0, 0]), '+Z': np.array([0, 0, 1]), '-Z': np.array([0, 0, -1])}
STUD = {(0, -1, 0): 'up', (0, 1, 0): 'down', (1, 0, 0): '+X', (-1, 0, 0): '-X', (0, 0, 1): '+Z', (0, 0, -1): '-Z'}


def classify(vector):
    key = tuple(int(round(v)) for v in vector)
    return STUD.get(key, 'angled') if np.allclose(vector, key, atol=1e-3) else 'angled'


def measure(model_name, section, parts, *, forward=None):
    source = confined(models_path(), model_name)
    model, overlay = physical_context(parse_source(source), parts, section=section)
    inspection = inspect_model(model, overlay)
    rows = []
    for item in inspection.occurrences:
        o = item.occurrence
        description = parts.by_code.get(o.part_code.casefold(), '') or ''
        matrix = np.asarray(o.matrix.rows, dtype=float)
        position = np.array([o.position.x, o.position.y, o.position.z], dtype=float)
        centre = position
        if item.local.bounds is not None:
            local = np.array([[item.local.bounds.min.x, item.local.bounds.min.y, item.local.bounds.min.z],
                              [item.local.bounds.max.x, item.local.bounds.max.y, item.local.bounds.max.z]])
            centre = matrix @ local.mean(axis=0) + position
        rows.append(dict(code=o.part_code, description=description, centre=centre,
                         stud=classify(matrix @ np.array([0, -1, 0]))))
    b = inspection.bounds
    extent = dict(x=float(b.max.x-b.min.x), y=float(b.max.y-b.min.y), z=float(b.max.z-b.min.z),
                  min=[float(b.min.x), float(b.min.y), float(b.min.z)], max=[float(b.max.x), float(b.max.y), float(b.max.z)])
    tyres = [r for r in rows if r['description'].casefold().startswith('tyre')]
    engines = [r for r in rows if any(w in r['description'].casefold() for w in ('engine', 'jet', 'turbine'))]
    propellers = [r for r in rows if any(w in r['description'].casefold() for w in ('propeller', 'rotor'))]
    technic = sum(1 for r in rows if r['description'].startswith('Technic'))
    result = dict(model=model_name, section=section, parts=len(rows), unique_parts=len({r['code'].casefold() for r in rows}),
                  technic_share=round(technic/len(rows), 2) if rows else 0.0, extent_ldu=extent,
                  extent_studs=dict(x=round(extent['x']/20, 1), y=round(extent['y']/20, 1), z=round(extent['z']/20, 1)),
                  stud_directions=dict(Counter(r['stud'] for r in rows)),
                  tyre_centres=[[round(float(v), 1) for v in r['centre']] for r in tyres],
                  engine_parts=[dict(code=r['code'], centre=[round(float(v), 1) for v in r['centre']]) for r in engines],
                  propeller_parts=[dict(code=r['code'], centre=[round(float(v), 1) for v in r['centre']]) for r in propellers],
                  geometry_complete=bool(inspection.complete))
    if forward:
        f = AXES[forward]
        across = np.array([0, 0, 1]) if abs(f[0]) else np.array([1, 0, 0])
        centres = np.array([r['centre'] for r in rows]) if rows else np.zeros((0, 3))
        along = centres @ f
        span = centres @ across
        half = max(abs(span.min()), abs(span.max())) if len(span) else 0
        outer = along[np.abs(span) >= 0.6*half] if half else along
        fuselage = along[np.abs(span) <= 0.15*half] if half else along
        length = float(along.max()-along.min()) if len(along) else 0
        nose = float(along.max()) if len(along) else 0
        result['frame'] = dict(forward=forward, length_ldu=round(length, 1), span_ldu=round(float(span.max()-span.min()), 1) if len(span) else 0,
                               height_ldu=round(extent['y'], 1),
                               outer_wing_station_from_nose_ldu=[round(nose-float(outer.max()), 1), round(nose-float(outer.min()), 1)] if len(outer) else None,
                               fuselage_station_from_nose_ldu=[round(nose-float(fuselage.max()), 1), round(nose-float(fuselage.min()), 1)] if len(fuselage) else None,
                               tyre_stations_from_nose_ldu=sorted({round(nose-float(np.array(c) @ f), 1) for c in result['tyre_centres']}),
                               tyre_track_ldu=round(float(max(np.array(c) @ across for c in result['tyre_centres'])-min(np.array(c) @ across for c in result['tyre_centres'])), 1) if result['tyre_centres'] else None,
                               engine_across_ldu=sorted({round(float(np.array(e['centre']) @ across), 1) for e in result['engine_parts']}),
                               engine_stations_from_nose_ldu=sorted({round(nose-float(np.array(e['centre']) @ f), 1) for e in result['engine_parts']}))
    return result


def markdown(results):
    lines = ['| Source section | Style | Parts | Technic share | Span × length × height (studs) | Studs up / sideways / down | Tyres | Engines |',
             '|---|---|---:|---:|---|---|---|---|']
    for r in results:
        d = r['stud_directions']
        sideways = sum(v for k, v in d.items() if k in ('+X', '-X', '+Z', '-Z'))
        if r.get('frame'):
            f = r['frame']
            size = f'{f["span_ldu"]/20:.0f} × {f["length_ldu"]/20:.0f} × {f["height_ldu"]/20:.0f} (forward {f["forward"]})'
        else:
            e = r['extent_studs']
            size = f'X {e["x"]:.0f} × Z {e["z"]:.0f} × Y {e["y"]:.0f} (forward not declared)'
        lines.append(f'| `{r["model"]}` / `{r["section"]}` | {r.get("style", "")} | {r["parts"]} | {r["technic_share"]:.0%} | {size} | '
                     f'{d.get("up", 0)} / {sideways} / {d.get("down", 0)} (angled {d.get("angled", 0)}) | {len(r["tyre_centres"])} | {len(r["engine_parts"])} |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key', action='append', help='selection key; default: every overview seed')
    parser.add_argument('--forward', choices=sorted(AXES), help='override the forward axis for the selected keys')
    parser.add_argument('--output', type=Path, default=HERE/'measurements.json')
    parser.add_argument('--markdown', action='store_true', help='print a Markdown table')
    args = parser.parse_args()
    seeds = json.loads((HERE/'selections.json').read_text())['references']
    chosen = [s for s in seeds if (s['key'] in args.key if args.key else s.get('overview'))]
    parts = get_parts()
    results = []
    for seed in chosen:
        forward = args.forward or seed.get('frame', {}).get('forward')
        r = measure(seed['model'], seed['section'], parts, forward=forward)
        r.update(key=seed['key'], style=seed.get('style', ''))
        results.append(r)
        print(f'{seed["key"]}: {r["parts"]} parts, extents {r["extent_studs"]}, studs {r["stud_directions"]}', flush=True)
    atomic_write(args.output, dumps(results)+'\n')
    if args.markdown:
        print(markdown(results))
