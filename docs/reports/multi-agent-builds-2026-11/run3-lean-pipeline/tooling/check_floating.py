"""List parts outside the main connected group of the WHOLE scene, by module (orchestrator tool).
Usage (repo root): .venv/bin/python output/urban-house/check_floating.py <scene.mpd> [module]
Ignore known analyzer blind spots: clipped glass panes (60608, 3854, 60797c04, 57895, 60601, 4035...),
1x1 round plates/flowers on tiles. Anything structural (plates, bricks, props) listed here is unsupported.
"""
import json, subprocess, sys, collections, tempfile, os
mpd = sys.argv[1]; only = sys.argv[2] if len(sys.argv) > 2 else None
MODS = ['street', 'ground', 'floor2', 'floor3', 'roof']
rep = tempfile.mktemp(suffix='.json')
subprocess.run(['./ldraw-agent', 'inspect', mpd, '--contacts', 'all', '--detail', 'full', '--limit', '9999',
                '--report', rep], check=False, stdout=subprocess.DEVNULL)
g = json.load(open(rep))['geometry']; os.remove(rep)
inst = {i['index']: i for i in g['instances']}; comps = g['optimistic_components']
main = max(comps, key=len)
print(f"parts {g['occurrence_count']}, groups {len(comps)}, main group {len(main)}")
out = collections.defaultdict(list)
for c in comps:
    if c is main: continue
    for i in c:
        p = inst[i]; mod = MODS[p['placement_path'][0]] if p['placement_path'] else 'scene'
        out[mod].append(f"{p['part']:<14} world {[round(v) for v in p['position']]} group-size {len(c)} src {p['section']}:{p['line_number']}")
for m, v in out.items():
    if only and m != only: continue
    print(f'== {m}: {len(v)} parts outside main group'); print('\n'.join('   ' + x for x in v))
