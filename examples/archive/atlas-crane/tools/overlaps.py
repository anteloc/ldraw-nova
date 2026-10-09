"""Rank suspicious overlap candidates from a `validate --detail full` report.

Filters out connector parts (pins, axles, bushes) and pairs inside one adapted asset,
then lists pairs by their smallest penetration depth (largest first)."""
import json, sys, collections
rep = json.load(open(sys.argv[1]))
minpen = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
g = rep['geometry']
inst = {i['index'] if 'index' in i else k: i for k, i in enumerate(g['instances'])}
CONNECT = {'2780', '6558', '43093', '3673', '4274', '11214', '32062', '4519', '3705', '32073', '3706', '44294',
           '3707', '60485', '3737', '3708', '50451', '3713', '32123b', '32123a', '87083', '6628', '15100',
           '32556', '32054', '62462', '3749', '18651', '32002', '2736', '41677', '99773', '32235'}
def ref(i):
    return inst[i]['part'].replace('.dat', '')
def path(i):
    p = inst[i].get('placement_path') or inst[i].get('path') or inst[i].get('section_path') or []
    return p
def module(i):
    s = inst[i].get('section', '?').replace('.ldr', '')
    return s[:40]
rows = []
for o in g['overlaps']:
    a, b = o['instances']
    if ref(a) in CONNECT or ref(b) in CONNECT:
        continue
    ma, mb = module(a), module(b)
    if ma == mb and ('atc-v8' in ma or 'atc-i6' in ma or 'atc-hook' in ma or 'atc-tank' in ma or 'atc-exhaust' in ma):
        continue
    pen = min(o['depths'])
    if o['status'] == 'oriented_bounds_separated':
        continue
    if {ref(a), ref(b)} == {'32019', '86652'}:
        continue
    if pen < minpen:
        continue
    rows.append((pen, a, b, ref(a), ref(b), ma, mb, o['status']))
rows.sort(reverse=True)
print(len(rows), 'suspicious pairs (min depth >=', minpen, ')')
c = collections.Counter((r[5], r[6]) for r in rows)
for k, n in c.most_common(40):
    print(f'{n:4d}  {k[0]}  <->  {k[1]}')
print()
for r in rows[:int(sys.argv[3]) if len(sys.argv) > 3 else 60]:
    print(f'{r[0]:6.1f} {r[1]:4d}:{r[3]:<12s} {r[2]:4d}:{r[4]:<12s} {r[5]} | {r[6]} {r[7]}')
