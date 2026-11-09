# Task T05 — floor2: floor2-facade, floor2-window-box
You are one of 16 parallel workers building "Linden Row House", an original 3-storey LDraw townhouse (café ground floor,
two apartments, roof terrace) in SNOT style: dark-red brick, white trim, tan accents, green shopfront, black ironwork.
The structure already exists. You add ONLY your submodels. Be fast and economical: do not read docs or other files,
do not explore the repo, do not write logs or reports. Repo root: /Users/captain/workspaces/workspace-ai/ldraw-nova

## Your files (create/edit only these)
- output/urban-house-run3/modules/floor2/parts/floor2-facade.py
- output/urban-house-run3/modules/floor2/parts/floor2-window-box.py

## Contract
- **floor2-facade** (placed 1x by floor2): front SNOT cladding: white window surrounds / tan sill bands / masonry texture panels around the two flanking windows (X -10..-6 and 6..10).
  Envelope X [-12, 12] Z [-9, -7.5] studs, h [8, 152] LDU (+4 for exposed studs). Build frame: built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z).
  Interfaces: contacts with floor2-walls (*) >= 8. Check: stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; symmetric; mirror-symmetric about X=0
- **floor2-window-box** (placed 2x by floor2): flower box under each flanking window, front face SNOT-mounted on headlight bricks; flowers on studs.
  Envelope X [-11, 11] Z [-10.5, -7.5] studs, h [8, 56] LDU (+4 for exposed studs). Build frame: box upright; front face on 4070 side studs.
  Interfaces: contacts with floor2-walls (4070) >= 4. Check: stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; mirror-symmetric about X=0

## Layout of this module
Existing structure: slab h0..8 (bay floor extends at X -4..4 to Z -10), brick (320) walls k=0..5, ring h152..160.
Front: window frames already in openings X -10..-6 and 6..10 (k1..k3, h32..104); OPEN bay opening X -4..4 for k1..k3 (h32..104) —
the bay sits on the slab extension X -4..4, Z -10..-8 and must close that opening (glazed). Side/back windows already framed.
Interior free zone: X -11..11, Z -6..7.

## Mount points in the existing walls (side studs; LDU module-local [X, Y, Z]; Y negative = up)
- 'head-L': studs face -Z, course k4 (stud centre h 118), bricks ['30414']: [-190,-118,-160]; [-170,-118,-160]; [-150,-118,-160]; [-130,-118,-160]
- 'head-R': studs face -Z, course k4 (stud centre h 118), bricks ['30414']: [130,-118,-160]; [150,-118,-160]; [170,-118,-160]; [190,-118,-160]
- 'pier-L': studs face -Z, course k2 (stud centre h 70), bricks ['11211']: [-230,-70,-160]; [-210,-70,-160]
- 'pier-R': studs face -Z, course k2 (stud centre h 70), bricks ['11211']: [210,-70,-160]; [230,-70,-160]
- 'pier-CL': studs face -Z, course k2 (stud centre h 70), bricks ['11211']: [-110,-70,-160]; [-90,-70,-160]
- 'pier-CR': studs face -Z, course k2 (stud centre h 70), bricks ['11211']: [90,-70,-160]; [110,-70,-160]
- 'box-L': studs face -Z, course k0 (stud centre h 22), bricks ['4070', '4070']: [-170,-22,-156]; [-150,-22,-156]
- 'box-R': studs face -Z, course k0 (stud centre h 22), bricks ['4070', '4070']: [150,-22,-156]; [170,-22,-156]
- 'rear-head-L': studs face +Z, course k4 (stud centre h 118), bricks ['30414']: [-90,-118,160]; [-110,-118,160]; [-130,-118,160]; [-150,-118,160]
- 'rear-head-R': studs face +Z, course k4 (stud centre h 118), bricks ['30414']: [150,-118,160]; [130,-118,160]; [110,-118,160]; [90,-118,160]
Use ctx.mounts[name]["studs"] in code. Mounts not meant for you belong to other tasks — leave them alone. Every mount stud must end up covered by the task that owns it (exposed side studs are a defect).

## API (everything you need; do NOT read other files)
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
smooth tiles), inside your envelope, and READ AS WHAT IT IS. Left/right counterparts mirror-symmetric. Furniture faces its table/wall.

## Loop
1. Write your part files.
2. `cd /Users/captain/workspaces/workspace-ai/ldraw-nova && .venv/bin/python output/urban-house-run3/check.py floor2 floor2-facade,floor2-window-box` → ≤12 lines, ends with RESULT PASS/FAIL. Fix and repeat.
3. When it PASSes, run it once more with `--snap` and Read every IMAGE it prints. Fix anything that looks wrong
   (floating, gaps, misaligned, clipping, ugly, not reading as what it is), re-check (no more snaps unless you changed a lot).
4. Stop when PASS and it looks right. Final reply: one line per submodel: PASS/FAIL + a short note.
