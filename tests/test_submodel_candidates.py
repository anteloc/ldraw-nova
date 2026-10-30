"""Keep the reviewed submodel candidates tied to their exact sources and valid xray recipes."""
import hashlib
import json

import pytest
from ldraw_xray import Style
from ldraw_xray.mpd import Document
from ldraw_xray.recipe import load_recipe

from ldraw_tools.common import ROOT

CANDIDATES = ROOT / 'examples/submodel-candidates'
ROWS = json.loads((CANDIDATES / 'candidates.json').read_text())


@pytest.mark.parametrize('row', ROWS, ids=[row['id'] for row in ROWS])
def test_candidate_source_and_recipes(row):
    source = ROOT / row['model']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    doc = Document.read(source)
    assert doc.block(row['section']).placements()
    assert row['parent'] in doc.parents_of(row['section'])
    for path in row['recipes']:
        recipe = load_recipe(CANDIDATES / path, Style())
        assert recipe['source'] == str(source.resolve()) and recipe['section'] == row['section']


def test_every_recipe_belongs_to_a_candidate():
    listed = {path for row in ROWS for path in row['recipes']}
    assert {f'recipes/{p.name}' for p in (CANDIDATES / 'recipes').glob('*.json')} == listed
    assert len({row['id'] for row in ROWS}) == len(ROWS) == 30
