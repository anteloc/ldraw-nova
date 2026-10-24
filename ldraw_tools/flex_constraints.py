"""Diagnose editable LSynth control records without inventing a curve solver.

Only SYNTH block boundaries are handled here. The installed LSynth parser owns
type-1 constraints and its definition tables own effective marker/wheel frames.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import numpy as np

from .flex import engine, preflight
from .flex_authoring import rigid
from .flex_knowledge import family, resolve


def diagnostic(code, message, action, *, severity='error', **where):
    return dict(code='flex.' + code, severity=severity, message=message, action=action, **where)


def blocks(text, cfg=None):
    from lsynth_nova.config import parse_type1, strclean
    cfg = cfg or engine()[0]
    preflight(text, cfg)
    result, current, section, label = [], None, None, None
    for number, raw in enumerate(text.splitlines(), 1):
        line = strclean(raw.lstrip())
        t = line.split()
        u = [v.upper() for v in t]
        if u[:2] == ['0', 'FILE']:
            section = line.split(None, 2)[2]
        elif u[:2] == ['0', 'NOFILE']:
            section = None
        elif line.startswith('0 //'):
            label = line[4:].strip()
        elif u[:3] == ['0', 'SYNTH', 'BEGIN']:
            _, definition, kind = resolve(t[3])
            current = dict(index=len(result) + 1, name=label or f'route-{len(result)+1}',
                           section=section, line=number, token=t[3], method=definition.type,
                           kind=kind, colour=t[4], constraints=[], controls=[], hidden=False)
            label = None
            result.append(current)
        elif u == ['0', 'SYNTH', 'END']:
            current['end_line'] = number
            current = None
        elif current is not None:
            if u[:2] == ['0', 'SYNTH']:
                current['controls'].append(dict(line=number, value=' '.join(u[2:])))
                if u[2:] == ['HIDE']: current['hidden'] = True
            elif t[:1] == ['1']:
                part = parse_type1(line)
                current['constraints'].append(dict(line=number, part=part))
            elif u[:3] == ['0', 'MLCAD', 'HIDE'] or t[:2] == ['0', '1']:
                current.setdefault('hidden_records', []).append(number)
    return result


def check_text(text):
    cfg, _, _ = engine()
    try:
        routes = blocks(text, cfg)
    except ValueError as exc:
        return dict(checks_passed=False, diagnostics=[diagnostic('source', str(exc),
                    'Correct the source control record; use original visible constraints and flex guide TYPE.')], routes=[])
    diagnostics, summaries = [], []
    for b in routes:
        where = dict(block=b['index'], name=b['name'], section=b['section'])

        def add(code, message, action, *, severity='error', **extra):
            diagnostics.append(diagnostic(code, message, action, severity=severity, **where, **extra))

        for line in b.get('hidden_records', []):
            add('hidden_constraint', 'Commented constraints are ignored on input.',
                'Keep type-1 constraints visible; SYNTH HIDE controls output ownership.', line=line)
        for c in b['controls']:
            if c['value'] not in {'SHOW', 'HIDE', 'INSIDE', 'OUTSIDE', 'CROSS'}:
                add('control', f"Unsupported block control {c['value']!r}.",
                    'Use SHOW/HIDE or documented band controls.', line=c['line'])
            elif b['kind'] == 'hose' and c['value'] in {'INSIDE', 'OUTSIDE', 'CROSS'}:
                add('control_kind', 'Wheel-route controls do not route a hose.',
                    'Use oriented path markers for this method.', line=c['line'])
        valid = []
        for c in b['constraints']:
            p = c['part']
            try:
                rigid(p.orient)
            except ValueError as exc:
                add('constraint_transform', str(exc), 'Recreate a proper marker/wheel rotation; do not normalize an arbitrary transform.', line=c['line'])
                continue
            index = cfg.hose_constraint(p.type) if b['kind'] == 'hose' else cfg.band_constraint_index(p.type)
            if index is None:
                add('not_a_constraint', f'{p.type} is not a {b["kind"]} constraint; LSynth ignores it for routing.',
                    'Move rigid context outside SYNTH; use a marker/wheel listed by flex guide TYPE.', line=c['line'], severity='warning')
            else:
                valid.append(c)
        if b['kind'] == 'hose':
            from lsynth_nova.hose import adjust_constraint
            if len(valid) < 2:
                add('marker_count', 'A hose needs at least two recognized visible markers.', 'Add start and end markers.', line=b['line'])
            effective = [adjust_constraint(c['part'], i == len(valid) - 1, cfg.hose_constraints) for i, c in enumerate(valid)]
            for i, (a, z) in enumerate(zip(effective, effective[1:])):
                d = np.array(z.offset) - a.offset
                length = float(np.linalg.norm(d))
                if length < 1e-5:
                    add('coincident_markers', 'Consecutive markers coincide.', 'Remove the duplicate; use distinct loop waypoints.', line=valid[i+1]['line'])
                    continue
                da, dz = -np.array(a.orient)[:, 1], -np.array(z.orient)[:, 1]
                if min(da @ d, dz @ d) < -1e-6:
                    add('backward_tangent', 'A marker points away from this span; synthesis may double back.',
                        'Inspect the indicated span; reverse an accidental end tangent or supply a deliberate wide return loop.',
                        line=valid[i+1]['line'], severity='warning', span_ldu=round(length, 4))
            if len(valid) > 16:
                add('dense_path', 'Many constraints increase coupling and can create sharp local bends.',
                    'Keep necessary passages, remove redundant constraints and inspect actual synthesis.', severity='warning', line=b['line'])
            frames = [dict(line=c['line'], at=p.offset, direction=(-np.array(p.orient)[:, 1]).tolist()) for c, p in zip(valid, effective)]
        else:
            frames = _band_frames(b, valid, cfg, add)
        summaries.append(dict(**where, line=b['line'], method=b['method'], kind=b['kind'], family=family(b['method']),
                              constraint_count=len(valid), hidden_wheels=b['hidden'], frames=frames))
    return dict(checks_passed=not any(d['severity'] == 'error' for d in diagnostics), routes=summaries,
                diagnostics=diagnostics, physical_validity='not_proven',
                coverage=dict(constraint_structure='checked', synthesized_geometry='not_checked',
                              fittings='not_checked', obstacles='not_checked', stock_length='not_checked', motion='not_checked'))


def _band_frames(b, valid, cfg, add):
    from lsynth_nova.band import BandConstraint, calc_tangent_line
    from lsynth_nova.config import Part
    if not valid:
        add('wheel_count', 'No recognized routing wheels.', 'Choose wheels from flex guide TYPE.', line=b['line'])
        return []
    p0 = valid[0]['part']
    table0 = cfg.band_constraints[cfg.band_constraint_index(p0.type)]
    plane = np.array(table0.orient) @ np.array(p0.orient).T
    frame_rows, circles, seen = [], [], []

    def inside_at(line):
        # Match synth_band: CROSS toggles the wrap side, not its dormant cross
        # field. Controls after the last wheel also set the closing wheel state.
        inside = 1
        for ctrl in b['controls']:
            if ctrl['line'] < line:
                if ctrl['value'] == 'INSIDE': inside = 1
                elif ctrl['value'] == 'OUTSIDE': inside = 0
                elif ctrl['value'] == 'CROSS': inside ^= 1
        return inside

    for c in valid:
        p = c['part']
        entry = cfg.band_constraints[cfg.band_constraint_index(p.type)]
        r = np.array(p.orient)
        normal = plane @ r @ np.array(entry.orient).T @ [0, 0, 1]
        # Match LSynth's steps before its unconditional flattening to Z=0.
        centre = plane @ (np.array(p.offset) - p0.offset) + table0.offset - plane @ r @ np.array(table0.orient).T @ entry.offset
        if abs(centre[2]) > 1e-4 or abs(abs(normal[2]) - 1) > 1e-6:
            add('wheel_plane', 'Wheel routing planes differ; LSynth flattens the route and may hide this error.',
                'Align the actual wheel planes before synthesis; use separate loops for different planes.', line=c['line'], plane_offset_ldu=float(centre[2]))
        duplicate = next((line for at, part, line in seen if part.lower() == p.type.lower() and np.allclose(at, p.offset, atol=1e-5, rtol=0)), None)
        if duplicate is not None:
            add('duplicate_wheel', f'Wheel position repeats line {duplicate}.',
                'Do not repeat the first wheel just to close a loop. If repetition is intentional, own wheels in the rigid model and use SYNTH HIDE.',
                line=c['line'], severity='warning')
        seen.append((p.offset, p.type, c['line']))
        frame_rows.append(dict(line=c['line'], part=p.type, at=p.offset, routing_centre=centre.tolist(), radius_ldu=entry.attrib))
        circles.append(BandConstraint(Part(p.type, [float(centre[0]), float(centre[1]), 0], p.orient),
                                      radius=entry.attrib, inside=inside_at(c['line'])))
    if not cfg.band_type(b['method']).pulley:
        closing = copy.deepcopy(circles[0])
        closing.inside = inside_at(b['end_line'])
        circles.append(closing)
    for i, (a, z) in enumerate(zip(circles, circles[1:])):
        if not calc_tangent_line(a, z):
            add('no_tangent', 'The selected wrap has no tangent between these wheels.',
                'Check wheel order and INSIDE/OUTSIDE/CROSS controls; separate or resize the actual wheel layout.',
                line=valid[i]['line'], next_line=valid[(i+1) % len(valid)]['line'])
    return frame_rows


def check(source):
    path = Path(source)
    raw = path.read_bytes()
    return dict(source=str(path.resolve()), source_sha256=hashlib.sha256(raw).hexdigest(), **check_text(raw.decode('utf-8-sig')))
