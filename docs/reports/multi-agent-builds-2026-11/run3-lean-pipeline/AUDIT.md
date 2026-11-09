# Run 3: honest quality audit (after the user's review)

The user judged the final model a mess: interpenetrating parts, blocked windows and more. This audit confirms it. My earlier report ("clean, about as good as run 2") was wrong, because the checks I relied on cannot see these defects, and I only looked at whole-house renders at small scale.

Images opened for this audit:
- `integration/audit/{ground,floor2}/panels/02-home-view.png`
- `integration/audit/{floor3,roof,street}/panels/01-home-view.png`

## Defects visible in module close-ups

| Module | Defect |
|---|---|
| ground | **The awning is a chaotic stack** of white/green slopes and plates with exposed studs, merged with the sign band. The sign doesn't read as a sign. The shopfront windows are small. The rustication panels stick out as blocks. The interior is two stools and a table. |
| floor2 | **The flanking front windows are blocked**: SNOT façade panels (grey and white plates with exposed studs) cover them completely. The window boxes are tan blocks with flowers mounted sideways. The interior is a stack of tan bricks plus one grey brick. |
| floor3 | The pilasters are bare studded plates, not finished columns. The cornice is a row of exposed round studs. The interior is block-like. |
| roof | Loose red bricks lie inside the deck behind the front parapet. The front parapet faces are rows of exposed round studs. The planters are green round bricks. |
| street | The lamps are stacked cones. The café chairs sink into the paving tiles. The right hedge is a block of green 2×4 bricks. The trees are spiky plants in white boxes. |

## Measured interpenetration missed by my metrics
`inspect --contacts all` reports 2048 oriented-bounds overlap candidates. Of these, 80 penetrate more than 4.5 LDU on every axis. Many are expected, such as glass inside its frame or a door leaf inside its frame. The real ones include:
- **shopfront windows against the lintel course** (7 cases). The 120-tall `2493b` windows run through course k4. My structure spec, which leaves the opening only to h104, contradicts my contract, which asks for glazing at least 96 tall.
- **bistro chairs inside the table** (12 cases);
- **café chairs inside the paving tiles** (12 cases);
- **planter flowers inside their plates** (6 cases);
- **the balcony fence inside a brick** (2 cases);
- **the lamp stack** (2 cases).

## Why the pipeline passed it
1. **"0 build errors" only covers curated rectangular-body overlaps.** The validator's `coverage.collision_review` warning ("remaining overlaps require material review") was the signal, and I treated it as noise.
2. **The contract checks test structure, not appearance.** They cover envelope, connectivity, interface contacts and symmetry. A panel that covers a window, or that shows bare studs, passes all of them.
3. **The glass check only looked 12 LDU behind the glass**, never in front of it. Blocked windows are occluded from the outside.
4. **Visual judgement was thin.** Workers looked once at 768 px snaps after reaching PASS, with a budget of 20 tool calls. The Opus reviewer saw 768 px whole-house views. I looked at whole-house views and declared success.
5. **The workers had too little room for design.** Haiku with a 2 k brief and about 20 turns produces structurally valid but crude geometry. The cost cuts removed the design iteration that run 2's workers had, at 60–90 turns each.

## What it would take
- **Automatic checks for the defect classes above:**
  - glass occluded from the outside;
  - studs on outward-facing façade surfaces;
  - deep oriented-bounds interpenetration between parts that are not frame and glass;
  - furniture inside furniture.
- **Close-up, per-module visual review at full resolution**, with tickets.
- **More design capacity where it shows:** façade and SNOT tasks need a stronger model or more turns. Interiors and props can stay on Haiku.
- **Fixing the contradiction between the structure spec and the contract** (shopfront height).

## After the quality pass (02:35–02:52, `integration/r2`, final `review/`)
Images opened:
- `integration/r2/mod-{ground,floor2,floor3,roof,street}/panels/01-home-view.png` (1024 px);
- `integration/r2/whole/panels/02-front-view.png`.

**Checks:** 0 build errors, 1655 parts, review passed, BOM matches. Contract checks are 48/49. The one FAIL is two floor-3 rear window frames that are not connected. **No VISUAL rows remain**: no blocked windows, no bare outward studs, no deep interpenetration.

**Visual:**
- **Fixed:**
  - the awning is now a clean sloped green/white striped canopy;
  - the floor-2 windows are open, with tan/white tiled surrounds;
  - the floor-3 cornice and pilasters are tiled and smooth;
  - the roof parapet has finished dentils.
- **Still weak:**
  - the sign band has no readable sign;
  - the window boxes carry sideways flowers;
  - the bay glass shows the red back wall;
  - the interiors are blocky but recognisable (sofa, bed, wardrobe, café tables);
  - a tan beam lies loose in front of the pergola on the roof;
  - the lamps are still stacked round bricks, so the slim-lamp rule was ignored;
  - the trees are spiky plants;
  - the two rear window frames on floor 3 float.

**Orchestrator score: about 3.5.** Pass 1 scored about 2.5 after this audit; run 2 scored 3.9.
