"""Source of contracts.json and the submodel tables in CONTRACTS.md (orchestrator-owned).
Run: .venv/bin/python output/urban-house-snot/contracts_src.py
Coordinates: module-local, X/Z in studs, h in LDU upward (h = -Y). Front = -Z.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent

def E(x, z, h):
    return dict(x=list(x), z=list(z), h=list(h))

def S(name, parent, env, purpose, frame='upright, studs up', count=1, mounts='', carries='', duties='',
      interfaces=(), snot=False, **kw):
    d = dict(name=name, parent=parent, count=count, envelope=env, purpose=purpose, build_frame=frame,
             mounts_on=mounts, carries=carries, duties=duties, snot=snot,
             interfaces=[dict(mount=m, part=p, min=n) for m, p, n in interfaces])
    d.update(kw)
    return d

FULL = E((-12, 12), (-8, 8), (0, 160))
FLAT = 'built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT'
AUDIT_SNOT = 'stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel'

MODULES = {
 'street': dict(worker='H5', origin=[0, 0, 0], submodels=[
  S('street-base', 'street', E((-16, 16), (-16, 16), (-4, 16)), '32x32 baseplate 3811, sidewalk paving (tiles), alley/garden paving; PLATE pads (not tiles) under every prop',
    mounts='scene origin', carries='every street submodel', duties='footprint bare; pads under props; no tile under any prop',
    forbid=[dict(x=[-12, 12], z=[-6, 10], h=[4.5, 999], why='house footprint (must stay bare baseplate studs)')]),
  S('street-kerb', 'street', E((-16, 16), (-17, -14), (0, 32)), 'kerb: dark grey 72 kerb course along the front edge with a SNOT tile face pointing -Z (sideways tiles on side-stud bricks)',
    frame=FLAT + ' (-Z)', snot=True, mounts='street-base', duties=AUDIT_SNOT,
    interfaces=[('street-base', '*', 4)]),
  S('street-lamp', 'street', E((-16, 16), (-16, -12), (0, 262)), 'slim fluted lamp post (architecture lamp() style; cap 98138 not 4589/6141)', count=2,
    mounts='street-base plate pads', duties='seated base; slim; |X|>=6; not hiding the shopfront', mirror_x=True),
  S('street-tree', 'street', E((-16, 16), (-16, -8), (0, 262)), 'street tree in a raised planter', count=2,
    mounts='street-base plate pads', duties='canopy inside the plot; clear of awning (ground awning spans X -10..10, Z -12..-8 of the house = scene Z -10..-6, h 100..132)', mirror_x=True),
  S('street-furniture', 'street', E((-16, 16), (-16, -6), (0, 80)), 'bench, fire hydrant, litter bin, post box',
    mounts='street-base plate pads', duties='every item seated on studs; facing the street/sidewalk sensibly',
    forbid=[dict(x=[-2, 2], z=[-8, -6], h=[4.5, 999], why='cafe doorway walkway')]),
  S('street-cafe-terrace', 'street', E((3, 11), (-12, -7), (0, 60)), 'cafe sidewalk table with 2 chairs facing it, maybe a parasol <=60 tall',
    mounts='street-base plate pads', duties='chairs face the table (check backrest direction vector)'),
  S('street-alley', 'street', E((-16, -12), (-6, 16), (0, 80)), 'side alley (left): paving 72, bins, a side gate'),
  S('street-garden', 'street', E((-16, 16), (-6, 16), (0, 120)), 'right hedge strip X 12..16 + back garden Z 10..16: closed fence/wall along the back edge, tidy shed with door and roof',
    forbid=[dict(x=[-12, 12], z=[-6, 10], h=[4.5, 999], why='house footprint')]),
  S('street-house-plaque', 'street-garden', E((-16, 16), (-6, 16), (0, 120)), 'house name/number plaque mounted SIDEWAYS on the garden wall or a gate pier (flat-built tile panel on side studs)',
    frame=FLAT, snot=True, duties=AUDIT_SNOT, interfaces=[('street-garden', '*', 2)]),
 ]),
 'ground': dict(worker='H1', origin=[0, 0, 40], submodels=[
  S('ground-slab', 'ground', E((-12, 12), (-8, 8), (0, 8)), 'floor slab 24x16 of plates on the baseplate, top h=8',
    carries='ground-walls, ground-interior', duties='full coverage; plates only'),
  S('ground-walls', 'ground', E((-12, 12), (-8.3, 8.3), (8, 152)), 'stone (72) wall core, 1 stud thick; front: piers X -12..-10 and 10..12, openings X -10..10 for the shopfront; side-stud bricks (30414/11211, studs -Z) in the pier courses and in the fascia course (top h=152) for the SNOT panels; side windows (window4) and back openings',
    mounts='ground-slab', carries='rustication, sign, awning, shopfront, rear', duties='openings match ground-shopfront/rear exactly; side-stud bricks exactly where the panels need them'),
  S('ground-rustication', 'ground', E((-12.5, 12.5), (-9, -7.5), (8, 128)), 'rusticated stone cladding panel for ONE front pier (2 wide, banded 72/19 tiles), placed twice (left pier, right pier)', count=2,
    frame=FLAT + ' (-Z)', snot=True, mounts='ground-walls side studs', duties=AUDIT_SNOT + '; both piers identical', mirror_x=True,
    interfaces=[('ground-walls', '*', 4)]),
  S('ground-shopfront', 'ground', E((-10, 10), (-8.5, -6), (8, 128)), 'two display windows >=96 LDU tall glazing (e.g. 1x4x5 frames 2493b + glass 2494, or 1x4x6 + glass) in 288 green, plus central door (X -2..2) in a 288 surround',
    mounts='ground-slab / ground-walls', duties='glazing >= 96 LDU tall; symmetric about X=0; door centred', mirror_x=False),
  S('ground-sign', 'ground', E((-10, 10), (-9, -7.5), (128, 156)), 'fascia SIGN: 288 board with a lettering-like pattern of 14/15 tiles, built FLAT, mounted on the fascia side-stud course',
    frame=FLAT + ' (-Z)', snot=True, mounts='ground-walls fascia side studs', duties=AUDIT_SNOT + '; reads as a sign; centred',
    interfaces=[('ground-walls', '*', 4)]),
  S('ground-awning', 'ground', E((-10, 10), (-12, -8), (100, 134)), 'sloped striped awning 288/15 over the shopfront, projecting to Z -12, underside >= h100, top <= h134',
    mounts='ground-walls / ground-shopfront (brackets, studs)', duties='every slope seated; stripes regular and symmetric; no floating valance',
    interfaces=[('ground-walls', '*', 2)]),
  S('ground-rear', 'ground', E((-12, 12), (6, 9), (8, 152)), 'rear facade details: back door, 2 windows, SNOT lintels/sills (tiles on side studs pointing +Z), a lamp',
    snot=True, frame='mixed; SNOT parts face +Z', mounts='ground-walls', duties=AUDIT_SNOT + '; rear must read as finished, not blank',
    interfaces=[('ground-walls', '*', 2)]),
  S('ground-interior', 'ground', E((-11, 11), (-7, 7), (8, 150)), 'cafe interior: counter with till/cakes, 2 tables with stools, shelf; clear of the doorway',
    mounts='ground-slab', duties='every item seated; stools around tables; nothing in the 4-stud door path'),
  S('ground-ring', 'ground', E((-12, 12), (-8, 8), (152, 160)), 'top interface: complete perimeter plate ring, top at h=160 (white 15)',
    mounts='ground-walls', carries='floor2-slab', duties='complete ring; top exactly h=160'),
 ]),
 'floor2': dict(worker='H2', origin=[0, -160, 40], submodels=[
  S('floor2-slab', 'floor2', E((-12, 12), (-10, 8), (0, 8)), 'floor slab: FOUR 6x16 plates 3027 running front-to-back (each rests on the front and back ring of the storey below) + bay floor plates to Z -10',
    carries='walls, bay, interior', duties='every slab plate rests on ring cells or is clutched by a plate that does'),
  S('floor2-walls', 'floor2', E((-12, 12), (-8.3, 8.3), (8, 152)), 'dark-red 320 brick wall core with window openings; side-stud bricks (studs -Z) where floor2-facade panels mount; headlight bricks 4070 for the window boxes',
    mounts='floor2-slab', carries='facade, window boxes, rear'),
  S('floor2-facade', 'floor2', E((-12, 12), (-9, -7.5), (8, 152)), 'front SNOT cladding: white window surrounds / tan sill bands / masonry texture panels around the two flanking windows (X -10..-6 and 6..10)',
    frame=FLAT + ' (-Z)', snot=True, duties=AUDIT_SNOT + '; symmetric', mirror_x=True,
    interfaces=[('floor2-walls', '*', 8)]),
  S('floor2-bay', 'floor2', E((-4, 4), (-10, -8), (8, 160)), 'glazed bay window, 8 wide, projecting to Z -10: >=60% glass, corbels below, sloped/tiled cap <= h160',
    mounts='floor2-slab bay plates', duties='reads as a glazed bay; supported; symmetric', mirror_x=True,
    interfaces=[('floor2-slab', '*', 2)]),
  S('floor2-window-box', 'floor2', E((-11, 11), (-10.5, -7.5), (8, 56)), 'flower box under each flanking window, front face SNOT-mounted on headlight bricks; flowers on studs', count=2,
    snot=True, frame='box upright; front face on 4070 side studs', duties=AUDIT_SNOT, mirror_x=True,
    interfaces=[('floor2-walls', '4070', 4)]),
  S('floor2-rear', 'floor2', E((-12, 12), (6, 9), (8, 152)), 'rear facade: 2 windows with SNOT white surrounds (+Z), a drainpipe or balconette',
    snot=True, frame='SNOT parts face +Z', duties=AUDIT_SNOT + '; rear reads finished', interfaces=[('floor2-walls', '*', 2)]),
  S('floor2-interior', 'floor2', E((-11, 11), (-7, 7), (8, 150)), 'living room: sofa facing a coffee table/TV, bookshelf, lamp, rug, plant',
    duties='every item seated on studs; sofa faces the table'),
  S('floor2-ring', 'floor2', E((-12, 12), (-8, 8), (152, 160)), 'top interface ring, top h=160', carries='floor3-slab'),
 ]),
 'floor3': dict(worker='H3', origin=[0, -320, 40], submodels=[
  S('floor3-slab', 'floor3', E((-12, 12), (-11, 8), (0, 8)), 'floor slab of 3027 6x16 plates front-to-back; balcony deck integrated (centre plates extend to Z -11)',
    duties='every slab plate rests on ring cells or is clutched; deck underside >= h0'),
  S('floor3-walls', 'floor3', E((-12, 12), (-8.3, 8.3), (8, 152)), 'dark-red 320 brick core; openings for French doors (X -2..2) and two tall flanking windows; side-stud courses for cornice and pilasters; side windows'),
  S('floor3-cornice', 'floor3', E((-12, 12), (-9, -7.5), (8, 40)), 'SNOT string course across the whole front: tan/white sideways plates + tiles (a 2-tone band)',
    frame=FLAT + ' (-Z)', snot=True, duties=AUDIT_SNOT + '; continuous across the front except the door opening', mirror_x=True,
    interfaces=[('floor3-walls', '*', 6)]),
  S('floor3-pilaster', 'floor3', E((-4, 4), (-9, -7.5), (8, 152)), 'white SNOT pilaster flanking the French doors (one section placed twice: X -3..-2 and 2..3)', count=2,
    frame=FLAT + ' (-Z)', snot=True, duties=AUDIT_SNOT, mirror_x=True, interfaces=[('floor3-walls', '*', 4)]),
  S('floor3-french-doors', 'floor3', E((-2, 2), (-8.5, -6), (8, 152)), 'pair of glazed French doors (white 15) in the X -2..2 opening'),
  S('floor3-balcony-rail', 'floor3', E((-6, 6), (-11, -8), (8, 56)), 'black 0 balcony railing ~40 tall around the deck edge, with 2 small planters',
    duties='continuous rail; posts seated; symmetric', mirror_x=True, interfaces=[('floor3-slab', '*', 4)]),
  S('floor3-windows', 'floor3', E((-12, 12), (-8.5, 8.5), (8, 152)), 'all window units of the storey (front flanking tall windows, 1 per side wall, 2 rear)',
    duties='frames seated in openings; glass in frames'),
  S('floor3-rear', 'floor3', E((-12, 12), (6, 9), (8, 152)), 'rear facade: SNOT window surrounds (+Z) and a string course matching the front',
    snot=True, frame='SNOT parts face +Z', duties=AUDIT_SNOT, interfaces=[('floor3-walls', '*', 2)]),
  S('floor3-interior', 'floor3', E((-11, 11), (-7, 7), (8, 150)), 'bedroom: bed, wardrobe, nightstand + lamp, rug', duties='seated; bed against a wall'),
  S('floor3-ring', 'floor3', E((-12, 12), (-8, 8), (152, 160)), 'top interface ring, top h=160', carries='roof-deck'),
 ]),
 'roof': dict(worker='H4', origin=[0, -480, 40], submodels=[
  S('roof-deck', 'roof', E((-12, 12), (-8, 8), (0, 16)), 'deck slab (plates spanning to the perimeter) + surface tiles; white 15 outer edge; plate pads under everything standing on it',
    duties='slab plates supported; nothing stands on tiles'),
  S('roof-parapet-front', 'roof', E((-12, 12), (-8.3, -6.5), (16, 96)), 'front parapet core (320) with side-stud courses for cornice and dentils; white coping',
    duties='continuous; coping 1 deep (Z -8..-7)'),
  S('roof-front-cornice', 'roof', E((-12, 12), (-9, -7.5), (0, 40)), 'white SNOT cornice band across the front at the base of the parapet',
    frame=FLAT + ' (-Z)', snot=True, duties=AUDIT_SNOT + '; the only roof part allowed to reach Z -9 besides dentils/pediment face', mirror_x=True,
    interfaces=[('roof-parapet-front', '*', 6)]),
  S('roof-dentils', 'roof', E((-12, 12), (-9, -7.5), (40, 88)), 'dentil course: alternating 98138 / 1x1 tiles on headlight bricks or a flat-built strip on side studs',
    snot=True, duties=AUDIT_SNOT + '; mirror-symmetric pattern', mirror_x=True, interfaces=[('roof-parapet-front', '*', 6)]),
  S('roof-pediment', 'roof', E((-4, 4), (-9, -6.5), (88, 150)), 'central pediment over the parapet with a SNOT nameplate (flat-built tile panel) and a stepped/triangular top',
    snot=True, frame='core upright; nameplate ' + FLAT, duties=AUDIT_SNOT + '; symmetric; reads as a pediment', mirror_x=True,
    interfaces=[('roof-parapet-front', '*', 2)]),
  S('roof-parapets', 'roof', E((-12, 12), (-8.3, 8.3), (16, 64)), 'side and back parapets: one brick course + white coping; gap where the stair-house meets the back wall'),
  S('roof-corner-pier', 'roof', E((-12, 12), (-9, -6), (16, 120)), 'white corner pier with urn (cap 98138), front corners; placed twice', count=2, mirror_x=True,
    duties='urn seated (98138, not 6141)'),
  S('roof-stair-house', 'roof', E((-6, 6), (2, 8), (16, 196)), 'stair-house with door4 facing front, lintel, roof (top <= 196)', duties='door faces the deck; closed walls; roof complete'),
  S('roof-skylight', 'roof-stair-house', E((-6, 6), (2, 8), (180, 200)), 'skylight on the stair-house roof, flush tiles, top <= h200', max_h=200,
    interfaces=[('roof-stair-house', '*', 2)]),
  S('roof-chimney', 'roof', E((7, 12), (-3, 5), (16, 190)), '2x2 brick chimney stack with cap and pots, against the right parapet'),
  S('roof-pergola', 'roof', E((-11, -1), (-6, 4), (16, 140)), 'timber pergola: 4 posts on pads, beams, evenly spaced slats', duties='4 posts seated; slats evenly spaced and centred'),
  S('roof-bistro-set', 'roof', E((-10, -2), (-5, 3), (16, 64)), 'bistro table + 4 chairs FACING the table, under the pergola', duties='chair backrests point AWAY from the table'),
  S('roof-planter', 'roof', E((-12, 12), (-8, 8), (16, 80)), 'planter box with plants that read as plants (leaves/flowers, not 2x2 round bricks); placed 3 times', count=3),
 ]),
}

def main():
    C = dict(scene_root='linden-row.ldr',
             module_origins={m: d['origin'] for m, d in MODULES.items()},
             blind_spot_parts=['60608', '3854', '60797c04', '57895', '60601', '4035', '60602', '60603', '4036', '2494'],
             modules={m: dict(worker=d['worker'], submodels=d['submodels']) for m, d in MODULES.items()})
    (HERE / 'contracts.json').write_text(json.dumps(C, indent=1))
    lines = []
    for m, d in MODULES.items():
        lines.append(f"\n### {m}.ldr — worker {d['worker']} (scene origin {d['origin']} LDU)\n")
        lines.append('| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |')
        lines.append('|---|---|---|---|---|---|---|---|')
        for k, s in enumerate(d['submodels'], 1):
            e = s['envelope']; itf = '; '.join(f"{i['mount']}/{i['part']} ≥{i['min']}" for i in s['interfaces']) or '—'
            extra = []
            if s.get('mirror_x'): extra.append('mirror-symmetric')
            if s.get('max_h'): extra.append(f"max_h {s['max_h']}")
            for fb in s.get('forbid', []): extra.append(f"forbid {fb['why']}")
            lines.append(f"| {k} | `{s['name']}.ldr`{' ✦' if s['snot'] else ''} | {s['count']} | {s['parent']} | {e['x']} / {e['z']} / {e['h']} | {s['build_frame']} | {itf} | {s['purpose']}. **Check:** {s['duties'] or 'seated, inside envelope, reads as what it is'}{'; ' + ', '.join(extra) if extra else ''} |")
    (HERE / 'submodel-tables.md').write_text('\n'.join(lines) + '\n')
    print(sum(len(d['submodels']) for d in MODULES.values()), 'submodels')

if __name__ == '__main__':
    main()
