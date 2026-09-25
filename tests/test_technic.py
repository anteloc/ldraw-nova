import json

import pytest
from ldraw import Model, Piece, Vector

from ldraw_tools.builder import rotation
from ldraw_tools.common import get_parts
from ldraw_tools.connectivity import inspect_connections, snap_report, apply_snap
from ldraw_tools.connection_adapter import connection_contacts
from ldraw_tools.technic import registry, definition, managed
from ldraw_tools.technic_review import review_structure


def model(*placements):
    return Model.from_pieces([Piece.place(code, colour=4, position=Vector(*at), matrix=matrix)
                             for code, at, matrix in placements], name='structure.ldr')


I = rotation()
PIN_Y = rotation('z', 90)
AXLE_Z = rotation('y', -90)


def errors(report):
    return {d['code'] for d in report['diagnostics'] if d['severity'] == 'error'}


def test_registry_matches_geometry_and_removes_phantom_holes(official):
    assert all(definition(official.geometry(c)) for c in registry()['parts'])
    m = model(('32523', (0, 0, 0), I))
    inspection = inspect_connections(m, official)
    assert len(inspection.occurrences[0].connections) == 3
    assert all(managed(f) for f in inspection.occurrences[0].connections)
    assert definition(official.geometry('32064'))
    assert definition(official.geometry('4265c'))


@pytest.mark.parametrize('y', [0, 30])
def test_collar_in_bore_and_tip_touch_are_not_connections(official, y):
    m = model(('32523', (0, 0, 0), I), ('2780', (0, y, 0), PIN_Y))
    assert not connection_contacts(inspect_connections(m, official))
    assert 'technic.invalid_seating' in errors(review_structure(m, official))


def test_pin_snap_seats_a_grip_and_reports_friction(official):
    m = model(('32523', (0, 0, 0), I), ('2780', (100, 0, 0), I))
    snap = snap_report(m, official, 1, 0, limit=1)
    candidate = snap['candidates'][0]
    assert abs(candidate['local_placement']['at'][1]) == 10
    fitted = apply_snap(m, snap)
    report = review_structure(fitted, official)
    assert report['joint_count'] == 1 and report['joints'][0]['friction'] is True
    assert not errors(report)


def test_cross_axle_bearing_keyed_roll_and_wrong_family(official):
    bearing = model(('3700', (0, 0, 0), I), ('3705', (0, 10, 0), AXLE_Z))
    report = review_structure(bearing, official)
    assert report['joints'][0]['behavior'] == 'bearing'
    assert 'technic.bearing_rotation' in {d['code'] for d in report['diagnostics']}
    keyed = model(('32064a', (0, 0, 0), I), ('3705', (0, 10, 0), AXLE_Z))
    assert review_structure(keyed, official)['joints'][0]['behavior'] == 'keyed'
    rolled = model(('32064a', (0, 0, 0), I), ('3705', (0, 10, 0), AXLE_Z*rotation('x', 45)))
    assert 'technic.invalid_seating' in errors(review_structure(rolled, official))
    wrong = model(('32064a', (0, 0, 0), I), ('2780', (0, 10, 10), AXLE_Z))
    assert not review_structure(wrong, official)['joints']


def test_mixed_connector_ports(official):
    m = model(('3700', (0, 0, 0), I), ('43093', (0, 10, 10), AXLE_Z),
              ('32064a', (0, 0, 20), I))
    report = review_structure(m, official)
    assert {j['behavior'] for j in report['joints']} == {'pin', 'keyed'}
    assert not errors(report)


def test_thin_layers_fill_one_grip(official):
    # Thin beam holes have odd half-module Z offsets.
    thin = ('32063', (0, 5, 10), I)
    m = model(thin, ('2780', (0, 10, 0), PIN_Y))
    assert 'technic.incomplete_grip' in errors(review_structure(m, official))
    filled = model(thin, ('32063', (0, -5, 10), I), ('2780', (0, 10, 0), PIN_Y))
    assert not errors(review_structure(filled, official))


def test_occupied_spans_and_holes(official):
    m = model(('32523', (0, 0, 0), I), ('32523', (0, 0, 0), I), ('2780', (0, 10, 0), PIN_Y))
    assert 'technic.occupied_span' in errors(review_structure(m, official))
    doubled = model(('32523', (0, 0, 0), I), ('2780', (0, 10, 0), PIN_Y), ('2780', (0, 10, 0), PIN_Y))
    assert 'technic.occupied_hole' in errors(review_structure(doubled, official))


def test_axle_accepts_disjoint_bushes_and_requires_retention(official):
    m = model(('32064a', (0, 0, 0), I), ('3705', (0, 10, 0), AXLE_Z),
              ('3713', (0, 10, -20), I), ('3713', (0, 10, 20), I))
    report = review_structure(m, official)
    assert report['joint_count'] == 3
    assert 'technic.axial_retention' not in {d['code'] for d in report['diagnostics']}
    assert not errors(report)
    pending = model(('32064a', (0, 0, 0), I), ('3705', (0, 10, 0), AXLE_Z),
                    ('3713', (0, 10, -20), I), ('3713', (100, 10, 20), I))
    snap = snap_report(pending, official, 3, 1, limit=20)
    assert any(c['collision']['status'] != 'blocked' and c['local_placement']['at'][2] >= 20
               for c in snap['candidates'])


def test_connected_pivot_is_not_a_restrained_frame(official):
    placements = [('32523', (0, 0, 0), I), ('32523', (0, 20, 0), I), ('3673', (0, 10, 0), PIN_Y)]
    report = review_structure(model(*placements), official, contract={'version': 1, 'require_rigid': True})
    assert 'technic.structural_restraint' in errors(report)
    restrained = review_structure(model(*placements, ('2780', (0, 10, 20), PIN_Y)), official,
                                   contract={'version': 1, 'require_rigid': True})
    assert not errors(restrained) and len(restrained['restrained_groups']) == 1


def test_required_second_mount_and_contract_indices(official):
    m = model(('32523', (0, 0, 0), I), ('32523', (0, 20, 0), I), ('2780', (0, 10, 0), PIN_Y),
              ('2780', (0, 10, 40), PIN_Y))
    c = {'version': 1, 'required_joints': [{'between': [3, 1]}]}
    assert 'technic.missing_required_joint' in errors(review_structure(m, official, contract=c))
    with pytest.raises(ValueError, match='absent'):
        review_structure(m, official, contract={'version': 1, 'required_joints': [{'between': [0, 100]}]})
    with pytest.raises(ValueError, match='revision'):
        review_structure(m, official, contract={'version': 1, 'model_sha256': '0'*64})


def test_assembly_order_and_geometry_revision_are_explicit(official):
    from dataclasses import replace
    from ldraw_tools.builder import build_plan
    plan = dict(version=1, author='Tests', sections=[dict(name='main.ldr', description='Pin insertion order', steps=[
        [dict(id='beam', ref='32523.dat', colour=4, at=[0, 0, 0])],
        [dict(id='pin', ref='2780.dat', colour=0, at=[0, 10, 0], matrix=PIN_Y.rows)],
        [dict(id='second', ref='32523.dat', colour=4, at=[0, 20, 0])],
    ])])
    _, m, ds = build_plan(plan, official)
    contract = {'version': 1, 'assembly': [{'connector': 1, 'before': [2]}]}
    assert not errors(review_structure(m, official, contract=contract))
    contract['assembly'][0]['before'] = [0]
    assert 'technic.insertion_order' in errors(review_structure(m, official, contract=contract))
    g = official.geometry('32523')
    assert definition(replace(g, points=(*g.points, Vector(100, 0, 0)))) is None


@pytest.mark.parametrize('name,levels', [('reinforced-frame', 2), ('box-chassis', 2),
                                      ('frame-tower', 1), ('frame-tower', 3), ('service-platform', 2)])
def test_structural_recipes_meet_declared_mounts_and_geometry(official, name, levels):
    from ldraw_tools.technic_recipes import structure_plan
    from ldraw_tools.builder import build_plan
    from ldraw_tools.geometry import analyze_geometry
    plan, contract = structure_plan(name, levels=levels)
    _, m, diagnostics = build_plan(plan, official)
    assert not [d for d in diagnostics if d['severity']=='error']
    report = review_structure(m, official, contract=contract)
    assert report['checks_passed'] and len(report['restrained_groups']) == 1
    assert not [d for d in analyze_geometry(m, official)['diagnostics'] if d['severity']=='error']


def test_structural_discovery_uses_selected_content_not_parent_theme():
    from ldraw_tools.discovery import structural_candidate
    row = dict(kind='submodels', description='A static chassis frame', theme='Technic',
               parent_description='Working gearbox and engine mechanism')
    assert structural_candidate(row, {'bom': [{'description': 'Technic Beam 5'}]})
    assert not structural_candidate(row, {'bom': [{'description': 'Technic Gear 16 Tooth'}]})
    assert not structural_candidate(dict(row, description='Motor and gearbox'))
    assert structural_candidate({'kind': 'parts', 'part': '2780.dat'})
    assert not structural_candidate({'kind': 'parts', 'part': '3648.dat'})
