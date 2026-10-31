"""Keep the submodel atlas tied to exact sources, hashed boards and current reviews."""
import importlib.util
import json
import re
from pathlib import Path

import pytest
from ldraw_xray import Style
from ldraw_xray.mpd import Document
from ldraw_xray.recipe import load_recipe

from conftest import mpd, ref
from ldraw_tools.common import ROOT, models_path
from ldraw_tools.discovery import source_id
from ldraw_tools.examples import families, search_examples
from ldraw_tools.manuals import current_manual, current_review, export_manual, review_manual, sha

ATLAS = ROOT / 'examples/submodel-atlas'
ROWS = json.loads((ATLAS / 'selections.json').read_text())['references']
PROMOTED = [row for row in ROWS if row['status'] == 'promoted']
CATALOG = json.loads((ATLAS / 'catalog.json').read_text())
ENTRIES = CATALOG['examples'] + CATALOG['details']
PATHS = ['model', 'plan', 'guide', 'manual', 'study_notes', 'board', 'preview', 'generator', 'visual_review']


def atlas_generator():
    spec = importlib.util.spec_from_file_location('submodel_atlas_generator', ATLAS / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('row', ROWS, ids=[row['key'] for row in ROWS])
def test_selection_source_parent_and_recipes(row):
    source = models_path() / row['model']
    assert sha(source) == row['source_sha256']
    doc = Document.read(source)
    assert doc.block(row['section']).placements()
    assert row['parent'] in doc.parents_of(row['section'])
    assert row['discovery']['id'] == source_id('submodels', model=row['model'], section=row['section'])
    for path in row['recipes']:
        assert Path(path).name.startswith(row['key'])
        recipe = load_recipe(ATLAS / path, Style())
        assert recipe['source'] == str(source.resolve()) and recipe['section'] == row['section']


def test_selection_set():
    listed = {path for row in ROWS for path in row['recipes']}
    assert {f'recipes/{p.name}' for p in (ATLAS / 'recipes').glob('*.json')} == listed
    assert len({row['key'] for row in ROWS}) == len(ROWS)
    assert len(PROMOTED) == 30
    # The DB5 front module stays excluded until its purpose is known.
    assert not any('10262' in row['model'] for row in ROWS)


@pytest.mark.parametrize('row', PROMOTED, ids=[row['key'] for row in PROMOTED])
def test_promoted_notes_are_complete(row):
    assert all(row['notes'][k].strip() for k in ['lesson', 'construction', 'interfaces', 'parent_context', 'reuse_notes'])
    assert all(row['guide'][k].strip() for k in ['parent_supplies', 'corrected_description', 'board_reading', 'limits'])
    assert row['use'] in {'adapt', 'inspiration'} and row['catalog_group'] in {'examples', 'details'}
    assert row['views'] == ['home'] and row['tags']


def test_catalog_lists_every_promoted_entry_in_its_group():
    assert [e['key'] for e in ENTRIES] == [r['key'] for r in PROMOTED if r['catalog_group'] == 'examples'] + \
        [r['key'] for r in PROMOTED if r['catalog_group'] == 'details']
    assert all(e['group'] == 'examples' for e in CATALOG['examples'])


@pytest.mark.parametrize('entry', ENTRIES, ids=[e['key'] for e in ENTRIES])
def test_entry_evidence_is_current(entry):
    folder = ATLAS / entry['key']
    seed = next(r for r in PROMOTED if r['key'] == entry['key'])
    for key in PATHS:
        if key in entry:
            assert (ATLAS / entry[key]).is_file(), key
    _, manual = current_manual(folder)
    text = (folder / 'board/board.json').read_text()
    assert '/Users/' not in text and str(ROOT) not in text
    boards = json.loads(text)['boards']
    assert [b['recipe'] for b in boards] == seed['recipes']
    for board in boards:
        assert board['image'] in manual['final_images'] and board['image'] in manual['artifact_hashes']
        assert board['recipe_sha256'] == sha(ATLAS / board['recipe'])
        assert board['source']['sha256'] == seed['source_sha256']
    assert 'board/board.json' in manual['artifact_hashes']
    if entry['use'] == 'adapt':
        assert entry['source_checks_passed'] and entry['bom_matches'] is True and 'generator' in entry
    else:
        assert not entry['source_checks_passed'] and 'generator' not in entry
    reviewed = current_review(folder) is not None
    assert entry['visual_review_status'] == ('visually_reviewed' if reviewed else 'pending')
    assert ('visual_review' in entry) == reviewed


@pytest.mark.parametrize('entry', [e for e in ENTRIES if e['use'] == 'adapt'], ids=lambda e: e['key'])
def test_reusable_plans_rebuild_with_matching_bom_and_attribution(official, entry):
    from ldraw_tools.builder import build_plan, load_plan
    from ldraw_tools.external import compare_bom
    folder = ATLAS / entry['key']
    text, model, diagnostics = build_plan(load_plan(folder / 'scene.plan.json'), official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    assert compare_bom(model, official, folder / 'renders/leocad-bom.csv')['matches']
    for attribution in json.loads((folder / 'extraction.json').read_text())['attribution']:
        if attribution.get('author'):
            assert attribution['author'] in text


def test_examples_search_finds_submodels_with_absolute_boards():
    assert 'submodel' in families()
    found = search_examples('differential', family='submodel', details=True, limit=50)['results']
    assert [r['key'] for r in found] == ['02-42075-rear-axle']
    snot = search_examples('snot', family='submodel', details=True, limit=50)
    assert snot['total'] >= 15
    assert {r['key'] for r in search_examples(family='submodel', limit=50)['results']} == \
        {r['key'] for r in PROMOTED if r['catalog_group'] == 'examples'}
    assert all(Path(r['board']).is_absolute() and Path(r['board']).is_file() for r in snot['results'])
    with pytest.raises(ValueError, match='scale'):
        search_examples(family='submodel', scale='microscale')


def test_readme_and_guide_links_resolve():
    for page in [ATLAS / 'README.md', *(ATLAS / e['guide'] for e in ENTRIES)]:
        for target in re.findall(r'\]\(([^)#\s]+)', page.read_text()):
            if '://' not in target:
                assert (page.parent / target).exists(), f'{page.relative_to(ROOT)}: {target}'


def fixture_atlas(tmp_path, monkeypatch, parts):
    generator = atlas_generator()
    inputs = tmp_path / 'inputs'
    (inputs / 'models').mkdir(parents=True)
    (inputs / 'recipes').mkdir()
    source = inputs / 'models/fixture.mpd'
    source.write_text(mpd(ref('sub.ldr'), name='main.ldr') + mpd(ref(), name='sub.ldr'))
    (inputs / 'recipes/fixture.json').write_text(json.dumps(dict(source='../models/fixture.mpd', section='sub.ldr',
        panels=[dict(label='Parent', parent='main.ldr', layers=[{'layer': 'highlight', 'select': 'section'}]),
                dict(label='Isolated', view='front')])))
    seed = dict(key='fixture', status='promoted', model='fixture.mpd', section='sub.ldr', source_sha256=sha(source),
        parent='main.ldr', title='Fixture brick', category='Fixture', tags=['fixture'], use='adapt',
        catalog_group='details', views=['home'], recipes=['recipes/fixture.json'],
        discovery=dict(id=source_id('submodels', model='fixture.mpd', section='sub.ldr'), source_field='fixture',
                       description='A brick', accuracy='accurate'),
        notes={k: 'Fixture note' for k in ['lesson', 'construction', 'interfaces', 'parent_context', 'reuse_notes']},
        guide={k: 'Fixture guide' for k in ['parent_supplies', 'corrected_description', 'board_reading', 'limits']})
    (inputs / 'selections.json').write_text(json.dumps({'version': 1, 'references': [seed]}))
    monkeypatch.setattr(generator, 'HERE', inputs)
    monkeypatch.setattr(generator, 'SELECTIONS', inputs / 'selections.json')
    monkeypatch.setattr(generator, 'models_path', lambda: inputs / 'models')
    monkeypatch.setattr(generator, 'get_parts', lambda: parts)
    monkeypatch.setattr('ldraw_tools.common.get_parts', lambda: parts)

    def steps(path, library, outdir, *, steps, views, **kwargs):
        rows = []
        for n in steps:
            for view in views:
                (Path(outdir) / f'step-{n:03}-{view}.png').write_bytes(b'fixture step')
                rows.append(dict(step=n, view=view, file=f'step-{n:03}-{view}.png'))
        return rows

    def render(path, library, outdir, **kwargs):
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / 'home.png').write_bytes(b'fixture final')
        (outdir / 'leocad-bom.csv').write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n')

    class Session:
        def __init__(self, config):
            pass

        def board(self, recipe, *, output, force):
            Path(output).mkdir(parents=True)
            (Path(output) / 'mosaic.png').write_bytes(b'fixture board')
            return dict(output=str(output), title='Fixture', mode='views', versions={}, synthetic_note='Synthetic',
                source=dict(source=str(source), section='sub.ldr', source_sha256=sha(source), steps=1, parents={}),
                panels=[dict(label='Parent', view='home', step=None, layers=[], warnings=[])],
                mosaic=dict(output='mosaic.png', legend=[], note='', duplicates=[], limitations=[]))

    monkeypatch.setattr('ldraw_tools.manuals.render_steps', steps)
    monkeypatch.setattr('ldraw_tools.manuals.render', render)
    monkeypatch.setattr('ldraw_xray.render.Session', Session)
    monkeypatch.setattr('ldraw_xray.config.XrayConfig.resolve', lambda **kwargs: None)
    # The fixture library has red but no real-library preview colour 7.
    prepare = generator.prepare_manual
    monkeypatch.setattr(generator, 'prepare_manual', lambda *a, **kw: prepare(*a, colour=4, **kw))
    return generator, inputs


def test_board_is_reviewed_exported_and_invalidated_with_the_build_pages(tmp_path, monkeypatch, parts):
    generator, inputs = fixture_atlas(tmp_path, monkeypatch, parts)
    out = tmp_path / 'atlas'
    generator.generate(out)
    folder = out / 'fixture'
    with pytest.raises(ValueError, match='every final image'):
        review_manual(folder, images=['manual/00/step-001-home.png', 'renders/home.png'], note='Without the board')
    review_manual(folder, images=['manual/00/step-001-home.png', 'renders/home.png', 'board/mosaic.png'], note='Fixture')
    row = generator.write_catalog(out)[0]
    assert row['visual_review_status'] == 'visually_reviewed' and row['board'] == 'fixture/board/mosaic.png'
    assert '![Inspection board](board/mosaic.png)' in (folder / 'GUIDE.md').read_text()
    export_manual(folder, tmp_path / 'export')
    assert (tmp_path / 'export/board/mosaic.png').read_bytes() == b'fixture board'
    # A changed board must remove the advertised review.
    (folder / 'board/mosaic.png').write_bytes(b'changed')
    assert generator.write_catalog(out)[0]['visual_review_status'] == 'pending'
    generator.generate(out, renders=False)
    assert not (folder / 'board').exists() and not (folder / 'visual-review.json').exists()
    assert 'board' not in json.loads((out / 'catalog.json').read_text())['details'][0]


def test_preflight_rejects_a_changed_source_before_touching_the_atlas(tmp_path, monkeypatch, parts):
    generator, inputs = fixture_atlas(tmp_path, monkeypatch, parts)
    (inputs / 'models/fixture.mpd').write_text(mpd(ref('sub.ldr'), name='main.ldr') + mpd(ref('3003.dat'), name='sub.ldr'))
    out = tmp_path / 'atlas'
    with pytest.raises(ValueError, match='source changed'):
        generator.generate(out)
    assert not out.exists()
    assert generator.probe(tmp_path / 'probe', [], parts) == []
