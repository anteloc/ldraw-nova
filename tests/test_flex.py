"""The adapter must preserve physical boundaries without weakening validation."""
import json
import subprocess

import numpy as np
import pytest

from ldraw_tools import flex
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT, atomic_write
from ldraw_tools.document import physical_context
from ldraw_tools.validation import validate_file


@pytest.fixture
def cfg():
    pytest.importorskip("lsynth_nova", reason="Optional LSynth integration: ./setup.sh --with-lsynth")
    return flex.engine()[0]


def test_missing_optional_dependency_is_actionable(monkeypatch):
    monkeypatch.setattr(flex, "availability", lambda: {"available": False})
    with pytest.raises(ValueError, match="setup.sh --with-lsynth"):
        flex.definitions()


def test_controls_reject_incomplete_and_unsafe_sources(cfg):
    source = (ROOT / "examples/flex/hose.ldr").read_text()
    for text, error in [
        (source.replace("TECHNIC_PNEUMATIC_HOSE_BEVELED", "NOT_A_TYPE"), "unknown synthesis type"),
        (source.replace("0 SYNTH END", ""), "Missing SYNTH END"),
        (source.replace("0 SYNTH END", "0 SYNTH BEGIN RUBBER_BAND 4\n0 SYNTH END"), "nested"),
        (source.replace("0 SYNTH SHOW", "0 FILE other.ldr"), "FILE boundary"),
        (source + "0 SYNTH SYNTHESIZED BEGIN\n", "original unsynthesized"),
        (source.replace("1 4 -60", "1 4 nan"), "nonfinite"),
        ("0 SYNTH HOSE_RES 0 0\n" + source, "resolution"),
        ("0 SYNTH BAND_RES 2\n" + source, "resolution"),
        (source.replace("BEVELED 4", "BEVELED 16"), "explicit surface colour"),
        (source.replace("1 4 -60", "0 GHOST 1 4 -60"), "GHOST"),
    ]:
        with pytest.raises(ValueError, match=error):
            flex.preflight(text, cfg)


@pytest.mark.parametrize("name,expected", [("hose", 1), ("band", 3), ("chain", 26)])
def test_assets_are_portable_and_count_physical_items(cfg, official, tmp_path, name, expected):
    output = tmp_path / f"{name}.mpd"
    report = flex.build(ROOT / f"examples/flex/{name}.ldr", output, official)
    raw = output.read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")
    model, diagnostics = validate_file(output, official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    physical, parts = physical_context(model, official)
    assert sum(r.quantity for r in physical.bill_of_materials(parts=parts)) == expected
    assert not any(p.reference.lower() in {"ls01.dat", "ls02.dat"} for p in physical.iter_occurrences())
    if name != "chain":
        part = report['blocks'][0]['part']
        posed = model.submodels[part]
        assert len(posed.pieces) > 10  # Many geometry segments, one physical item.
        assert any(not np.allclose(np.array(p.matrix.rows).T @ np.array(p.matrix.rows), np.eye(3), atol=1e-3) for p in posed.pieces)
        assert report['embedded_sources']
        assert 'Redistributable under CCAL version 2.0' in raw.decode()
    else:
        assert report['blocks'][0]['representation'] == 'links'
        assert not report['embedded_sources']
    flex.build(ROOT / f"examples/flex/{name}.ldr", output, official, force=True)
    assert output.read_bytes() == raw
    assert json.loads(output.with_suffix('.manifest.json').read_text())['review_required']


def test_constraints_and_previous_output_survive_failure(cfg, official, tmp_path):
    source = tmp_path / 'source.ldr'
    source.write_bytes((ROOT / 'examples/flex/hose.ldr').read_bytes())
    output = tmp_path / 'hose.mpd'
    flex.build(source, output, official)
    old = output.read_bytes(), output.with_suffix('.manifest.json').read_bytes()
    with pytest.raises(ValueError, match='already exists'):
        flex.build(source, output, official)
    source.write_text(source.read_text().replace('LS01.dat', 'LS02.dat', 1).replace('0 SYNTH END', ''))
    original = source.read_bytes()
    with pytest.raises(ValueError, match='Missing SYNTH END'):
        flex.build(source, output, official, force=True)
    assert (output.read_bytes(), output.with_suffix('.manifest.json').read_bytes()) == old
    assert source.read_bytes() == original
    with pytest.raises(ValueError, match='original constraints separate'):
        flex.build(output, output, official, force=True)


def test_lsynth_warning_is_a_failure_even_with_exit_zero(cfg, official, tmp_path, monkeypatch):
    monkeypatch.setattr(flex.subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(a, 0, '', 'lsynth: warning: no tangent'))
    with pytest.raises(ValueError, match='no tangent'):
        flex.build(ROOT / 'examples/flex/band.ldr', tmp_path / 'bad.mpd', official)
    assert not list(tmp_path.iterdir())


def test_generated_roundoff_does_not_allow_stretched_complete_parts(cfg, official, tmp_path):
    source = tmp_path / 'stretched.ldr'
    source.write_text((ROOT / 'examples/flex/hose.ldr').read_text() + '\n1 4 0 0 100 2 0 0 0 1 0 0 0 1 3001.dat\n')
    with pytest.raises(ValueError, match='assembly.nonrigid'):
        flex.build(source, tmp_path / 'asset.mpd', official)
    # A different four-place rotation exceeds the existing validator's tolerance.
    angle = np.radians(17.4)
    m = np.array([[np.cos(angle), 0, -np.sin(angle)], [0, 1, 0], [np.sin(angle), 0, np.cos(angle)]]).round(4)
    line = '1 4 0 0 0 ' + ' '.join(map(str, m.ravel())) + ' 3711.dat'
    fixed, changes = flex.rigid_links([line])
    assert changes
    assert max(abs(np.array(changes[0]['after']) - m).ravel()) <= .000051
    for matrix in ['2 0 0 0 1 0 0 0 1', '-1 0 0 0 1 0 0 0 1']:
        line = f'1 4 0 0 0 {matrix} 3711.dat'
        assert flex.rigid_links([line]) == ([line], [])


def test_mpd_submodel_and_existing_plan_assets(cfg, official, tmp_path):
    source = tmp_path / 'source.mpd'
    hose = (ROOT / 'examples/flex/hose.ldr').read_text().replace('hose.ldr', 'hose with spaces.ldr')
    source.write_text('0 FILE scene.ldr\n0 Scene\n0 Name: scene.ldr\n0 Author: Test\n'
                      '1 4 0 0 0 1 0 0 0 1 0 0 0 1 hose with spaces.ldr\n'
                      '1 4 0 0 100 1 0 0 0 1 0 0 0 1 hose with spaces.ldr\n'
                      '0 FILE hose with spaces.ldr\n' + hose + '0 NOFILE\n')
    output = tmp_path / 'asset.mpd'
    report = flex.build(source, output, official)
    assert report['root'] == 'scene.ldr'
    plan = dict(version=1, author='Test', assets=['asset.mpd'], sections=[
        dict(name='main.ldr', description='Placed flex asset', steps=[[dict(id='flex', ref='scene.ldr', colour=4, at=[0, 0, 0])]])])
    # Follow the real plan schema and loader, including relative asset resolution.
    atomic_write(tmp_path / 'scene.plan.json', json.dumps(plan))
    text, model, diagnostics = build_plan(load_plan(tmp_path / 'scene.plan.json'), official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    physical, parts = physical_context(model, official)
    assert sum(r.quantity for r in physical.bill_of_materials(parts=parts)) == 2


def test_source_cannot_override_bundled_geometry(cfg, official, tmp_path):
    source = tmp_path / 'source.mpd'
    source.write_text('0 FILE hose.ldr\n' + (ROOT / 'examples/flex/hose.ldr').read_text()
                      + '0 FILE LS23.dat\n0 My alternate geometry\n0 !LDRAW_ORG Unofficial_Part\n')
    with pytest.raises(ValueError, match='overrides bundled LSynth geometry'):
        flex.build(source, tmp_path / 'asset.mpd', official)


def test_bundled_legacy_headers_are_preserved_and_repairs_recorded(cfg, official, tmp_path):
    hose = (ROOT / 'examples/flex/hose.ldr').read_text().replace('LS01.dat', 'LS02.dat')
    for method, names in [('TECHNIC_PNEUMATIC_HOSE_BEVELED', {'ls22.dat'}), ('TECHNIC_FLEX-SYSTEM_HOSE', {'ls50.dat', 'ls51.dat'})]:
        source = tmp_path / 'source.ldr'
        source.write_text(hose.replace('TECHNIC_PNEUMATIC_HOSE_BEVELED', method))
        output = tmp_path / 'asset.mpd'
        report = flex.build(source, output, official, force=True)
        repaired = {s['name'] for s in report['embedded_sources'] if s['changes']}
        assert names <= repaired
        if 'ls22.dat' in names:
            assert 'Fredrik Glöckner' in output.read_text()
