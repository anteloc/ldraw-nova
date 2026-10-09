"""Print a part's measured bounds and connector positions/axes (axis = frame column 1)."""
import json, subprocess, sys

def probe(ref, kinds=None, limit=200):
    r = subprocess.run(['./ldraw-agent', 'part', ref, '--limit', str(limit)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    out = []
    for c in d.get('connectors', []):
        if kinds and c['kind'] not in kinds:
            continue
        f = c.get('frame')
        axis = [f[0][1], f[1][1], f[2][1]] if f else None
        out.append((c['kind'], [round(v, 2) for v in c['position']], [round(v, 2) for v in axis] if axis else None, c.get('feature_id')))
    return d, out

if __name__ == '__main__':
    kinds = None
    args = sys.argv[1:]
    if args and args[0].startswith('--kinds='):
        kinds = set(args[0][8:].split(','))
        args = args[1:]
    for ref in args:
        d, out = probe(ref, kinds)
        b = d.get('bounds') or {}
        print(f"## {ref} {d['metadata']['description']} min {[round(v,1) for v in b.get('min',[])]} max {[round(v,1) for v in b.get('max',[])]} conn={d.get('connector_count')}")
        for k, p, a, fid in out:
            print(f"   {k:10s} {p} axis {a}")
