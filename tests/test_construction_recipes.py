"""Every recipe rebuilds byte for byte into its reviewed MPD, without errors."""
from pathlib import Path

import pytest

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.knowledge import examples

ROOT = Path(__file__).resolve().parents[1]
PLANS = sorted((ROOT / 'examples/recipes').glob('*.plan.json'))


@pytest.mark.parametrize('plan', PLANS, ids=lambda p: p.name.removesuffix('.plan.json'))
def test_recipe_rebuilds_its_reviewed_model(plan, official):
    text, _, diagnostics = build_plan(load_plan(plan), official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    assert text.encode() == plan.with_name(plan.name.replace('.plan.json', '.mpd')).read_bytes()


def test_every_recipe_is_registered_and_current():
    rows = {r['id']: r for r in examples(ROOT) if r['id'].startswith('recipe-')}
    assert {f"recipe-{p.name.removesuffix('.plan.json')}" for p in PLANS} == set(rows)
    assert all(r['scope'] == 'construction' for r in rows.values())  # a stale model hash would hold the entry
