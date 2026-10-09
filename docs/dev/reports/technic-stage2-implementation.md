# Technic stage 2: construction from mechanism examples

Implemented and checked on 2026-09-26. Agents can now discover mechanism references, study rendered build pages, describe intended operation and export editable assemblies for new models. **Analytical mechanism verification is deferred at the user's request.** The implementation adds no motion solver, transmission analysis or functional-certification requirement.

Start with the [mechanism atlas](../../examples/mechanism-atlas/README.md) and [agent workflow](../agent/mechanisms.md). The [evidence snapshot](technic-stage2-evidence.json) records exact sources, Jev results, hashes and checks.

## What agents can do

`discover search ... --construction mechanism` considers the selected description and measured BOM, allowing useful assemblies regardless of the parent's theme. It works with Jev and offline FTS; relevance and mechanism vocabulary are discovery filters, not proof of completeness or function.

`mechanism prepare` extracts the chosen section with dependencies and attribution. It produces a manual for each assembly section, highlighted step images, per-step placement lists, a physical BOM, containing-parent placements, operation notes and an editable placement plan. Subassemblies remain callouts and embedded DAT geometry remains attached to its physical parts. Empty groups are omitted while source step numbers are retained, including a final group without a trailing STEP.

The renderer uses LeoCAD's step-export facility, as in the preceding `ldraw-render-steps.sh` trial. Argument lists replace shell interpolation, temporary outputs prevent stale renders from masquerading as new ones, and the existing embedded-part adapter supports custom definitions. Cameras stay fixed to the completed section's bounds throughout the sequence. The installed shell script is unchanged.

`mechanism review` records the images actually opened and binds the manual's artifacts by hash. `mechanism export` requires current visual review, descriptive operation notes, passing source checks and a matching rendered BOM. Exported files rebuild without the annotated-model originals; the toolkit and ordinary parts library are still needed. The placement plan positions the whole source assembly, and the bundled MPD remains editable for internal changes. Its origin anchor is a placement frame, not an asserted physical joint.

The [atlas generator](../../examples/mechanism-atlas/generate.py) recreates selected studies from pinned source hashes. Each study also has its own portable placement generator. Refreshing a study invalidates its old visual review. Existing System and Stage 1 structural defaults remain unchanged; mechanisms use normal source/geometry checks with connector analysis explicitly skipped, and fixed-member contracts remain scoped to stationary supports.

## The six studies

| Study | Source model / section | Placements | Steps | Images opened |
| --- | --- | ---: | ---: | ---: |
| Gear and axle module | `42042-1.mpd` / `42042 - gearbox4.ldr` | 35 | 5 | 16 |
| Worm-drive support | `42042-1_Tower-Crane.mpd` / `42042 - spoolwormgear.ldr` | 14 | 3 | 7 |
| Steering rack carriage | `9393-1.mpd` / `9393 - steering.ldr` | 10 | 3 | 7 |
| Piston and crank | `42048-1.mpd` / `42048 - engine.ldr` | 19 | 4 | 9 |
| Differential | `42083-1.mpd` / `42083 - frontaxlediff.ldr` | 29 | 4 | 9 |
| Driven turntable | `42068-1.mpd` / `42068 - turntable.ldr` | 25 | 3 | 7 |

Total: **132 physical placements, 22 source steps, 49 step images and six final previews**. All 55 images were opened. All source checks pass and all six Python/LeoCAD BOMs match by part, colour and quantity.

These selections teach complementary constructions while staying small enough to inspect. The steering section lacks its driving pinion; the worm section needs the parent's winding assembly; the gearbox section needs parent context for the complete power path. Those dependencies are explicit in the guides and operation notes. The piston source groups the internal pieces and cylinder in one step, so its pictures cannot reveal every part before enclosure. Per-step lists and source inspection fill that construction-information gap.

Visual review caught a dropped embedded cylinder in the initial piston preview even though its BOM matched. Preserving the complete preview dependency closure fixed it; a regression test covers the embedded part and subpart. The corrected images were regenerated and inspected. See the [visual review](../../examples/mechanism-atlas/visual-review.md).

## Evidence and checks

- A bounded live Jev availability request succeeded. Five new role-specific searches queried `SUBMODELS_DESCRIPTIONS_JEV.full_description`, scoring 150 candidates each. The gear module retains the preceding live Jev trial's selection. Exact ranks, scores, returned text and source identities are in [selections.json](../../examples/mechanism-atlas/selections.json). Searches ran sequentially after concurrent CLI calls exposed a shared-cache SQLite lock.
- Offline discovery with `--construction mechanism --engine fts` returned three measured worm-drive references, including the selected crane module. It uses explicit keyword ranking and makes no TypeSafe calls.
- All six original model hashes still match. The piston extraction records 13 comment-order repairs around INVERTNEXT in copied embedded geometry; the other five extractions record no such changes. Original authors and licences remain in the copied sections.
- Every curated study passed CLI export → build → ordinary geometry validation → BOM comparison, and its exported local `generate.py` rebuilt successfully. The rebuilt BOMs match the retained LeoCAD exports. These checks include the piston model's embedded definitions.
- **206 tests passed in 80.78 seconds.** The seven new tests cover final unterminated steps, empty step gaps, nested callouts, colour inheritance, embedded dependencies, artifact integrity, incomplete/stale reviews, refresh invalidation, export boundaries, source paths with spaces, fresh renderer outputs and mechanism discovery. Existing structural, vehicle, System and reference tests also pass.
- A Node DOM harness exercised all 49 step/view selections in the six offline HTML manuals, their part tables and previous/next navigation. This checks viewer behavior, not browser layout. The rendered PNGs were inspected separately.

Source checks retain warnings: the temporary validation wrapper lacks a Name header; contacts are deliberately skipped; curved Technic parts exceed the rectangular-body collision coverage. The exported placement builder supplies its own complete model header. No warning has been reclassified as a mechanism failure or hidden as a functional success.

The manuals provide reusable construction evidence and teach how to study additional sources. Their operation notes are interpretations, and the renders share the source's assumptions. Physical operation, load capacity, insertion movements and motion clearance are not certified; analytical mechanism verification remains outside this stage's requested scope.
