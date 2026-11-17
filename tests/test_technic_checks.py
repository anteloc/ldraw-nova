"""Technic build checks and the kinematic graph, on small built models.

The mutation test is the gate from the plan: a correct gear train with a
pivoting lever passes clean, and each of five typical mistakes made to it must
produce a finding that names the part the mistake was made on.
"""
import copy

import numpy as np
import pytest

from ldraw_tools.builder import check_schema
from ldraw_tools.identity import Plan
from ldraw_tools.validation import validate_text
from ldraw_tools.workflow import build_checked, check_model

RAIL = dict(id='rail', ref='32524.dat', colour=71, at=[0, 0, 0], orient=dict(up='+X', x='+Z'))
OPTIONS = dict(detail='summary', contacts='auto', output_limit=200, pair_limit=200, offset=0, instance_limit=100000)


def shaft(axle, hole, gear, gear_hole, cap='32123a.dat'):
    """An axle in a rail hole, a bush outside, a gear inside and a half bush after the gear."""
    a = axle
    return [
        [dict(id=a, ref='3705.dat', colour=0, on=dict(to='rail', hole=hole, pin='shaft', end='-X', past=20))],
        [dict(id=f'{a}-bush', ref='3713.dat', colour=71, on=dict(to=a, hole='hole-0', pin='shaft', next_to='rail', side='-X'))],
        [dict(id=f'{a}-gear', ref=gear, colour=7, on=dict(to=a, hole=gear_hole, pin='shaft', next_to='rail', side='+X'))],
        [dict(id=f'{a}-cap', ref=cap, colour=71, on=dict(to=a, hole='hole-0', pin='shaft', next_to=f'{a}-gear', side='+X'))],
    ]


def plan(steps, mechanism=None):
    section = dict(name='m.ldr', description='test', steps=steps)
    if mechanism:
        section['mechanism'] = mechanism
    result = Plan(dict(version=1, author='tests', sections=[section]))
    check_schema(result)
    return result


def built(official, steps, mechanism=None):
    return build_checked(plan(steps, mechanism), official, **OPTIONS)


def codes(report):
    return {d['code'] for d in report['diagnostics']}


def named(report, code):
    return [p['path'] for d in report['diagnostics'] if d['code'] == code for p in d.get('placements', [])]


GEARS = [[RAIL], *shaft('input', 'hole-1', '3647.dat', 'hole-0'), *shaft('output', 'hole-3', '3648b.dat', 'hole-2')]
LEVER = [[dict(id='lever', ref='32316.dat', colour=4,
               join=dict(to='rail', holes={'hole-6': 'hole-0'}, side='+X', roll=90, pins='3673.dat'))]]
CONTRACT = dict(ground='rail', input='input', outputs=['output'], pivots=[['lever', 'rail']], dof=2)


def test_probe_defects_now_fail_the_build(official):
    beam = lambda name, at, **kw: dict(id=name, ref='32524.dat', colour=71, at=at, **kw)
    _, _, report = built(official, [[beam('a', [0, 0, 0]), beam('b', [0, 0, 0], yaw=90)]])
    assert not report['checks_passed'] and 'technic.cell_overlap' in codes(report)
    _, _, report = built(official, [[beam('a', [0, 0, 0]), beam('b', [0, 0, 130])]])
    assert not report['checks_passed'] and 'technic.cell_overlap' in codes(report)
    _, _, report = built(official, [[beam('a', [0, 0, 0]),
                                     dict(id='x', ref='3705.dat', colour=0, at=[0, 0, 10], orient=dict(up='-Z', x='+Y'))]])
    assert not report['checks_passed'] and 'technic.through_solid' in codes(report)
    _, _, report = built(official, [[beam('a', [0, 0, 0]), beam('b', [20, 0, 0])]])
    assert not codes(report) & {'technic.cell_overlap', 'technic.through_solid'}


def test_gear_train_is_clean_and_traced(official):
    _, _, report = built(official, GEARS + LEVER, CONTRACT)
    assert report['checks_passed'], report['diagnostics']
    assert not [c for c in codes(report) if c.startswith('technic.')]
    technic = report['geometry']['technic']
    assert technic['meshes'] == 1 and technic['gears'] == 2
    mechanism = report['mechanism']['m.ldr']
    assert mechanism['input_moves'] == {'input': True}
    assert mechanism['output_moves_with_input'] == {'output': True}
    assert mechanism['degrees_of_freedom'] == 2
    assert any('8:24' in mesh for mesh in mechanism['graph']['meshes'])


def test_gears_out_of_reach_do_not_mesh_and_the_contract_says_so(official):
    apart = [[RAIL], *shaft('input', 'hole-1', '3647.dat', 'hole-0'), *shaft('output', 'hole-4', '3648b.dat', 'hole-2')]
    _, _, report = built(official, apart, dict(ground='rail', input='input', outputs=['output']))
    assert not report['checks_passed']
    assert named(report, 'technic.mechanism_uncoupled') == ['output']


def test_gear_short_of_meshing_is_named(official):
    # A second beam beside the first, 2.5 LDU low: its gear meets the first gear's plane 42.5 LDU away.
    steps = [[RAIL, dict(RAIL, id='rail-2', at=[40, -2.5, 0])], *shaft('input', 'hole-1', '3647.dat', 'hole-0'),
             [dict(id='output', ref='3705.dat', colour=0, on=dict(to='rail-2', hole='hole-3', pin='shaft', end='-X', past=20))],
             [dict(id='output-gear', ref='3648b.dat', colour=7,
                   on=dict(to='output', hole='hole-2', pin='shaft', next_to='rail-2', side='-X'))]]
    _, _, report = built(official, steps)
    gap = [d for d in report['diagnostics'] if d['code'] == 'technic.gear_gap']
    assert gap and abs(gap[0]['off'] - 2.5) < 0.01
    assert {p['path'] for p in gap[0]['placements']} == {'input-gear', 'output-gear'}


def test_the_frame_is_what_carries_the_shafts_not_the_biggest_crank(official):
    # From a smoke-trial gearbox: the crank (arm, pin and two round grips) has as many members as the
    # two beams and more parts, but the beams carry both shafts. The 8-tooth gear must not be "locked".
    seat = lambda to, hole, pin, **kw: dict(to=to, hole=hole, pin=pin, **kw)
    beam = dict(ref='40490.dat', colour=71, orient=dict(up='+X', x='+Z'))
    steps = [[dict(beam, id='beam-a', at=[0, 0, 0]),
              dict(id='tie', ref='6558.dat', colour=1, on=seat('beam-a', 'hole-0', 'grip-0', side='+X')),
              dict(id='spacer', ref='18654.dat', colour=72, on=seat('tie', 'hole-0', 'grip-1')),
              dict(id='input', ref='32073.dat', colour=71, on=seat('beam-a', 'hole-5', 'shaft', end='-X', past=20)),
              dict(id='output', ref='3706.dat', colour=0, on=seat('beam-a', 'hole-3', 'shaft', end='-X', past=20)),
              dict(id='input-gear', ref='3647.dat', colour=72, on=seat('input', 'hole-0', 'shaft', next_to='beam-a', side='+X')),
              dict(id='output-gear', ref='3648b.dat', colour=19, on=seat('output', 'hole-2', 'shaft', next_to='beam-a', side='+X')),
              dict(beam, id='beam-b', on=seat('input', 'hole-5', 'shaft', next_to='input-gear', side='+X')),
              dict(id='bush-b', ref='3713.dat', colour=4, on=seat('input', 'hole-0', 'shaft', next_to='beam-b', side='+X')),
              dict(id='out-bush-a', ref='3713.dat', colour=4, on=seat('output', 'hole-0', 'shaft', next_to='beam-a', side='-X')),
              dict(id='out-bush-b', ref='3713.dat', colour=4, on=seat('output', 'hole-0', 'shaft', next_to='beam-b', side='+X')),
              dict(id='crank', ref='60483.dat', colour=4, on=seat('input', 'hole-0', 'shaft', next_to='beam-a', side='-X')),
              dict(id='handle', ref='6558.dat', colour=1, on=seat('crank', 'hole-1', 'grip-0', side='-X')),
              dict(id='grip-1', ref='18654.dat', colour=14, on=seat('handle', 'hole-0', 'grip-1')),
              dict(id='grip-2', ref='18654.dat', colour=14, on=seat('handle', 'hole-0', 'grip-2'))]]
    _, _, report = built(official, steps)
    assert 'technic.locked_shaft' not in codes(report), report['diagnostics']
    assert report['geometry']['technic']['meshes'] == 1


def test_loose_axle_open_pin_and_unbacked_worm(official):
    steps = [[RAIL],
             [dict(id='axle', ref='3706.dat', colour=0, on=dict(to='rail', hole='hole-3', pin='shaft', end='-X', past=20))],
             [dict(id='worm', ref='4716.dat', colour=7, on=dict(to='axle', hole='hole-0', pin='shaft', slide=60))],
             [dict(id='pin', ref='2780.dat', colour=0, on=dict(to='rail', hole='hole-0', pin='grip-0', side='-X'))]]
    _, _, report = built(official, steps)
    assert named(report, 'technic.loose_axle') == ['axle']
    assert named(report, 'technic.open_pin') == ['pin']
    assert named(report, 'technic.thrust_unbacked') == ['worm']
    backed = steps[:2] + [
        [dict(id='stop', ref='3713.dat', colour=71, on=dict(to='axle', hole='hole-0', pin='shaft', next_to='rail', side='-X'))],
        [dict(id='worm', ref='4716.dat', colour=7, on=dict(to='axle', hole='hole-0', pin='shaft', next_to='rail', side='+X'))],
        [dict(id='cap', ref='3713.dat', colour=71, on=dict(to='axle', hole='hole-0', pin='shaft', next_to='worm', side='+X'))]]
    _, _, report = built(official, backed)
    assert not codes(report) & {'technic.loose_axle', 'technic.thrust_unbacked', 'technic.open_pin'}


def _line(text, identity):
    lines = text.split('\r\n')
    marker = next(i for i, line in enumerate(lines) if line.startswith(f'0 // {identity}:'))
    return lines, marker + 1


def _moved(text, identity, delta=None, turn=None, delete=False):
    lines, index = _line(text, identity)
    if delete:
        del lines[index]
        return '\r\n'.join(lines)
    tokens = lines[index].split()
    position = np.array([float(v) for v in tokens[2:5]])
    matrix = np.array([float(v) for v in tokens[5:14]]).reshape(3, 3)
    if delta is not None:
        position = position + np.asarray(delta, float)
    if turn is not None:
        matrix = turn(matrix)
    numbers = [*position, *matrix.ravel()]
    tokens[2:14] = ['%g' % round(v, 9) for v in numbers]
    lines[index] = ' '.join(tokens)
    return '\r\n'.join(lines)


def _review(official, text):
    model, diagnostics = validate_text(text, official, name='m.ldr')
    return check_model(model, official, diagnostics, **OPTIONS)


def test_mutations_of_a_correct_mechanism_are_each_reported(official):
    text, _, base = built(official, GEARS + LEVER, CONTRACT)
    assert base['checks_passed']
    about_x = lambda m: np.array([[1, 0, 0], [0, np.cos(np.pi / 4), -np.sin(np.pi / 4)],
                                  [0, np.sin(np.pi / 4), np.cos(np.pi / 4)]]) @ m

    def instances(report, code):
        return {i for d in report['geometry']['diagnostics'] if d['code'] == code for i in d.get('instances', [])}

    order = {name: i for i, name in enumerate(
        line.split(':')[0].removeprefix('0 // ') for line in text.split('\r\n') if line.startswith('0 // '))}
    found = {}
    report = _review(official, _moved(text, 'output-gear', delta=[0, -5, 0]))
    found['gear moved 5 LDU'] = order['output-gear'] in instances(report, 'technic.gear_gap')
    report = _review(official, _moved(text, 'lever', delta=[0, 10, 0]))
    found['beam moved half a stud'] = order['lever'] in instances(report, 'technic.through_solid')
    report = _review(official, _moved(text, 'input-bush', delete=True))
    shifted = {k - (k > order['input-bush']) for k in [order['input']]}
    found['bush removed'] = bool(shifted & instances(report, 'technic.loose_axle'))
    report = _review(official, _moved(text, 'output', turn=about_x))
    found['axle turned 45 degrees'] = order['output'] in instances(report, 'technic.invalid_seating')
    friction = copy.deepcopy(LEVER)
    friction[0][0]['join']['pins'] = '2780.dat'
    _, _, report = built(official, GEARS + friction, CONTRACT)
    found['pivot pinned with friction pins'] = 'lever' in named(report, 'technic.pivot_locked')
    recall = sum(found.values()) / len(found)
    assert recall >= 0.9, found
