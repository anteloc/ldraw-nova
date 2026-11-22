---
name: transmissions
description: 'Technic transmission patterns: parallel gear trains, bevel trains and winches, worm-driven adjustment, differentials, Cardan shafts (U-joints), selectors and driving rings, with worked references (worm-drive support module, differential in an axle frame, 42075 differential rear axle mounted tilted). Use when transmitting or turning drive, building a gearbox, differential, winch or worm drive.'
---

# Technic transmissions

Choose and build a drive path: parallel gears, bevel corners and winches, worm adjustment, differentials, Cardan shafts and selector gearboxes. Port placement, mesh distances and the `technic.*` checks are in the parent [technic](../SKILL.md) skill. The measurements here come from real sets (W16, Defender, Chiron, Mustang studies in `examples/technic-studies/README.md`): they are starting evidence for construction, not universal constants or Nova checks.

Start from a checked recipe when one fits: `technic-gear-pair`, `technic-bevel-corner`, `technic-worm-drive` in `examples/recipes/` ([write-plans](../../write-plans/SKILL.md)).

## Parallel gear trains

The W16 has three meshes: input 20T to central-crank 12T, then central 24T to each of two lower-crank 24T gears. The first pair uses double-bevel parts on **parallel shafts**: the part name alone does not determine the arrangement.

| Pair in `42083 - engine.ldr` | Centres in section coordinates | Plane | Spacing |
| --- | --- | --- | ---: |
| Input `83` to central `82` | (0,90,-40) to (0,50,-40) | Z=-40 | 40 |
| Central `68` to lower `84/16` | (0,50,200) to (-36,98,200) | Z=200 | 60 |
| Central `68` to lower `85/16` | (0,50,200) to (36,98,200) | Z=200 | 60 |

- The lower gears are 72 LDU apart, so they are not another 24T/24T mesh. Offsets of 36 and 48 LDU give the 60 LDU centre distance: a useful nonrectangular shaft arrangement. Keep the real support locations when adapting it.
- Pitch radius `1.25 * tooth_count` LDU is a shortlist calculation for the reviewed profiles. Then inspect the actual gear type, tooth plane, thickness, bushes and support stack. Do not apply it to every bevel, worm, rack or turntable.
- Before quoting a ratio, state axis conventions: raw discovery reports can reverse local axes and list gears in another order. About common +Z axes the W16 increments are -5/3 (input to central) and -1 (central to each lower).

## Bevel trains and winches

The Defender routes a vertical knob shaft through a longitudinal intermediate shaft to a transverse drum: **two 12T/12T bevel meshes and three rotating shaft groups**.

- Preserve the mating tooth/apex geometry at each turn, with bearings and retention for every shaft.
- A change of direction is a packaging tool: an accessible control drives an output on another face.
- Separate drum, ratchet, pawl, rope and hook roles in the brief. The source shows drum rotation while rope/hook and pawl stay static; it does not establish winding, holding a load or one-way engagement. Supply those parts for a new crane or winch and describe unreviewed action honestly.

## Worm-driven adjustment

A single-start worm (`4716.dat`) turns its wheel with ratio magnitude `1 / teeth`. The Mustang audit shows it beside an 8T wheel driving an output shaft and liftarm cranks; the link from cranks to frame is unresolved, so it is not a solved ride-height recipe.

- The thread is finite: the source detector accepts contact within ±16 LDU along the worm's local Z, inside thread geometry reaching about ±20. These are detection bounds for this part, not mounting tolerances.
- Check perpendicular shaft axes, distance (10 LDU + the gear's pitch radius), wheel midplane **and** thread overlap. A correct distance between infinite axis lines can still put the gear beyond the thread.
- Back the worm on both sides (`technic.thrust_unbacked`). Friction, backdriving and self-locking are not established.

### Worm-drive support module

From 42042 Tower Crane (`42042 - spoolwormgear.ldr`, 14 placements). Liftarms and cross blocks mount a worm shaft and a separate axle carrying an 8-tooth gear; the winding drum and cable belong to the parent `42042 - tower.ldr`. Preserve the worm/gear placement, bush stack and thin-beam layer; copy the support geometry as a unit. No load-holding claim.

```sh
./ldraw-agent mechanism export worm-drive --outdir output/my-worm-drive
./ldraw-agent build output/my-worm-drive/scene.plan.json --contacts none --output output/my-worm-drive/my-worm-drive.mpd
```

## Differentials

- Treat the carrier, two side gears and carrier-mounted spider as separate roles. The carrier supports the spider axis; side shafts leave through bearings and need retention.
- In the ideal symmetric arrangement the carrier angle is the mean of the side angles about common axes. That explains the layout; it says nothing about traction or torque split.
- Do not glue the three coaxial shafts together, and do not replace the mechanism with two independent wheel axles.
- For a new chassis, adapt the housing/frame mounts while keeping the internal bevel arrangement, shaft spacing and axle stops.

### Differential in an axle frame

From 42083 (`42083 - frontaxlediff.ldr`, 29 placements). An open rectangular frame and beam mounts carry the carrier, internal bevels, two axle outputs and mating drive gears; the parent `42083 - frontaxle.ldr` supplies wheels and chassis. Keep internals, axle insertion depths and the frame; place the whole module first, then adapt the exterior supports.

```sh
./ldraw-agent mechanism export differential --outdir output/my-differential
./ldraw-agent build output/my-differential/scene.plan.json --contacts none --output output/my-differential/my-differential.mpd
```

### 42075 differential rear axle with U-joints, mounted tilted

An **inspiration** study (63 parts; `manual export` is blocked because the shock child is a generated spring mesh of raw polygons). Steps: differential with 12-tooth bevels (2), input double bevel and U-joint entering the differential in its open 7×5 frame (3), cross-block hub frames and half-shafts (5), shock child (7). The parent places it with matrix `-1 0 0 / 0 0.932 -0.363 / 0 -0.363 -0.932` (about 21° about X plus a half turn).

- Keep the differential frame, U-joint input and half-shafts together.
- Derive the tilt for the new chassis instead of copying the matrix: the tilt sets the input shaft angle.
- Replace the spring mesh with a real shock absorber part. Travel and U-joint angles were not checked.
- Inspect: `./ldraw-agent discover show submodel-a6ae0a0fca56420448522444`; replay its board with `./ldraw-xray board run examples/submodel-atlas/recipes/02-42075-rear-axle.json --output output/boards/02-42075-rear-axle`.

## Cardan shafts

- A joint has two yokes and a cross with different axes. Measure the joint centre, shaft lines and fork orientations; do not infer them from an axle's bounds. Leave space around both forks and adjacent axle tips.
- The Defender pairs joints with parallel end shafts, equal bends and matched fork phasing, which cancels the speed variation at the far end (the middle shaft still varies). This is a routing technique, not a rule that any two-joint shaft is constant velocity.
- Moving suspension changes joint centres and bend angles. Do not combine a fixed-geometry propshaft with moving suspension by placing their ends close together; check reach, fork phase and the hub interface at the delivered pose.

## Selectors and driving rings

- Constant-mesh gears can spin freely on a shaft until a driving ring engages their clutch faces. Identify free gears, axle-locked gears, shaft joiners, sliding rings, extensions, forks and stops before reusing a gearbox.
- The Defender four-speed alternates two rings across four states; ring A starts at +10 LDU toward first gear, so neutral and opposite are -10 and -20 from that pose. Setting every slider to a guessed neutral changes the assembly.
- Keep ring travel and fork space clear in the enclosure. The fork follows an arc while the ring follows a line: a plausible final picture does not prove engagement throughout the lever's travel.
- The Chiron's saved gearbox has **395 retained source parts plus two added `32270.dat` gears** (`R/S6_12T`, `R/S5_12T`): a qualified reconstruction, not verified official parts. Its animation timings are approximations; learn packaging and topology only.

## Reuse a real-set module

1. Read the build manual and parent context first; the parent often supplies the drum, wheels or bearings.
2. `mechanism export NAME --outdir DIR` writes a `scene.plan.json` placing the whole module with a proper transform. Its `source_origin` is a positioning frame, not an asserted connector.
3. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Inspect the combined model.
4. Operation notes are interpretations of source and images: no movement, load rating or physical operation is certified.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/mechanism-patterns/transmissions.md](references/docs-agent-guides-mechanism-patterns-transmissions.md)
- [examples/worm-drive/GUIDE.md](references/examples-worm-drive-GUIDE.md)
- [examples/differential/GUIDE.md](references/examples-differential-GUIDE.md)
- [examples/42075-differential-axle/GUIDE.md](references/examples-42075-differential-axle-GUIDE.md)
