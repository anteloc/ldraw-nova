"""Small offline visual selection boards made from actual LeoCAD geometry."""
from html import escape
from pathlib import Path

from ldraw import inspect_model

from .builder import build_plan
from .catalog import resolve_part, resolve_colour
from .common import atomic_write, dumps, jsonable
from .external import render


def part_board(refs, parts, library, outdir, *, colour=19, timeout=90):
    if not 1<=len(refs)<=12:raise ValueError('A part board takes 1–12 references; curate a shortlist first')
    if isinstance(colour,str):
        colour=resolve_colour(colour,parts) if colour.startswith('@') else int(colour)
    if colour in {16,24} or colour not in parts.colours_by_code:raise ValueError('Choose an explicit installed surface colour')
    outdir=Path(outdir).resolve();outdir.mkdir(parents=True,exist_ok=True)
    cards=[];records=[]
    for index,ref in enumerate(refs):
        code=(resolve_part(ref,parts) if ref.startswith('@') else ref).casefold().removesuffix('.dat')
        plan=dict(version=1,author='ldraw-nova part board',sections=[dict(name='part-preview.ldr',description=f'Part preview: {code}',steps=[[dict(id='candidate',ref=code+'.dat',colour=colour,at=[0,0,0])]])])
        text,model,diagnostics=build_plan(plan,parts)
        if any(d['severity']=='error' for d in diagnostics):raise ValueError(f'Cannot preview {ref}: {dumps(diagnostics)}')
        inspection=inspect_model(model,parts)
        if not inspection.complete:raise ValueError(f'Incomplete geometry for {ref}')
        folder=outdir/f'{index:02d}';source=folder/'part.mpd';atomic_write(source,text)
        render(source,library,folder,views=['home'],timeout=timeout,bounds=inspection.bounds)
        g=parts.geometry(code)
        size=jsonable(g.bounds.size)
        record=dict(ref=ref,filename=code+'.dat',description=parts.by_code.get(code,''),size_ldu=size,colour=colour,
                    bounds=jsonable(g.bounds),image=f'{index:02d}/home.png',source=f'{index:02d}/part.mpd',diagnostics=diagnostics)
        records.append(record)
        cards.append(f'<article><img src="{record["image"]}" alt="{escape(record["description"],quote=True)}"><h2>{escape(record["description"])}</h2><code>{escape(ref)}</code><p>{escape(code)}.dat · {" × ".join(f"{v:g}" for v in size)} LDU</p><a href="{record["source"]}">Inspect source</a></article>')
    html='<!doctype html><html lang="en"><meta charset="utf-8"><title>LDraw part shortlist</title><style>body{font:16px system-ui;margin:32px;background:#f5f2eb;color:#21292b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:24px}article{background:white;padding:18px;border-radius:12px}img{width:100%;height:230px;object-fit:contain}h2{font-size:18px}code{overflow-wrap:anywhere}a{color:#245e54}</style><h1>Part shortlist</h1><p>Actual library geometry. Each view is fitted independently: compare the listed dimensions, not image size. Bounds include studs and decoration; they are not stacking heights.</p><main>'+''.join(cards)+'</main></html>'
    atomic_write(outdir/'index.html',html)
    atomic_write(outdir/'board.json',dumps(records)+'\n')
    return dict(board=str(outdir/'index.html'),manifest=str(outdir/'board.json'),parts=records)
