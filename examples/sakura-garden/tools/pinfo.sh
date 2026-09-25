#!/bin/sh
# Compact bounds/stud summary for one or more parts.
cd "$(dirname "$0")/../../.." || exit 2
for p in "$@"; do
  ./ldraw-agent part "$p" --limit 60 2>/dev/null | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception: print('$p: NOT FOUND'); sys.exit()
m=d['metadata']; b=d.get('bounds') or {}
st=d.get('stud_positions') or []
ys=sorted({round(s[1],1) for s in st})
kinds={}
for c in d.get('connectors',[]): kinds[c.get('kind')]=kinds.get(c.get('kind'),0)+1
print('%-10s %-58s min=%s max=%s studs=%d@y%s conn=%s %s' % ('$p', m['description'][:58], [round(v,1) for v in b.get('min',[])], [round(v,1) for v in b.get('max',[])], len(st), ys, kinds, (m.get('status') or '')+(' ->'+str(m.get('replacement')) if m.get('replacement') else '')))
"
done
