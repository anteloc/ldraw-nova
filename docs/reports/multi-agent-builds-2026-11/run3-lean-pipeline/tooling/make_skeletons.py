"""Generate contracts.json, module generate.py files, task briefs and tasks.json (orchestrator-owned).
Run from repo root: .venv/bin/python output/urban-house-run3/make_skeletons.py
"""
import json, subprocess, sys
from pathlib import Path
RUN = Path(__file__).resolve().parent
REPO = RUN.parents[1]
subprocess.run([sys.executable, str(RUN / 'contracts_src.py')], check=True, capture_output=True)
sys.path.insert(0, str(RUN)); sys.path.insert(0, str(REPO))
from lib.storey_core import mounts, CORE  # noqa: E402

C = json.loads((RUN / 'contracts.json').read_text())
SUB = {s['name']: dict(s, module=m) for m, d in C['modules'].items() for s in d['submodels']}

TASKS = [
    ('T01', 'ground', ['ground-rustication', 'ground-shopfront']),
    ('T02', 'ground', ['ground-sign', 'ground-awning']),
    ('T03', 'ground', ['ground-rear']),
    ('T04', 'ground', ['ground-interior']),
    ('T05', 'floor2', ['floor2-facade', 'floor2-window-box']),
    ('T06', 'floor2', ['floor2-bay']),
    ('T07', 'floor2', ['floor2-rear', 'floor2-interior']),
    ('T08', 'floor3', ['floor3-cornice', 'floor3-pilaster']),
    ('T09', 'floor3', ['floor3-french-doors', 'floor3-balcony-rail', 'floor3-windows']),
    ('T10', 'floor3', ['floor3-rear', 'floor3-interior']),
    ('T11', 'roof', ['roof-parapet-front', 'roof-front-cornice', 'roof-dentils', 'roof-pediment']),
    ('T12', 'roof', ['roof-parapets', 'roof-corner-pier', 'roof-chimney']),
    ('T13', 'roof', ['roof-stair-house', 'roof-skylight']),
    ('T14', 'roof', ['roof-pergola', 'roof-bistro-set', 'roof-planter']),
    ('T15', 'street', ['street-base', 'street-kerb', 'street-lamp', 'street-tree']),
    ('T16', 'street', ['street-furniture', 'street-cafe-terrace', 'street-alley', 'street-garden', 'street-house-plaque']),
]

LAYOUT = {
    'ground': """Existing structure (do not rebuild): slab h0..8; stone (72) walls courses k=0..5 (body h 8+24k..32+24k), ring h152..160.
Front wall: piers X -12..-10 and 10..12; OPEN X -10..10 for courses k0..k3 (h 8..104) = your shopfront opening.
The opening is EXACTLY 96 LDU tall: nothing of the shopfront may reach above h104 (course k4 is a brick lintel).
Proven layout: a 1-brick stall-riser (h8..32) under each display window + m.add(ctx.A.window4(288, 47), 288, x, 32, -7.5)
(4 wide, 72 tall: h32..104); the entrance X -2..2 = m.add(ctx.A.window4(288, 47), 288, 0, 8, -7.5) (glazed door, h8..80)
+ a 1-brick 288 transom on top (h80..104). Fill the rest of X -10..10 with 288 bricks/columns so the opening is closed.
course k4 (h104..128) over the opening = 'lintel' side-stud bricks; k5 (h128..152) = 'fascia' side-stud bricks.
Back wall has a door X -2..2 and windows X -8..-4, 4..8 (frames already placed). Side walls: windows Z -2..2.
Interior free zone: X -11..11, Z -6..7 (inside face of walls: X ±11, Z -7/+7). Keep a 4-stud path X -2..2 from front to back door.""",
    'floor2': """Existing structure: slab h0..8 (bay floor extends at X -4..4 to Z -10), brick (320) walls k=0..5, ring h152..160.
Front: window frames already in openings X -10..-6 and 6..10 (k1..k3, h32..104); OPEN bay opening X -4..4 for k1..k3 (h32..104) —
the bay sits on the slab extension X -4..4, Z -10..-8 and must close that opening (glazed). Side/back windows already framed.
Interior free zone: X -11..11, Z -6..7.""",
    'floor3': """Existing structure: slab h0..8 incl. balcony deck X -6..6 out to Z -11; brick walls k=0..5, ring h152..160.
Front openings (EMPTY, yours): French doors X -2..2 (k0..k5, h8..152); tall windows X -10..-6 and 6..10 (k1..k4, h32..128).
Side openings Z -2..2 (k1..k3) on both sides and back openings X -8..-4, 4..8 (k1..k3) are EMPTY too: floor3-windows fills ALL of them.
Interior free zone: X -11..11, Z -6..7.""",
    'roof': """Existing: roof-deck = four grey 6x16 plates, top h=8, studs exposed over X -12..12, Z -8..8 (build on these studs).
Fixed layout (stay in your area): front parapet Z -8..-7 between X -11 and 11 ONLY (the corners belong to the corner piers),
with cornice/dentils/pediment face to Z -9 over the same X range;
side parapets on X -12..-11 and 11..12 (Z -7..8); back parapet Z 7..8 EXCEPT the stair-house gap X -3..3;
corner piers at the two front corners (X ±12..±11, Z -8..-6); stair-house X -3..3, Z 4..8, walls h8..196 (door faces -Z);
chimney X 9..11, Z -1..1; pergola X -11..-4, Z -6..1 with the bistro set under it; planters (3 placements):
P1 X 5..9 Z -6..-4, P2 X 5..9 Z 4..6, P3 X -11..-7 Z 4..6.""",
    'street': """Baseplate 32x32 (3811) top at Y=0 (module origin = plate centre; street module is at the scene origin).
House footprint X -12..12, Z -6..10 = BARE baseplate (nothing there). Sidewalk Z -16..-6; kerb along Z -16..-15.
Prop slots (street-base must put PLATES, not tiles, under each so props clutch; everything else smooth tiles 71):
lamps X ±10, Z -14 (2x2 pad each; SLIM posts: use m.add(ctx.A.lamp(), 0, x, h, z) on the pad, not stacked round bricks); trees X ±13, Z -13 (4x4 pad each); bench X -10..-6, Z -10..-9; hydrant X 9, Z -14 (1x1);
litter bin X -3, Z -14 (2x2); post box X 3, Z -14 (1x1); cafe terrace X 4..10, Z -11..-8 (plate area).
Cafe door walkway X -2..2, Z -8..-6 must stay clear. Alley X -16..-12, Z -6..16 belongs ENTIRELY to street-alley (its own paving 72 + bins);
street-base must leave that area empty (bare baseplate), and also leave the garden areas to street-garden.
Garden: right strip X 12..16, Z -6..16 (hedge) + back yard Z 10..16 (fence/wall along Z 15..16, shed at X -11..-7, Z 11..15).
Plaque on the garden wall, mounted sideways (flat-built tile panel on side studs).""",
}

CHEAT = """## API (everything you need; do NOT read other files)
A part file is `output/urban-house-run3/modules/<module>/parts/<submodel>.py` defining `build(ctx)` that returns a Module:
```python
def build(ctx):
    m = ctx.Module('<submodel>', 'one-line description')   # name MUST equal the submodel name
    P = ctx.PALETTE      # brick 320, stone 72, trim 15, accent 19, shop 288, door 70, glass 47, metal 0, roof 72, paving 71, green 2, flower 5
    m.add('3010', P['brick'], x, h, z, yaw=0)          # stud units: x/z in STUDS (cell centre = .5), h = BODY TOP in LDU upward
    ctx.add(m, '3069b', P['trim'], [X, Y, Z], R)        # LDU units (Y up is NEGATIVE), R = 3x3 rotation (numpy) or None
    m.step()                                            # optional: start a new build step
    m.place = [([0, 0, 0], None)]                       # optional: placements of this section (default: once at origin)
    return m
```
Coordinates are module-local: X across the facade, Z depth (front = -Z), h up (Y = -h). Brick body 24, plate/tile 8, stud pitch 20.
Bricks/plates/tiles have their ORIGIN AT THE BODY TOP: a brick on a surface at h=8 is placed with h=32.
Rotations: yaw in degrees about the vertical (m.add(..., yaw=90)), or R=ctx.Ry(deg); never mirror.
Helpers (stud units): ctx.A.line(m, x0, z, n, h, colour, axis='x'|'z', plate=False) = run of n studs starting at lower corner x0;
ctx.A.slab(m, x0, z0, w, d, h, colour, tile=False); ctx.A.window4(trim, glass)/ctx.A.door4(trim, leaf) return Modules
(4 wide, 72 / 144 tall, bottom at h=0 of where you place them, front -Z): m.add(ctx.A.window4(15, 47), 15, x, h_bottom, z, yaw=0).
SNOT (sideways studs) — the verified recipe:
```python
R = ctx.panel_R('-Z')                      # a FLAT-built part/section (studs up) turned so its studs face -Z (out of the front);
                                           # its local +X stays +X, its local +Z becomes world UP. '+Z' for the back wall.
stud = ctx.mounts['fascia']['studs'][0]    # world/module LDU point of a side stud (see Mount points below)
origin = ctx.seat(R, (sx, 8, sz), stud)    # (sx,8,sz) = a socket of the part in its own frame (plates/tiles: y=8, x/z = ±10, ±30 ...)
ctx.add(m, '3710', P['trim'], origin, R)   # 1x4 plate now clutches that stud row; put tiles on its studs in the same frame
```
A flat panel built as its own ctx.Module (plate + tiles on top, built studs-up around its origin) can be seated the same way:
ctx.add(m, panel_module, colour, origin, R). Side-stud rows of different courses are 24 LDU apart — one panel mounts on ONE course.
Common parts: bricks 3005 1x1, 3004 1x2, 3622 1x3, 3010 1x4, 3009 1x6, 3008 1x8, 3003 2x2, 3001 2x4; plates 3024 1x1, 3023b 1x2,
3623 1x3, 3710 1x4, 3666 1x6, 3460 1x8, 3022 2x2, 3020 2x4, 3795 2x6, 3034 2x8; tiles 3070b 1x1, 3069b 1x2, 63864 1x3, 2431 1x4,
6636 1x6, 3068b 2x2, 98138 round 1x1 (use as caps), 3062b round brick 1x1; slopes 3040b 1x2 45°, 3039 2x2 45°, 3298 2x3 33°, 3665 inverted 1x2;
side-stud bricks 87087 (1x1), 11211 (1x2), 30414 (1x4), 4070 headlight; windows via ctx.A.window4; glass colour 47;
fence 30055 1x4x2 spindled; flowers 24866 (on a stud); plant 6064b; lamp post 2039; chair 4079; bars/handles 2432.
QUALITY RULES (an automatic check enforces them; RESULT must be PASS with no VISUAL lines for your submodels):
- No bare studs on facades: every plate/brick turned sideways must be covered with tiles (studs must not face the street).
- Never cover or block a window or door opening, not even with transparent plates. Glass must show the room behind it.
- No interpenetration: parts must not sit inside other parts (chairs beside a table, not in it; nothing pushed into tiles).
- Every element must look like what it is (a sign has a framed board with lettering-like tiles; an awning is a sloped striped canopy;
  furniture is recognisable: sofa = seat + back + arms, bed = frame + mattress + pillow, table = top on a leg).
Unsure about a part: `./ldraw-agent part <id>` (bounds + connector positions). Every part must sit on studs (no floating, no part on
smooth tiles), inside your envelope, and READ AS WHAT IT IS. Left/right counterparts mirror-symmetric. Furniture faces its table/wall."""


def rows(names):
    out = []
    for n in names:
        s = SUB[n]; e = s['envelope']
        itf = '; '.join(f"contacts with {i['mount']} ({i['part']}) >= {i['min']}" for i in s['interfaces']) or 'none'
        extra = []
        if s.get('mirror_x'): extra.append('mirror-symmetric about X=0')
        if s.get('max_h'): extra.append(f"top <= h{s['max_h']}")
        for fb in s.get('forbid', []): extra.append(f"FORBIDDEN zone {fb['why']}: X {fb['x']} Z {fb['z']}")
        out.append(f"- **{n}** (placed {s['count']}x by {s['parent']}): {s['purpose']}.\n"
                   f"  Envelope X {e['x']} Z {e['z']} studs, h {e['h']} LDU (+4 for exposed studs). Build frame: {s['build_frame']}.\n"
                   f"  Interfaces: {itf}. Check: {s['duties'] or 'seated, inside envelope, reads as what it is'}"
                   + (f"; {'; '.join(extra)}" if extra else ''))
    return '\n'.join(out)


def mount_text(module, names):
    ms = mounts(module)
    if not ms:
        return ''
    lines = ['## Mount points in the existing walls (side studs; LDU module-local [X, Y, Z]; Y negative = up)']
    for k, v in ms.items():
        st = '; '.join(f'[{x:g},{y:g},{z:g}]' for x, y, z in v['studs'])
        lines.append(f"- '{k}': studs face {v['face']}, course k{v['course']} (stud centre h {v['stud_h']}), bricks {v['refs']}: {st}")
    lines.append('Use ctx.mounts[name]["studs"] in code. Mounts not meant for you belong to other tasks — leave them alone. '
                 'Every mount stud must end up covered by the task that owns it (exposed side studs are a defect).')
    return '\n'.join(lines)


def brief(tid, module, names):
    cmd_subs = ','.join(names)
    return f"""# Task {tid} — {module}: {', '.join(names)}
You are one of 16 parallel workers building "Linden Row House", an original 3-storey LDraw townhouse (café ground floor,
two apartments, roof terrace) in SNOT style: dark-red brick, white trim, tan accents, green shopfront, black ironwork.
The structure already exists. You add ONLY your submodels. Be fast and economical: do not read docs or other files,
do not explore the repo, do not write logs or reports. Repo root: {REPO}

## Your files (create/edit only these)
{chr(10).join(f'- output/urban-house-run3/modules/{module}/parts/{n}.py' for n in names)}

## Contract
{rows(names)}

## Layout of this module
{LAYOUT[module]}

{mount_text(module, names)}

{CHEAT}

## Loop
1. Write your part files.
2. `cd {REPO} && .venv/bin/python output/urban-house-run3/check.py {module} {cmd_subs}` → ≤12 lines, ends with RESULT PASS/FAIL. Fix and repeat.
3. When it PASSes, run it once more with `--snap` and Read every IMAGE it prints. Fix anything that looks wrong
   (floating, gaps, misaligned, clipping, ugly, not reading as what it is), re-check (no more snaps unless you changed a lot).
4. Stop when PASS and it looks right. Final reply: one line per submodel: PASS/FAIL + a short note.
"""


def module_generate(module):
    return f'''"""Assemble {module}: orchestrator core + task parts. Run from repo root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.assemble import assemble
if __name__ == "__main__":
    out, problems = assemble("{module}")
    print({{"module": "{module}", "problems": problems}})
'''


def main():
    tasks = []
    for tid, module, names in TASKS:
        mdir = RUN / 'modules' / module
        (mdir / 'parts').mkdir(parents=True, exist_ok=True)
        (mdir / 'generate.py').write_text(module_generate(module))
        b = RUN / 'briefs' / f'{tid}.md'
        b.write_text(brief(tid, module, names))
        strong = tid in ('T02', 'T05', 'T11')
        tasks.append(dict(id=tid, module=module, submodels=names, brief=str(b), model='sonnet' if strong else 'haiku',
                          budget=0.60 if strong else 0.12, repair_budget=0.25 if strong else 0.06))
    for m in C['modules']:
        (RUN / 'modules' / m / 'parts').mkdir(parents=True, exist_ok=True)
        (RUN / 'modules' / m / 'generate.py').write_text(module_generate(m))
    covered = {n for _, _, ns in TASKS for n in ns} | {n for v in CORE.values() for n in v}
    missing = set(SUB) - covered
    (RUN / 'tasks.json').write_text(json.dumps(tasks, indent=1))
    sizes = {t['id']: len(Path(t['brief']).read_text()) // 4 for t in tasks}
    print(json.dumps(dict(tasks=len(tasks), missing=sorted(missing), brief_tokens=sizes)))


if __name__ == '__main__':
    main()
