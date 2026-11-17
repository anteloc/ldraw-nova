"""Derived Technic ports, the seats that use them, and the faster inspection.

The reviewed registry is the oracle for the derivation: every hand-measured
port must come out of the shadow metadata at the same place, kind and length.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from ldraw_tools import technic_ports
from ldraw_tools.builder import build_plan, check_schema
from ldraw_tools.common import DATA
from ldraw_tools.identity import BuildError, Plan
from ldraw_tools.placement import facts, port_runs
from ldraw_tools.technic import registry

ROOT = Path(__file__).resolve().parents[1]
RAIL = dict(id='rail', ref='32524.dat', colour=71, at=[0, 0, 0], orient=dict(up='+X', x='+Z'))


def build(official, *steps):
    plan = Plan(dict(version=1, author='tests', sections=[dict(name='m.ldr', description='test', steps=list(steps))]))
    check_schema(plan)
    context = {}
    text, model, diagnostics = build_plan(plan, official, context=context)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    rows = {}
    pieces = [line.split() for line in text.splitlines() if line.startswith('1 ')]
    names = [name for name, record in context['identity'].entries['m.ldr'].items() if record['piece'] is not None]
    for name, piece in zip(names, pieces):
        rows[name] = [float(v) for v in piece[2:5]]
    return rows


def test_derivation_reproduces_every_reviewed_port(official):
    reviewed = json.loads((DATA / 'technic-parts.json').read_text())['parts']
    missing = []
    for code, entry in reviewed.items():
        geometry = official.geometry(code)
        derived = technic_ports.entry(code, geometry.description, geometry.connections)['ports']
        for port in entry['ports']:
            if port['kind'] not in technic_ports.MECHANICAL:
                continue
            if not any(d['kind'] == port['kind'] and np.linalg.norm(np.subtract(d['at'], port['at'])) < 0.5
                       and abs(abs(np.dot(d['axis'], port['axis'])) - 1) < 1e-3 and abs(d['length'] - port['length']) <= 0.5
                       for d in derived):
                missing.append((code, port['id']))
    assert not missing


def test_generated_table_matches_the_installed_metadata(official):
    table = json.loads((DATA / 'technic-ports.json').read_text())
    sample = ['40490', '3648b', '32140', '87083', '32054', '4716', '26287', '64782', '15100', '42003']
    for code in sample:
        geometry = official.geometry(code)
        fresh = technic_ports.entry(code, geometry.description, geometry.connections)
        saved = dict(table['parts'][code])
        withheld = {p['id'] for p in saved.pop('withheld', [])}
        fresh['ports'] = sorted(fresh['ports'], key=lambda p: p['id'])
        saved['ports'] = sorted(saved['ports'] + [p for p in table['parts'][code].get('withheld', [])], key=lambda p: p['id'])
        if withheld:
            saved['role'] = fresh['role']
        assert fresh == saved, code


def test_reviewed_parts_override_and_new_parts_are_listed(official):
    parts = registry()['parts']
    assert 'geometry_sha256' in parts['32523'] and parts['40490']['source'] == 'shadow'
    assert parts['3648b']['role'] == 'gear' and parts['87083']['ports'][0]['stops'] == ['+']
    assert [p['kind'] for p in parts['43093']['ports']] == ['pin', 'axle']
    described = facts(official, '40490')
    assert described['technic_ports'] == {
        'hole-0..hole-8': 'pin_hole axis +Y length 20.0, at [0.0, 0.0, -80.0] then every [0.0, 0.0, 20.0]'}


def test_port_runs_keep_irregular_ports_apart():
    ports = [dict(id='hole-0', kind='axle_hole', at=[0, 0, 0], axis=[0, 1, 0], length=20),
             *[dict(id=f'hole-{i}', kind='pin_hole', at=[0, 0, 20 * i], axis=[0, 1, 0], length=20) for i in (1, 2, 3)],
             dict(id='hole-4', kind='pin_hole', at=[20, 0, 60], axis=[0, 1, 0], length=20)]
    runs = port_runs(ports)
    assert list(runs) == ['hole-0', 'hole-1..hole-3', 'hole-4']


def test_axle_and_gear_seats_need_no_arithmetic(official):
    rows = build(official, [RAIL],
                 [dict(id='axle', ref='3706.dat', colour=0, on=dict(to='rail', hole='hole-3', pin='shaft', end='-X', past=20))],
                 [dict(id='stop', ref='3713.dat', colour=71, on=dict(to='axle', hole='hole-0', pin='shaft', next_to='rail', side='-X'))],
                 [dict(id='gear', ref='3648b.dat', colour=7, on=dict(to='axle', hole='hole-2', pin='shaft', next_to='rail', side='+X'))],
                 [dict(id='cap', ref='3713.dat', colour=71, on=dict(to='axle', hole='hole-0', pin='shaft', next_to='gear', side='+X'))])
    # The 6-long axle starts 20 LDU outside the rail; the stack is flush on both sides of it.
    assert rows['axle'] == [30, 0, 0] and rows['stop'] == [-20, 0, 0] and rows['gear'] == [20, 0, 0] and rows['cap'] == [40, 0, 0]


def test_pin_side_chooses_where_the_free_grip_goes(official):
    for side, x in (('+X', 10), ('-X', -10)):
        rows = build(official, [RAIL], [dict(id='pin', ref='2780.dat', colour=0,
                                             on=dict(to='rail', hole='hole-0', pin='grip-0', side=side))])
        assert rows['pin'] == [x, 60, 0]


def test_join_lays_a_beam_on_matching_holes_and_inserts_pins(official):
    rows = build(official, [RAIL], [dict(id='lap', ref='32316.dat', colour=72,
                                         join=dict(to='rail', holes={'hole-0': 'hole-0', 'hole-1': 'hole-1'}, side='+X'))])
    assert rows['lap'] == [20, 20, 0]
    assert rows['lap-pin-0'] == [10, 60, 0] and rows['lap-pin-1'] == [10, 40, 0]
    bent = build(official, [RAIL], [dict(id='ell', ref='32140.dat', colour=4,
                                         join=dict(to='rail', holes={'hole-3': 'hole-0'}, side='-X', pins='43093'))])
    assert bent['ell'] == [-20, 0, 0] and bent['ell-pin-0'] == [-10, 0, 0]


def test_join_places_a_module_by_a_hole_of_one_of_its_parts(official):
    module = dict(name='arm.ldr', description='arm', steps=[[dict(id='beam', ref='32316.dat', colour=4, at=[0, 0, 0])]])
    plan = Plan(dict(version=1, author='tests', sections=[
        dict(name='m.ldr', description='test', steps=[[RAIL], [dict(
            id='arm', ref='arm.ldr', colour=4,
            join=dict(to='rail', holes={'hole-2': 'beam/hole-0', 'hole-3': 'beam/hole-1'}, side='+X'))]]), module]))
    check_schema(plan)
    text, _, diagnostics = build_plan(plan, official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    placed = [line for line in text.splitlines() if line.startswith('1 ')]
    assert sum(line.endswith('2780.dat') for line in placed) == 2
    assert '1 4 20 -20 0 0 1 0 0 0 -1 -1 0 0 arm.ldr' in placed


@pytest.mark.parametrize('join, message', [
    (dict(to='rail', holes={'hole-0': 'hole-0'}, side='+Z'), 'must run along the hole axis: use -X or \\+X'),
    (dict(to='rail', holes={'hole-0': 'hole-0', 'hole-2': 'hole-1'}, side='+X'), '40.0 LDU apart, but .* are 20.0'),
    (dict(to='rail', holes={'hole-0': 'hole-9'}, side='+X'), 'has no port .hole-9.; ports: hole-0'),
])
def test_join_errors_name_the_fix(official, join, message):
    with pytest.raises(BuildError, match=message):
        build(official, [RAIL], [dict(id='lap', ref='32316.dat', colour=72, join=join)])


def test_wrong_connector_for_an_axle_hole_is_explained(official):
    with pytest.raises(BuildError, match='a pin needs a pin hole, an axle end an axle hole'):
        build(official, [RAIL], [dict(id='ell', ref='32140.dat', colour=4,
                                      join=dict(to='rail', holes={'hole-3': 'hole-0'}, side='-X'))])


def test_fast_bounds_are_bit_identical_to_the_library_loop(official):
    import ldraw.inspection as inspection
    from ldraw import Matrix, Vector
    from ldraw_tools import connection_adapter
    from ldraw_tools.placement import about, orient
    assert inspection.transformed_bounds is connection_adapter.transformed_bounds
    library = inspection.library_transformed_bounds
    turns = [np.eye(3), orient('-Z'), about('+Y', 45), about([1, 2, 3], 61.3)]
    for code in ('3001', '32278', '2780'):
        points = official.geometry(code).points
        for turn in turns:
            pose = dict(position=Vector(12.5, -40, 7.5), matrix=Matrix(np.round(turn, 12).tolist()))
            a, b = library(points, **pose), connection_adapter.transformed_bounds(points, **pose)
            assert (a.min.x, a.min.y, a.min.z, a.max.x, a.max.y, a.max.z) == (b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z)


def test_document_overlay_reuses_library_geometry_but_not_embedded_parts(official, tmp_path):
    import ldraw.part_geometry as geometry
    from ldraw_tools.document import parse_source, physical_context
    text = ('0 FILE main.ldr\n0 Main\n0 Name: main.ldr\n0 Author: Tests\n0 !LDRAW_ORG Model\n'
            '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3004.dat\n1 4 0 -24 0 1 0 0 0 1 0 0 0 1 custom-part.dat\n0 NOFILE\n'
            '0 FILE custom-part.dat\n0 Custom\n0 Name: custom-part.dat\n0 Author: Tests\n0 !LDRAW_ORG Unofficial_Part\n'
            '1 16 0 0 0 1 0 0 0 1 0 0 0 1 3005.dat\n0 NOFILE\n')
    source = tmp_path / 'main.mpd'
    source.write_text(text)
    model = parse_source(source)
    _, overlay = physical_context(model, official)
    assert overlay is not official
    overlay.geometry('3004')
    overlay.geometry('custom-part')
    library = geometry._cache_for(official)
    assert '3004' in library and 'custom-part' not in library
    assert geometry._cache_for(overlay).local('custom-part') is not None
