# Measured Technic interfaces and structure contracts

## Name the intended connections

Each placement already has an `id`. A path such as `ram/cylinder` selects that
part through its parent placement. Paths are relative to the containing section;
use every parent ID. Repeated placements use their expanded `id-0`, `id-1` names.
Names refer to the current source, not the order of parts in an inspection.

Put the structural intent directly on the section:

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

This checks the two actual joints and requires an earlier STEP for the pin. `require_rigid` asks for one rigid structure, so it fails on a section with moving parts (`technic.mechanism_scope`); use `"scope": "joints"` for the mounts of a mechanism and a `mechanism` contract for what should move.
The existing Technic seating, occupied-span and restraint rules still apply.
Use `"retained_axles": ["drive-axle"]` when both axial stops are required;
a still-engaged bush with a gap against its supported stack then fails review.
Use `"scope": "joints"` for mounts in a delivered mechanism pose; it checks
declared connections and seating without claiming that the whole machine is
rigid. Keep `require_rigid` off in that scope. Neither scope verifies motion.

Old `"structure": "frame.structure.json"` files retain their numeric indices
and revision checks. Imported MPDs retain their numeric inspection selectors;
named paths require authored plan placements. A path to a whole module does not
identify one physical joint: select its actual mating part.

## Use measured ports and real lengths

Ports come from two tables, merged by `technic.registry()`:

- **Reviewed** (`ldraw_tools/data/technic-parts.json`): 39 hand-measured parts (common Technic bricks, straight beams, a thin beam, a rectangular frame, an axle/pin cross block, pins, axle-pins, a half pin, axles, bushes, a 16-tooth gear, a pneumatic cylinder). Each entry fingerprints its expanded geometry. They override the derived table.
- **Derived** (`ldraw_tools/data/technic-ports.json`, written by `scripts/technic_ports.py`): about 1,600 Technic parts, wheels and motors, read from the authored `SNAP_CYL` cylinders of the LDCad shadow library. A male is cut at its collars and where it changes between pin and axle, long pins into 20 LDU grips; long bores into 20 LDU cells; lengths snap to the 10 LDU module. A cross that is not square to the part's own axes (the end hole of a bent liftarm, turned by the bend) records its `radial` direction. Each entry fingerprints the connector metadata it was made from, so a changed library part loses its ports instead of keeping stale ones. The derivation reproduces all 150 reviewed ports (`tests/test_technic_ports.py`).

`scripts/technic_corpus.py ports` seats every derived pin and axle of the official Technic sets in `data/models-annotated`: a port that seats in fewer than half of its uses is withheld from the tools (`withheld` in the table) and re-measured on the next run. On the current corpus the table covers 98% of the Technic placements of 215 Technic-heavy sets, and 94% of their pins and axles seat. `technic parts` lists parts by role and use; `part CODE` lists one part's ports. Coordinates are **local LDU**.

An axle may stop partway into a hole: it keys or bears on what it fills if it fills a whole module, less the 2.5 LDU by which nominal lengths can exceed a blind bore. A cross keys within 5° of roll. A pin grip seats when it sits wholly in its hole, or two half-depth layers fill it.

`technic.invalid_seating` reports a pair that cannot be built: tilted or offset axes, a cross out of line, a pin in an axle hole, an axle with too little inside the hole, a pin barely touching a hole, or one hole across both grips of a pin (the collar in the bore). It also reports a pin that sits off-centre or part-way into a hole with at least 7.5 LDU (a plate's depth) inside. Studded sets do that with plates on bricks, so that case is always a warning. A half-filled grip is the warning `technic.incomplete_grip`. Neighbours on one shaft may seem to overlap by up to 3 LDU, because derived lengths round thin parts (7–8 LDU) up to 10; only larger overlaps are `technic.occupied_span`.

Seating findings (`invalid_seating`, `occupied_hole`, `occupied_span`) are errors only when every part involved has reviewed ports. With a derived port they are warnings, because on official sets the derived ports' findings fire above the one-per-1,000-placements rate an error may have. Fix them all the same.

- Hole pitch is normally 20 LDU. Brick/plate body heights are 24/8. Two plates between studded Technic bricks produce a 40-LDU hole separation.
- Three beam holes span 40 LDU between their end centres. Solid bounds are not nominal placement dimensions.
- Sampled thick/thin beams are 20/10 LDU thick. Two thin layers can share a 20-LDU pin grip; one alone does not complete its retaining seat.
- Origins, axes and keyed roll vary. Use port frames and proper rotations. Never stretch or reflect a physical part to close a frame.
- Cross holes constrain axle roll; suitable round holes act as bearings. Neither establishes axial retention by itself.

Pins have separate grips; mixed connectors have separate pin and axle ends. Friction comes from reviewed part identity, not colour or LDCad's editor `slide` flag. This repository-owned registry remains active when external shadows are disabled.

## Check mechanisms in the built pose

Every build that contains Technic ports runs `technic_checks.review`: solid-cell collisions, pins in the air, axles that can slide out, unbacked worms, and the findings of the kinematic graph in `mechanism.py` (rigid groups by union of studs, friction pins and keyed axle fits; revolute joints at frictionless pins and axles in round holes; gear, bevel, worm and rack couplings at the distances measured in the official sets, `ldraw_tools/data/technic-gears.json`). The [Technic card](../cards/technic.md#what-the-build-checks) lists the codes and their fixes.

Each rule was run on the official sets before it was enabled (`scripts/technic_corpus.py checks`; results in `docs/reports/benchmarks/technic-corpus.json`). Errors fire on fewer than 0.2 placements in 1,000 of correct official models. A gear held at an axle end only by its cross hole is how LEGO builds, so it is not reported.

A section's `mechanism` contract runs an instantaneous mobility analysis: the rank of the joint and gear constraints with the frame held still. It reports whether each input can move, which outputs move with it, which pivots are locked and the degrees of freedom of the working parts (pins that only spin are not counted). It ignores play, travel limits and strength, can mislead at a singular pose, and treats ball joints and telescoping parts as rigid. `technic trace PLAN` prints the graph.

## Check intended joints and restraint

`technic check` defaults to 500 occurrences; select a module with `--section` or deliberately increase `--max-instances`. Occurrence indices and contracts belong to the same selection. Read coverage and warnings even when `checks_passed` is true.

A [structure contract](../../../ldraw_tools/data/structure.schema.json) is a separate JSON file:

```json
{
  "version": 1,
  "require_rigid": true,
  "required_joints": [{"between": [1, 0]}, {"between": [1, 2]}],
  "assembly": [{"connector": 1, "before": [2]}]
}
```

Occurrence 1 must connect both members and appear in an earlier LDraw STEP than closing member 2. Generated contracts also bind to `model_sha256`. After changing or reordering a model, regenerate and review the contract; do not reuse stale indices or discard a revision mismatch. Hand-authored development contracts may omit the hash.

The checker reports receiving-hole engagement, thin-layer completion, duplicate occupation, missing mounts, unretained axles and bearings that still rotate. It checks connector-before-closure STEP constraints and groups members joined by at least two separated parallel pin axes. One pin remains a pivot; loops of such joints receive an unbraced-loop warning.

**This is a conservative restraint rule, not a general rigidity solver.** A valid diagonal truss or another pattern may require manual review or an additional reviewed recipe. `require_rigid` fails when the rule cannot join the structural members or their interfaces are unreviewed. Declare System body mounts individually too: one successful attachment cannot satisfy a four-point mounting design.

Swept insertion paths, hand access, arbitrary solid collisions, strength, stiffness, overturning stability and manufacturing tolerances remain outside the automated proof. Open hidden faces and the underside, review the build sequence, and report remaining physical checks.

## Automatic Technic checks

Put `"structure": "frame.structure.json"` on the section whose occurrence indices the contract describes. `technic plan` writes this link for you. `build` and `review` run that section's required-joint, seating, restraint and assembly-order checks, even with `--contacts none`. Included plans retain their own section contracts and relative paths.

Review saves the results under `structure` in `validation.json` and copies the contracts into `structure/`. A stale model hash or invalid occurrence index fails explicitly. Regenerate and review contracts after changing structural geometry or ordering; do not discard the mismatch. [Technic contracts](technic.md#check-intended-joints-and-restraint) describe the coverage and limitations.

## Mechanism part inventory

```sh
./ldraw-agent technic catalog --family gear
./ldraw-agent technic catalog 'constant velocity'
./ldraw-agent technic catalog 85543-f3
./ldraw-agent technic catalog --output output/mechanism-parts.json
./ldraw-agent technic catalog --model MODEL.mpd --connectors --output output/model-parts.json
```

`--output` saves every selected row; `--limit` limits only terminal rows. Use
`--force` to replace a catalog. `--connectors` expands part-local evidence and
may take longer for the whole library; search first for routine inspection.

The catalog combines every assignment in supplied `technic.py`, mechanical
name matches from other supplied categories, database descriptions and an
explicit [online watchlist](../../../ldraw_tools/data/mechanism-parts-watchlist.json).
Python assignments are read as data, without importing the generated module.
Duplicate sanitized names retain separate source lines and values.

Default catalog counts describe metadata records; installed availability and canonical identity remain unknown. Inventory includes historical, printed, composite and supplementary parts; these are not unique mould or retail-availability counts. Completeness is bounded by the listed inputs.

Model inventory expects a self-contained MPD/LDR. Unresolved external assemblies
are rejected instead of being counted as one physical part; embed them first.

Rows retain exact references, DB descriptions, sanitized symbols, source lines,
family tags and structural-profile keys. Default discovery does not load library
files. Explicit `--connectors` first narrows by query/family/model, then supplies
headers, licences, hashes, alias transforms and interface evidence for that
selection. Installed then means the file exists, not complete dependencies or
retail colour availability. Unofficial watchlist entries are not downloaded.
Use [part-information sources](../guides/part-information.md) for targeted queries;
construction guidance and examples still establish the building method.

`structural_profile` refers to the measured registry; `technic parts/check`
still enforce its geometry fingerprint. Search families and
[mechanism notes](../../../ldraw_tools/data/mechanism-part-notes.json) do not grant
validated animation support. `motion_profile: unreviewed` keeps that gap explicit.

Connector reports include provenance and section profiles, including possible
primitive-inferred false positives. Embedded DAT definitions retain their
physical boundary and need separate review; installed namesakes do not provide
their interfaces. Follow the [advanced workflow](../guides/mechanisms.md) to
establish mobility, torque transfer and constraints.

For new metadata, update the supplied information sources through their normal
maintenance process. Explicit connector inspection also depends on the installed library. Add known missing parts to the watchlist with a dated official
LDraw library/tracker URL. Add reviewed local frames only after inspecting the
exact variant, aliases and geometry; keep fixtures for executable support.

