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

This checks the two actual joints and requires an earlier STEP for the pin.
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

The initial registry covers the original **34 definitions plus aliases**, plus the measured workshop interfaces: common Technic bricks, straight beams, a thin beam, a rectangular frame, an axle/pin cross block, ordinary and long pins, axle-pins, a stud-ended half pin, axles and bushes. `technic parts` lists exact IDs, nominal ports, part roles and `geometry_matches`. Coordinates are **local LDU**.

Each entry fingerprints its expanded geometry. Changed or unreviewed definitions do not receive curated ports. Do not update a hash without measuring and reviewing the new part. Additional connector blocks, bent/flexible members, panels and hubs need interface curation before a strict structural contract can rely on them.

- Hole pitch is normally 20 LDU. Brick/plate body heights are 24/8. Two plates between studded Technic bricks produce a 40-LDU hole separation.
- Three beam holes span 40 LDU between their end centres. Solid bounds are not nominal placement dimensions.
- Sampled thick/thin beams are 20/10 LDU thick. Two thin layers can share a 20-LDU pin grip; one alone does not complete its retaining seat.
- Origins, axes and keyed roll vary. Use port frames and proper rotations. Never stretch or reflect a physical part to close a frame.
- Cross holes constrain axle roll; suitable round holes act as bearings. Neither establishes axial retention by itself.

Pins have separate grips; mixed connectors have separate pin and axle ends. Friction comes from reviewed part identity, not colour or LDCad's editor `slide` flag. This repository-owned registry remains active when external shadows are disabled.

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
name matches from other supplied categories, installed part names and an
explicit [online watchlist](../../../ldraw_tools/data/mechanism-parts-watchlist.json).
Python assignments are read as data, without importing the generated module.
Duplicate sanitized names retain separate source lines and values.

Generate counts from the current library. Inventory includes historical, printed, composite and supplementary parts; these are not unique mould or retail-availability counts. Completeness is bounded by the listed inputs.

Model inventory expects a self-contained MPD/LDR. Unresolved external assemblies
are rejected instead of being counted as one physical part; embed them first.

Rows retain exact references, original descriptions, sanitized symbols and
source lines, headers, licences, hashes, alias chains/transforms, family tags
and existing structural-profile keys. Installed means the file exists, not
complete dependencies or retail colour availability. Missing parts stay visible;
unofficial watchlist entries are not downloaded automatically.

`structural_profile` refers to the measured registry; `technic parts/check`
still enforce its geometry fingerprint. Search families and
[mechanism notes](../../../ldraw_tools/data/mechanism-part-notes.json) do not grant
validated animation support. `motion_profile: unreviewed` keeps that gap explicit.

Connector reports include provenance and section profiles, including possible
primitive-inferred false positives. Embedded DAT definitions retain their
physical boundary and need separate review; installed namesakes do not provide
their interfaces. Follow the [advanced workflow](../guides/mechanisms.md) to
establish mobility, torque transfer and constraints.

For new parts, refresh the library through its normal update process and rerun
the command. Add known missing parts to the watchlist with a dated official
LDraw library/tracker URL. Add reviewed local frames only after inspecting the
exact variant, aliases and geometry; keep fixtures for executable support.

