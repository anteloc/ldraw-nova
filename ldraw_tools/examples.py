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
    status_path=ROOT/'examples/status.json'
    status=json.loads(status_path.read_text()) if status_path.is_file() else {}
    terms=query.casefold().split();rows=[]
    for row in catalog['details' if details else 'examples']:
        text=' '.join(str(row.get(k,'')) for k in ['key','title','category','lesson','description','placement_notes','modules']).casefold()
        if not all(t in text for t in terms):continue
        if scale and row.get('scale')!=scale:continue
        item={k:v for k,v in row.items() if k not in ['source_sha256']}
        for key in ['model','plan','guide','preview','generator','visual_review','manual','operation','study_notes']:
            if key in item:item[key]=str(path.parent/item[key])
        if 'model' in item:
            checked=status.get(Path(item['model']).resolve().relative_to(ROOT).as_posix())
            item.pop('checks_passed',None)   # superseded by the current check verdict
            item['check']=(f"{checked['verdict']}: {checked['problems']}"+(' (official model: gaps in check, not defects)' if checked['verdict']=='GAP' else '')
                           if checked else 'not checked (run scripts/example_status.py)')
        rows.append(item)
    return dict(total=len(rows),results=rows[:limit],truncated=len(rows)>limit,
                note='Recipes in docs/reference always pass check; prefer them. Use an example for its ideas; '
                     'one whose check is FAIL has construction defects you must not copy.')
