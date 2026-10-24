"""Measurements of actual LSynth placements, with explicit geometric coverage.

No replica synthesis or physical simulation. Distances refer to the segment-origin
polylines in the generated asset. Round-tube checks require an explicit radius.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from .common import jsonable, normalized
from .document import parse_source, section_table
from .flex import engine
from .flex_constraints import check, diagnostic


def polyline(points):
    points = np.asarray(points, dtype=float)
    if len(points) < 2:
        raise ValueError('Generated route has fewer than two segment origins')
    points = points[np.r_[True, np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-7]]
    if len(points) < 2:
        raise ValueError('Generated route has no measurable span')
    return points, np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]


def shape(points):
    points, run = polyline(points)
    chords = np.diff(points, axis=0)
    lengths = np.linalg.norm(chords, axis=1)
    units = chords / lengths[:, None]
    turn = np.degrees(np.arccos(np.clip((units[:-1] * units[1:]).sum(1), -1, 1)))
    samples = np.unique(np.r_[np.arange(0, run[-1], 2.0), run[-1]])
    r = np.column_stack([np.interp(samples, run, points[:, k]) for k in range(3)])
    radius, at = None, None
    # A 12 LDU window limits noise from LSynth's uneven curve sampling.
    if len(r) >= 7:
        a, b, c = r[:-6], r[3:-3], r[6:]
        ab, bc, ca = [np.linalg.norm(v, axis=1) for v in (a - b, b - c, c - a)]
        twice_area = np.linalg.norm(np.cross(b - a, c - a), axis=1)
        radii = np.divide(ab * bc * ca, 2 * twice_area, out=np.full(len(b), np.inf), where=twice_area > 1e-9)
        i = int(np.argmin(radii))
        if np.isfinite(radii[i]):
            radius, at = float(radii[i]), b[i].tolist()
    row = dict(polyline_length_ldu=float(run[-1]), minimum_sampled_radius_ldu=radius,
               radius_at=at, bend_sampling='2 LDU arc-length samples, 12 LDU circumradius window; sharp segment turns reported separately',
               max_segment_turn_degrees=float(turn.max()) if len(turn) else 0,
               turn_at=points[1 + int(np.argmax(turn))].tolist() if len(turn) else None,
               segment_spacing_ldu=dict(min=float(lengths.min()), max=float(lengths.max())),
               first=points[0].tolist(), last=points[-1].tolist())
    return row, points, run


def closest_segments(a, b, *, self_gap=None):
    """Exact distance between two polylines, bounded-memory batches.

    Check the unconstrained line minimum and all four endpoint-to-segment minima.
    For self checks exclude nearby arc-length neighbours, never whole end zones.
    """
    a, ar = polyline(a)
    b, _ = polyline(b)
    best = (float('inf'), None, None)
    q, v = b[:-1], np.diff(b, axis=0)
    vv = (v * v).sum(1)
    for base in range(0, len(a)-1, 64):
        p = a[base:base+64 if base+64 < len(a) else len(a)-1]
        u = a[base+1:base+1+len(p)] - p
        w = p[:, None] - q[None]
        uu = (u*u).sum(1)[:, None]
        uv = u @ v.T
        uw = (u[:, None] * w).sum(2)
        vw = (v[None] * w).sum(2)
        den = uu*vv - uv*uv
        s = np.divide(uv*vw - vv*uw, den, out=np.zeros_like(den), where=np.abs(den)>1e-12)
        t = np.divide(uu*vw - uv*uw, den, out=np.zeros_like(den), where=np.abs(den)>1e-12)
        valid = (np.abs(den)>1e-12) & (s>=0) & (s<=1) & (t>=0) & (t<=1)
        dist = np.where(valid, np.linalg.norm(w+s[:,:,None]*u[:,None]-t[:,:,None]*v[None], axis=2), np.inf)
        for ss in (0.0, 1.0):
            tt = np.clip((vw + ss*uv)/vv, 0, 1)
            d = np.linalg.norm(w+ss*u[:,None]-tt[:,:,None]*v[None], axis=2)
            improve = d < dist
            dist, s, t = np.where(improve,d,dist), np.where(improve,ss,s), np.where(improve,tt,t)
        for tt in (0.0, 1.0):
            ss = np.clip((tt*uv-uw)/uu, 0, 1)
            d = np.linalg.norm(w+ss[:,:,None]*u[:,None]-tt*v[None], axis=2)
            improve = d < dist
            dist, s, t = np.where(improve,d,dist), np.where(improve,ss,s), np.where(improve,tt,t)
        if self_gap is not None:
            i = np.arange(base, base+len(p))[:, None]
            j = np.arange(len(q))[None]
            # Difference between the end of the earlier segment and start of the later.
            dist[(j <= i+1) | (ar[j] - ar[i+1] <= self_gap)] = np.inf
        i, j = np.unravel_index(np.argmin(dist), dist.shape)
        if dist[i,j] < best[0]:
            best = (float(dist[i,j]), (p[i]+s[i,j]*u[i]).tolist(), (q[j]+t[i,j]*v[j]).tolist())
    return best


def check_asset(source, asset, *, source_report=None, block=None, min_radius=None, max_turn=None,
                tube_radius=None, min_separation=None, length=None, length_tolerance=1,
                obstacles=None, obstacle_section=None, parts=None):
    for name, v in dict(min_radius=min_radius, max_turn=max_turn, tube_radius=tube_radius,
                        min_separation=min_separation, length=length, length_tolerance=length_tolerance).items():
        if v is not None and (not np.isfinite(v) or v < 0):
            raise ValueError(f'{name} must be finite and nonnegative')
    if tube_radius == 0:
        raise ValueError('tube_radius must be positive')
    report = copy.deepcopy(source_report) if source_report is not None else check(source)
    if hashlib.sha256(Path(source).read_bytes()).hexdigest() != report['source_sha256']:
        raise ValueError('Stale source report; recheck the saved constraints before measuring the asset')
    if not report['checks_passed']:
        return report
    path = Path(asset)
    manifest = json.loads(path.with_suffix('.manifest.json').read_text())
    if not isinstance(manifest,dict) or not isinstance(manifest.get('blocks'),list):
        raise ValueError('Invalid flex manifest; rebuild the asset from its constraints')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cfg, config, _ = engine()
    for key, value in [('source_sha256', report['source_sha256']), ('model_sha256', digest),
                       ('config_sha256', hashlib.sha256(config.read_bytes()).hexdigest())]:
        if manifest.get(key) != value:
            raise ValueError(f'Stale or mismatched {key}; rebuild this asset from the saved constraints with flex build')
    records = manifest['blocks']
    for record in records:
        if (not isinstance(record,dict) or not {'method','representation','segment_count'} <= record.keys()
                or not isinstance(record['segment_count'],int) or record['segment_count'] < 1):
            raise ValueError('Invalid flex block manifest; rebuild the asset from its constraints')
    if len(records) != len(report['routes']):
        raise ValueError('Manifest block count differs from the source; rebuild the asset')
    if block is not None and (not isinstance(block, int) or not 1 <= block <= len(records)):
        raise ValueError('block must identify an existing SYNTH block (1-based)')
    selected_hoses = [r for r in report['routes'] if r['kind']=='hose' and (block is None or r['block']==block)]
    if not selected_hoses and (obstacles or any(v is not None for v in (min_radius,max_turn,tube_radius,min_separation,length))):
        raise ValueError('Hose geometry limits require a selected hose block; inspect band/link closure and engagement separately')
    model = parse_source(path)
    sections = section_table(model)
    diagnostics = report['diagnostics']
    rows, curves = [], []
    for route, record in zip(report['routes'], records):
        where = dict(block=route['block'], name=route['name'], section=route['section'], line=route['line'])
        if record['method'] != route['method']:
            raise ValueError('Manifest method differs from source; rebuild the asset')
        if 'part' in record:
            pieces = sections[normalized(record['part'])].pieces
        else:
            if 'first_piece' not in record:
                raise ValueError('Link measurements need a current flex manifest; rebuild the asset')
            sec = sections[normalized(record['section'])]
            i = record['first_piece']
            pieces = sec.pieces[i:i+record['segment_count']]
        if len(pieces) != record['segment_count']:
            raise ValueError('Generated segment count differs from manifest')
        points = [jsonable(p.position) for p in pieces]
        if route['kind'] == 'band':
            # LSynth emits each outgoing straight run before the arc around its
            # wheel. File order is not loop traversal order: joining these origins
            # would invent long jumps, false hairpins and a false closure gap.
            if block is None or route['block'] == block:
                rows.append(dict(**where, method=route['method'], representation=record['representation'],
                    generated_segments=len(pieces), measurement_basis='unordered generated placement origins',
                    placement_origin_bounds_ldu=dict(min=np.min(points,axis=0).tolist(), max=np.max(points,axis=0).tolist()),
                    closure_check='not_measured: file order is not loop traversal; inspect joining geometry and engagement'))
            continue
        measurement_basis = 'successive generated segment origins (end offsets excluded)'
        if len(pieces) == 1 and route['kind'] == 'hose':
            definition = cfg.hose_type(route['method'])
            if definition.fill != -1 or definition.start.attrib:
                raise ValueError('Single fixed segment has no calibrated route length; inspect its geometry')
            # A straight STRETCH cable can legitimately be one long placement.
            # Recover its span from that actual transform, not the source chord.
            m = np.array(pieces[0].matrix.rows)
            start = np.array(points[0]) - m @ definition.start.offset
            axis = m[:,1]
            sign = 1 if axis @ np.array(route['frames'][0]['direction']) >= 0 else -1
            points = [start, start+sign*axis]
            measurement_basis = 'single stretched placement longitudinal axis (may include end/section overhang)'
        measurements, pts, run = shape(points)
        if route['kind'] == 'hose':
            curves.append((route, pts, run))
        if block is not None and route['block'] != block:
            continue
        row = dict(**where, method=route['method'], representation=record['representation'],
                   generated_segments=len(pieces), measurement_basis=measurement_basis, **measurements)

        def add(code, message, action, **extra):
            diagnostics.append(diagnostic(code, message, action, **where, **extra))

        if route['kind'] == 'hose':
            radius = row['minimum_sampled_radius_ldu']
            if min_radius is not None:
                if radius is not None and radius < min_radius:
                    add('bend', f'Sampled bend radius {radius:.3f} is below {min_radius:g} LDU.',
                        'Inspect this bend; change its approach or increase free space, then synthesize again.', at=row['radius_at'])
                elif radius is None and row['max_segment_turn_degrees'] > 1e-3:
                    add('bend_unresolved', 'Route is too short for the sampled bend window.',
                        'Inspect the segment turns and end geometry; do not treat missing radius as a passing bend.')
            if max_turn is not None and row['max_segment_turn_degrees'] > max_turn:
                add('segment_turn', f'Adjacent segments turn {row["max_segment_turn_degrees"]:.3f} degrees.',
                    'Use a broader route; inspect ring gaps and end transitions.', at=row['turn_at'])
            # These end sleeves have independently checked geometric conventions in the press fixture.
            if route['method'] == 'TECHNIC_PNEUMATIC_HOSE_BEVELED':
                row['endpoint_check'] = 'generated sleeves against source marker frames; physical nozzle placement still requires inspection'
                for end, piece, frame, sign in [('start',pieces[0],route['frames'][0],1), ('end',pieces[-1],route['frames'][-1],-1)]:
                    direction = np.array(frame['direction'])
                    expected = np.array(frame['at']) + sign*16*direction
                    actual = np.array(jsonable(piece.position))
                    axis = np.array(piece.matrix.rows)[:,1]
                    axis /= np.linalg.norm(axis)
                    if np.linalg.norm(actual-expected)>0.01 or abs(abs(axis@direction)-1)>1e-5:
                        add('endpoint', f'{end} sleeve does not match its constraint frame.',
                            'Inspect the marker direction and endpoint definition; check the actual synthesized end.', at=actual.tolist())
            else:
                row['endpoint_check'] = 'manual: family-specific end geometry is not calibrated by this checker'
            if tube_radius is not None:
                distance, at, other = closest_segments(pts, pts, self_gap=max(np.pi*2*tube_radius, 6))
                row['self_separation_ldu'] = distance if np.isfinite(distance) else None
                row['self_neighbour_exclusion_ldu'] = max(np.pi*2*tube_radius, 6)
                if distance < 2*tube_radius - 1e-5:
                    add('self_intersection', 'Non-neighbouring route spans intersect the specified round tube envelope.',
                        'Change the loop or passage at this crossing; do not add dense markers.', at=at, other_at=other, distance_ldu=distance)
        rows.append(row)
    if length is not None:
        if len(rows) != 1 or not any(r['block'] == rows[0]['block'] for r, _, _ in curves):
            raise ValueError('--length requires one hose; select --block')
        actual = rows[0]['polyline_length_ldu']
        if abs(actual-length) > length_tolerance:
            diagnostics.append(diagnostic('length', f'Polyline length {actual:.3f} differs from target {length:g}.',
                'Adjust the slack route, keeping the actual physical endpoints fixed; this measurement excludes end offsets.', block=rows[0]['block']))
    separations = []
    required = min_separation if min_separation is not None else (2*tube_radius if tube_radius is not None else None)
    for i, (a, pa, _) in enumerate(curves):
        for b, pb, _ in curves[i+1:]:
            if block is not None and block not in {a['block'], b['block']}:
                continue
            if a['section'] != b['section']:
                continue
            d, at, other = closest_segments(pa, pb)
            separations.append(dict(blocks=[a['block'],b['block']], distance_ldu=d, at=at, other_at=other))
            if required is not None and d < required - 1e-5:
                diagnostics.append(diagnostic('separation', f'Route separation {d:.3f} is below {required:g} LDU.',
                    'Inspect this pair, including fittings; change the lane or route. No endpoint zones were omitted.',
                    blocks=[a['block'],b['block']], at=at, other_at=other))
    coverage = dict(report['coverage'], synthesized_geometry='measured actual placements in each source section frame',
                    bend='explicit geometric limit checked on selected hoses' if min_radius is not None else 'measured; no acceptance limit supplied',
                    self_intersection='nonlocal round-tube spans checked; near neighbours require bend/turn review' if tube_radius is not None else 'not_checked: specify measured --tube-radius',
                    separation='selected hoses and same-section neighbours checked' if required is not None else 'measured; no acceptance limit supplied',
                    band_closure='not_measured: file order is not traversal; inspect link engagement and physical closure',
                    stock_length='not_proven: polyline length is not manufactured material length')
    obstacle_rows = []
    if obstacles:
        if tube_radius is None or parts is None:
            raise ValueError('Obstacle checks require parts and an explicit --tube-radius')
        if len({r['section'] for r,_,_ in curves if block is None or r['block']==block}) > 1:
            raise ValueError('Select --block for obstacle checks on sources with multiple local section frames')
        obstacle_rows = obstacle_boxes(obstacles, obstacle_section, parts,
            [(r,p,s) for r,p,s in curves if block is None or r['block']==block], tube_radius)
        for hit in obstacle_rows:
            diagnostics.append(diagnostic('obstacle_bounds', 'Round route envelope overlaps a rigid part bounding box.',
                'Inspect the named part in context: boxes include holes and mating regions. No end-zone exemptions were applied.',
                severity='warning', **hit))
        coverage['obstacles'] = 'conservative oriented boxes, sampled at <=1 LDU; potential overlaps require inspection'
    elif obstacle_section:
        raise ValueError('--obstacle-section requires --obstacles')
    return dict(**{k:v for k,v in report.items() if k not in {'checks_passed','coverage'}},
                checks_passed=not any(d['severity']=='error' for d in diagnostics), coverage=coverage,
                asset=str(path.resolve()), model_sha256=digest, measurements=rows, separations=separations,
                measured_hose_pairs=len(separations),
                obstacle_candidates=obstacle_rows, visual_review='required: open contextual images; this command does not render',
                settings=dict(block=block, min_radius=min_radius, max_turn=max_turn, tube_radius=tube_radius,
                    min_separation=min_separation, length=length, length_tolerance=length_tolerance,
                    obstacles=str(Path(obstacles).resolve()) if obstacles else None, obstacle_section=obstacle_section,
                    obstacles_sha256=hashlib.sha256(Path(obstacles).read_bytes()).hexdigest() if obstacles else None),
                measurement_limits=['Segment-origin polylines omit family-specific end offsets and non-round cross sections.',
                                    'Bend sampling is finite; inspect sharp local turns too.',
                                    'Different MPD sections are different local frames; pair checks do not compare them.',
                                    'Band placement order is not loop traversal; no band length, curvature or closure metric is inferred.',
                                    'No physical bend, tension, elasticity, stock-length or motion certification.'])


def obstacle_boxes(source, section, parts, curves, radius):
    from .collision import oriented_box
    from .connectivity import inspect_connections
    from .document import physical_context
    model = parse_source(source)
    model, library = physical_context(model, parts, section)
    inspection = inspect_connections(model, library)
    from .geometry import geometry_complete
    if not geometry_complete(inspection):
        raise ValueError('Obstacle geometry is incomplete; resolve missing parts first')
    hits = []
    for route, pts, run in curves:
        samples = np.unique(np.r_[np.arange(0,run[-1],1.0),run[-1]])
        p = np.column_stack([np.interp(samples,run,pts[:,k]) for k in range(3)])
        for item in inspection.occurrences:
            box = oriented_box(item)
            if box is None:
                raise ValueError(f'Obstacle {item.index} has no usable rigid bounds')
            centre, rotation, half = box
            local = np.abs((p-centre) @ rotation)-half
            distance = np.linalg.norm(np.maximum(local,0),axis=1)+np.minimum(local.max(1),0)
            i = int(np.argmin(distance))
            # Half the sampling step is an uncertainty margin, not extra material.
            if distance[i] <= radius+0.5:
                hits.append(dict(block=route['block'], occurrence=item.index, part=item.occurrence.reference,
                                 at=p[i].tolist(), sampled_box_surface_distance_ldu=float(distance[i])))
    return hits
