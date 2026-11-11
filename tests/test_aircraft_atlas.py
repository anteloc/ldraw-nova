"""Keep the aircraft atlas tied to exact sources, hashed boards, current reviews and installed packages."""
import json
import re
from pathlib import Path

import pytest
from ldraw_xray import Style
from ldraw_xray.mpd import Document
from ldraw_xray.recipe import load_recipe

from ldraw_tools.atlas import Atlas, GUIDE_KEYS, NOTE_KEYS
from ldraw_tools.common import ROOT, models_path
from ldraw_tools.discovery import source_id
from ldraw_tools.examples import families, search_examples
from ldraw_tools.knowledge import examples, resolve
from ldraw_tools.manuals import current_manual, current_review, sha

ATLAS = Atlas(ROOT / 'examples/aircraft-atlas', family='aircraft')
ROWS = ATLAS.rows()
PROMOTED = [row for row in ROWS if row['status'] == 'promoted']
CATALOG = json.loads((ATLAS.directory / 'catalog.json').read_text())
PATHS = ['model', 'plan', 'guide', 'manual', 'study_notes', 'board', 'preview', 'generator', 'visual_review']


def package(row):
    return ROOT / 'examples' / row['package']


@pytest.mark.parametrize('row', ROWS, ids=[row['key'] for row in ROWS])
def test_selection_source_parent_and_recipes(row):
    source = models_path() / row['model']
    assert sha(source) == row['source_sha256']
    doc = Document.read(source)
    assert doc.block(row['section']).placements()
    parents = doc.parents_of(row['section'])
    assert (row['parent'] is None and not parents) or row['parent'] in parents
    assert row['discovery']['id'] == source_id('submodels', model=row['model'], section=row['section'])
    for path in row['recipes']:
        assert Path(path).name.startswith(row['key'])
        recipe = load_recipe(ATLAS.directory / path, Style())
        assert recipe['source'] == str(source.resolve()) and recipe['section'] == row['section']


def test_selection_set():
    listed = {path for row in ROWS for path in row['recipes']}
    assert {f'recipes/{p.name}' for p in (ATLAS.directory / 'recipes').glob('*.json')} == listed
    assert len({row['key'] for row in ROWS}) == len(ROWS) == len({row['package'] for row in ROWS})
    assert len(PROMOTED) == 28
    # Every listed source set contributes at least one package.
    assert {row['model'] for row in PROMOTED} == {'9394-1_Propeller-Plane.mpd', '10159-1.mpd', '8855-1.mpd', '42040-1.mpd',
                                                  '10226-1.mpd', '6392-1.mpd', '5892-1.mpd', '7893-1.mpd'}


@pytest.mark.parametrize('row', PROMOTED, ids=[row['key'] for row in PROMOTED])
def test_promoted_notes_are_complete(row):
    assert all(row['notes'][k].strip() for k in NOTE_KEYS)
    assert all(row['guide'][k].strip() for k in GUIDE_KEYS)
    assert row['use'] in {'adapt', 'inspiration'} and row['catalog_group'] in {'examples', 'details'}
    assert row['tags'] and row['style'] and row['discovery']['accuracy']
    assert (row['views'] == ['home']) != bool(row['overview'])


@pytest.mark.parametrize('row', PROMOTED, ids=[row['key'] for row in PROMOTED])
def test_installed_package_is_registered_reviewed_and_current(row):
    folder = package(row)
    record = resolve(row['package'])
    assert record['scope'] == ('construction' if row['use'] == 'adapt' else 'inspiration'), record.get('export_blocker')
    assert f'aircraft:{row["key"]}' in record['aliases'] and 'aircraft' in record['families']
    assert record['model_sha256'] == sha(folder / 'source.mpd')
    assert record['origin']['section'] == row['section'] and record['origin']['sha256'] == row['source_sha256']
    _, manual = current_manual(folder)
    assert manual['source']['section'] == row['section'] and manual['source']['sha256'] == row['source_sha256']
    assert manual.get('image_mode') == ('overview' if row['overview'] else 'steps')
    assert manual['title'] == row['title']
    assert current_review(folder) is not None
    text = (folder / 'board/board.json').read_text()
    assert '/Users/' not in text and str(ROOT) not in text
    boards = json.loads(text)['boards']
    assert [b['recipe'] for b in boards] == row['recipes']
    for board in boards:
        assert board['image'] in manual['final_images'] and board['image'] in manual['artifact_hashes']
        assert board['recipe_sha256'] == sha(ATLAS.directory / board['recipe'])
        assert board['source']['sha256'] == row['source_sha256']
    if row['use'] == 'adapt':
        assert manual['source_checks_passed'] and manual['bom_matches'] is True and (folder / 'generate.py').is_file()
    else:
        assert not manual['source_checks_passed'] and 'generator' not in record
    notes = json.loads((folder / 'study-notes.json').read_text())
    assert all(notes[k] == row['notes'][k] for k in NOTE_KEYS)


def test_catalog_lists_every_promoted_entry_in_its_group():
    entries = CATALOG['examples'] + CATALOG['details']
    assert CATALOG['family'] == 'aircraft'
    installed = {e['key']: e['group'] for e in entries if e['key'] in {r['key'] for r in PROMOTED}}
    assert installed == {r['key']: r['catalog_group'] for r in PROMOTED}
    for entry in entries:
        for key in PATHS:
            if key in entry:
                assert (ATLAS.directory / entry[key]).is_file(), key


@pytest.mark.parametrize('row', [r for r in PROMOTED if r['use'] == 'adapt'], ids=lambda r: r['key'])
def test_reusable_plans_rebuild_with_matching_bom_and_attribution(official, row):
    from ldraw_tools.builder import build_plan, load_plan
    from ldraw_tools.external import compare_bom
    folder = package(row)
    text, model, diagnostics = build_plan(load_plan(folder / 'scene.plan.json'), official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    assert compare_bom(model, official, folder / 'renders/leocad-bom.csv')['matches']
    for attribution in json.loads((folder / 'extraction.json').read_text())['attribution']:
        if attribution.get('author'):
            assert attribution['author'] in text


def test_aircraft_family_search_and_scopes():
    assert 'aircraft' in families()
    keys = {r['key'] for r in search_examples(family='aircraft', limit=100, scope='all')['results']}
    assert {r['key'] for r in PROMOTED if r['catalog_group'] == 'examples'} <= keys
    details = search_examples(family='aircraft', details=True, limit=100, scope='all')['results']
    assert {r['key'] for r in PROMOTED if r['catalog_group'] == 'details'} <= {r['key'] for r in details}
    default = search_examples(family='aircraft', details=True, limit=100)['results'] + search_examples(family='aircraft', limit=100)['results']
    assert all(r['scope'] == 'construction' for r in default)
    inspiration = {r['key'] for r in search_examples(family='aircraft', limit=100, scope='inspiration')['results']}
    assert {r['key'] for r in PROMOTED if r['use'] == 'inspiration' and r['catalog_group'] == 'examples'} <= inspiration
    found = {r['id'] for r in search_examples('propeller', family='aircraft', details=True, limit=20)['results']}
    assert '10226-geared-propeller' in found
    # Retired and removed aircraft lessons stay out of default retrieval but resolve by identity.
    assert resolve('an225')['scope'] == 'archive' and resolve('courier-jet')['scope'] == 'archive'
    assert resolve('airliner-engine')['scope'] == 'archive' and '7893-jet-nacelle' in resolve('airliner-engine')['lesson']
    assert not [r for r in examples() if r['id'] in {'an225', 'courier-jet', 'airliner-engine', 'airliner-wheel-bogie'} and r['scope'] != 'archive']


def test_readme_and_guide_links_resolve():
    pages = [ATLAS.directory / 'README.md', *(package(r) / 'README.md' for r in PROMOTED), *(package(r) / 'GUIDE.md' for r in PROMOTED)]
    for page in pages:
        for target in re.findall(r'\]\(([^)#\s]+)', page.read_text()):
            if '://' not in target:
                assert (page.parent / target).exists(), f'{page.relative_to(ROOT)}: {target}'


def test_measurements_match_the_overview_seeds():
    rows = json.loads((ATLAS.directory / 'measurements.json').read_text())
    assert {r['key'] for r in rows} == {r['key'] for r in PROMOTED if r['overview']}
    for row in rows:
        assert row['parts'] > 0 and row['frame']['forward'] in {'+X', '-X', '+Z', '-Z'}
