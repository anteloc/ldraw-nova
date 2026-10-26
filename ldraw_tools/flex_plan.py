"""Compile named plan routes through the existing LSynth authoring/checking path."""
from __future__ import annotations

import hashlib
import json

import numpy as np

from .common import CACHE, DATA, atomic_write, jsonable
from .flex_authoring import Endpoint, Waypoint, band, document, hose, placement


def ports(parts, ref):
    """Named fitting interfaces apply only to the measured geometry revision."""
    catalog = json.loads((DATA / 'flex-ports.json').read_text())['parts']
    code = ref.casefold().removesuffix('.dat')
    record = catalog.get(code)
    if record is None:
        raise ValueError(f'No named flex ports on {ref}; select an inspected feature or measured local frame')
    local = parts.geometry(code)
    digest = hashlib.sha256(json.dumps([jsonable(v) for v in local.points], separators=(',', ':')).encode()).hexdigest()
    if digest != record['geometry_sha256']:
        raise ValueError(f'Named flex ports on {ref} belong to a different geometry revision; inspect the part')
    return record['ports']


def endpoint(spec, identity, section, parts):
    pose = identity.resolve(section, spec['part'])
    options = dict(lead=spec.get('lead', 0), local_up=spec.get('up'))
    if 'port' in spec:
        available = ports(parts, pose['ref'])
        if spec['port'] not in available:
            raise ValueError(f"Unknown port {spec['port']!r} on {pose['ref']}; choose {', '.join(available)}")
        port = available[spec['port']]
        return Endpoint.on_part(pose['at'], pose['matrix'], port['at'], port['outward'], **options)
    if 'feature' in spec:
        return Endpoint.from_feature(parts, pose['ref'].removesuffix('.dat'), spec['feature'],
                                     at=pose['at'], matrix=pose['matrix'], **options)
    return Endpoint.on_part(pose['at'], pose['matrix'], spec['at'], spec['outward'], **options)


def prepare_inline(section, entry, identity, parts, *, author):
    from .flex_workflow import build
    route = entry['flex']
    namespace = 'route-' + hashlib.sha256((section + '/' + entry['id']).encode()).hexdigest()[:16]
    if 'wheels' in route:
        rows = []
        for wheel in route['wheels']:
            if isinstance(wheel, dict):
                rows.append('0 SYNTH ' + wheel['control'])
            else:
                pose = identity.resolve(section, wheel)
                rows.append(placement(pose['ref'], pose['at'], pose['matrix']))
        block = band(rows, method=route['method'], colour=entry['colour'], name=entry['id'], hide=True)
    else:
        start = endpoint(route['from'], identity, section, parts)
        end = endpoint(route['to'], identity, section, parts)
        via = [Waypoint(**w) if isinstance(w, dict) else Waypoint(w) for w in route.get('via', [])]
        block = hose(start, end, via=via, method=route['method'], colour=entry['colour'], name=entry['id'])
    source = document(block, name=namespace + '.ldr', author=author)
    folder = CACHE / 'inline-flex' / hashlib.sha256(source.encode()).hexdigest()
    path = folder / 'constraints.ldr'
    atomic_write(path, source)
    curves = []
    report = build(path, folder / 'asset.mpd', parts, namespace=namespace, force=True,
                   checks=route.get('checks'), timeout=route.get('timeout', 90), curves_out=curves)
    report['placement'] = identity.where(section, entry['id'])
    return report, curves


def review_routes(model, parts, source_map, curves, *, instance_limit=100000):
    """Measure interactions across module instances in the assembled frame."""
    from .connectivity import inspect_connections
    from .flex_review import closest_segments, obstacle_candidates, polyline
    from .geometry import geometry_complete
    from .identity import placement_location
    diagnostics, routes, seen = [], [], set()
    for row in source_map:
        route = row.get('inline_route')
        if not route or route['path'] in seen:
            continue
        seen.add(route['path'])
        route = dict(route, source=dict(placement_location(row), path=route['path']))
        measured, settings = curves[route['section'], route['placement']]
        for _, points, _ in measured:
            points, run = polyline(points @ np.asarray(route['matrix']).T + route['at'])
            routes.append((route, points, run, settings))
    pairs = []
    for i, (a, pa, _, sa) in enumerate(routes):
        for b, pb, _, sb in routes[i+1:]:
            distance, at, other = closest_segments(pa, pb)
            limits = [s['min_separation'] for s in (sa, sb) if 'min_separation' in s]
            if all('tube_radius' in s for s in (sa, sb)):
                limits.append(sa['tube_radius'] + sb['tube_radius'])
            limit = max(limits) if limits else None
            pairs.append(dict(routes=[a['path'], b['path']], distance_ldu=distance, required_ldu=limit))
            if limit is not None and distance < limit - 1e-5:
                diagnostics.append(dict(code='flex.separation', severity='error',
                    message=f'Routes are {distance:.3f} LDU apart; require {limit:g}.',
                    routes=[a['path'], b['path']], at=at, other_at=other,
                    placements=[a['source'], b['source']], distance_ldu=distance, required_ldu=limit,
                    action='Change the named route passage or hardware layout; recheck both routes.'))
    checked = []
    if any('tube_radius' in s for _, _, _, s in routes):
        inspection = inspect_connections(model, parts, instance_limit)
        if not geometry_complete(inspection):
            raise ValueError('Rigid obstacle geometry is incomplete; resolve missing parts first')
        excluded = {r['index'] for r in source_map if 'inline_route' in r}
        by_index = {r['index']: r for r in source_map}
        for route, pts, run, settings in routes:
            if 'tube_radius' not in settings:
                continue
            checked.append(route['path'])
            hits = obstacle_candidates(inspection, [(dict(block=1), pts, run)], settings['tube_radius'], exclude=excluded)
            for hit in hits:
                owner = by_index[hit['occurrence']]
                diagnostics.append(dict(code='flex.obstacle_bounds', severity='warning',
                    message='Route envelope overlaps a rigid part bounding box; mating regions and holes are included.',
                    route=route['path'], obstacle=owner['path'], placements=[placement_location(owner)], **hit,
                    action='Inspect this part and route in context; this candidate is not a proven material collision.'))
    return dict(checks_passed=not any(d['severity'] == 'error' for d in diagnostics),
                coordinate_space='reviewed assembly', separations=pairs, diagnostics=diagnostics,
                coverage=dict(route_instances=len(routes), measured_pairs=len(pairs),
                              pairs_without_limit=sum(p['required_ldu'] is None for p in pairs),
                              obstacles_checked=checked,
                              band_closure='manual: inspect the seam and engagement',
                              material_collision='conservative bounds only; inspect candidates'))
