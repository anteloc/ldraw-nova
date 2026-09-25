"""Summarise connector components from `inspect --contacts all --detail full`.

Prints the main component size and every smaller group as section + parts, so
each can be explained (metadata gap, deliberately loose, or floating).
"""
import json
import sys
from collections import Counter

d = json.load(open(sys.argv[1]))
g = d.get('geometry', d)
inst = {i['index']: i for i in g['instances']}
comps = sorted(g.get('optimistic_components') or [], key=len, reverse=True)
print('components', len(comps), 'sizes', [len(c) for c in comps[:5]], 'truncated', g.get('components_truncated'))
kinds = Counter()
for c in comps[1:]:
    parts = tuple(sorted(inst[k]['part'].removesuffix('.dat') for k in c))
    secs = tuple(sorted({inst[k]['section'] for k in c}))
    kinds[(secs, parts)] += 1
for (secs, parts), n in kinds.most_common():
    print(f'{n:3d} x  {",".join(secs)[:48]:48}  {" ".join(parts)[:90]}')
