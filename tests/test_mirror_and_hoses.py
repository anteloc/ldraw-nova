"""Mirrored modules and the pneumatic hose aids."""
import numpy as np
import pytest

from ldraw_tools.builder import build_plan, check_schema
from ldraw_tools.flex_authoring import Endpoint
from ldraw_tools.flex_plan import default_lead, endpoint, feasibility, ports, route_checks
from ldraw_tools.identity import BuildError, Plan
from ldraw_tools.workflow import build_checked

ARM = dict(name='arm.ldr', description='Steering arm module', steps=[
    [dict(id='kingpin', ref='3705.dat', colour=0, at=[0, 0, 0], orient=dict(up='+X', x='+Y'))],
    [dict(id='arm', ref='32140.dat', colour=72, on=dict(to='kingpin', hole='hole-0', pin='shaft'))],
    [dict(id='pin', ref='2780.dat', colour=0, on=dict(to='arm', hole='hole-4', pin='grip-0', side='+Y'))]])


def plan(*placements, module=ARM):
    result = Plan(dict(version=1, author='tests', sections=[
        dict(name='m.ldr', description='mirror test', steps=[list(placements)]), module]))
    check_schema(result)
    return result


def test_mirrored_module_is_the_mirror_image_with_proper_rotations(official):
    text, _, report = build_checked(plan(dict(id='left', ref='arm.ldr', colour=16, at=[-60, 0, 0]),
                                         dict(id='right', ref='arm.ldr', colour=16, at=[60, 0, 0], mirror='x'),
                                         dict(id='spare', ref='arm.ldr', colour=16, at=[60, 0, 100], mirror='x')),
                                    official, detail='summary', contacts='auto')
    assert report['checks_passed']
    rows = {r['path']: r for r in report['source_map']}
    for name in ('arm', 'kingpin', 'pin'):
        left, right = np.array(rows[f'left/{name}']['position']), np.array(rows[f'right/{name}']['position'])
        assert np.allclose(right, left * [-1, 1, 1])
        assert np.isclose(np.linalg.det(rows[f'right/{name}']['matrix']), 1)
    assert text.count('0 FILE arm-mirror-x.ldr') == 1


def test_a_worm_has_a_handedness_and_is_not_mirrored(official):
    worm = dict(name='worm.ldr', description='worm', steps=[[dict(id='worm', ref='4716.dat', colour=7, at=[0, 0, 0])]])
    with pytest.raises(BuildError, match='no plane of symmetry'):
        build_plan(plan(dict(id='w', ref='worm.ldr', colour=16, at=[0, 0, 0], mirror='x'), module=worm), official)


def test_mirror_needs_a_section(official):
    with pytest.raises(BuildError, match='mirror applies to a section'):
        build_plan(plan(dict(id='beam', ref='32524.dat', colour=71, at=[0, 0, 0], mirror='x')), official)


def test_every_pneumatic_part_has_named_nozzles(official):
    assert ports(official, '4694c01-f1') == {'upper': dict(at=[10, 15, 0], outward=[1, 0, 0]),
                                             'inlet': dict(at=[10, 26, 6], outward=[1, 0, 0]),
                                             'lower': dict(at=[10, 37, 0], outward=[1, 0, 0])}
    tee = ports(official, '4697b')
    assert set(tee) == {'nozzle-0', 'nozzle-1', 'nozzle-2'} and tee['nozzle-2']['outward'] == [0.0, 1.0, 0.0]


def test_pneumatic_hoses_have_floors_a_plan_cannot_lower():
    assert route_checks('TECHNIC_PNEUMATIC_HOSE_BEVELED', None) == dict(min_radius=15, min_separation=10)
    assert route_checks('TECHNIC_PNEUMATIC_HOSE_BEVELED', {'min_radius': 20})['min_radius'] == 20
    with pytest.raises(ValueError, match='below the 15 LDU pneumatic hose floor'):
        route_checks('TECHNIC_PNEUMATIC_HOSE_BEVELED', {'min_radius': 8})
    assert route_checks('STRING_BAND', {'min_radius': 2}) == {'min_radius': 2}


def test_pneumatic_fittings_get_a_straight_lead_unless_the_plan_sets_one(official):
    assert default_lead('TECHNIC_PNEUMATIC_HOSE_BEVELED') == 22 and default_lead('STRING_BAND') == 0

    class Poses:
        def resolve(self, section, name):
            return dict(ref='4694c01-f1.dat', at=[0, 0, 0], matrix=np.eye(3).tolist())

    assert endpoint(dict(part='valve', port='inlet'), Poses(), 'm.ldr', official, lead=22).lead == 22
    assert endpoint(dict(part='valve', port='inlet', lead=6), Poses(), 'm.ldr', official, lead=22).lead == 6


def test_fittings_that_face_away_or_sit_too_close_are_warned_early():
    start = Endpoint([0, 0, 0], [0, 0, -1])
    behind = Endpoint([0, 0, 100], [0, 0, 1])
    assert [r['code'] for r in feasibility(start, behind, dict(min_radius=15))] == ['flex.ports_face_away']
    close = Endpoint([20, 0, 0], [-1, 0, 0])
    assert 'flex.ports_too_close' in [r['code'] for r in feasibility(Endpoint([0, 0, 0], [1, 0, 0]), close, dict(min_radius=15))]
    assert not feasibility(Endpoint([0, 0, 0], [1, 0, 0]), Endpoint([200, 0, 0], [-1, 0, 0]), dict(min_radius=15))
