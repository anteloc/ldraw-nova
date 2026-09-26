"""Point-level clearance check for the turntable base against the 11L beams and the centre pin.

Oriented bounding boxes cannot separate these parts. This samples the expanded geometry
points of 99009 (from the toolkit inspection) and tests them against the beams' solid
volume (1L slab minus the round bores) and the 87082 centre bulge. Points on faces
(within 0.05 LDU) count as touching, not penetration. Sampling, not a proof.
"""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import get_parts, jsonable
from ldraw_tools.connectivity import inspect_connections

EPS = 0.05
parts = get_parts()
_, model, _ = build_plan(load_plan(HERE/'turntable-frame.plan.json'), parts)
inspection = inspect_connections(model, parts)
occ = {o.index: o for o in inspection.occurrences}

def world_points(o):
    pts = np.array([jsonable(p) for p in o.local.points])
    return pts @ np.asarray(o.occurrence.matrix.rows).T + np.array(jsonable(o.occurrence.position))

def inside_beam(p, z0):
    x, y, z = p.T
    # 1L beam slab: y in [-10,10] (stud height side), z0 +/- 9 thick? use measured local bounds
    body = (np.abs(y) < 10-EPS) & (np.abs(z-z0) < 10-EPS) & (np.abs(x) < 100+10-EPS)
    ends = np.abs(x) > 100
    body &= ~ends | (np.hypot(np.abs(x)-100, y) < 10-EPS)
    holes = np.arange(-100, 101, 20)
    in_bore = np.min(np.abs(x[:, None]-holes[None, :]), axis=1)**2 + y**2 < 8.0**2 + EPS
    return body & ~in_bore

def inside_centre_bulge(p):
    x, y, z = p.T  # 87082 hub: vertical ring, outer radius 9, y in [-10,10], |z| <= 10
    return (np.hypot(x, z) < 9-EPS) & (np.hypot(x, z) > 6+EPS) & (np.abs(y) < 10-EPS)

base = [o for o in occ.values() if o.occurrence.part_code.lower().removesuffix('.dat') == '99009'][0]
pts = world_points(base)
print(f'99009 sampled points: {len(pts)}; y range {pts[:,1].min():.1f}..{pts[:,1].max():.1f}')
result = 0
for name, z0 in (('rear 11L beam', 20), ('front 11L beam', -20)):
    hits = pts[inside_beam(pts, z0)]
    print(f'{name}: {len(hits)} base points inside solid' + (f', e.g. {hits[:3].round(2).tolist()}' if len(hits) else ''))
    result |= bool(len(hits))
hits = pts[inside_centre_bulge(pts)]
print(f'87082 centre hub: {len(hits)} base points inside the hub ring' + (f', e.g. {hits[:3].round(2).tolist()}' if len(hits) else ''))
low = pts[pts[:, 1] > -10.5]
print(f'base points at or below beam top (y > -10.5): {len(low)}; their |z| max {np.abs(low[:,2]).max() if len(low) else None}')
sys.exit(result)
