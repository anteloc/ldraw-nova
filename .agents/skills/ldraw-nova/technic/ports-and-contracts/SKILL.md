---
name: ports-and-contracts
description: 'Reference for measured Technic interfaces: naming intended connections, measured ports and real lengths, checking mechanisms in the built pose, joint and restraint contracts, the automatic Technic checks, and a by-role table of the most used Technic parts with their hole, grip and shaft ports. Use when looking up a Technic part''s ports, writing a section''s structure or mechanism contract, or interpreting a technic.* diagnostic in depth.'
---

# Technic ports and contracts

Reference for measured Technic interfaces: where ports come from, how seating is judged, how to write `structure` contracts, what the automatic checks cover, and the ports of the parts official sets use most. How to place by port and the check-code fixes are in the parent [technic](../SKILL.md) skill.

## Structure contracts (inline, named)

Each placement has an `id`; `ram/cylinder` selects a part through its parent placement. Paths are relative to the containing section and use every parent ID; repeated placements use their expanded `id-0`, `id-1` names. Put the intent on the section:

```json
"structure": {
  "require_rigid": true,
  "required_joints": [
    {"between": ["pin", "left"]},
    {"between": ["pin", "right"]}
  ],
  "assembly": [{"connector": "pin", "before": ["right"]}]
}
```

| Field | Effect |
|---|---|
| `required_joints` | each named pair must actually connect |
| `assembly` | the connector must appear in an earlier STEP than the parts in `before` |
| `require_rigid` | one rigid structure; fails on a section with moving parts (`technic.mechanism_scope`) |
| `"scope": "joints"` | checks declared connections and seating of a mechanism's mounts in the delivered pose, without claiming the whole is rigid; keep `require_rigid` off |
| `retained_axles` | e.g. `["drive-axle"]`: both axial stops required; an engaged bush with a gap against its stack fails review |

- Neither scope verifies motion: use a `mechanism` contract for what should move.
- A path to a whole module does not identify one joint: select the actual mating part.
- Declare System body mounts individually; one successful attachment cannot satisfy a four-point mount.
- The restraint rule groups members joined by **two separated parallel pin axes**. One pin is a pivot; loops of single-pin joints get an unbraced-loop warning. It is conservative, not a rigidity solver: a valid diagonal truss may need manual review.

### External (numeric) contracts

Older `"structure": "frame.structure.json"` files use occurrence indices:

```json
{
  "version": 1,
  "require_rigid": true,
  "required_joints": [{"between": [1, 0]}, {"between": [1, 2]}],
  "assembly": [{"connector": 1, "before": [2]}]
}
```

Generated contracts bind to `model_sha256`; after changing or reordering a model, regenerate and review the contract (`technic plan` writes the link). A stale hash or invalid index fails explicitly; never discard the mismatch. `build` and `review` run the contract even with `--contacts none`; review saves results under `structure` in `validation.json`. `technic check` defaults to 500 occurrences: scope with `--section` or raise `--max-instances`, and read coverage even when `checks_passed` is true.

## Where ports come from

Merged by `technic.registry()`:

- **Reviewed** (`ldraw_tools/data/technic-parts.json`): 39 hand-measured parts (common bricks, straight beams, a thin beam, a rectangular frame, an axle/pin cross block, pins, axle-pins, a half pin, axles, bushes, a 16-tooth gear, a pneumatic cylinder), geometry-fingerprinted. They override the derived table.
- **Derived** (`ldraw_tools/data/technic-ports.json`): about 1,600 Technic parts, wheels and motors from LDCad `SNAP_CYL` shadow data. Males are cut at collars and pin/axle changes (long pins into 20 LDU grips), bores into 20 LDU cells, lengths snapped to 10 LDU. A cross not square to the part's axes (bent liftarm end hole) records its `radial` direction. A changed library part loses its ports rather than keeping stale ones.
- A port that seats in fewer than half its uses across 215 Technic-heavy official sets is `withheld`. Coverage: 98% of Technic placements; 94% of pins and axles seat.

## Seating rules

- An axle may stop partway into a hole: it keys or bears on what it fills if it fills a whole module, less 2.5 LDU (nominal lengths can exceed a blind bore). A cross keys within 5° of roll.
- A pin grip seats when wholly in its hole, or when two half-depth layers fill it. Two thin (10 LDU) layers can share a grip; one alone does not complete it.
- `technic.invalid_seating`: tilted or offset axes, cross out of line, pin in an axle hole, too little axle inside, a pin barely touching, one hole across both grips (collar in the bore). A pin off-centre or part-way in with at least 7.5 LDU inside is always a warning (studded sets do this).
- Neighbours on one shaft may seem to overlap by up to 3 LDU because thin parts (7–8 LDU) round up to 10; only larger overlaps are `technic.occupied_span`.
- Seating findings are errors only when every part involved has reviewed ports; with a derived port they are warnings. Fix them all the same.
- Friction comes from reviewed part identity, not colour or LDCad's `slide` flag.

## Dimensions

- Hole pitch 20 LDU; brick/plate bodies 24/8; two plates between studded Technic bricks give 40 LDU hole separation.
- Three beam holes span 40 LDU between end centres. Solid bounds are not nominal placement dimensions.
- Thick/thin beams are 20/10 LDU. Cross holes constrain roll; round holes act as bearings; neither gives axial retention.
- Origins, axes and keyed roll vary: use port frames and proper rotations. Never stretch or reflect a part to close a frame.

## What the automatic checks cover

Every build with Technic ports runs `technic_checks.review`: solid-cell collisions, pins in the air, axles that can slide out, unbacked worms, and the kinematic graph (rigid groups by studs, friction pins and keyed fits; revolute joints at frictionless pins and axles in round holes; gear, bevel, worm and rack couplings at distances measured in official sets, `ldraw_tools/data/technic-gears.json`). Each rule was run on official sets first: errors fire on fewer than 0.2 placements in 1,000 of correct models. A gear held at an axle end only by its cross hole is how LEGO builds, so it is not reported.

The `mechanism` contract is an instantaneous mobility analysis (rank of joint and gear constraints with the frame held). It ignores play, travel limits and strength, can mislead at a singular pose, and treats ball joints and telescoping parts as rigid. Swept insertion paths, hand access, arbitrary collisions, strength, stiffness and stability are outside the automated proof: open hidden faces and the underside and report remaining physical checks.

## Mechanism part inventory

```sh
./ldraw-agent technic catalog --family gear
./ldraw-agent technic catalog 'constant velocity'
./ldraw-agent technic catalog 85543-f3
./ldraw-agent technic catalog --output output/mechanism-parts.json
./ldraw-agent technic catalog --model MODEL.mpd --connectors --output output/model-parts.json
```

`--output` saves every row (`--limit` limits only terminal rows); `--force` replaces a catalog; `--connectors` adds interface and alias evidence for a narrowed selection. Default counts are metadata records, not installed availability or retail colours. Model inventory needs a self-contained MPD: embed external assemblies first. `motion_profile: unreviewed` marks parts without validated animation support.

## Most used parts and their ports

Axis letters are the part's own axes; positions are local LDU. `hole-0..hole-6 … step [0, 0, 20]` is seven holes 20 LDU apart. `./ldraw-agent part CODE` gives one part in full; `./ldraw-agent technic parts --query WORDS` searches the rest. The full by-role table (beams, connectors, pins, axles, bushes, gears, wheels) is in the verbatim copy.

| Part | Description | Ports (summary) |
|---|---|---|
| `32524` | Beam 7 | hole-0..6 pin holes along Z from -60, step 20 |
| `32316` | Beam 5 | hole-0..4 pin holes from -40 |
| `32523` | Beam 3 | hole-0..2 pin holes from -20 |
| `32278` / `32525` / `40490` | Beam 15 / 11 / 9 | pin holes from -140 / -100 / -80 |
| `32140` | Liftarm 2 x 4 bent 90 | hole-0 axle; hole-1..3 pin; hole-4 pin at [20,0,60] |
| `32526` | Beam 3 x 5 bent 90 | hole-0..4 pin along Z; hole-5..6 pin along X from [20,0,80] |
| `60483` | Beam 2 liftarm | hole-0 axle, hole-1 pin |
| `64179` | Beam 7 x 5 open centre 5 x 3 | 20 pin holes around the frame, axes X/Y/Z mixed |
| `6536` | Cross block 1 x 2 (axle/pin) | hole-0 axle along X; hole-1 pin along Z at [0,20,0] |
| `42003` | Cross block 1 x 3 (axle/pin/pin) | hole-0 axle X; hole-1..2 pin Z |
| `3700` / `3701` / `3894` | Technic brick 1x2 / 1x4 / 1x6 | pin holes along Z, 10 below the top |
| `2780` | Pin with friction | grip-0..1 along X, friction |
| `6558` | Pin long with friction | grip-0..2, friction |
| `3673` | Pin (frictionless) | grip-0..1 |
| `43093` | Axle pin with friction | pin-end, axle-end |
| `32002` | Pin 3/4 | grip-0 (20), grip-1 (10) |
| `4519` / `3705` / `32073` / `3706` / `3707` | Axle 3 / 4 / 5 / 6 / 8 | `shaft` along X, 60/80/100/120/160 long |
| `87083` | Axle 4 with stop | `shaft` 80, stop + |
| `3713` | Bush with two flanges | hole-0 axle hole Z, 20 |
| `32123a` / `32123b` | Bush 1/2 | hole-0 axle hole Z, 10 |
| `3647` | Gear 8 tooth | hole-0 axle hole Z |
| `94925` | Gear 16 tooth reinforced | hole-0 axle hole Z |
| `3648b` | Gear 24 tooth | hole-2 axle hole at centre; hole-0,1,3,4 pin holes |
| `32270` | Gear 12 tooth double bevel | hole-0 axle hole Z |
| `32269` | Gear 20 tooth double bevel | hole-0 axle hole Z |
| `4716` | Worm gear 2L | hole-0..1 axle holes Z |
| `87761` | Gear rack 1 x 7 | pin holes at ±60, axle holes at ±40 |
| `62821` | Differential, 28 tooth bevel | hole-0..1 pin holes Z at ±25 |
| `56145` | Wheel rim 20 x 30 | hole-0 axle hole Z at z -10 |

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/reference/technic.md](references/docs-agent-reference-technic.md)
- [docs/agent/reference/technic-parts.md](references/docs-agent-reference-technic-parts.md)
