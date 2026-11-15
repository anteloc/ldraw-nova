"""Connector placement: orient, on {to, face, stud, socket, roll}, grids and facts.

The parrot head regression replaces two hand-derived SNOT placements (their
matrices and stud - R * socket origins) with connector seats and requires the
same MPD bytes.
"""
import copy
import json
from pathlib import Path

import jsonschema
import numpy as np
import pytest

from ldraw_tools.builder import build_plan, check_schema, load_plan
from ldraw_tools.placement import facts, orient
from ldraw_tools.report import schema_diagnostic

ROOT = Path(__file__).resolve().parents[1]


def placement(plan, identity):
    return next(e for s in plan['sections'] for step in s['steps'] for e in step if e['id'] == identity)


def test_orient_points_studs_and_keeps_x_when_possible():
    forward = orient('-Z')
    assert np.allclose(forward @ [0, -1, 0], [0, 0, -1]) and np.allclose(forward @ [1, 0, 0], [1, 0, 0])
    side = orient('+X')
    assert np.allclose(side @ [0, -1, 0], [1, 0, 0]) and np.allclose(side @ [1, 0, 0], [0, 0, 1])
    assert np.isclose(np.linalg.det(orient('+X', '-Y')), 1)
    with pytest.raises(ValueError, match='parallel'):
        orient('up', 'down')


def test_part_facts_group_studs_and_sockets_by_face(official):
    side = facts(official, '87087')
    assert side['studs'] == {'-Y': [[0.0, 0.0, 0.0]], '-Z': [[0.0, 10.0, -10.0]]}
    assert side['sockets'] == {'+Y': [[0.0, 24.0, 0.0]]}
    assert side['origin'] == 'at the body top, centred' and side['body']['size'] == [20.0, 24.0, 20.0]


def test_connector_seats_reproduce_hand_derived_parrot_snot(official):
    source = load_plan(ROOT / 'examples/parrot/head.plan.json')
    expected, _, _ = build_plan(source, official)
    seated = copy.deepcopy(source)
    for identity, face in (('beak-lower-jumper', '+X'), ('rear-plate', '-X')):
        entry = placement(seated, identity)
        entry.pop('at'), entry.pop('matrix')
        entry['on'] = {'to': 'core-left', 'face': face, 'stud': 1, 'socket': 0, 'roll': -90}
    context = {}
    text, _, diagnostics = build_plan(seated, official, context=context)
    assert text == expected
    assert not [d for d in diagnostics if d['severity'] == 'error']
    seats = {s['placement']: s for s in context['seats']}
    assert seats['beak-lower-jumper']['mated'] == 1 and seats['beak-lower-jumper']['stud'] == [20.0, -10.0, -10.0]


def test_seat_on_a_part_inside_a_module_and_explicit_orient(official):
    plan = dict(version=1, author='Test', sections=[
        dict(name='scene.ldr', description='Scene', steps=[[
            dict(id='core', ref='core.ldr', colour=4, at=[100, 0, 0], yaw=90)], [
            dict(id='tile', ref='3070b.dat', colour=15, on=dict(to='core/side', face='-Z'))]]),
        dict(name='core.ldr', description='Core', steps=[[dict(id='side', ref='87087.dat', colour=16, at=[0, 0, 0])]])])
    _, model, diagnostics = build_plan(plan, official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    tile = model.pieces[1]
    # yaw 90 turns the brick's -Z face toward -X; the tile sits outside it.
    assert np.allclose([tile.position.x, tile.position.y, tile.position.z], [82, 10, 0])
    assert np.allclose(np.array(tile.matrix.rows) @ [0, -1, 0], [-1, 0, 0])
    wrong = copy.deepcopy(plan)
    wrong['sections'][0]['steps'][1][0]['orient'] = {'up': '+X'}
    with pytest.raises(ValueError, match='socket must face the stud'):
        build_plan(wrong, official)


def test_missing_face_lists_available_faces(official):
    plan = dict(version=1, author='Test', sections=[dict(name='a.ldr', description='A', steps=[[
        dict(id='brick', ref='3001.dat', colour=4, at=[0, 0, 0])], [
        dict(id='tile', ref='3070b.dat', colour=15, on=dict(to='brick', face='+X'))]])])
    with pytest.raises(ValueError, match=r'no studs facing \+X; studs by face: -Y: 8'):
        build_plan(plan, official)


def test_grid_repeat_ids_and_offsets(parts):
    plan = dict(version=1, author='Test', sections=[dict(name='a.ldr', description='A', steps=[[
        dict(id='tile', ref='3022.dat', colour=4, at=[0, 0, 0],
             repeat=dict(count=[2, 3], step=[[40, 0, 0], [0, 0, 40]]))]])])
    _, model, _ = build_plan(plan, parts)
    positions = sorted((p.position.x, p.position.z) for p in model.pieces)
    assert positions == [(x, z) for x in (0, 40) for z in (0, 40, 80)]
    bad = copy.deepcopy(plan)
    bad['sections'][0]['steps'][0][0]['repeat']['step'] = [40, 0, 0]
    with pytest.raises(ValueError, match='two step vectors'):
        build_plan(bad, parts)


def test_schema_failure_explains_mixed_modes_with_pointer():
    plan = dict(version=1, author='Test', sections=[dict(name='a.ldr', description='A', steps=[[
        dict(id='x', ref='3001.dat', colour=4, at=[0, 0, 0], on='base')]])])
    with pytest.raises(jsonschema.ValidationError) as caught:
        check_schema(plan)
    diagnostic = schema_diagnostic(caught.value, 'plan.json')
    assert diagnostic['pointer'] == '/sections/0/steps/0/0'
    assert 'mixes position modes at, on' in diagnostic['message'] and len(json.dumps(diagnostic)) < 600


def test_default_roll_covers_the_most_studs_and_face_defaults_to_top(official):
    plan = dict(version=1, author='Test', sections=[dict(name='a.ldr', description='A', steps=[[
        dict(id='core', ref='30414.dat', colour=71, at=[0, -24, 0], yaw=90)], [
        dict(id='panel', ref='3710.dat', colour=15, on=dict(to='core', face='-Z', stud=0, socket=0)),
        dict(id='cap', ref='3710.dat', colour=4, on=dict(to='core'))]])])
    context = {}
    _, model, diagnostics = build_plan(plan, official, context=context)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    seats = {s['placement']: s for s in context['seats']}
    assert seats['panel']['mated'] == 4 and seats['panel']['stud_face'] == '-Z'
    assert seats['cap']['mated'] == 4 and seats['cap']['stud_face'] == '-Y'


def test_roll_on_a_top_stud_matches_yaw_for_the_cat_ear(official):
    source = load_plan(ROOT / 'examples/cat/head.plan.json')
    ear = placement(source, 'left-ear')
    seated = copy.deepcopy(source)
    entry = placement(seated, 'left-ear')
    entry.pop('at'), entry.pop('matrix')
    entry['on'] = {'to': 'face-base', 'stud': 1, 'socket': 1, 'roll': 45}
    _, model, _ = build_plan(seated, official)
    piece = next(p for p in model.pieces if p.reference.casefold() == '35480.dat' and p.position.x < 0)
    assert np.allclose([piece.position.x, piece.position.y, piece.position.z], ear['at'], atol=1e-8)
    assert np.allclose(piece.matrix.rows, ear['matrix'], atol=1e-8)
