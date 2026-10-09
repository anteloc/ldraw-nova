# Build manuals and advanced spaceship support

Implemented and verified on 2026-09-26. The [general build-manual workflow](../agent/build-manuals.md) now documents how to discover a submodel, read its source steps as illustrated instructions, inspect its parent interfaces and add a useful construction to any atlas. The [spaceship workflow](../agent/spaceships.md) and [atlas](../../examples/spaceship-atlas/README.md) apply it to advanced spacecraft, including Star Wars examples.

## Tooling and agent workflow

`manual prepare`, `manual review` and `manual export` expose the source-step process independently of mechanism-specific notes. General studies describe their lesson, construction, interfaces, parent context and reuse notes. The existing mechanism commands remain compatible and retain their operation-specific fields. Analytical mechanism verification remains deferred.

Preparation preserves original source steps and child callouts, embedded part definitions, explicit colour inheritance, attribution and bounded repairs. `--overview` supplies completed-model views and section/step data for selecting smaller studies, clearly labeled separately from build pages. Both forms bind source, notes, checks and images to the review by hash. Changed evidence or incomplete review blocks export.

`spaceship list`, `spaceship details` and `examples --family spaceship` expose the atlas. `spaceship brief starfighter|freighter|capital-ship` supplies distinct silhouette, palette, module, dedicated-part and review guidance. `spaceship export` copies a reviewed construction and its editable placement plan. It explicitly rejects the inspiration-only entries; a brief does not claim to generate a model.

Agent instructions and README navigation now route spaceships to their own design process: decide scale and identity, choose dedicated canopy/engine/wing parts, build a real frame and mounts, shape the hull, concentrate surface detail and inspect the underside and hidden interfaces. Ordinary System, Technic and mechanism workflows remain available where appropriate.

## Selected sources and visual study

Eight Jev-selected references form the first atlas: one complete **434-part B-wing**, five reusable cockpit/wing/nacelle/armour/service constructions, and two larger inspiration studies: a **1,493-part UCS Y-wing** and **1,335-part Star Destroyer**. The five smaller constructions contain 125, 41, 49, 31 and 15 placements. Exact identities, original hashes and selection evidence are in [selections.json](../../examples/spaceship-atlas/selections.json).

The atlas includes **15 rendered source groups**, including nested assembly levels, with two views each; four complete-assembly overviews; and final previews for the smaller manuals. All **50 retained images were opened**. The [visual review](../../examples/spaceship-atlas/visual-review.md) explains the useful techniques, source axes, parent dependencies and visible limits. All eight Python/LeoCAD BOM comparisons match.

Sources with a single STEP group provide a single construction state. The canopy example additionally exposes three nested sections, including the pilot and helmet. The overview entries retain source step data without claiming a rendered build sequence. This keeps large-model study practical while letting an agent generate detailed pages for a selected section later.

The first cockpit candidate was replaced after visual inspection and parent-source review contradicted its initial interpretation. This is why the workflow requires examining the actual geometry rather than accepting semantic descriptions as sufficient evidence.

## Corrections and retained limits

Inspection exposed a tooling bug: pyldraw3's combined completeness flag treats warnings about optional connector metadata as incomplete inspection. The geometry and manual paths now distinguish those warnings from missing solid geometry. Warnings remain visible, and skipped geometry, unknown diagnostics and errors still prevent a complete-geometry result. Connector or structural checkers have not been silently relaxed.

The B-wing copy required three precise translations in a rounded wing plate/tile stack, each smaller than **0.00033 LDU**. The atlas generator matches each original placement exactly before applying the recorded position change. It preserves part identity, colour and orientation, retains original attribution, and records both original and prepared source hashes. The original library file is unchanged, and the strict collision tolerance is unchanged.

The larger Y-wing retains overlap diagnostics; the Star Destroyer retains transform and overlap diagnostics. Both are explicitly inspiration-only and blocked from checked export. These records are not declarations that the original physical sets cannot work. They describe unresolved issues in the supplied digital source under the tooling's checks. Dense full-model render edges also limit close construction inspection; use a smaller selected section for that work.

Legacy aliases and minifigure parts in the canopy source remain visible. Any substitution needs a new fit review. Standard source checks also retain temporary-wrapper header and connection/collision-coverage warnings. No motion simulation, physical strength, insertion access or flight performance is certified.

## Verification

- Live Jev availability was checked with one uncached request. Seven bounded searches covered whole fighters, larger ships, freighters, engines, cockpits and hull/wing details. Exact field/query/results are in the [evidence snapshot](spaceship-support-evidence.json).
- All eight original source hashes still match. Copied-source adjustments are separate and reproducible.
- All six reusable entries passed CLI export, build, ordinary geometry validation, BOM comparison and their local generator. Both inspiration entries were rejected by export without creating a destination.
- General `manual review`/`export`, all three design-brief commands and family example listing were exercised. Exported sources rebuild without the annotated-model originals.
- **211 tests passed in 159.63 seconds.** New regressions cover general notes/export, overview versus step evidence, missing/stale images, connector-warning versus solid-geometry completeness, independent spaceship briefs and inspiration export refusal. Existing mechanism and structural tests also pass.
- A Node DOM harness exercised 30 step/view selections and nested callout navigation; it also checked all 16 overview image paths and labels. This verifies viewer behavior and local assets, not browser layout. PNG inspection was performed separately.

The implementation is complete for example-based construction and design support. Future agents can use the same manual procedure to grow the spaceship atlas or any of the existing atlas families.
