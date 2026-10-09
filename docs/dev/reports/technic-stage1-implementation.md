# Technic stage 1: implementation and verification

**Later scope update:** the user subsequently authorized [Stage 2 construction from mechanism examples](technic-stage2-implementation.md), with analytical mechanism verification deferred. The scope statements below describe the Stage 1 decision at the time of its verification.

Verified on 2026-09-26. Stage 1 now supports **static Technic structures and their System body mounts**. The [structural atlas](../../examples/technic-atlas/README.md) provides four editable examples; the [agent workflow](../agent/technic.md) explains how to adapt them. Stage 2 mechanisms remain gated on the user's explicit decision.

## What changed

- A [reviewed registry](../../ldraw_tools/data/technic-parts.json) covers 34 part definitions and four aliases: frames, beams, Technic bricks, pins, mixed axle-pins, axles, bushes and a stud-ended System bridge. Exact geometry fingerprints prevent silently applying the reviewed ports to changed definitions.
- Connector inspection, snapping and geometry checks use those measured ports. Seating checks reject collar-in-bore and tip-only placements, incorrect keyed roll, incomplete thin-layer grips and duplicate occupation. Axles can carry separate members and retainers on distinct intervals. Existing System interfaces remain available.
- `technic check` reports joint engagement, required mounts, axle retention, remaining pivots and connector-before-closure STEP constraints. A [structure contract](../../ldraw_tools/data/structure.schema.json) can bind these requirements to a model revision. The checker groups members attached through multiple separated pin axes; it does not infer rigidity from simple connectivity.
- `technic list`, `technic parts`, `technic plan` and `examples --family technic` expose the vocabulary and recipes. Plans use the existing assembly schema and build command. Tower recipes support one, two or three cells.
- Discovery accepts `--construction technic-structure`. It considers the selected section and its expanded BOM, allowing useful static sections from models with mechanisms while filtering obvious mechanism contents. The default System scope is preserved. Both the Jev route and explicit offline FTS use this scope; source results still require structural review.
- Agent documentation now routes Technic structures through their own checks, assembly-access review, body-mount planning and visual review. Mechanism work remains outside the authorized stage.

## Checked examples

| Example | Placements | Reviewed mechanical contacts | Restrained member groups | Python/LeoCAD BOM |
| --- | ---: | ---: | ---: | --- |
| [Reinforced frame](../../examples/technic-atlas/reinforced-frame/GUIDE.md) | 13 | 16 | 1 | Match |
| [Box chassis](../../examples/technic-atlas/box-chassis/GUIDE.md) | 18 | 24 | 1 | Match |
| [Frame tower](../../examples/technic-atlas/frame-tower/GUIDE.md) | 36 | 56 | 1 | Match |
| [Service platform](../../examples/technic-atlas/service-platform/GUIDE.md) | 55 | 32 | 1 | Match |

Each includes its MPD, plan, generator, mounting contract, geometry report, structural report, BOM comparison and seven rendered views. All pass geometry checks without errors and their structural contracts without diagnostics. Mechanical-contact counts exclude the service platform's ordinary stud connections; its contract also checks the eight pin-to-deck mounts.

All **28 views were opened and inspected**: home, front, back, right, left, top and bottom. The [visual review](../../examples/technic-atlas/visual-review.md) records appearance, underside mounts, corrections and remaining physical checks. Per-model review records bind the model and all seven image files by SHA-256. Regeneration preserves a review only while those hashes match.

## Verification performed

The complete automated suite passed: **199 tests in 77.97 seconds**. Technic regressions cover geometry fingerprints and aliases, phantom-hole removal, seating, keyed roll, mixed connectors, thin layers, occupied spans, retained axles, legal snap positions, pivot versus multiple-pin restraint, missing mounts, stale contracts, STEP order, every recipe and all three tower heights. Existing System, vehicle, discovery and import tests also passed.

The CLI plan → build → structural-check workflow succeeded with a generated revision-bound contract. Rebuilding the atlas reproduced the checked-in MPD bytes and preserved the matching reviews. Changed-source and changed-image checks confirmed that stale reviews are not carried forward. Documentation commands use portable repository paths.

A bounded **offline FTS** query for `frame chassis support` searched `SUBMODELS_DESCRIPTIONS_JEV.full_description` in structural mode. Of 24 shortlisted sections, 19 passed measurement filters; four were rejected for mechanism contents and one for exceeding 250 placements. The four returned sections were:

| Source model | Section | Placements |
| --- | --- | ---: |
| `42099-1.mpd` | `42099 - chassis3.ldr` | 24 |
| `42096-1.mpd` | `42096 - chassis4.ldr` | 21 |
| `42125-1.mpd` | `42125 - chassisfront2.ldr` | 21 |
| `42129-1.mpd` | `42129 - hframe.ldr` | 33 |

These are discovery candidates, not newly approved recipes. Their parent models contain mechanisms; the selected sections have no mechanism parts identified by the filter. They include parts outside the initial reviewed registry, so importing them does not establish a passing strict structural contract. This verification exercised the explicit offline engine; it makes no new claim about live Jev availability.

The compact [evidence record](technic-stage1-evidence.json) retains counts, source hashes, test results and discovery identifiers. Detailed command logs and the full offline search report are under ignored `output/technic-stage1/` in the implementation workspace.

## Boundaries for using stage 1

The multiple-pin rule is conservative, not a general rigidity or truss solver. A valid construction outside that vocabulary may need further interface curation and manual review. `require_rigid` concerns the recognized structural members; warnings about shaft rotation or axial retention still need attention, and intended body mounts must be declared individually.

General solid collisions, swept insertion paths, hand access, real mould tolerances, strength, stiffness and loaded stability remain outside the automated proof. Geometry validation and visual inspection remain necessary. No physical build or load test was performed, and no mechanisms were implemented. The user decides whether these stage-1 results justify proceeding to stage 2.
