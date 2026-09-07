"""Create the offline teaching gallery and bounded machine-readable indexes.

This script checks report/render hashes. Visual-review observations are authored
separately after opening images; generating a gallery never marks a view reviewed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from html import escape
from pathlib import Path

from generate import DESIGNS, ROOT
from ldraw_tools.common import atomic_write, dumps


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_status(folder,key,*,detail=False):
    sha=digest(folder/(key+'.mpd'))
    validation=json.loads((folder/'validation.json').read_text())
    bom=json.loads((folder/'bom-comparison.json').read_text())
    renders=json.loads((folder/'render-manifest.json').read_text())
    if not validation['checks_passed'] or not bom['matches']:
        raise ValueError(f'{key}: failing checks/BOM')
    if any(v['source_sha256']!=sha for v in [validation,bom,renders]):
        raise ValueError(f'{key}: stale report; rebuild/render this exact revision')
    required={'home.png'} if detail else {'home.png','front.png','top.png'}
    if not required.issubset(renders['images']):raise ValueError(f'{key}: missing review views')
    for name,expected in renders['images'].items():
        if digest(folder/name)!=expected:raise ValueError(f'{key}: changed render {name}')
    review_path=folder/'visual-review.json'
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    reviewed=review.get('source_sha256')==sha and required.issubset(review.get('viewed_images',[]))
    return dict(source_sha256=sha,checks_passed=True,bom_matches=True,visual_review_recorded=reviewed,
                physical_placements=validation['geometry']['occurrence_count'])


def catalogue(root=ROOT):
    root=Path(root);rows=[]
    for key,meta in DESIGNS.items():
        folder=root/key;row={k:v for k,v in meta.items() if k!='factory'}
        row.update(artifact_status(folder,key),model=f'{key}/{key}.mpd',plan=f'{key}/scene.plan.json',
                   guide=f'{key}/README.md',preview=f'{key}/home.png')
        row['sections']=len(json.loads((folder/'scene.plan.json').read_text())['sections'])
        rows.append(row)
        atomic_write(folder/'design-brief.json',dumps(row)+'\n')
        plan=json.loads((folder/'scene.plan.json').read_text())
        modules='\n'.join(f'| `{s["name"]}` | {s["description"]} |' for s in plan['sections'][1:])
        text=f'''# {row['title']}

{row['category']} · {row['scale']} scale · {row['physical_placements']} physical placements · {row['sections']} FILE sections.

![LeoCAD home view](home.png)

[MPD]({key}.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

{row['lesson']}

**Place details:** {row['fit']}

**Avoid:** {row['avoid']}

This is an original teaching model. The [LEGO example]({row['source']}) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
{modules}

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py {key} --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/{key}/scene.plan.json --output output/{key}.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
'''
        atomic_write(folder/'README.md',text)
    details=json.loads((root/'details/catalog.json').read_text())
    for row in details:
        row.update(artifact_status(root/'details'/row['key'],row['key'],detail=True))
    atomic_write(root/'details/catalog.json',dumps(details)+'\n')
    manifest=dict(version=1,classification='Practical teaching families, not exhaustive official LEGO categories',
                  source_date='2026-09-07',examples=rows,details=details)
    atomic_write(root/'catalog.json',dumps(manifest)+'\n')
    cards=[]
    for row in rows:
        key=row['key'];search=' '.join(str(row[k]) for k in ['key','title','category','lesson','modules'])
        cards.append(f'''<article data-search="{escape(search.casefold(),quote=True)}" data-scale="{row['scale']}">
<a href="{key}/README.md"><img class="building" data-key="{key}" src="{key}/home.png" alt="{escape(row['title'])}"></a>
<div class="copy"><p class="eyebrow">{escape(row['category'])} · {row['scale']}</p><h2>{escape(row['title'])}</h2>
<p>{escape(row['lesson'])}</p><p class="count">{row['physical_placements']} placements · {row['sections']} modules</p>
<p><a href="{row['model']}">MPD</a> · <a href="{row['plan']}">Plan</a> · <a href="{row['guide']}">Construction guide</a></p>
<details><summary>Where the details belong</summary><p>{escape(row['fit'])}</p><p>Avoid: {escape(row['avoid'])}</p>
<a href="{key}/validation.json">Checks</a> · <a href="{key}/bom-comparison.json">BOM</a> · <a href="{key}/visual-review.json">Visual review</a></details></div></article>''')
    detail_cards=[]
    for row in details:
        key=row['key']
        detail_cards.append(f'''<article><img src="details/{key}/home.png" alt="{escape(row['description'])}"><div class="copy"><h2>{escape(key)}</h2><p>{escape(row['description'])}</p>
<p><a href="{row['model']}">MPD</a> · <a href="{row['plan']}">Plan</a> · <a href="details/{key}/interface.json">Interface and envelope</a></p></div></article>''')
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>LDraw building atlas</title><style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f5f1e8;color:#202c2b;font:16px/1.5 system-ui}header,section{max-width:1520px;margin:auto;padding:32px}header{padding-top:64px}h1{font-size:clamp(32px,5vw,64px);line-height:1.05;margin:8px 0 24px}h2{font-size:21px;line-height:1.25;margin:8px 0 16px}header>p{max-width:780px}.eyebrow{text-transform:uppercase;font-size:11px;letter-spacing:.08em;color:#4d6e68}a{color:#245b51}nav{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:28px 0 0}input,select{font:inherit;padding:10px 12px;border:1px solid #8b9f98;border-radius:5px;background:white}input{flex:1;min-width:200px}main,.detail-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}article{background:white;border:1px solid #dbded4;border-radius:9px;overflow:hidden}article img{display:block;width:100%;aspect-ratio:5/4;object-fit:contain;background:#303436}.copy{padding:22px}p{margin:0 0 14px}.count{font-size:13px;color:#65716b}summary{cursor:pointer}details[open] summary{margin-bottom:12px}#count{margin:0 0 16px}footer{padding:32px;text-align:center;color:#65716b}[hidden]{display:none!important}@media(max-width:1000px){main,.detail-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:640px){main,.detail-grid{grid-template-columns:1fr}header,section{padding:22px}}</style></head><body>
<header><p class="eyebrow">A construction reference for generative agents</p><h1>Buildings with a sense of place.</h1><p>21 original studies across everyday, historic, natural and imagined settings. Choose a building family, study its silhouette and interfaces, then design a new composition.</p>
<p><a href="README.md">Start here</a> · <a href="../../docs/agent/building-atlas.md">Placement and aesthetic fit</a> · <a href="#details">Reusable details</a> · <a href="taxonomy.md">Families and sources</a></p>
<nav><input id="search" aria-label="Find buildings" placeholder="Find a family, feature or lesson…"><select id="scale" aria-label="Scale"><option value="all">All scales</option><option>minifigure</option><option>microscale</option></select><select id="view" aria-label="View"><option value="home">Home view</option><option value="front">Front elevation</option><option value="top">Site plan</option></select></nav></header>
<section><p id="count" aria-live="polite"></p><main>'''+''.join(cards)+'''</main></section>
<section id="details"><h1>Parts of a place.</h1><p>These modules include actual source, measured envelopes and local attachment frames. Check their containing scene as well as the isolated module.</p><div class="detail-grid">'''+''.join(detail_cards)+'''</div></section>
<footer>Actual LeoCAD geometry. Views are fitted independently; compare dimensions in the plans and reports. Checks and BOM agreement do not certify physical buildability.</footer>
<script>
const search=document.querySelector('#search'),scale=document.querySelector('#scale'),view=document.querySelector('#view'),cards=[...document.querySelectorAll('main article')];
function filter(){const terms=search.value.toLowerCase().split(/\\s+/).filter(Boolean);let n=0;for(const card of cards){card.hidden=!(terms.every(t=>card.dataset.search.includes(t))&&(scale.value==='all'||scale.value===card.dataset.scale));if(!card.hidden)n++}document.querySelector('#count').textContent=`${n} of ${cards.length} building studies`;}
search.addEventListener('input',filter);scale.addEventListener('change',filter);view.addEventListener('change',()=>{for(const img of document.querySelectorAll('img.building'))img.src=`${img.dataset.key}/${view.value}.png`});filter();
</script></body></html>'''
    atomic_write(root/'gallery.html',html)
    table='\n'.join(f'| {r["category"]} | [{r["title"]}]({r["key"]}/README.md) | {r["physical_placements"]} | {r["lesson"]} |' for r in rows)
    atomic_write(root/'examples-table.md','| Family | Generated example | Placements | Lesson |\n|---|---|---:|---|\n'+table+'\n')
    sources='\n'.join(f'| {r["category"]} | [{r["title"]}]({r["key"]}/README.md) | [LEGO family evidence]({r["source"]}) |' for r in rows)
    atomic_write(root/'taxonomy.md','''# Building families and source evidence

This is a practical teaching taxonomy based on the kinds of buildings represented in LEGO sets, including historic themes. It is an authored classification, not an official exhaustive list. Function, setting and scale overlap: a castle can also be a landmark, and a shop can sit inside a medieval village. Choose the closest family and combine lessons when a request crosses boundaries.

LEGO's [buildings category](https://www.lego.com/en-us/categories/buildings) explicitly spans modular city scenes, houses, castles and monuments. Official product/instruction pages below establish the wider range. Sources were checked on 2026-09-07; prices and retail availability are not used. The generated examples are original compositions, not replicas of these sets or copied instruction models.

| Teaching family | Original example | Primary source |
|---|---|---|
'''+sources+'\n\nThe frontier source is an official instruction booklet that depicts a Western sheriff/jail playset; the adventure source identifies The Temple of Anubis. No claims of historical or cultural reconstruction accuracy are made.\n')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    result=catalogue(p.parse_args().root)
    print(len(result['examples']),'building families and',len(result['details']),'detail examples indexed')
