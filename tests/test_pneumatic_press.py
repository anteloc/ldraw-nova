"""The pneumatic press's hoses must be seated, smooth and clear; its rigid joints must line up."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

from ldraw_tools import flex
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.collision import oriented_box
from ldraw_tools.common import ROOT, jsonable
from ldraw_tools.connectivity import inspect_connections
from ldraw_tools.geometry import analyze_geometry

EXAMPLE = ROOT / 'examples/flex/pneumatic-press'
TUBE_RADIUS = 5            # LS23 cross-section; LS22 end sleeves are r=6 and 16 LDU long
MIN_BEND_RADIUS = 15
END_ZONE = 30              # hoses leave the valve side by side; spacing there is set by its nozzles


def generator():
    spec = importlib.util.spec_from_file_location('press_generate', EXAMPLE / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def posed_hoses(text):
    """{posed part: [(position, matrix, ref)]} in file order, which is the generator's HOSES order."""
    parts, current = {}, None
    for line in text.replace('\r', '').splitlines():
        if line.startswith('0 FILE '):
            current = line[7:].strip() if '-flex-' in line else None
            if current:
                parts[current] = []
        elif current and line.startswith('1 '):
            f = line.split()
            parts[current].append((np.array(f[2:5], float), np.array(f[5:14], float).reshape(3, 3), f[14]))
    return [parts[k] for k in sorted(parts)]


def centreline(segments):
    points = np.array([p for p, _, _ in segments])
    keep = np.r_[True, np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-6]
    return points[keep]


@pytest.fixture(scope='module')
def built(official):
    text, model, diagnostics = build_plan(load_plan(EXAMPLE / 'press.plan.json'), official)
    return text, model, diagnostics, analyze_geometry(model, official, contacts='all', output_limit=5000)


def test_generator_reproduces_plan_and_constraints(tmp_path):
    g = generator()
    plan, hoses = tmp_path / 'press.plan.json', tmp_path / 'hoses.ldr'
    subprocess.run([sys.executable, str(EXAMPLE / 'generate.py'), '--output', str(plan), '--hoses', str(hoses)],
                   check=True, capture_output=True)
    assert plan.read_text() == (EXAMPLE / 'press.plan.json').read_text()
    assert hoses.read_bytes() == (EXAMPLE / 'hoses.ldr').read_bytes() == g.hose_source().encode()


def test_hose_asset_regenerates_byte_for_byte(official, tmp_path):
    pytest.importorskip('lsynth_nova', reason='Optional LSynth integration: ./setup.sh --with-lsynth')
    out = tmp_path / 'hoses.mpd'
    flex.build(EXAMPLE / 'hoses.ldr', out, official, namespace='press-hoses')
    assert out.read_bytes() == (EXAMPLE / 'hoses.mpd').read_bytes()


def test_build_matches_reviewed_model_and_groups(built):
    text, _, diagnostics, report = built
    assert not [d for d in diagnostics if d['severity'] == 'error']
    assert text.encode() == (EXAMPLE / 'press.mpd').read_bytes()
    assert report['occurrence_count'] == 41
    instances = {i['index']: i['part'] for i in report['instances']}
    singles = sorted(instances[g[0]] for g in report['optimistic_components'] if len(g) == 1)
    # One rigid structure; posed hoses carry no connectors; the rest are documented checker gaps below.
    assert report['optimistic_component_count'] == 7
    assert singles == ['2797c01-f1.dat', '74981-f2.dat', 'press-hoses-flex-01.dat',
                       'press-hoses-flex-02.dat', 'press-hoses-flex-03.dat']


def test_unmatched_rigid_joints_are_exactly_aligned(built, official):
    """The checker leaves the cylinder's connholes and the pump's base sockets unmatched; check them here."""
    g = generator()
    _, model, _, _ = built
    occurrences = inspect_connections(model, official).occurrences
    by_part = {}
    for o in occurrences:
        by_part.setdefault(o.occurrence.part_code, []).append(o)
    (cylinder,) = by_part['74981-f2']
    vec = lambda v: np.array(jsonable(v), float)
    holes = [f for f in cylinder.connections if str(f.kind) == 'pin_hole' and abs(vec(f.axis)[1]) < 1e-9]
    # 3673 is 40 LDU long about its origin along local X; read centre and axis from each placement.
    pins = [(vec(o.occurrence.position), np.array(o.occurrence.matrix.rows, float)[:, 0]) for o in by_part['3673']]
    assert len(holes) == len(pins) == 2                                    # mount ring and rod-end ring
    for hole in holes:
        h, ha = vec(hole.position), vec(hole.axis)
        p, pa = min(pins, key=lambda pin: np.linalg.norm(pin[0] - h))
        assert abs(abs(ha @ pa) - 1) < 1e-9
        assert np.linalg.norm((p - h) - ((p - h) @ ha) * ha) < 1e-9       # coaxial
        assert abs((p - h) @ ha) == pytest.approx(10)                      # pin half fills the 20 LDU ring
    (pump,) = by_part['2797c01-f1']
    sockets = [vec(f.position) for f in pump.connections if str(f.kind) == 'pin_hole' and abs(vec(f.axis)[1]) == 1]
    studs = [vec(f.position) for o in by_part['92438'] + by_part['3035'] for f in o.connections if str(f.kind) == 'stud']
    assert len(sockets) == 4
    for socket in sockets:
        assert min(np.linalg.norm(s - socket) for s in studs) < 1e-9
    assert g.PUMP[1] == -14


def test_hose_sleeves_sit_coaxially_on_their_nozzles():
    g = generator()
    hoses = posed_hoses((EXAMPLE / 'hoses.mpd').read_text())
    assert len(hoses) == len(g.HOSES)
    for segments, (_, _, start, end, _) in zip(hoses, g.HOSES):
        for (p, m, ref), name in ((segments[0], start), (segments[-1], end)):
            base, axis = g.nozzle(name)
            y = m[:, 1] / np.linalg.norm(m[:, 1])
            rel = p - base
            assert ref.endswith('ls22.dat'), name
            assert abs(y @ axis) == pytest.approx(1, abs=1e-6), name
            assert np.linalg.norm(rel - (rel @ axis) * axis) < 1e-6, name
            assert rel @ axis == pytest.approx(16, abs=1e-6), name           # sleeve covers the whole nozzle


def test_hoses_are_smooth_separated_and_clear_of_parts(built, official):
    _, model, _, _ = built
    hoses = [centreline(s) for s in posed_hoses((EXAMPLE / 'hoses.mpd').read_text())]
    for points in hoses:
        chords = np.diff(points, axis=0)
        lengths = np.linalg.norm(chords, axis=1)
        units = chords / lengths[:, None]
        turn = np.arccos(np.clip((units[1:] * units[:-1]).sum(1), -1, 1))
        radius = np.where(turn > 1e-9, (lengths[1:] + lengths[:-1]) / 2 / np.maximum(turn, 1e-12), np.inf)
        assert radius.min() >= MIN_BEND_RADIUS
    inner = []
    for points in hoses:
        run = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
        inner.append(points[(run > END_ZONE) & (run < run[-1] - END_ZONE)])
    for a in range(len(inner)):
        for b in range(a + 1, len(inner)):
            gap = np.linalg.norm(inner[a][:, None] - inner[b][None], axis=2).min()
            assert gap >= 2 * TUBE_RADIUS, (a, b, gap)
    occurrences = inspect_connections(model, official).occurrences
    boxes = [oriented_box(o) for o in occurrences if '-flex-' not in o.occurrence.part_code]
    for points in inner:
        for centre, rotation, half in filter(None, boxes):
            local = (points - centre) @ rotation
            assert not np.any(np.all(np.abs(local) < half, axis=1))
