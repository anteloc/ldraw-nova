---
name: write-plans
description: 'Writes model.plan.json (or a generate.py that emits it): sections, steps and placements with id, ref, colour and one position mode (at, on, on {to, face, stud, socket}, under, join, attach), plus orient, yaw, roll, repeat, mirror, offset_studs, includes, module anchors and contracts. Includes the construction recipes (small checked plans for every placement mode) and how to split large models into modules with their own origins. Use when authoring or editing a plan, choosing how to position a part, stacking bricks and plates, repeating or mirroring structure, or organising a model into submodel sections.'
---

# Write plans

A plan is a JSON file of named placements; `build` turns it into an MPD. This skill covers the plan format, every position mode, orientation, repetition, mirroring, modules and generators, plus the checked recipes to copy from. The JSON schema at `ldraw_tools/data/plan.schema.json` is the complete contract: unknown keys, malformed vectors, mixed position modes, duplicate IDs, unresolved references, invalid colours and nonfinite numbers fail explicitly.

## The format

```json
{
  "version": 1,
  "author": "Your name",
  "sections": [{
    "name": "model.ldr",
    "description": "A red brick with a sideways tile",
    "steps": [
      [{"id": "base", "ref": "3001.dat", "colour": 4, "at": [0, 0, 0]}],
      [{"id": "top", "ref": "3022.dat", "colour": 1, "on": "base"}],
      [{"id": "lamp", "ref": "87087.dat", "colour": 15, "on": {"to": "top"}}],
      [{"id": "lens", "ref": "3070b.dat", "colour": 14, "on": {"to": "lamp", "face": "-Z"}}]
    ]
  }]
}
```

- A plan has `version: 1`, an accurate `author` and ordered `sections`. The first section is the scene main (the MPD root).
- Each section has a unique flat `.ldr` name, a `description` and `steps`: arrays of placements. It may declare `anchors` and its own `author`/`license`.
- A placement has a section-local unique `id`, a real `ref`, a `colour` and **exactly one** position mode. Add `purpose` when it explains something useful. A later placement may refer to an earlier one by `id`.
- `ref` is a part (`3003.dat`), a module (`pillar.ldr`) or a category symbol (`@arches.Arch1X6X2WithThickTopAndReinforcedUnderside`). `colour` is a code or a symbol such as `@colours.Tan`. Symbols resolve against the installed library without changing the plan.
- `includes` imports other JSON plans; `assets` imports MPDs or declares flexible sources. A section may link a `structure` contract. All paths are relative to the declaring plan.

**For a user model:** set `author` to the contributing agent/model names and versions, add `"license": "CC-BY-NC"`, and prefix the root section's `description` with `[AI-GENERATED] ` exactly once. Keep `name` and submodel references unchanged. There is no plan field for keywords or the licence comment: `finalize` adds them ([review-and-deliver](../review-and-deliver/SKILL.md)). Plans and generators stay internal.

## Choose a position

| Mode | Use it for | Example |
|---|---|---|
| `at` | explicit coordinates in the section, in LDU | `"at": [0, -24, 40]` |
| `on` (ID) | a curated upright brick/plate stacked on an earlier one | `"on": "base"` |
| `on` (object) | any part seated by a socket on a stud of another part, on any face | `"on": {"to": "core", "face": "-Z", "stud": 0}` |
| `on` (Technic) | a pin or axle in a hole, or a holed part on a pin or axle | `"on": {"to": "beam", "hole": "hole-1", "pin": "grip-0", "side": "+X"}` |
| `join` | a Technic part or section laid on another by matching holes, pins inserted | `"join": {"to": "rail", "holes": {"hole-0": "hole-0", "hole-1": "hole-1"}, "side": "+X"}` |
| `under` | any part hung by a stud in a socket of the part above | `"under": {"to": "deck", "socket": 0}` |
| `attach` | aligning authored module anchors | `"attach": {"to": "lower", "anchor": "seat", "using": "base"}` |
| `snap` | searching actual connector evidence on a part/submodel | `"snap": {"to": "base", "near": [0, -8, 0]}` |

Sideways seats: [snot-construction](../snot-construction/SKILL.md). Technic ports and `join`: [technic](../technic/SKILL.md).

### Orientation

- `at` accepts one of `yaw` (degrees about +Y), `orient` or a proper 3×3 `matrix`. You never need to write a matrix.
- `orient: {"up": D, "x": D}` points the part's studs (local -Y) toward `up` and its local +X toward `x`. Directions are `+X -X +Y -Y +Z -Z up down` or vectors; `x` defaults to +X (or +Z when `up` is along X).
- `on` (ID) requires upright parts, so only `yaw` applies. `attach` and connector seats set orientation themselves; `snap` takes `yaw` or `matrix` as a starting orientation.

### `on` (ID): stacking bricks and plates

Only for the curated upright studded parts listed by `./ldraw-agent profiles`. The upper part's underside meets the lower part's top body plane:

```text
y_upper = y_lower - height_of_upper_body
```

A plate on a brick at Y=0 goes at Y=-8; a brick on that plate at Y=-32. Do not subtract the lower part's height or add 4 LDU for the stud: bounding boxes legitimately overlap.

- `offset_studs: [x, z]` shifts by whole or half studs in the **support's** local axes (×20 LDU). A centred 1×1 over a 2×2 needs an offset to a real stud, e.g. `[0.5, 0.5]`, not `[0, 0]`.
- `yaw` is the new part's orientation in the section, independent of the support's yaw.
- Not available for unknown profiles, tiles, slopes, rotated sideways parts or submodel references: use the connector form.
- Bricks touching side by side have no clutch: bridge them with a plate. Lay long plates across seams.

### `on` (object): connector seats

| Field | Meaning |
|---|---|
| `to` | an earlier placement in this section, or a path such as `module/part` into a placed module |
| `face`, `stud` | the support's stud: face in the support part's own frame (default `-Y`, the top) and index on that face, in the order `part` lists them (default 0) |
| `socket`, `socket_face` | the placed part's socket and an optional face filter (default socket 0) |
| `socket_at`, `socket_axis` | for a placed section: the point of the section that sits on the stud, and the direction its underside faces (default `+Y`) |
| `roll` | degrees about the seated socket's axis, right-handed like `yaw`; omitted, the quarter turn covering the most studs |
| `orient` (beside `on`) | an explicit orientation instead of `roll`; it must make the socket face the stud |

The builder computes the origin `stud - R * socket` from connector data. It fails with the available faces, studs or sockets when a selection does not exist. `build --report FILE` lists each seat under `seats` with `mated`, the number of support studs covered.

### `on` (Technic), `join`, `under`

- **Technic `on`:** `hole` and `pin` port IDs (from `part` → `technic_ports`). Along the shared axis use one of `slide` (LDU), `end` with `past` (0 is flush) or `next_to` with `side`. `side` on a pin or axle names where the rest of it extends; `flip` turns a holed part end for end; `roll` turns about the axis. The seat must pass the Technic fit rules.
- **`join`:** `holes` maps holes of `to` to holes of the placed object (`PART/hole-N` inside a section); `side` is the direction from `to` where the placed object lies. Two pairs fix the turn; with one, `roll` sets it. One connector per pair is inserted as `ID-pin-0`, `ID-pin-1`…; `pins` picks it (default `2780.dat`, `3673.dat` for a pivot, an axle-pin such as `43093.dat` for an axle hole, `false` for none), `pin_colour` its colour, `flip` turns the object over.
- **`under`:** mirrors the stud seat. `socket`/`socket_face` pick the support's socket (default `+Y`, its underside); `stud`/`face` the placed part's stud (default `-Y`, its top); `stud_at`/`stud_axis` seat a section; `roll` turns about the socket axis.

### `attach` and `snap`

- `attach` aligns two named anchor frames; optional `offset` is in the supporting anchor's axes. It sets position and orientation: do not combine with `at`, `on`, `yaw`, `matrix` or `repeat`. The target ID must already exist in this section.
- `snap` searches up to 100 connector candidates and moves the whole reference rigidly. `near` guides ranking (default: the support's position); `moving_leaf`/`fixed_leaf` (default 0) pick physical leaves; `moving_feature`, `fixed_feature`, `candidate` make selection explicit. It fails on absent interfaces, bad leaf indices or a body collision, and cannot coexist with `at`, `on`, `attach`, `offset_studs` or `repeat`. Details: [connectors-and-snapping](../reference/connectors-and-snapping/SKILL.md).

```json
{"id":"cap", "ref":"cap.ldr", "colour":1,
 "snap":{"to":"base", "near":[0,-8,0], "moving_leaf":0, "fixed_leaf":0}}
```

## Repeat and mirror

```json
{"id":"roof-slope", "ref":"3039.dat", "colour":320,
 "at":[-140,-24,-130], "repeat":{"count":8,"step":[40,0,0]}}
```

- Expands to `roof-slope-0` … `roof-slope-7`. `step` is in the section's axes and does not rotate with `yaw`. `repeat` works with `at` only.
- `"count": [4, 2]` with `"step": [[40, 0, 0], [0, 0, 20]]` makes a grid with IDs `id-i-j`.
- Use an included submodel for a repeated multi-part construction, and Python loops for conditional patterns.
- `"mirror": "x"` (or `y`, `z`) on a section placement places a mirrored copy `NAME-mirror-x.ldr`, built once. Each part becomes its own mirror image with a proper rotation, or its Left/Right partner. A part with real handedness (a worm gear) stops the build: place it by hand. Paths into the copy use the original IDs.

## Organise larger models

- Put each module (wing, floor, cab, panel) in its own section with its own origin, and build it upright. Place it like a part: `{"id": "wing-left", "ref": "wing.ldr", "colour": 15, "at": [...]}`.
- Parts inside a module that use colour 16 take the placement's colour. Use 16 only when an explicit ancestor colour resolves every visible leaf. Colour 24 is for edges, not placements.
- A path such as `wing-left/flap` names a part inside a placed module; `on.to` accepts paths.
- Keep the first section (the root) short: it places modules.
- Partition by purpose, interfaces and repair boundaries: chassis/body, core/skin, frame/tool, floor/roof, figure limbs. MPD hierarchy is authoring structure; it does not establish rigid bodies or connections.
- Before filling a module, record its purpose, envelope, local origin, attachment frames, inherited palette, mating parts and review status. Reserve openings and keep the connectors neighbours need clear.

### Anchors

```json
"anchors": {
  "base": {"at": [0, 8, 0]},
  "next": {"at": [0, -160, 0]}
}
```

```json
[
  {"id":"lower", "ref":"lane-ground.ldr", "colour":19, "at":[0,-8,0]},
  {"id":"upper", "ref":"lane-upper.ldr", "colour":19,
   "attach":{"to":"lower", "anchor":"next", "using":"base"}}
]
```

The builder solves `T_moving = T_support × A_support × T_offset × inverse(A_moving)`. Frames may carry a proper `matrix` (identity if omitted). Anchors are authored intentions, **not inferred connectors**: check the real parts at each interface.

### Includes and assets

- `"includes": ["buildings.plan.json"]`: each file loads once, cycles and duplicate section names fail, the root plan's first section stays the MPD main, and included modules keep their own author/licence unless overridden. Generated sections loaded through includes still need the AI attribution.
- `"assets": ["assets/clock.mpd"]` embeds an extracted MPD's definitions with original headers. Names must not collide with generated sections, other assets or the official library.
- Copy an attributed dependency closure from a reference with `extract --section NAME --namespace UNIQUE --output output/assets/NAME.mpd`; keep its `.manifest.json`, use the returned `root` name, and check its diagnostics before reuse.

### Review a composed model at three scales

1. **Detail:** windows, hinges, one angled roof joint; render the selected section.
2. **Module:** `--section NAME --colour CODE` for a floor or roof: clearances, support, step order, boundary interfaces.
3. **Scene:** the whole assembly, cross-module overlaps, BOM comparison, several views. Module checks alone cannot catch collisions introduced by composing.

Contacts are computed automatically through 500 physical leaves (`--contacts auto`); above that, skipped coverage is reported. `--contacts all` forces the full computation, `--contacts none` reports no connectivity conclusion. `--detail summary` keeps totals, errors and coverage; `--detail full --limit 30 --offset 60` pages occurrences.

## Generate with Python

Write a `generate.py` that emits the plan when the model has loops, mirrored halves, conditional openings or many similar parts. Generate ordinary dictionaries and lists, and keep repairs in the generator so a rebuild preserves them (direct JSON edits are overwritten on regeneration).

```sh
.venv/bin/python examples/plan-basics/python_api.py
./ldraw-agent review output/tower.mpd
```

| API | Purpose |
|---|---|
| `builder.load_plan(path)` | resolve relative includes/assets and preserve headers |
| `builder.build_plan(plan, parts)` | serialized text, parsed model and source diagnostics |
| `workflow.build_checked(plan, parts, **geometry_options)` | geometry and declared structural checks; text, model and combined report |
| `builder.rotation(axis, degrees)` | a proper rotation |
| `common.get_parts()` | load the configured library and shadow metadata |
| `geometry.analyze_geometry(model, parts, ...)` | inspect geometry and connection evidence |

`build_plan` does not run full assembly geometry or structural contracts: use `load_plan` then `build_checked` for the complete path. Do not add a second parser/serializer. Larger examples: `examples/plan-basics/bridge.plan.json` (colour-inheriting pillars), `examples/copper-lane/generate.py` (see [buildings](../design-models/buildings/SKILL.md)).

## Inspect before placing

- `./ldraw-agent part CODE` gives the origin, the body box without studs, the full bounds, and studs and sockets per face in the order seats count them. `--full` adds every connector record and provenance. **Bounding-box height is not stacking height.**
- Example: `3001.dat` (2×4 brick) has bounds X=-40..40, Y=-4..24, Z=-20..20; body 24 high, full bounds 28; stud centres X=-30,-10,10,30 and Z=-10,10 at Y=0.
- `dimensions PART...` gives cached extents; category `ldu_y`/`studs_*` fields describe extents, not connection planes (the `3659` arch cache says 37.41 LDU, the file measures 28).
- Never read library `.dat` files. Part lookup: [find-constructions-and-parts](../find-constructions-and-parts/SKILL.md).

## Construction recipes

Small checked plans in `examples/recipes/`, each passing `review` with matching BOMs. `knowledge search` returns them first when one fits; copy the placements and change parts, colours and studs.

```sh
./ldraw-agent review examples/recipes/side-stud-cover.plan.json --outdir output/recipes/side-stud-cover
```

| Recipe (`examples/recipes/…plan.json`) | Lesson |
|---|---|
| `side-stud-cover` | 30414 side-stud brick carries a 1×4 tile on all four studs: `on {to: core, face: -Z}`; default turn, no `roll`. Parts 30414, 2431, 3710. |
| `headlight-lamp` | 4070 headlight brick + round 1×1 tile on its recessed stud (4 LDU inside, tile stands 4 proud). Parts 4070, 98138. |
| `bracket-grille` | 99780 bracket on a plate's front studs turns two studs forward; grille tile on them. Pick the plate stud with `stud: N`. |
| `side-panels` | One upright panel section seated on both sides of a 52107: `on {to: core, face: F, socket_at: [-10, 8, 0], roll: 0}`. No mirrored copy needed. |
| `window-wall` | 60592 frame on a sill between 1×1 columns; glass 60601 shares the frame origin; lintel plate on frame studs (socket 1). |
| `inverted-nose` | 3660b inverted slope hung under a 2×2 plate: `under {to: deck}`; tile on top. |
| `jumper-centre` | 3794b jumper gives a centred stud half a stud off grid; round tile centred on the brick. |
| `roof-slope-row` | Four 3039 slopes on a 2×8 plate with `on {to: plate, stud: 0, 4, 8, 12}`. |
| `technic-pin-frame` | `join` a 32524 beam to a 64179 open frame at two holes; two spaced pins = rigid, one pin = hinge. |
| `technic-gear-pair` | 8:24 gears mesh 40 LDU apart (holes two apart); each shaft in two beams, bushed both sides; mechanism contract. |
| `technic-rack-steering` | Kingpin hubs (6536), L-liftarm arms (32140), 1×7 rack (87761), 12-tooth pinion; 1 degree of freedom. |
| `technic-wheel-axle` | Two pinned beams as a bearing, axle, bushes, rim 56145, tyre 55976 via `snap: {to: rim}`. |
| `technic-bevel-corner` | Two 12-tooth double bevels (32270) turn drive 90° in an open frame; gears placed with `slide`. |
| `technic-worm-drive` | Worm 4716 meshes a 24-tooth gear 40 LDU away between two open frames; bushes take the thrust. |
| `technic-suspension-arm` | Arm on a frictionless pin (`pins: 3673.dat`), 6.5L shock 76537; angle from the law of cosines (74.41°). |
| `technic-cylinder-lever` | Pneumatic cylinder 74981-f2 raises a lever; 79.40° from the triangle; hoses afterwards. |

## Declared checks

- A section's `mechanism` (`ground`, `input`/`inputs`, `outputs`, `pivots`, `dof`, all placement paths) declares what should move; `build` checks it against the built pose. Named inline `structure` contracts declare intended connections. See [technic](../technic/SKILL.md) and [ports-and-contracts](../technic/ports-and-contracts/SKILL.md).
- Inline flexible placements go in the same `steps`: [flexible-parts](../flexible-parts/SKILL.md).
- The builder emits UTF-8 without BOM, CRLF, headers, comments and steps. New part geometry, textures or local colours need extra review: [ldraw-format](../reference/ldraw-format/SKILL.md).

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/cards/plan.md](references/docs-agent-cards-plan.md)
- [docs/agent/reference/plans.md](references/docs-agent-reference-plans.md)
- [docs/agent/guides/place-parts.md](references/docs-agent-guides-place-parts.md)
- [docs/agent/guides/compose-modules.md](references/docs-agent-guides-compose-modules.md)
- [examples/recipes/README.md](references/examples-recipes-README.md)
