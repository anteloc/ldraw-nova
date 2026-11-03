"""Check the intended joints numerically: coaxial male/female connectors with real axial overlap.

Complements `ldraw-agent validate`, whose reviewed Technic registry does not yet cover
48989, 87082, 6629, 99009, 26287 and 32062. Uses the same connector metadata as
`ldraw-agent part` (LDCad shadow + primitive-derived) and the placed instance transforms.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
report = json.loads((HERE/'turntable-frame.validation.json').read_text())
inst = {i['index']: i for i in report['geometry']['instances']}
cache = {}

def connectors(part):
    if part not in cache:
        out = subprocess.run(['./ldraw-agent', 'part', part, '--limit', '1000'], capture_output=True, text=True, check=True).stdout
        cache[part] = json.loads(out)['connectors']
    return cache[part]

def spans(idx, female):
    o = inst[idx]; M = np.array(o['matrix']); t = np.array(o['position'])
    for c in connectors(o['part']):
        if (c['role'] == 'female') != female or c['kind'] not in ('pin', 'axle', 'pin_hole', 'axle_hole'):
            continue
        L = sum(s['length'] for s in c['profile']['sections'])
        axis = M @ np.array([row[1] for row in c['frame']]); p = t + M @ np.array(c['position'])
        lo, hi = (-L/2, L/2) if c['profile'].get('centered') else (0, L)
        yield c['kind'], p, axis/np.linalg.norm(axis), lo, hi

def joint(male, female):
    best = (0, None)
    for mk, mp, ma, mlo, mhi in spans(male, False):
        for fk, fp, fa, flo, fhi in spans(female, True):
            if abs(ma @ fa) < 0.9999:
                continue
            d = fp - mp; along = d @ ma; radial = np.linalg.norm(d - ma*along)
            if radial > 0.2:
                continue
            s = np.sign(ma @ fa)
            a, b = sorted((along + s*flo, along + s*fhi))
            ov = min(mhi, b) - max(mlo, a)
            if ov > best[0]:
                best = (round(ov, 2), f'{mk}->{fk} at {np.round(fp, 1).tolist()}')
    return best

JOINTS = [
    ('cross-left pins in B1', 6, 0), ('cross-left pins in B2', 6, 12),
    ('cross-right pins in B1', 7, 0), ('cross-right pins in B2', 7, 12),
    ('centre pin in B1', 5, 0), ('centre pin in B2', 5, 12),
    ('blue pin 5 through turntable lug', 8, 10), ('blue pin 7 through turntable lug', 9, 10),
    ('B1 pin 8 in rear-right arm', 3, 13), ('B1 pin 10 in rear-right arm', 4, 13),
    ('B1 pin 2 in rear-left arm', 1, 14), ('B1 pin 4 in rear-left arm', 2, 14),
    ('B2 pin 8 in front-right arm', 24, 25), ('B2 blue pin 10 in front-right arm', 22, 25),
    ('B2 pin 4 in front-left arm', 23, 26), ('B2 blue pin 2 in front-left arm', 21, 26),
    ('bend pin in front-right arm', 27, 25), ('bend pin in front-left arm', 28, 26),
    ('7L pin in front-right arm', 31, 25), ('7L pin in front-left arm', 30, 26),
    ('right link rear axle in joiner', 16, 15), ('right link front axle in joiner', 17, 15),
    ('right link rear axle in rear leg', 16, 13), ('right link front axle in front leg', 17, 25),
    ('left link rear axle in joiner', 19, 18), ('left link front axle in joiner', 20, 18),
    ('left link rear axle in rear leg', 19, 14), ('left link front axle in front leg', 20, 26),
]
failed = 0
for name, m, f in JOINTS:
    ov, where = joint(m, f)
    ok = ov >= 15
    failed += not ok
    print(f"{'OK ' if ok else 'BAD'} {name:38} {inst[m]['part']:>10} -> {inst[f]['part']:<10} overlap {ov:5} LDU  {where}")
print(f'{len(JOINTS)-failed}/{len(JOINTS)} joints engaged by >= 15 LDU')
sys.exit(1 if failed else 0)
