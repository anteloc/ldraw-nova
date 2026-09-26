"""Find a small, relevant set of generated teaching examples."""
import json
from pathlib import Path
from .common import ROOT


def search_examples(query='', *, limit=5, scale=None, details=False, family='building'):
    if family not in {'building','vehicle','reference','technic','mechanism','spaceship'}:raise ValueError('Unknown example family')
    if family in {'vehicle','technic','mechanism','spaceship'} and scale:raise ValueError('This example family does not use building scale filters')
    path=ROOT/f'examples/{family}-atlas/catalog.json'
    if not path.is_file():raise ValueError(f'{family.title()} atlas catalog missing')
    catalog=json.loads(path.read_text())
    terms=query.casefold().split();rows=[]
    for row in catalog['details' if details else 'examples']:
        text=' '.join(str(row.get(k,'')) for k in ['key','title','category','lesson','description','placement_notes','modules']).casefold()
        if not all(t in text for t in terms):continue
        if scale and row.get('scale')!=scale:continue
        item={k:v for k,v in row.items() if k not in ['source_sha256']}
        for key in ['model','plan','guide','preview','generator','visual_review','manual','operation','study_notes']:
            if key in item:item[key]=str(path.parent/item[key])
        rows.append(item)
    return dict(total=len(rows),results=rows[:limit],truncated=len(rows)>limit,
                note='Select a matching family and scale, read its construction guide and visual review, then adapt its modules to the new brief.')
