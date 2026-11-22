---
name: technic
description: 'Builds Technic models (beams, liftarms, pins, axles, gears, wheels) by naming ports: frame first, then shafts, gears and links, wheels, cladding. Covers technic parts, technic gears, part ports (hole-N, grip-N, shaft), on {to, hole, pin, side}, join {to, holes, side, pins}, the technic.* build checks, mechanism contracts and good mechanical practice. Use when a brief involves beams, pins, axles, gears, chassis or any mechanism; this replaces the SNOT default for Technic briefs.'
---

# Technic

Technic parts join through pins and axles in holes. Name the ports; the tool turns and positions each part, inserts pins for you and checks the result the way a Technic builder would. Everything is checked in the built pose; nothing is animated. Use this skill instead of the SNOT default for any brief with beams, pins, axles, gears or mechanisms. General plan fields: [write-plans](../write-plans/SKILL.md).

## Work in this order

1. **Frame**: beams joined at two holes per joint, or with an L-liftarm or a triangle. One pin per joint is a hinge.
2. **Shafts**: each axle in round holes of the frame, with a bush or keyed part on each side so it cannot slide out.
3. **Gears and links** at exact mesh distances; pivots on frictionless pins.
4. **Wheels**, then panels and System cladding; hoses last ([flexible-parts](../flexible-parts/SKILL.md)).

Before placing parts, write down the silhouette, main dimensions in studs, where loads go and where the body attaches. Design skeleton and visible body together: a body built first leaves no room for joints. Lay out shaft lines and gear pairs on the stud grid first. Put a repeated or left/right assembly in its own section and place it twice; the other side takes `"mirror": "x"`.

## Find parts and ports

```sh
./ldraw-agent technic parts --role member --top 25   # most used beams and connectors; also gear, connector, shaft, wheel
./ldraw-agent technic parts --query "liftarm bent"
./ldraw-agent part 32140 3648b 2780                   # ports of several parts in one call
./ldraw-agent technic gears 8 24                      # pitch radii and mesh distances
```

`part` lists `technic_ports`: holes `hole-N` (`pin_hole` or `axle_hole`), pin halves `grip-N` and axles `shaft`, each with centre, axis and length. About 1,600 Technic parts have ports. A by-role port table is in [ports-and-contracts](ports-and-contracts/SKILL.md).

## Place parts by their ports

A pin or axle into a hole; `side` is where the rest of it sticks out:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "pin", "ref": "2780.dat", "colour": 0, "on": {"to": "rail", "hole": "hole-0", "pin": "grip-0", "side": "+X"}}
```

A beam laid on another by matching holes. The tool inserts one pin per pair (`IDENT-pin-0`, …): friction `2780` by default, `"pins": "3673.dat"` for a pivot, `"pins": false` for none:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "arm", "ref": "32316.dat", "colour": 72, "join": {"to": "rail", "holes": {"hole-0": "hole-0", "hole-1": "hole-1"}, "side": "+X"}}
```

An axle and the parts on it, each flush against the last:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "axle", "ref": "3706.dat", "colour": 0, "on": {"to": "rail", "hole": "hole-3", "pin": "shaft", "end": "-X", "past": 20}},
{"id": "bush", "ref": "3713.dat", "colour": 71, "on": {"to": "axle", "hole": "hole-0", "pin": "shaft", "next_to": "rail", "side": "-X"}},
{"id": "gear", "ref": "3648b.dat", "colour": 7, "on": {"to": "axle", "hole": "hole-2", "pin": "shaft", "next_to": "rail", "side": "+X"}}
```

- `end` + `past`: that end of the axle stands `past` LDU beyond the face of the holed part (0 is flush).
- `next_to` + `side`: the part sits flush against that neighbour, on that side, along the axle.
- `slide` moves along the axis; `roll` turns about it (a cross hole tries 45° itself); `flip` turns a holed part end for end.
- `join` also places a whole section: name the hole of a part inside it, `"holes": {"hole-2": "mount/hole-0"}`.

A failed seat names the fit rule that failed and lists both parts' ports.

## Dimensions

- Hole pitch is 20 LDU (one stud). A beam is 20 thick, a thin liftarm 10. An axle N long is 20 × N LDU.
- Technic bricks have their holes 10 below the top; two plates between bricks put their holes 40 apart.
- Parallel gears mesh with axes 1.25 × (teeth A + teeth B) LDU apart. On whole studs: 8+8 (1 stud); 8+24, 12+20 and 16+16 (2); 8+40, 12+36 and 24+24 (3); 24+40 (4); 40+40 (5).
- Two 12-tooth bevels mesh with each centre 15 LDU from where the axes cross.
- A worm meshes a gear whose axis passes 10 LDU + its pitch radius from the worm's axis.

## What the build checks

| Code | Meaning and fix |
|---|---|
| `technic.through_solid` (error) | A pin or axle crosses plastic where there is no hole: move it onto the hole. |
| `technic.cell_overlap` (error) | Two members fill the same space: lay one beside the other. |
| `technic.invalid_seating` | A pin or axle is at a hole but not seated; the rule named says why. Fix it even when it is only a warning. |
| `technic.occupied_hole`, `technic.occupied_span` | Two parts claim one hole or one stretch of a shaft: move one along the axle. |
| `technic.incomplete_grip`, `technic.misaligned` | Half a pin grip is in the air (add a layer or use a 3/4 pin `32002`); a pin or axle is 1.5–5 LDU off a hole's axis (seat it with `on`). |
| `technic.loose_axle` | The axle can slide out: a bush or keyed part against the bearing, or an axle with a stop. |
| `technic.open_pin` | A pin sticks out into the air: seat a part on it or remove it. |
| `technic.gear_gap`, `technic.gear_clash` | Gears are off their mesh distance by the LDU stated. |
| `technic.locked_shaft` | A meshing gear is fixed to the frame: run its axle in round holes. |
| `technic.unsupported_shaft`, `technic.overhung_gear` | A geared shaft runs in no bearing, or its gear is more than two studs from one. |
| `technic.unbraced_mesh` | The two shafts of a mesh sit in different frames: carry both in one beam. |
| `technic.thrust_unbacked` | Nothing backs a worm along its axle: put a bush or beam flush against it. |

## Declare what should move

Add a `mechanism` to the section, beside `steps`. For the axle above:

```json
{"ground": "rail", "input": "axle", "outputs": ["gear"]}
```

- `build` checks that the input can turn and each output moves with it (`technic.mechanism_locked`, `technic.mechanism_uncoupled`); an output that moves on its own is `technic.mechanism_loose`.
- `"dof": N` states the expected degrees of freedom (`technic.mechanism_dof`).
- `"pivots": [["arm", "rail"]]` lists pairs that must turn about each other (`technic.pivot_locked`).
- `./ldraw-agent technic trace PLAN` prints the rigid groups, joints and gear meshes.

A section's `structure` contract names joints that must exist and their assembly order: see [ports-and-contracts](ports-and-contracts/SKILL.md). Motion or travel studies are optional: [motion-studies](motion-studies/SKILL.md).

## Construction rules

- **Frames.** Two pins per joint (`join` with two hole pairs), an L-liftarm (`32140`, `32526`) or a triangle. A rectangle of single-pin joints is a parallelogram and folds.
- **Shafts.** Each axle in round holes of one rigid frame, in two bearings when you can, with a bush (`3713`, `32123a`) or keyed part against each outer face. An axle in a cross hole of the frame cannot turn.
- **Gears.** Only at mesh distance, both shafts in the same beam or frame, each gear within two studs of a bearing. Back a worm on both sides.
- **Pivots.** A frictionless pin (`3673`, long `32556`) or an axle in round holes. Friction pins (`2780`, `6558`) lock: use them for structure.
- **Modules.** Build a repeated or mirrored assembly once in its own section and `join` it to the frame by its holes.
- Do not write your own checker or geometry script. If a check looks wrong, say so in your report.

## Mount the body

- Technic bricks (`3700`, `3701`, `3894`) carry studs on top and holes through their sides: a System body sits on their studs.
- A half pin with a stud (`4274`) in a beam hole gives a single stud for a tile or plate.
- Panels (such as `64782`) and fairings hang on pins and axle-pins: seat the pin in the frame first, then the panel on it.

Keep the skeleton's main lines clear and the palette controlled. Compare all seven views and a thumbnail; fix proportions and unsupported mounts before decoration. A vehicle body clad in System bricks also gets the mandatory silhouette pass ([design-models](../design-models/SKILL.md)).

## Choose a construction by function

| Intended feature | Pattern | Subskill |
|---|---|---|
| Visible drive route | parallel gears: keep shaft lines and tooth planes | [transmissions](transmissions/SKILL.md) |
| Drive around a corner | bevel train: support each shaft, retain the drum | [transmissions](transmissions/SKILL.md) |
| Slow adjustment | worm drive beside the finite threaded span | [transmissions](transmissions/SKILL.md) |
| Split an axle or drivetrain | differential: carrier, side gears, spider | [transmissions](transmissions/SKILL.md) |
| Route drive past obstacles | Cardan shafts: centres, yokes, crosses, phasing | [transmissions](transmissions/SKILL.md) |
| Select a transmission path | driving rings: loose vs axle-locked gears | [transmissions](transmissions/SKILL.md) |
| Compact visible reciprocation | cam followers above phased cams | [engines](engines/SKILL.md) |
| Recognizable crank engine | slider cranks: rods, crank, guides distinct | [engines](engines/SKILL.md) |
| Independent wheel corners | wishbones and shocks on real mounts | [suspension-steering](suspension-steering/SKILL.md) |
| Steerable front axle | rack, tie rods and knuckles | [suspension-steering](suspension-steering/SKILL.md) |
| Raise a platform without tilting | four-bar lift with matched arms | [lifts-and-linkages](lifts-and-linkages/SKILL.md) |
| Indexed control detail | paddles and pawls with return and detent | [lifts-and-linkages](lifts-and-linkages/SKILL.md) |

These are patterns, not a list of permitted subjects: a car's wing linkage can teach a cargo lift. Real-set starting examples are placed by coordinates; read them for proportions and part choices, then build with ports. The `technic-*` recipes in `examples/recipes/` are small checked plans to copy ([write-plans](../write-plans/SKILL.md)).

## Find references in real sets

```sh
./ldraw-agent knowledge search 'technic gear pair'
./ldraw-agent knowledge search 'rack and pinion steering'
./ldraw-agent search submodels 'steering rack'
./ldraw-agent discover search submodels 'a compact braced chassis frame' --construction technic-structure --engine fts --limit 5
```

`search submodels` reads the official sets' section titles; `discover` ranks and prepares them ([find-constructions-and-parts](../find-constructions-and-parts/SKILL.md)). Inspect a reference's parent: it often supplies what the section lacks (the pinion for a steering rack, the bearings for a gearbox).

## Subskills

Read the one that matches your task:

- [transmissions](transmissions/SKILL.md): Technic transmission patterns: parallel gear trains, bevel trains and winches, worm-driven adjustment, differentials, Cardan shafts (U-joints), selectors and driving rings, with worked references (worm-drive support module, differential in an axle frame, 42075 differential rear axle mounted tilted). Use when transmitting or turning drive, building a gearbox, differential, winch or worm drive.
- [engines](engines/SKILL.md): Technic engines and reciprocating constructions: crank-and-connecting-rod engines, cam followers and how to integrate an engine's appearance, with worked references (single-cylinder piston and crank, 42050 V8 crank train under the cylinder banks). Use when building a piston engine, crankshaft, cam or any reciprocating mechanism.
- [suspension-steering](suspension-steering/SKILL.md): Technic suspension and steering: suspension corners, shock absorbers and fixed mounts, rack-and-pinion steering, and combining steering, suspension and drive, with worked references (steering rack carriage, 8081 steerable front axle whose pinion lives in the parent). Use when building a vehicle chassis with steering, wishbones, swing arms or shocks.
- [lifts-and-linkages](lifts-and-linkages/SKILL.md): Technic lifts, links and indexed controls: orientation-preserving (parallelogram) lifts, paddles, pawls and indexing, and the surroundings a mechanism needs. Use when building a lifting arm, linkage, lever, ratchet or indexed control.
- [motion-studies](motion-studies/SKILL.md): Mechanism relations and the optional motion study: interface graphs, partitioning by rigidity, choosing inputs, gear and joint relations in the correct frame, technic trace, and the separate ldraw-mecha animation project, with the supported gear drive starter. Use only when a brief asks to show or verify motion; static mechanisms are checked by the build.
- [ports-and-contracts](ports-and-contracts/SKILL.md): Reference for measured Technic interfaces: naming intended connections, measured ports and real lengths, checking mechanisms in the built pose, joint and restraint contracts, the automatic Technic checks, and a by-role table of the most used Technic parts with their hole, grip and shaft ports. Use when looking up a Technic part's ports, writing a section's structure or mechanism contract, or interpreting a technic.* diagnostic in depth.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/cards/technic.md](references/docs-agent-cards-technic.md)
- [docs/agent/guides/technic.md](references/docs-agent-guides-technic.md)
