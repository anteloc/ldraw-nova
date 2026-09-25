"""Reproduce the Technic readiness measurements; this is not a structural solver.

Run from the repository root with .venv/bin/python. Outputs go under output/.
Only reads the installed library and shadow files; uses the normal library cache.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from importlib.metadata import version
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ldraw import Model, Piece, Vector
from ldraw.connection_types import snap_transform
from ldraw_tools.builder import rotation, serialize_mpd
from ldraw_tools.common import get_parts, jsonable
from ldraw_tools.connectivity import snap_report
from ldraw_tools.geometry import analyze_geometry


CODES = (
    '3001', '3022', '3700', '3701', '3702', '6541', '32000', '32064',
    '32523', '32316', '32524', '32525', '32348', '32063', '32073',
    '64179', '39793', '2780', '3673', '6558', '32556', '4274',
    '32062', '3705', '3706', '3713', '4265c', '43093', '11214',
    '15100', '6536', '32054', '87082', '2444', '3749', '3710',
)


def feature_record(feature):
    return {
        'id': feature.feature_id,
        'kind': str(feature.kind), 'role': str(feature.role),
        'position': jsonable(feature.position), 'axis': jsonable(feature.axis),
        'frame': jsonable(feature.frame), 'profile': jsonable(feature.profile),
        'freedoms': sorted(str(f) for f in feature.freedoms),
        'source': str(feature.source), 'group': feature.group,
        'confidence': feature.confidence,
    }


def main():
    out = ROOT / 'output/technic-research'
    out.mkdir(parents=True, exist_ok=True)
    parts = get_parts()
    geometries = {code: parts.geometry(code) for code in CODES}
    measurements = {}
    for code, geometry in geometries.items():
        source = parts.part(code=code).path
        measurements[code] = {
            'description': geometry.description, 'complete': geometry.complete,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'bounds': jsonable(geometry.bounds),
            'size': jsonable(geometry.bounds.size) if geometry.bounds else None,
            'coverage': str(geometry.connection_metadata.coverage),
            'diagnostics': jsonable(geometry.diagnostics),
            'features': [feature_record(f) for f in geometry.connections],
        }

    def feature(code, kind):
        return min((f for f in geometries[code].connections if str(f.kind) == kind),
                   key=lambda f: (str(f.source) != 'ldcad_shadow',
                                  not f.centered, -f.length, abs(f.position)))

    def place(code, at=(0, 0, 0), matrix=None, colour=4):
        kwargs = {'matrix': matrix} if matrix is not None else {}
        return Piece.place(code, colour=colour, position=Vector(*at), **kwargs)

    def aligned(moving, fixed, moving_kind, fixed_kind, axial_offset=0, roll=0):
        mf, ff = feature(moving, moving_kind), feature(fixed, fixed_kind)
        pose = snap_transform(mf, ff)
        # All selected moving pins/axles have their local axis along X.
        matrix = pose.matrix * rotation('x', roll)
        position = pose.position + ff.axis * axial_offset
        return [place(fixed, colour=14), place(moving, jsonable(position), matrix, 1)]

    beam_hole = feature('32523', 'pin_hole')
    assert abs(beam_hole.position) == 0 and abs(beam_hole.axis.y) == 1
    pin_pose = snap_transform(feature('2780', 'pin'), beam_hole)
    fixtures = {
        'axle-in-cross-hole': aligned('3705', '32064', 'axle', 'axle_hole'),
        'axle-in-cross-hole-roll-45': aligned('3705', '32064', 'axle', 'axle_hole', roll=45),
        'axle-in-round-hole': aligned('3705', '3700', 'axle', 'pin_hole'),
        'pin-in-cross-hole': aligned('2780', '32064', 'pin', 'axle_hole'),
        # 43093's round end occupies local X = -20..0; its axle end is X = 0..19.5.
        'axle-pin-round-end-in-hole': aligned('43093', '3700', 'axle', 'pin_hole', axial_offset=10),
        'pin-collar-inside-hole': aligned('2780', '32523', 'pin', 'pin_hole'),
        'pin-tip-touch-only': aligned('2780', '32523', 'pin', 'pin_hole', axial_offset=30),
        'pin-fully-separated': aligned('2780', '32523', 'pin', 'pin_hole', axial_offset=40),
    }
    for code in ('2780', '3673'):
        pose = snap_transform(feature(code, 'pin'), beam_hole)
        fixtures[f'two-beams-one-{code}'] = [
            place('32523', colour=14), place('32523', (0, 20, 0), colour=4),
            place(code, (0, 10, 0), pose.matrix, 1),
        ]
    fixtures['two-beams-two-pins'] = [
        *fixtures['two-beams-one-2780'],
        place('2780', (0, 10, 20), pin_pose.matrix, 1),
    ]

    # This reproduces the grid relationship in LEGO Education's notebook:
    # two plates between studded Technic bricks produce a 40-LDU hole pitch.
    # In the negative control, one brace end is aligned and the other misses.
    for gap, label in [(0, 'unspaced'), (16, 'two-plates')]:
        fixtures[f'system-technic-brace-{label}'] = [
            place('3701', colour=14), place('3701', (0, 24 + gap, 0), colour=14),
            place('32523', (0, 30, -20), rotation('x', 90), 4),
            place('3673', (0, 10, -10), rotation('y', 90), 1),
            place('3673', (0, 50, -10), rotation('y', 90), 1),
        ]
        if gap:
            fixtures[f'system-technic-brace-{label}'] += [
                place('3710', (0, 24, 0), colour=15),
                place('3710', (0, 32, 0), colour=15),
            ]

    reports = {}
    for name, pieces in fixtures.items():
        model = Model.from_pieces(pieces, name=f'{name}.ldr')
        (out / f'{name}.mpd').write_text(serialize_mpd(model))
        report = analyze_geometry(model, parts, contacts='all')
        reports[name] = {key: report[key] for key in (
            'complete', 'physical_validity', 'occurrence_count', 'contact_count',
            'contacts', 'confirmed_component_count', 'optimistic_component_count',
            'overlaps', 'connection_coverage', 'diagnostics',
        )}

    snap_cases = {}
    for moving, fixed in [('2780', '32523'), ('3705', '32064'), ('3705', '3700')]:
        model = Model.from_pieces([place(fixed), place(moving, (100, 0, 0))], name='snap.ldr')
        snap_cases[f'{moving}-to-{fixed}'] = snap_report(model, parts, 1, 0, limit=2)

    def connector_signature(code):
        return [{k: v for k, v in feature_record(f).items()
                 if k not in ('id', 'source')} for f in geometries[code].connections]

    def primary_pin_signature(code):
        return {k: v for k, v in feature_record(feature(code, 'pin')).items()
                if k not in ('id', 'source')}

    derived = {
        '3700_hole_centres': [jsonable(f.position) for f in geometries['3700'].connections
                             if str(f.kind) == 'pin_hole'],
        '32523_authored_hole_centres': sorted({tuple(jsonable(f.position))
            for f in geometries['32523'].connections
            if f.name == 'connhole' and str(f.source) == 'ldcad_shadow'}),
        'stacked_technic_brick_hole_pitch': 24,
        'stacked_with_two_plates_hole_pitch': 24 + 2 * 8,
        'three_hole_beam_end_hole_distance': 40,
    }

    evidence = {
        'purpose': 'Pre-implementation research; contact evidence is not a rigidity or buildability proof.',
        'pyldraw3_version': version('pyldraw3'),
        'reproduce': '.venv/bin/python docs/reports/technic-structure-probe.py',
        'measurements': measurements,
        'friction_and_smooth_pin_all_connector_signatures_equal':
            connector_signature('2780') == connector_signature('3673'),
        'friction_and_smooth_pin_primary_connector_signatures_equal':
            primary_pin_signature('2780') == primary_pin_signature('3673'),
        'derived_measurements': derived,
        'fixtures': reports,
        'snap_probes': snap_cases,
    }
    (out / 'evidence.json').write_text(json.dumps(evidence, indent=2, default=str) + '\n')
    summary = {
        'purpose': evidence['purpose'], 'pyldraw3_version': evidence['pyldraw3_version'],
        'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'reproduce': evidence['reproduce'], 'units': 'LDU',
        'raw_evidence': 'output/technic-research/evidence.json (generated, not committed)',
        'measurements': {code: {
            **{k: v for k, v in m.items() if k != 'features'},
            'feature_count': len(m['features']),
            'kinds': dict(Counter(f['kind'] for f in m['features'])),
            'sources': dict(Counter(f['source'] for f in m['features'])),
        } for code, m in measurements.items()},
        'derived_measurements': derived,
        'pin_profiles': {code: {
            'primary': primary_pin_signature(code),
            'raw_feature_count': len(measurements[code]['features']),
        } for code in ('2780', '3673')},
        'primary_pin_signatures_equal': evidence['friction_and_smooth_pin_primary_connector_signatures_equal'],
        'all_pin_signatures_equal': evidence['friction_and_smooth_pin_all_connector_signatures_equal'],
        'three_hole_beam_raw_features': measurements['32523']['features'],
        'fixtures': {name: {
            **{k: v for k, v in report.items() if k not in ('contacts', 'overlaps')},
            'contact_pairs': sorted({tuple(c['instances']) for c in report['contacts']}),
            'overlap_candidate_count': len(report['overlaps']),
        } for name, report in reports.items()},
        'snap_probes': {name: {
            'returned_candidates': len(report['candidates']),
            'first_candidate': {k: report['candidates'][0][k]
                for k in ('local_placement', 'contact_status', 'collision')}
                if report['candidates'] else None,
        } for name, report in snap_cases.items()},
    }
    discovery_path = out / 'structural-references.json'
    if discovery_path.exists():
        discovery = json.loads(discovery_path.read_text())
        summary['reference_discovery'] = {
            'query': discovery['query'], 'engine': discovery['engine'],
            'index_signature': discovery['index_signature'],
            'filters': discovery['filters'],
            'review_status': 'Research candidates, not approved structural recipes.',
            'results': [{
                **{key: row[key] for key in ('id', 'model', 'section', 'description', 'source_sha256')},
                'physical_placements': row['inventory']['physical_placements'],
                'physical_accounting_complete': row['inventory']['physical_accounting_complete'],
                'reachable': row['inventory']['reachable'],
            } for row in discovery['results']],
        }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, default=str) + '\n')
    for code, measurement in measurements.items():
        counts = Counter(f['kind'] for f in measurement['features'])
        print(code, measurement['description'], measurement['size'], measurement['coverage'], dict(counts))
    print('Friction/smooth main profiles equal:', evidence['friction_and_smooth_pin_primary_connector_signatures_equal'])
    for name, report in reports.items():
        print(name, 'contacts=', report['contact_count'], 'confirmed_groups=', report['confirmed_component_count'])
    print('Evidence:', out / 'evidence.json')


if __name__ == '__main__':
    main()
