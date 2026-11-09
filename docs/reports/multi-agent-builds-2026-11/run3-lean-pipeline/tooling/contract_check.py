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


import numpy as np

SIDE_STUDS = {'30414': [(-30, 10, -10), (-10, 10, -10), (10, 10, -10), (30, 10, -10)],
              '11211': [(-10, 10, -10), (10, 10, -10)], '87087': [(0, 10, -10)], '4070': [(0, 10, -6)]}
SEE_THROUGH = {'30055', '2432', '6141', '24866', '4589', '3062b'}
LEAVES = {'60623', '60616a', '60797c04', '60797', '3644'}
FRAMES = {'60594', '60596', '2493b', '2493', '60593', '60592', '60598', '4033', '4132', '30044', '57894', '60599', '3853', '3854', '2494', '4035', '60032'}
STUDDED = {'3024', '3023b', '3023', '3623', '3710', '3666', '3460', '3022', '3020', '3021', '3795', '3034', '3031', '3032',
           '3035', '3036', '3027', '4282', '3005', '3004', '3622', '3010', '3009', '3008', '3003', '3001', '3002', '3007'}
GLASS = {'60608', '3854', '60797c04', '57895', '60601', '2494', '4036', '60602', '60603', '4035', '3855', '60803'}


def is_trans(c):
    try:
        c = int(c)
    except (TypeError, ValueError):
        return False
    return 33 <= c <= 47 or c in (52, 54, 57, 182, 230, 231, 234, 236)


def visual_checks(g, inst, owner, module_of, origin, local_box, C):
    """Module/scene-mode checks for defects found by eye in run 2: exposed SNOT side studs and glass
    with an opaque body right behind it (within 12 LDU, inward)."""
    out = []
    boxes = [(i['index'], np.array(i['bounds']['min']), np.array(i['bounds']['max'])) for i in g['instances']]
    exposed = {}
    for i in g['instances']:
        ref = i['part'].lower().replace('.dat', '')
        if ref not in SIDE_STUDS:
            continue
        M = np.array(i['matrix']); P = np.array(i['position'])
        d = M @ np.array([0, 0, -1.0])
        for q in SIDE_STUDS[ref]:
            pt = P + M @ np.array(q, float) + 3 * d
            hit = any(j != i['index'] and np.all(pt >= lo - 1) and np.all(pt <= hi + 1) for j, lo, hi in boxes)
            if not hit:
                o = origin(module_of[i['index']]) if module_of[i['index']] else [0, 0, 0]
                loc = [float(round((pt[0] - 3 * d[0] - o[0]) / 20, 1)), int(round(-(pt[1] - o[1]))), float(round((pt[2] - 3 * d[2] - o[2]) / 20, 1))]
                exposed.setdefault(owner.get(i['index']) or '?', []).append(loc)
    for own, locs in exposed.items():
        out.append(dict(submodel=f'VISUAL exposed side studs ({own})', module=own.split('-')[0], parts=len(locs), status='FAIL',
                        fails=[f'{len(locs)} side stud(s) with nothing mounted on them (x studs, h, z studs): ' + '; '.join(map(str, locs[:8]))],
                        notes=[], locs=locs))
    backed, blocked = {}, {}
    for i in g['instances']:
        ref = i['part'].lower().replace('.dat', '')
        col = i['colour'].get('code') if isinstance(i['colour'], dict) else i['colour']
        if ref not in GLASS and not (is_trans(col) and ref not in STUDDED):
            continue
        mod = module_of[i['index']]
        if not mod or mod == 'street':
            continue
        (xa, xb), (ha, hb), (za, zb) = local_box(i)
        if (hb - ha) < 0.5 * 20 * max(xb - xa, zb - za):
            continue                      # horizontal glass (skylight): not a facade pane
        cx, cz = (xa + xb) / 2, (za + zb) / 2
        lo = np.array(i['bounds']['min'], float); hi = np.array(i['bounds']['max'], float)
        if cz < -6.5: ax, sgn = 2, 1
        elif cz > 6.5: ax, sgn = 2, -1
        elif cx < -10.5: ax, sgn = 0, 1
        elif cx > 10.5: ax, sgn = 0, -1
        else:
            continue
        tlo, thi = lo.copy(), hi.copy()
        span = thi - tlo
        for k in range(3):
            if k != ax:
                tlo[k] += 0.25 * span[k]; thi[k] -= 0.25 * span[k]
        if sgn > 0:
            tlo[ax], thi[ax] = hi[ax] + 2, hi[ax] + 12
        else:
            tlo[ax], thi[ax] = lo[ax] - 12, lo[ax] - 2
        mine = owner.get(i['index'])
        # outward box: what stands right in front of the pane (blocked window)
        olo, ohi = tlo.copy(), thi.copy()
        if sgn > 0:
            olo[ax], ohi[ax] = lo[ax] - 30, lo[ax] - 2
        else:
            olo[ax], ohi[ax] = hi[ax] + 2, hi[ax] + 30
        covered, culprits = 0.0, []
        for j, blo, bhi in boxes:
            jj = inst[j]
            jcol = jj['colour'].get('code') if isinstance(jj['colour'], dict) else jj['colour']
            jref = jj['part'].lower().replace('.dat', '')
            if j == i['index'] or (is_trans(jcol) and jref not in STUDDED) or jref in GLASS | SEE_THROUGH | FRAMES | LEAVES:
                continue
            if jj.get('section') == i.get('section'):
                continue
            ov = np.clip(np.minimum(ohi, bhi) - np.maximum(olo, blo), 0, None)
            if np.any(ov <= 0):
                continue
            area = [ov[k] for k in range(3) if k != ax]
            full = [ohi[k] - olo[k] for k in range(3) if k != ax]
            frac = area[0] * area[1] / (full[0] * full[1])
            covered += frac
            culprits.append((frac, f"{jj['part']}({owner.get(j)})", owner.get(j) or '?'))
        if culprits and covered >= 0.5:
            culprits.sort(reverse=True)
            own_b = culprits[0][2]
            culprits = [c[1] for c in culprits]
            blocked.setdefault(own_b, []).append(f"{i['part']}({mine}) at x{round(cx,1)} h{round((ha+hb)/2)} z{round(cz,1)} covered {min(covered,1):.0%} by {', '.join(sorted(set(culprits))[:3])}")
        for j, blo, bhi in boxes:
            jj = inst[j]
            jcol = jj['colour'].get('code') if isinstance(jj['colour'], dict) else jj['colour']
            if j == i['index'] or owner.get(j) == mine or is_trans(jcol) or jj['part'].lower().replace('.dat', '') in GLASS:
                continue
            ov = np.clip(np.minimum(thi, bhi) - np.maximum(tlo, blo), 0, None)
            area = [ov[k] for k in range(3) if k != ax]
            full = [thi[k] - tlo[k] for k in range(3) if k != ax]
            if ov[ax] > 0 and area[0] * area[1] >= 0.5 * full[0] * full[1]:
                backed.setdefault(mine or '?', []).append(f"{i['part']} behind by {jj['part']}({owner.get(j)}) at x{round(cx,1)} h{round((ha+hb)/2)} z{round(cz,1)}")
                break
    for own, items in blocked.items():
        out.append(dict(submodel=f'VISUAL window blocked from outside ({own})', module=own.split('-')[0], parts=len(items), status='FAIL',
                        fails=[f'{len(items)} window pane(s) blocked by your part(s) within 30 LDU in front: ' + '; '.join(items[:5])], notes=[]))
    # 2) bare studs facing out of a facade (sideways studded plates/bricks with nothing on their studs)
    bare = {}
    for i in g['instances']:
        ref = i['part'].lower().replace('.dat', '')
        if ref not in STUDDED or ref in SIDE_STUDS:
            continue
        M = np.array(i['matrix']); up = M @ np.array([0, -1.0, 0])
        if abs(up[1]) > 0.5:
            continue
        a = int(np.argmax(np.abs(up))); sg = np.sign(up[a])
        lo = np.array(i['bounds']['min'], float); hi = np.array(i['bounds']['max'], float)
        tlo, thi = lo.copy(), hi.copy()
        for k in range(3):
            if k != a:
                span = hi[k] - lo[k]; tlo[k] += 0.3 * span; thi[k] -= 0.3 * span
        f = hi[a] if sg > 0 else lo[a]
        tlo[a], thi[a] = (f - 3, f + 2) if sg > 0 else (f - 2, f + 3)
        hit = any(j != i['index'] and np.all(np.minimum(thi, bhi) - np.maximum(tlo, blo) > 0) for j, blo, bhi in boxes)
        if not hit:
            (xa, xb), (ha, hb), (za, zb) = local_box(i)
            bare.setdefault(owner.get(i['index']) or '?', []).append(f"{i['part']} x{round((xa+xb)/2,1)} h{round((ha+hb)/2)} z{round((za+zb)/2,1)}")
    for own, items in bare.items():
        out.append(dict(submodel=f'VISUAL bare studs facing out ({own})', module=own.split('-')[0], parts=len(items), status='FAIL',
                        fails=[f'{len(items)} sideways plate/brick(s) show bare studs on a facade (cover them with tiles): ' + '; '.join(items[:6])], notes=[]))
    # 3) deep interpenetration (oriented bounds overlap > 4.5 LDU on every axis), frame/glass/leaf pairs excluded
    deep = {}
    for o in g.get('overlaps') or []:
        if min(o['depths']) <= 4.5:
            continue
        a_, b_ = [inst[k] for k in o['instances']]
        refs = {a_['part'].lower().replace('.dat', ''), b_['part'].lower().replace('.dat', '')}
        if refs & (GLASS | LEAVES) or (a_['section'] == b_['section'] and any(t in (a_['section'] or '') for t in ('window4', 'door4'))):
            continue
        oa, ob = owner.get(a_['index']) or '?', owner.get(b_['index']) or '?'
        for own in {oa, ob}:
            deep.setdefault(own, []).append(f"{a_['part']}({oa}) x {b_['part']}({ob}) depth {min(o['depths']):.0f}")
    for own, items in deep.items():
        out.append(dict(submodel=f'VISUAL interpenetration ({own})', module=own.split('-')[0], parts=len(items), status='FAIL',
                        fails=[f'{len(items)} deep part overlap(s) (parts inside each other): ' + '; '.join(items[:6])], notes=[]))
    for own, items in backed.items():
        out.append(dict(submodel=f'VISUAL glass backed by opaque ({own})', module=own.split('-')[0], parts=len(items), status='FAIL',
                        fails=[f'{len(items)} glass part(s) with an opaque part within 12 LDU behind: ' + '; '.join(items[:5])], notes=[]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mpd'); ap.add_argument('--module'); ap.add_argument('--submodel'); ap.add_argument('--json')
    ap.add_argument('--only', help='comma list of submodels to report'); ap.add_argument('--no-visual', action='store_true')
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
    CORE_SECS = {'ground-slab', 'ground-walls', 'ground-ring', 'floor2-slab', 'floor2-walls', 'floor2-ring', 'floor3-slab',
                 'floor3-walls', 'floor3-ring', 'roof-deck', 'street-base'}
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

    # main group = the component holding the most structural (core) parts, not merely the largest one
    anchors = {i for i, o in owner.items() if o and o.replace('.ldr', '') in CORE_SECS}
    if anchors:
        main_group = set(max(comps, key=lambda c: (len(anchors & set(c)), len(c))))

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
        if a.only and s['name'] not in a.only.split(','):
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
    if not a.submodel and not a.only and not a.no_visual:
        results += visual_checks(g, inst, owner, module_of, origin, local_box, C)
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
