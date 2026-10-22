"""Keep the Halcyon's SNOT modules seated on the stud faces they were designed for."""
import copy
import importlib.util
import json

import numpy as np
import pytest

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT
from ldraw_tools.geometry import analyze_geometry

EXAMPLE = ROOT / 'examples/snot/halcyon'

# (module section, mount section, mount part): seated stud/socket contacts. The intake, exhaust
# and cannon sections are placed twice, so their counts cover both placements.
SNOT_INTERFACES = {
    ('halcyon-flank-s.ldr', 'halcyon-hull.ldr', '30414.dat'): 12,
    ('halcyon-flank-p.ldr', 'halcyon-hull.ldr', '30414.dat'): 12,
    ('halcyon-pod-panel-s.ldr', 'halcyon-hull.ldr', '30414.dat'): 8,
    ('halcyon-pod-panel-p.ldr', 'halcyon-hull.ldr', '30414.dat'): 8,
    ('halcyon-intake.ldr', 'halcyon-hull.ldr', '30414.dat'): 8,
    ('halcyon-exhaust.ldr', 'halcyon-hull.ldr', '30414.dat'): 8,
    ('halcyon-aft-cap.ldr', 'halcyon-hull.ldr', '30414.dat'): 4,
    ('halcyon-cannon.ldr', 'halcyon-wing-s.ldr', '87087.dat'): 1,
    ('halcyon-cannon.ldr', 'halcyon-wing-p.ldr', '87087.dat'): 1,
    ('halcyon-cockpit.ldr', 'halcyon-hull.ldr', '3032.dat'): 4,
}


def plan():
    return json.loads((EXAMPLE / 'halcyon.plan.json').read_text())


def interface_contacts(report):
    instances = {i['index']: i for i in report['instances']}
    found = {key: [] for key in SNOT_INTERFACES}
    for contact in report['contacts']:
        pair = [instances[i] for i in contact['instances']]
        for module, mount, part in SNOT_INTERFACES:
            for a, b in (pair, pair[::-1]):
                if a['section'] == module and (b['section'], b['part']) == (mount, part):
                    found[module, mount, part].append(contact)
    return found


def analyze(official, source):
    text, model, diagnostics = build_plan(source, official)
    return text, diagnostics, analyze_geometry(model, official, contacts='all', output_limit=5000)


@pytest.fixture(scope='module')
def reviewed(official):
    return analyze(official, load_plan(EXAMPLE / 'halcyon.plan.json'))


def test_generator_reproduces_committed_plan():
    spec = importlib.util.spec_from_file_location('halcyon_generate', EXAMPLE / 'generate.py')
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    assert generator.build() == plan()


def test_every_placement_is_a_proper_rotation():
    for section in plan()['sections']:
        for step in section['steps']:
            for entry in step:
                m = np.array(entry.get('matrix', np.eye(3)))
                assert np.allclose(m.T @ m, np.eye(3)) and np.isclose(np.linalg.det(m), 1), entry['id']


def test_reproduces_reviewed_model_as_one_connected_group(reviewed):
    text, diagnostics, report = reviewed
    assert not diagnostics
    assert text.encode() == (EXAMPLE / 'halcyon.mpd').read_bytes()
    assert report['complete']
    assert report['occurrence_count'] == 195
    assert report['optimistic_component_count'] == 1
    assert not [d for d in report['diagnostics'] if d['severity'] == 'error']


def test_snot_modules_seat_exactly_on_their_stud_faces(reviewed):
    found = interface_contacts(reviewed[2])
    for key, expected in SNOT_INTERFACES.items():
        assert len(found[key]) == expected, key
        assert all(c['residual']['distance'] < 1e-6 and c['residual']['alignment'] > 0.999999
                   for c in found[key]), key


def test_a_flank_moved_one_ldu_outboard_is_detected(official):
    moved = copy.deepcopy(plan())
    flank = next(e for step in moved['sections'][0]['steps'] for e in step if e['id'] == 'flank-s')
    flank['at'][0] += 1
    _, diagnostics, report = analyze(official, moved)
    assert not diagnostics
    assert not interface_contacts(report)['halcyon-flank-s.ldr', 'halcyon-hull.ldr', '30414.dat']
    assert report['optimistic_component_count'] == 2
