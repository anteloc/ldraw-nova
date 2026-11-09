"""Per-submodel contract checker for the Linden Row SNOT run (orchestrator-owned; do not edit).

Usage (repo root):
  .venv/bin/python output/urban-house-snot/contract_check.py <built.mpd> [--module M] [--submodel S] [--json OUT]

Works on a module test harness (module placed at the origin) or on the whole scene (linden-row.ldr,
module origins from contracts.json). Every leaf part is attributed to the deepest contracted section in
its placement chain (uncontracted helper sections inherit their parent's owner). For each contracted
submodel it checks:
  exists/count   section present and placed `count` times by its declared `parent`
  envelope       every owned part's bounds inside the submodel envelope (module-local studs X/Z, h LDU up)
  connected      owned parts are in the scene's main contact group (blind-spot parts excepted)
  interfaces     contacts between owned parts and `part` ('*' = any part) inside submodel `mount` >= `min`
  forbid         optional boxes (module-local) no owned part may enter (reserved zones)
  colours        no colour 16/24 on leaves; duplicates: no identical placements
  max_h          optional: highest owned point <= max_h
  mirror_x       optional: owned parts mirror-symmetric about module X=0 (by bounds centre)
Module-level: parts owned by the module root directly (not inside a contracted submodel) are reported.
Exit code 0 = all PASS, 1 = any FAIL.
"""
import argparse, collections, json, subprocess, sys, tempfile, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOL = 0.6  # LDU
STUD = 4.0  # envelope tops tolerate exposed studs (part bounds include the 4 LDU stud); max_h does not


def parse_mpd(path):
    secs, order, cur = {}, [], None
    for line in open(path, encoding='utf-8'):
        t = line.split()
        if not t:
            continue
        if t[0] == '0' and len(t) > 2 and t[1] == 'FILE':
            cur = ' '.join(t[2:]).lower(); secs[cur] = []; order.append(cur)
        elif t[0] == '1' and cur is not None:
            secs[cur].append(' '.join(t[14:]).lower())
    return secs, order


def code(c):
    return c.get('code') if isinstance(c, dict) else c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mpd'); ap.add_argument('--module'); ap.add_argument('--submodel'); ap.add_argument('--json')
    a = ap.parse_args()
    C = json.load(open(HERE / 'contracts.json'))
    blind = {p.lower().replace('.dat', '') for p in C['blind_spot_parts']}
    secs, order = parse_mpd(a.mpd)
    root = order[0]
    scene = root == C['scene_root'].lower()
    subs = {}
    for mod, md in C['modules'].items():
        for s in md['submodels']:
            subs[s['name'].lower() + '.ldr'] = dict(s, module=mod)
    module_roots = {m + '.ldr': m for m in C['modules']}

    rep = tempfile.mktemp(suffix='.json')
    subprocess.run(['./ldraw-agent', 'inspect', a.mpd, '--contacts', 'all', '--detail', 'full', '--limit', '99999',
                    '--report', rep], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    g = json.load(open(rep))['geometry']; os.remove(rep)
    inst = {i['index']: i for i in g['instances']}
    comps = g['optimistic_components'] or [[]]
    main_group = set(max(comps, key=len))

    owner, module_of = {}, {}
    for i in g['instances']:
        s, chain = root, []
        for k in i['placement_path']:
            s = secs[s][k]; chain.append(s)
        mod = next((module_roots[c] for c in chain if c in module_roots), None)
        own = None
        for c in chain[:-1]:
            if c in subs:
                own = c
        owner[i['index']] = own or (mod + '.ldr' if mod else None)
        module_of[i['index']] = mod

    def origin(mod):
        return C['module_origins'][mod] if scene else [0, 0, 0]

    def local_box(i):
        o = origin(module_of[i['index']])
        (x0, y0, z0), (x1, y1, z1) = i['bounds']['min'], i['bounds']['max']
        return ((x0 - o[0]) / 20, (x1 - o[0]) / 20), (-(y1 - o[1]), -(y0 - o[1])), ((z0 - o[2]) / 20, (z1 - o[2]) / 20)

    owned = collections.defaultdict(list)
    for idx, o in owner.items():
        owned[o].append(idx)
    contacts = [tuple(c['instances']) for c in g['contacts']]

    present_modules = {m for m in module_of.values() if m}
    results = []
    for name, s in subs.items():
        if s['module'] not in present_modules:
            continue
        if a.module and s['module'] != a.module:
            continue
        if a.submodel and s['name'] != a.submodel:
            continue
        fails, notes = [], []
        if name not in secs:
            results.append(dict(submodel=s['name'], module=s['module'], status='FAIL', fails=['section missing'], notes=[]))
            continue
        parent = s['parent'].lower() + '.ldr'
        n = secs.get(parent, []).count(name)
        if n != s.get('count', 1):
            fails.append(f"placed {n}x by {s['parent']} (contract {s.get('count', 1)})")
        mine = [inst[i] for i in owned.get(name, [])]
        if not mine:
            fails.append('owns no parts')
        env = s['envelope']; tol_s = TOL / 20
        out = []
        top = None
        for i in mine:
            (xa, xb), (ha, hb), (za, zb) = local_box(i)
            top = hb if top is None else max(top, hb)
            if xa < env['x'][0] - tol_s or xb > env['x'][1] + tol_s or za < env['z'][0] - tol_s or zb > env['z'][1] + tol_s \
                    or ha < env['h'][0] - TOL or hb > env['h'][1] + STUD + TOL:
                out.append(f"{i['part']} x[{xa:.2f},{xb:.2f}] z[{za:.2f},{zb:.2f}] h[{ha:.0f},{hb:.0f}]")
        if out:
            fails.append(f'{len(out)} part(s) outside envelope: ' + '; '.join(out[:6]))
        for fb in s.get('forbid', []):
            hit = []
            for i in mine:
                (xa, xb), (ha, hb), (za, zb) = local_box(i)
                if xa < fb['x'][1] - tol_s and xb > fb['x'][0] + tol_s and za < fb['z'][1] - tol_s and zb > fb['z'][0] + tol_s \
                        and ha < fb['h'][1] - TOL and hb > fb['h'][0] + TOL:
                    hit.append(i['part'])
            if hit:
                fails.append(f"{len(hit)} part(s) inside forbidden zone {fb.get('why', fb)}: {', '.join(sorted(set(hit)))}")
        if 'max_h' in s and top is not None and top > s['max_h'] + TOL:
            fails.append(f"max_h {top:.0f} > {s['max_h']}")
        floating = [i for i in mine if i['index'] not in main_group and i['part'].lower().replace('.dat', '') not in blind]
        if floating:
            fails.append(f'{len(floating)} part(s) outside main contact group: ' +
                         '; '.join(f"{i['part']}@{[round(v) for v in i['position']]}" for i in floating[:8]))
        bs = [i for i in mine if i['index'] not in main_group and i['part'].lower().replace('.dat', '') in blind]
        if bs:
            notes.append(f'{len(bs)} blind-spot part(s) outside main group (accepted)')
        bad_col = [i for i in mine if code(i['colour']) in (16, 24, '16', '24')]
        if bad_col:
            fails.append(f'{len(bad_col)} part(s) with colour 16/24')
        seen = collections.Counter((i['part'], str(code(i['colour'])), tuple(round(v, 1) for v in i['position']),
                                    tuple(round(v, 3) for r in i['matrix'] for v in r)) for i in mine)
        d = sum(v - 1 for v in seen.values() if v > 1)
        if d:
            fails.append(f'{d} duplicate placement(s)')
        mine_set = {i['index'] for i in mine}
        for itf in s.get('interfaces', []):
            mount = itf['mount'].lower() + '.ldr'; part = itf['part'].lower().replace('.dat', '')
            cnt = 0
            for x, y in contacts:
                for p, q in ((x, y), (y, x)):
                    if p in mine_set and owner.get(q) == mount and (part == '*' or inst[q]['part'].lower().replace('.dat', '') == part):
                        cnt += 1
            line = f"interface -> {itf['mount']}/{itf['part']}: {cnt} contacts (min {itf['min']})"
            (fails if cnt < itf['min'] else notes).append(line)
        if s.get('mirror_x'):
            def key(i, flip):
                (xa, xb), (ha, hb), (za, zb) = local_box(i)
                cx = (xa + xb) / 2 * (-1 if flip else 1)
                return (i['part'], str(code(i['colour'])), round(cx * 2) / 2, round((ha + hb) / 2), round((za + zb) / 2 * 2) / 2)
            A = collections.Counter(key(i, False) for i in mine); B = collections.Counter(key(i, True) for i in mine)
            diff = sum((A - B).values())
            if diff:
                fails.append(f'mirror_x: {diff} part(s) without a mirrored counterpart')
        results.append(dict(submodel=s['name'], module=s['module'], parts=len(mine),
                            status='FAIL' if fails else 'PASS', fails=fails, notes=notes))
    stray = []
    for m in present_modules:
        if a.module and m != a.module:
            continue
        direct = owned.get(m + '.ldr', [])
        if direct:
            stray.append(dict(submodel=f'{m} (root, not in any submodel)', module=m, parts=len(direct), status='FAIL',
                              fails=[f'{len(direct)} part(s) placed directly in {m}.ldr, outside every contracted submodel: ' +
                                     ', '.join(sorted({inst[i]["part"] for i in direct}))[:200]], notes=[]))
    results += stray
    for r in results:
        print(f"{r['status']:4} {r['submodel']:<28} parts={r.get('parts', 0)}")
        for f in r['fails']:
            print('       FAIL ' + f)
        for n in r['notes']:
            print('       ok   ' + n)
    npass = sum(r['status'] == 'PASS' for r in results)
    print(f'--- {npass}/{len(results)} PASS; scene main group {len(main_group)}/{g["occurrence_count"]}')
    if a.json:
        json.dump(results, open(a.json, 'w'), indent=1)
    sys.exit(0 if npass == len(results) else 1)


if __name__ == '__main__':
    main()
