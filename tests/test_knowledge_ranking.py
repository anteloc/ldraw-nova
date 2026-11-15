"""Golden queries against the repository's knowledge base.

Each query is one an agent asks while building; an acceptable answer must
appear in the top three. Update the expectations only when a better answer
replaces a listed one, never to accommodate a worse ranking.
"""
import pytest

from ldraw_tools.knowledge import brief, detail, resolve, search

GOLDEN = [
    ('side stud bracket', {'docs/agent/cards/snot.md#1-choose-a-support-with-side-studs',
                           'docs/agent/reference/snot-interfaces.md#brackets', 'b-wing-6208#front'}),
    ('plate stacking height', {'docs/agent/guides/place-parts.md#stacking-ordinary-bricks-and-plates'}),
    ('headlight brick', {'recipe-headlight-lamp'}),
    ('side stud tile cover', {'recipe-side-stud-cover'}),
    ('window in a wall', {'recipe-window-wall'}),
    ('vehicle grille bracket', {'recipe-bracket-grille'}),
    ('1x1 brick with stud on 1 side', {'docs/agent/reference/snot-interfaces.md#side-stud-bricks',
                                       'docs/agent/cards/snot.md#1-choose-a-support-with-side-studs'}),
    ('floating group gap', {'docs/agent/cards/checks.md#checks-card',
                            'docs/agent/reference/validation.md#repair-by-diagnostic'}),
    ('seat a module on side studs', {'docs/agent/cards/snot.md#3-build-surfaces-as-modules', 'recipe-side-panels'}),
]


@pytest.mark.parametrize('query,acceptable', GOLDEN)
def test_golden_query_has_an_acceptable_answer_in_the_top_three(query, acceptable):
    top = [r['id'] for r in search(query, limit=3)['results']]
    assert acceptable & set(top), (query, top)


def test_dimensions_match_however_they_are_written():
    ids = [{r['id'] for r in search(q, limit=5)['results']} for q in ('brick 1x1 with headlight', 'brick 1 x 1 with headlight',
                                                                      'brick 1×1 with headlight')]
    assert ids[0] == ids[1] == ids[2]


def test_guide_sections_resolve_and_guidance_scope_lists_only_guides():
    row = resolve('docs/agent/cards/checks.md#checks-card')
    assert row['kind'] == 'guide-section' and 'assembly.floating_group' in row['lesson']
    whole = detail(resolve('docs/agent/cards/plan.md'))
    assert whole['open'].startswith('docs/agent/cards/plan.md') and 'orient' in whole['text']
    guides = search('stud', scope='guidance', limit=20)['results']
    assert guides and all('anchor' in r for r in guides)


def test_brief_results_are_small_and_point_at_a_file():
    results = [brief(r) for r in search('side stud', limit=5)['results']]
    assert all(len(str(r)) < 600 and r.get('open') for r in results)
