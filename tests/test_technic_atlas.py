"""Atlas maintenance must retain structural entries and invalidate stale reviews."""
import importlib.util
import json
from pathlib import Path

import pytest

from conftest import mpd, ref
from ldraw_tools.manuals import export_manual, review_manual, sha


def atlas_generator():
    path = Path(__file__).resolve().parents[1] / 'examples/technic-atlas/generate_mechanisms.py'
    spec = importlib.util.spec_from_file_location('technic_atlas_generator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_inputs(tmp_path, monkeypatch, parts):
    generator = atlas_generator()
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    (inputs / 'source.mpd').write_text(mpd(ref()))
    (inputs / 'origin.json').write_text('{"original_author":"Tests"}\n')
    seed = dict(key='fixture', title='Fixture mechanism', category='Fixture', lesson='Test source reuse',
        source='source.mpd', section='main.ldr', source_sha256=sha(inputs / 'source.mpd'),
        provenance_files={'origin.json': sha(inputs / 'origin.json')}, views=['home'],
        operation={key:'Fixture context' for key in
            ['function','fixed','moving','input','output','parent_context','reuse_notes']},
        origin_summary='Fixture source', adaptation='Fixture adaptation',
        construction_notes='One source group', qualification='No motion claim')
    (inputs / 'mechanism-selections.json').write_text(json.dumps({'references':[seed]}))
    monkeypatch.setattr(generator, 'HERE', inputs)
    monkeypatch.setattr(generator, 'get_parts', lambda: parts)
    # The real placement builder also resolves through get_parts.
    monkeypatch.setattr('ldraw_tools.common.get_parts', lambda: parts)
    return generator, inputs


def test_changed_input_rejected_before_replacing_existing_atlas(tmp_path, monkeypatch, parts):
    generator, inputs = fixture_inputs(tmp_path, monkeypatch, parts)
    out = tmp_path / 'atlas'; out.mkdir()
    catalog = out / 'catalog.json'; catalog.write_text('{"examples":[]}\n')
    before = catalog.read_bytes()
    (inputs / 'source.mpd').write_text('changed')
    with pytest.raises(ValueError, match='provenance'):
        generator.generate(out, renders=False)
    assert catalog.read_bytes() == before
    assert not (out / 'mechanisms').exists()


def test_portable_export_keeps_provenance_and_refresh_invalidates_review(tmp_path, monkeypatch, parts):
    generator, inputs = fixture_inputs(tmp_path, monkeypatch, parts)

    def steps(path, library, outdir, *, steps, views, **kwargs):
        rows=[]
        for n in steps:
            for view in views:
                name=f'step-{n:03}-{view}.png'
                (Path(outdir) / name).write_bytes(b'fixture step')
                rows.append(dict(step=n,view=view,file=name))
        return rows

    def render(path, library, outdir, **kwargs):
        outdir.mkdir(parents=True,exist_ok=True)
        (outdir / 'home.png').write_bytes(b'fixture final')
        (outdir / 'leocad-bom.csv').write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n')

    monkeypatch.setattr('ldraw_tools.manuals.render_steps', steps)
    monkeypatch.setattr('ldraw_tools.manuals.render', render)
    # The fixture library has red but no real-library preview colour 7.
    prepare = generator.prepare_manual
    monkeypatch.setattr(generator, 'prepare_manual', lambda *a, **kw: prepare(*a, colour=4, **kw))
    out = tmp_path / 'atlas'; out.mkdir()
    structure = dict(key='frame',title='Retained frame',lesson='Keep frame',physical_placements=1,
                     model='frame.mpd',guide='frame.md',structure_contract='structure.json')
    (out / 'catalog.json').write_text(json.dumps({'examples':[structure]}))
    generator.generate(out)
    folder=out / 'mechanisms/fixture'
    review_manual(folder,images=['manual/00/step-001-home.png','renders/home.png'],note='Fixture images')
    rows=json.loads((out / 'catalog.json').read_text())['examples']
    current=generator.write_catalog(out,rows)
    assert current[0] == structure
    assert current[1]['visual_review_status']=='visually_reviewed'
    export_manual(folder,tmp_path / 'export')
    assert (tmp_path / 'export/provenance/origin.json').read_bytes()==(inputs / 'origin.json').read_bytes()
    # A changed retained artifact must remove the advertised review.
    (folder / 'provenance/origin.json').write_text('{}')
    stale=generator.write_catalog(out,current)
    assert stale[1]['visual_review_status']=='pending' and 'visual_review' not in stale[1]
    with pytest.raises(ValueError,match='changed'):
        export_manual(folder,tmp_path / 'stale-export')
    generator.generate(out,renders=False)
    refreshed=json.loads((out / 'catalog.json').read_text())['examples']
    assert refreshed[0]==structure
    assert refreshed[1]['bom_matches'] is None
    assert 'preview' not in refreshed[1] and 'visual_review' not in refreshed[1]
    assert not (folder / 'visual-review.json').exists()
    with pytest.raises(ValueError,match='review'):
        export_manual(folder,tmp_path / 'unreviewed-export')
