# Construction stages: implementation and evidence

The next working layer is implemented on `hybrid-approach`: small parameterized constructions, measurable feature requirements, exact fitting calibration, and a common check/render/review/export route. The designer still owns the composition. This layer reduces repeated placement reasoning and makes unresolved construction visible before repetition; it does not automatically invent good architecture.

## Implemented

- `construction list/export`: a two-layer bonded floor (nine width/depth combinations), a glazed bay (arched or straight trim), and a supported entrance canopy (six depth/height combinations). All 17 combinations pass static and feature checks. Exported source stays editable and records mounting grids, reserved spaces, build sequence, supported parameters and part/source hashes. New techniques remain possible through isolated studies.
- `stage prepare/review/export`: accepts JSON plans or MPDs from any authoring route. Preparation runs the same static check, optional feature requirements, fitted-camera LeoCAD views and BOM comparison. All views need a recorded review. Changed sources, included plan content, imported assets, requirements, artifacts, part dependencies, connectors, colours or checking code invalidate export. Failures preserve the prior delivery. A failed preparation can be retried without reusing old acceptance.
- Five feature checks: dimension limits, envelope coverage, vertical clearance, empty reserved volumes, and direct module connections. A connected canopy moved away from its doorway passes geometry and fails coverage, as intended. These are conservative envelope checks, not functional simulation.
- Four reference-backed window fittings: exact part codes, relative transforms and complete DAT dependency hashes. Matching pairs contribute connections and retain their observed mesh overlap and reference evidence in reports. Shifted panes, duplicate panes, changed part definitions and neighbouring wall collisions do not inherit the calibration. Generic tolerances remain unchanged.

The shared export route is an enforceable tool path, not a restriction on arbitrary filesystem writes. Instructions now require it for final System models. The existing separately scoped mechanism workflow remains distinct.

## What was verified

The full suite passed **296 tests**. After correcting cropped preview framing, the **45 focused construction/stage tests** passed again. They exercise every parameter combination, unbonded floors, wrong canopy coverage, occupied clearances, fitting perturbations, shared-primitive cache invalidation, stale source/evidence, changed included plans and requirements, missing renders, mismatched BOMs, failed refreshes and preservation of previous deliveries.

The three default constructions were generated, checked, rendered with real LeoCAD, opened from home/front/right/top, reviewed and exported through the new gate. Python/LeoCAD BOMs match exactly. Their local evidence is in `output/construction-implementation/`:

| Default study | Parts | Static / feature checks | Review |
|---|---:|---|---|
| [Bonded floor](../../output/construction-implementation/reviewed/bonded-floor.mpd) | 32 | PASS / PASS | Accepted as a construction sample; loads and parent support remain untested |
| [Glazed bay](../../output/construction-implementation/reviewed/glazed-bay.mpd) | 15 | PASS / PASS | Accepted; the arch above the rectangular frame remains open |
| [Entrance canopy](../../output/construction-implementation/reviewed/entrance-canopy.mpd) | 41 | PASS / PASS | Accepted; door swing and column stiffness remain untested |

Views: [floor](../../output/construction-implementation/bonded-floor-stage/views/home.png), [bay](../../output/construction-implementation/glazed-bay-stage/views/home.png), [entrance](../../output/construction-implementation/entrance-canopy-stage/views/home.png). The sibling stage folders contain source snapshots, requirement results, BOM comparisons, hashes and actual review notes. Cropped default LeoCAD views were caught during inspection and replaced with cameras fitted to full model bounds.

The unchanged repaired **2,651-part Copper Lane control** now passes the calibrated checker: zero reported collisions, seating errors, duplicates, disconnected parts or unresolved overlaps; 106 exact calibrated fittings. Its stage took 4.68 seconds for preparation/checks and 40.81 seconds for five rendered views plus BOM comparison in one local run. The defaults took roughly 0.4–0.5 seconds for preparation/checks and 11–12 seconds for four views. These exclude agent design, research, review and library initialization; they are not end-to-end agent benchmarks.

**The large control's visual review requests revision.** Its front remains excessively repetitive at this height, the side/rear elevations are plain, and the chimney tops need better treatment. It retains the inherited scope without stairs. Static PASS and a matching BOM did not cause visual acceptance: `stage export` correctly refused to promote it. [Technical stage](../../output/construction-implementation/large-stage/stage.json) · [front view](../../output/construction-implementation/large-stage/views/front.png) · [review](../../output/construction-implementation/large-stage/visual-review.json) · [blocked export](../../output/construction-implementation/large-export-rejection.json).

The three existing negative controls still fail: shifted panes produce four collisions and four disconnected parts; a lifted roof leaves 137 disconnected parts; the half-stud sign mistake leaves the sign disconnected. The updated Willow Quay check still reports **all 178 collisions**, two seating errors and 2,364 parts outside its main recognized group. Only 42 legitimate window-pair overlap reviews were resolved; six other overlaps remain unresolved. [Controls](../../output/construction-implementation/negative-controls.json) · [Willow Quay recheck](../../output/construction-implementation/willow-quay-check.json). All 57 frozen benchmark files retain their original hashes.

## Remaining work and limits

This establishes a tested construction foundation, not reliable open-ended agent design. A fresh Sol benchmark has not been run with these tools. The next useful trial should choose a new composition, review its massing first, then give Sol bounded construction tasks with parent interfaces. It should include an unfamiliar join, a fixed effort limit and separately recorded design/tool/repair time.

The catalog still needs supported roof/dormer/chimney constructions, stair/landing interfaces and more varied wall/corner techniques. Existing master references remain available while those are established. No current static pass proves strength, insertion order, usable door motion, retail part/colour availability or complete buildability. Visual review is a recorded judgment, not an automated aesthetic score.

Usage: [construction workflow](../agent/construction-workflow.md) and [tool commands](../agent/tooling.md#construction-studies-and-stage-review). The earlier [construction-reuse experiment](construction-led-evolution.md) remains historical evidence; its raw pre-calibration reports have not been rewritten.
