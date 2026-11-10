"""The shared atlas library prepares studies outside the repo, installs only reviewed ones, and registers them."""
import json
from pathlib import Path

import pytest

from conftest import mpd, ref
from ldraw_tools import atlas as A
from ldraw_tools.discovery import source_id
from ldraw_tools.knowledge import examples, resolve
from ldraw_tools.manuals import review_manual, sha


def fixture_atlas(tmp_path, monkeypatch, parts, *, overview=False):
    root = tmp_path/'repo'
    (root/'examples'/'test-atlas'/'recipes').mkdir(parents=True)
    (root/'docs/agent').mkdir(parents=True)
    models = tmp_path/'models'; models.mkdir()
    source = models/'fixture.mpd'
    source.write_text(mpd(ref('sub.ldr'), name='main.ldr') + mpd(ref(), name='sub.ldr'))
    atlas = A.Atlas(root/'examples/test-atlas', family='test', root=root)
    (atlas.directory/'recipes/fixture.json').write_text(json.dumps(dict(source='../../../../models/fixture.mpd', section='sub.ldr',
        panels=[dict(label='Parent', parent='main.ldr', layers=[{'layer': 'highlight', 'select': 'section'}]),
                dict(label='Isolated', view='front')])))
    monkeypatch.setattr(A, 'models_path', lambda: models)
    monkeypatch.setattr(A, 'get_parts', lambda: parts)
    monkeypatch.setattr('ldraw_tools.common.get_parts', lambda *a, **k: parts)
    seed = A.scaffold(atlas, key='fixture', package='fixture-brick', model='fixture.mpd', section='sub.ldr',
                      title='Fixture brick', category='Fixture', style='test style', tags=['fixture'], use='adapt',
                      group='details', overview=overview, views=['home', 'front'] if overview else ['home'],
                      recipes=['recipes/fixture.json'], techniques=['system'])
    assert seed['parent'] == 'main.ldr' and seed['status'] == 'candidate'
    assert seed['discovery']['id'] == source_id('submodels', model='fixture.mpd', section='sub.ldr')
    assert seed['discovery']['description'] == 'Test model'
    rows = atlas.rows()
    rows[0]['notes'] = {k: 'Fixture note' for k in A.NOTE_KEYS}
    rows[0]['guide'] = {k: 'Fixture guide' for k in A.GUIDE_KEYS}
    atlas.save(rows)

    def steps(path, library, outdir, *, steps, views, **kwargs):
        out = []
        for n in steps:
            for view in views:
                (Path(outdir)/f'step-{n:03}-{view}.png').write_bytes(b'fixture step')
                out.append(dict(step=n, view=view, file=f'step-{n:03}-{view}.png'))
        return out

    def render(path, library, outdir, *, views=('home',), **kwargs):
        outdir.mkdir(parents=True, exist_ok=True)
        for view in views:
            (outdir/f'{view}.png').write_bytes(b'fixture final '+view.encode())
        (outdir/'leocad-bom.csv').write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n')

    class Session:
        def __init__(self, config):
            pass

        def board(self, recipe, *, output, force):
            Path(output).mkdir(parents=True)
            (Path(output)/'mosaic.png').write_bytes(b'fixture board')
            return dict(output=str(output), title='Fixture', mode='views', versions={}, synthetic_note='Synthetic',
                source=dict(source=str(source), section='sub.ldr', source_sha256=sha(source), steps=1, parents={}),
                panels=[dict(label='Parent', view='home', step=None, layers=[], warnings=[])],
                mosaic=dict(output='mosaic.png', legend=[], note='', duplicates=[], limitations=[]))

    monkeypatch.setattr('ldraw_tools.manuals.render_steps', steps)
    monkeypatch.setattr('ldraw_tools.manuals.render', render)
    monkeypatch.setattr('ldraw_xray.render.Session', Session)
    monkeypatch.setattr('ldraw_xray.config.XrayConfig.resolve', lambda **kwargs: None)
    prepare = A.prepare_manual
    monkeypatch.setattr(A, 'prepare_manual', lambda *a, **kw: prepare(*a, colour=4, **kw))
    return atlas, root


def test_scaffold_rejects_duplicates_and_unknown_sections(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts)
    with pytest.raises(ValueError, match='already exists'):
        A.scaffold(atlas, key='fixture', package='other', model='fixture.mpd', section='sub.ldr', title='x', category='x')
    with pytest.raises(ValueError, match='already exists'):
        A.scaffold(atlas, key='other', package='fixture-brick', model='fixture.mpd', section='sub.ldr', title='x', category='x')
    with pytest.raises(ValueError, match='does not place'):
        A.scaffold(atlas, key='other', package='other', model='fixture.mpd', section='sub.ldr', title='x', category='x', parent='sub.ldr')


def test_generate_refuses_the_examples_tree_and_installs_only_reviewed_studies(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts)
    with pytest.raises(ValueError, match='separate'):
        A.generate(atlas, atlas.directory, promoted=False)
    with pytest.raises(ValueError, match='separate'):
        A.generate(atlas, root/'examples/anything', promoted=False)
    out = tmp_path/'out'
    rows = A.generate(atlas, out, promoted=False)
    assert rows[0]['visual_review_status'] == 'pending' and rows[0]['package'] == 'fixture-brick'
    folder = out/'fixture'
    assert (folder/'board/mosaic.png').is_file() and (folder/'GUIDE.md').is_file() and (folder/'generate.py').is_file()
    guide = (folder/'GUIDE.md').read_text()
    assert 'manual export examples/fixture-brick' in guide and 'board run examples/test-atlas/recipes/fixture.json' in guide
    assert 'test style' in guide
    with pytest.raises(ValueError, match='visual review'):
        A.install(atlas, out, 'fixture')
    review_manual(folder, images=['manual/00/step-001-home.png', 'renders/home.png', 'board/mosaic.png'], note='Fixture')
    result = A.install(atlas, out, 'fixture')
    package = root/'examples/fixture-brick'
    assert result['id'] == 'fixture-brick' and result['scope'] == 'construction' and result['alias'] == 'test:fixture'
    assert package.is_dir() and (package/'README.md').is_file() and (package/'visual-review.json').is_file()
    assert atlas.seed('fixture')['status'] == 'promoted'
    record = resolve('fixture-brick', root=root)
    assert record['scope'] == 'construction' and record['families'] == ['test'] and record['techniques'] == ['system']
    assert record['model_sha256'] == sha(package/'source.mpd') and record['origin']['section'] == 'sub.ldr'
    assert Path(record['board']).is_file() and (root/record['study_guide']).is_file()
    assert resolve('test:fixture', root=root)['id'] == 'fixture-brick'
    with pytest.raises(ValueError, match='package exists'):
        A.install(atlas, out, 'fixture')
    assert A.install(atlas, out, 'fixture', force=True)['id'] == 'fixture-brick'
    # The compatibility catalog is a projection of the installed README.
    catalog_rows = A.refresh(atlas)
    assert [r['key'] for r in catalog_rows] == ['fixture']
    catalog = json.loads((atlas.directory/'catalog.json').read_text())
    assert catalog['family'] == 'test' and catalog['details'][0]['id'] == 'fixture-brick'
    assert 'fixture-brick' in (atlas.directory/'index.html').read_text()


def test_refresh_notes_updates_hashed_notes_and_drops_the_review(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts)
    rows = atlas.rows(); rows[0]['status'] = 'candidate'; rows[0]['notes'] = {k: '' for k in A.NOTE_KEYS}; atlas.save(rows)
    out = tmp_path/'out'
    A.generate(atlas, out, promoted=False)  # candidates render before their notes exist
    folder = out/'fixture'
    review_manual(folder, images=['manual/00/step-001-home.png', 'renders/home.png', 'board/mosaic.png'], note='Too early')
    with pytest.raises(ValueError, match='complete the study notes'):
        A.install(atlas, out, 'fixture')
    rows = atlas.rows(); rows[0]['notes'] = {k: 'Written after opening the images' for k in A.NOTE_KEYS}; atlas.save(rows)
    assert A.refresh_notes(atlas, out, 'fixture')['review'] == 'pending'
    assert not (folder/'visual-review.json').exists()
    assert 'Written after opening the images' in (folder/'study-notes.json').read_text()
    assert 'Written after opening the images' in (folder/'GUIDE.md').read_text()
    with pytest.raises(ValueError, match='visual review'):
        A.install(atlas, out, 'fixture')
    review_manual(folder, images=['manual/00/step-001-home.png', 'renders/home.png', 'board/mosaic.png'], note='Final')
    assert A.install(atlas, out, 'fixture')['scope'] == 'construction'


def test_overview_seed_renders_completed_views_only(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts, overview=True)
    out = tmp_path/'out'
    A.generate(atlas, out, promoted=False)
    manual = json.loads((out/'fixture/manual.json').read_text())
    assert manual['image_mode'] == 'overview'
    assert set(manual['final_images']) == {'renders/home.png', 'renders/front.png', 'board/mosaic.png'}
    assert not list((out/'fixture/manual/00').glob('step-*.png'))
    assert 'Completed-model views' in (out/'fixture/GUIDE.md').read_text()


def test_inspiration_rows_cannot_be_installed_as_reusable_when_checks_pass(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts)
    rows = atlas.rows(); rows[0]['use'] = 'inspiration'; atlas.save(rows)
    out = tmp_path/'out'
    A.generate(atlas, out, promoted=False)
    review_manual(out/'fixture', images=['manual/00/step-001-home.png', 'renders/home.png', 'board/mosaic.png'], note='Fixture')
    with pytest.raises(ValueError, match='checks pass'):
        A.install(atlas, out, 'fixture')


def test_preflight_rejects_a_changed_source(tmp_path, monkeypatch, parts):
    atlas, root = fixture_atlas(tmp_path, monkeypatch, parts)
    (tmp_path/'models/fixture.mpd').write_text(mpd(ref('sub.ldr'), name='main.ldr') + mpd(ref('3003.dat'), name='sub.ldr'))
    with pytest.raises(ValueError, match='source changed'):
        A.generate(atlas, tmp_path/'out', promoted=False)
    assert not (tmp_path/'out').exists()
    assert A.probe(atlas, tmp_path/'probe', [], parts) == []
