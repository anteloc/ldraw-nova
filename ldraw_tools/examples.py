"""Compatibility projection of explicitly registered knowledge examples."""
from .common import ROOT
from .knowledge import examples, search


def families():
    return sorted({family for row in examples(ROOT) for family in row['families']})


def search_examples(query='', *, limit=5, scale=None, details=False, family=None, scope='default'):
    if family is not None and family not in families():
        raise ValueError('Unknown example family; choose ' + ', '.join(families()))
    result = search(query, limit=limit, scope=scope, family=family, scale=scale,
                    only_examples=True, details=True if details else (False if family else None), root=ROOT)
    for row in result['results']:
        candidates = [a for a in row['aliases'] if not family or a.startswith(family + ':')]
        row['key'] = candidates[0].split(':', 1)[1] if candidates else row['id']
        row['lesson'] = row['excerpt']
        row['use'] = 'inspiration' if row['scope'] == 'inspiration' else 'scoped-study'
    return result
