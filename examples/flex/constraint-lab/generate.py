"""Executable constraint experiments using real LSynth output, never a replica.

Run from the repository root:
  .venv/bin/python examples/flex/constraint-lab/generate.py --outdir output/flex-lab
  .venv/bin/python examples/flex/constraint-lab/generate.py --outdir output/flex-families --families

These are geometry fixtures, not mechanically supported assemblies. The complete
pneumatic press remains the reference for fitting ownership and physical mounts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))

from ldraw_tools import flex  # noqa: E402
from ldraw_tools.common import get_parts  # noqa: E402
from ldraw_tools.flex_authoring import Endpoint, Waypoint, band, document, hose, placement  # noqa: E402
from ldraw_tools.flex_constraints import check  # noqa: E402
from ldraw_tools.flex_review import check_asset  # noqa: E402


def corner(radius=32, *, midpoint=False, z=0, method='TECHNIC_PNEUMATIC_HOSE_BEVELED', name='corner'):
    r=radius
    via=[Waypoint((0,0,z),(1,0,0),(0,0,1))]
    if midpoint:
        via.append(Waypoint((r/np.sqrt(2),-r+r/np.sqrt(2),z),(1,-1,0),(0,0,1)))
    via.append(Waypoint((r,-r,z),(0,-1,0),(0,0,1)))
    return hose(Endpoint((-60,0,z),(1,0,0),up=(0,0,1)),
                Endpoint((r,-r-60,z),(0,1,0),up=(0,0,1)),via=via,method=method,name=name)


def cases():
    yield 'straight',hose(Endpoint((0,0,0),(1,0,0),22),Endpoint((160,0,0),(-1,0,0),22))
    for r in (6,24,32,48):
        yield f'corner-{r}',corner(r)
    yield 'corner-32-midpoint',corner(32,midpoint=True)
    yield 'bundle',corner(48,name='lower')+corner(48,z=12,name='upper')
    yield 'return',hose(Endpoint((-60,0,0),(1,0,0),up=(0,0,1)),
        Endpoint((-60,-96,0),(1,0,0),up=(0,0,1)),via=[
            Waypoint((0,0,0),(1,0,0),(0,0,1)),Waypoint((48,-48,0),(0,-1,0),(0,0,1)),
            Waypoint((0,-96,0),(-1,0,0),(0,0,1))],name='return')


def family_cases():
    cfg,_,_=flex.engine()
    for h in cfg.hose_types:
        # A straight route is a synthesis smoke test, not a claimed manufactured length.
        yield h.type.lower(),hose(Endpoint((0,0,0),(1,0,0),up=(0,0,1)),
            Endpoint((400,0,0),(-1,0,0),up=(0,0,1)),method=h.type,name=h.type)
    for b in cfg.band_types:
        part=('4019.dat' if b.type in {'TECHNIC_CHAIN_LINK','CHAIN'} else
              '3736.dat' if b.type=='TECHNIC_CHAIN_LINK_WITH_TWO_STUDS' else
              '57519.dat' if b.type=='TECHNIC_CHAIN_TREAD_38' else '4185.dat')
        yield b.type.lower(),band([placement(part,(-100,0,0)),placement(part,(100,0,0))],method=b.type,name=b.type)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--outdir',type=Path,default=ROOT/'output/flex-lab')
    p.add_argument('--families',action='store_true',help='Smoke-test all installed definitions; report unsupported dependencies')
    p.add_argument('--force',action='store_true',help='Overwrite previously generated experiment files')
    a=p.parse_args()
    if a.outdir.exists() and any(a.outdir.iterdir()) and not a.force:
        p.error('Output is nonempty; choose a new directory or explicitly --force generated experiment files')
    a.outdir.mkdir(parents=True,exist_ok=True)
    parts=get_parts()
    rows=[]
    for name,source in family_cases() if a.families else cases():
        folder=a.outdir/name
        folder.mkdir(exist_ok=True)
        src,dst=folder/'constraints.ldr',folder/'asset.mpd'
        src.write_bytes(document(source,name='constraints.ldr').encode())
        row=dict(name=name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
        try:
            lint=check(src)
            (folder/'constraints.json').write_text(json.dumps(lint,indent=2)+'\n')
            if not lint['checks_passed']:
                raise ValueError('Constraint checks failed; read constraints.json')
            flex.build(src,dst,parts,force=a.force)
            report=check_asset(src,dst,**({} if a.families else dict(min_radius=15,tube_radius=5)))
            (folder/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
            row.update(synthesized=True,checks_passed=report['checks_passed'],
                       measurements=report['measurements'],diagnostics=report['diagnostics'])
        except ValueError as e:
            row.update(synthesized=False,checks_passed=False,error=str(e))
        rows.append(row)
        print(name, 'measured' if row.get('synthesized') else row.get('error'), flush=True)
    report=dict(engine=flex.availability(),scope='geometry fixtures, not physical approvals',
                geometric_limits=None if a.families else dict(min_radius=15,tube_radius=5),cases=rows)
    (a.outdir/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(a.outdir/'results.json')


if __name__=='__main__':
    main()
