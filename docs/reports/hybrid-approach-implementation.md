# Master-led hybrid: implementation and remaining work

10 October 2026. Branch: `hybrid-approach`, based on master at `45f2fdba`.

The authoring process now puts composition and visual iteration first. Master's reference discovery, architectural examples, custom generators, JSON plans, module assets and subject-specific construction guides remain available. The optional kit supplies placement helpers underneath that process. It does not prescribe a whole-model recipe or substitute construction statistics for visual judgment.

## Implemented

- **Drafts before construction approval.** `build --draft` and `Model.save(..., draft=True)` write explicitly tagged, renderable drafts despite unresolved geometry. `look` renders contact sheets without requiring a passing construction check. Invalid assembly source still fails.
- **A design brief that survives repairs.** Instructions require early views, spatial and visual feature requirements, and repairs that preserve proportions and function. The [brief template](../agent/design-brief.md) records feature intent and review evidence. This is an authoring/review record, not an automatic natural-language verifier.
- **Optional placement helpers.** Grid placement, port mating, hinges, pins, walls, fills and mirroring coexist with explicit coordinates and matrices. Exploration is the default; `strict=True` supplies incremental construction feedback. `Model.plan()` exports the existing version-1 plan format.
- **Composed module interfaces.** Sections export real ports and plan anchors. Nested and rotated instances preserve port positions, directions and reference frames. New parts can mate to these ports; whole-module mating is not implemented. Finish a section before instancing it.
- **Final saves preserve the last accepted file.** Kit `save(path)` checks a temporary candidate and raises `KitValidationError` on FAIL or REVIEW. It replaces the output only after PASS. Legacy `build` retains master's selected-check behavior; the agent workflow also requires the new `check` and relevant subject-specific checks before delivery.
- **More conservative construction evidence.** Compatible profiles and socket entry direction are checked before mating. Connected bodies are still tested outside their shared cylindrical engagement region. Similar descriptions, overlapping boxes and matching embedded-part bounds do not establish connections. Unknown connectors, incomplete meshes, unsupported transforms and unresolved overlaps remain visible. Declaring an overlap cannot turn it into PASS.

The new commands are additive: `ports`, `check` and `look`. Existing discovery, extraction, build, geometry, Technic, mechanism and render commands remain available. Pillow is pinned for contact-sheet composition.

## Verification

The regression suite covers rejected window/chimney intersections, unsupported ridge placement, incompatible profiles, reverse socket entry, failed-save preservation, explicit drafts, valid stud/pin/wheel assemblies, rotated and nested module interfaces, strict module placement, recursive-section rejection, embedded parts without connectors, graph requirements, and actual LeoCAD rendering of a failing assembly.

The [canopy study](../../examples/python_kit.py) demonstrates draft-to-engineering repair: the canopy begins disconnected; four columns are added while its 6-by-4-stud footprint and height remain unchanged. The final static check passes. Generated source, plan, reports and images are under `output/porch-study/`.

Rechecking the original audit fixtures gives:

| Input | Current result |
|---|---|
| Two overlapping `60592` windows | FAIL: one collision and one disconnected part |
| Isolated `3043` ridge / inverted `6143` chimney | FAIL: one collision and one disconnected part |
| Original 134-part Hollyhock Cottage | FAIL: two ridge/chimney collisions and six disconnected chimney parts; two shutter/window overlaps require review |

Reports are retained under `output/hybrid-verification/`. The supplied cottage source was not changed. Reported collision severity is a coarse displacement estimate, not a precise penetration measurement.

Run verification with `.venv/bin/pytest -q`. Run the small authoring demonstration with `.venv/bin/python examples/python_kit.py`; its module docstring contains the preview commands.

Local validation: the full suite passed **249 tests**; after adding the final embedded-part and graph regressions, `tests/test_hybrid.py` passed **25 tests** (251 distinct tests passed across these runs). `git diff --check` is clean. Both canopy contact sheets were rendered with LeoCAD and opened for visual review: the final views retain the draft canopy's dimensions and height and show its added supports.

## Boundaries and next work

PASS means the covered static checks found no unresolved findings. It does not establish physical strength, inventory availability, mechanism motion or beauty. The checker uses body meshes with male studs excluded, supported body boxes, and available authored/inferred connector metadata. It is not an independent physical simulator.

A known valid `4275b`/`4276b` finger hinge at 30 degrees remains REVIEW because its permitted engagement region has not been validated. The regression deliberately preserves that uncertainty. Geometry-specific hinge, clip, tyre, gear and flexible-part support needs reviewed positive examples and deliberately corrupted negative examples; broad family exemptions would reintroduce false passes.

The next construction work is explicit support faces, reserved openings/envelopes and whole-module attachment; reviewed roof/chimney, dormer, porch and retained wheel/axle details; and connection occupancy checks shared with master's detailed Technic tooling. Repairs should be tested against preserved feature dimensions as well as construction results.

The remaining product evaluation is a matched generation benchmark across buildings and Technic prompts: repeated runs with the same model, agent settings and part library, judged on composition, feature completion, reviewed defects and unresolved interfaces. This implementation has not established an improvement in generated-model beauty or proved general mechanical correctness. It establishes the creative workflow and construction safeguards needed to evaluate that next.
