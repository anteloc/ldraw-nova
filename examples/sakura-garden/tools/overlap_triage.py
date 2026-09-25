"""Triage bounding-box overlap candidates from an `inspect --detail full` report.

Groups candidate pairs by (part, part, status) and flags pairs whose overlap
depths exceed stud engagement in all three axes. The flag is a review aid,
not a collision proof: hollow and irregular parts overlap in bounds legally.
"""
import json
import sys
from collections import Counter, defaultdict

report = json.load(open(sys.argv[1]))
g = report.get('geometry', report)
inst = {i['index']: i for i in g['instances']}
groups = Counter()
deep = defaultdict(list)
for o in g['overlaps']:
    a, b = (inst[k] for k in o['instances'])
    key = tuple(sorted([a['part'], b['part']])) + (o['status'],)
    groups[key] += 1
    dx, dy, dz = o['depths']
    if o['status'] != 'oriented_bounds_separated' and min(dx, dz) > 2 and dy > 4.5:
        deep[key].append((round(dx, 1), round(dy, 1), round(dz, 1), a['section'], a['position'],
                          b['section'], b['position']))
for key, n in groups.most_common():
    flag = f'  DEEP x{len(deep[key])}' if deep[key] else ''
    print(f'{n:5d}  {key[0]:>12} {key[1]:>12}  {key[2]}{flag}')
if '--deep' in sys.argv:
    for key, rows in deep.items():
        print('==', key)
        for r in rows[:6]:
            print('   ', r)
