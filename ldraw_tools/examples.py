"""Find a small, relevant set of generated teaching examples."""
import json
from pathlib import Path
from .common import ROOT


SCALED = {'building', 'reference'}  # families with minifigure/microscale filters


def families():
    """Every examples/NAME-atlas with a catalog is a family."""
    return sorted(p.parent.name.removesuffix('-atlas') for p in (ROOT/'examples').glob('*-atlas/catalog.json'))


def search_examples(query='', *, limit=5, scale=None, details=False, family='building'):
    if family not in families():raise ValueError('Unknown example family; choose '+', '.join(families()))
    if family not in SCALED and scale:raise ValueError('This example family does not use building scale filters')
    path=ROOT/f'examples/{family}-atlas/catalog.json'
    catalog=json.loads(path.read_text())
    candidates=list(catalog['details' if details else 'examples'])
    if family == 'spaceship' and not details:
        from .spaceships import default_reference
        candidates.insert(0,default_reference())
    terms=query.casefold().split();rows=[]
    for row in candidates:
        text=' '.join(str(row.get(k,'')) for k in ['key','title','category','tags','lesson','description','placement_notes','modules']).casefold()
        if not all(t in text for t in terms):continue
        if scale and row.get('scale')!=scale:continue
        item={k:v for k,v in row.items() if k not in ['source_sha256']}
        for key in ['model','plan','guide','preview','generator','visual_review','manual','operation','study_notes','board']:
            if key in item:item[key]=str(path.parent/item[key])
        rows.append(item)
    return dict(total=len(rows),results=rows[:limit],truncated=len(rows)>limit,
                note='Select a matching family and scale, read its construction guide and visual review, then adapt its modules to the new brief.')
