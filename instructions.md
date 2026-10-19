# Generate and review an LDraw model

Deliver the requested editable model, reproducible source, checks, BOM and viewed previews. Creative composition leads: explore the subject, silhouette, proportions, palette and character, then engineer the chosen design. Keep important features during repairs. Geometry passing alone does not complete a visual brief.

Python generators, explicit coordinates, ordinary JSON/MPD and the optional [kit](docs/agent/kit.md) are all valid. Small constructions teach techniques; no whole-model template is required. Render unfinished studies freely.

**Start here**

Run from the repository root:

```sh
./ldraw-agent doctor
```

Run `./setup.sh` if needed. The parts library is `LDRAW_DIR`, then `LDRAWDIR`, or global `--library`. Use the installed LeoCAD through the render tools. Keep `data/models-annotated/`, `data/ldraw-info.db`, categories and library parts unchanged; put generated work under `output/`.

For buildings, read the short [construction workflow](docs/agent/construction-workflow.md), then choose relevant [visual examples](examples/building-atlas/README.md). The [runnable starter](examples/construction-studies/starter/README.md) demonstrates generation, actual parent support and final review in sequence. Use the remaining guides on demand:

| Need | Guide |
|---|---|
| Composition, palette, depth and character | [Visual design](docs/agent/visual-design.md) |
| Features that must survive repairs | [Design brief](docs/agent/design-brief.md) |
| Modular plans, includes, source extraction | [Complex models](docs/agent/complex-models.md) |
| Placement, connections, fit | [Geometry](docs/agent/geometry.md), [kit](docs/agent/kit.md), [snapping](docs/agent/snapping.md) |
| Useful source models and constructions | [Reference discovery](docs/agent/reference-discovery.md), [build manuals](docs/agent/build-manuals.md) |
| System vehicles | [Vehicle workflow](docs/agent/vehicles.md), [atlas](examples/vehicle-atlas/README.md) |
| Spaceships | [Spacecraft workflow](docs/agent/spaceships.md), [atlas](examples/spaceship-atlas/README.md) |
| Fixed Technic structures | [Structural workflow](docs/agent/technic.md), [creative design](docs/agent/technic-design.md) |
| Mechanisms | [Mechanism workflow](docs/agent/mechanisms.md), [source studies](examples/technic-studies/README.md); analytical motion verification remains deferred |
| Exact command/options or source rules | [Tooling](docs/agent/tooling.md), [LDraw reference](docs/agent/ldraw-reference.md), [validation](docs/agent/validation.md) |

The language authority is [docs/ldraw-specs.pdf](docs/ldraw-specs.pdf); use `spec --page 65` or keyword search and the [source map](docs/agent/specification-map.md). Distinguish assembly constraints from part-authoring rules.

**Design and discover**

Record subject/story, meaningful scale, major masses, palette roles, a focal feature, supporting details and retained spatial relationships in a short brief. Size and part count do not substitute for design. For buildings, reserve entrances, glazing, room access, stairs, roof openings and furnishing space before filling walls and floors.

```sh
./ldraw-agent examples --curated --role facade --limit 3
./ldraw-agent examples --curated --role planting --limit 2
./ldraw-agent construction list
./ldraw-agent design palettes
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
```

Open reference images and inspect the selected source. Read its evidence scope, actual dimensions, parent supports, permitted edits and limitations. A source-valid model or an isolated detail can still fail construction in context. Preserve attribution when copying; use `extract` for dependency-closed source with namespaced references and manifests. `manual prepare` exposes construction steps that a finished view hides.

Use [reference discovery](docs/agent/reference-discovery.md) for broader precedents. Before Jev, perform its documented availability check; on failure use `discover search models|submodels|parts ... --engine fts` and report the offline fallback once. Query one role at a time. Relevance ranking does not establish fit.

Render rough masses early. For an open brief, explore substantially different compositions and develop the strongest. Draft output can contain unresolved construction:

```sh
./ldraw-agent build output/my-model/draft.plan.json --draft --contacts none --output output/my-model/draft.mpd
./ldraw-agent look output/my-model/draft.mpd --outdir output/my-model/composition
```

Open the images. Revise proportions and character before extensive repetition. Study one complete risky section with actual neighbouring walls, floor/supports and openings; preserve its checked dimensions when expanding. Recheck any changed interface in its new parent. A chimney needs support through a reserved roof opening; a roof peak's highest point is not an attachment.

**Author and check**

Use the [plan schema](ldraw_tools/data/plan.schema.json), existing `load_plan`/`build_plan`, or `Model.plan()`. Keep repairs in the reproducible generator/plan. The [starter generator](examples/construction-studies/starter/generate.py) supplies legal IDs, step arrays, includes, named colours and a parent attachment.

- Negative Y is up; stud pitch is 20 LDU; plate body height is 8 and brick body height is 24. Stud protrusions do not add a stacking gap.
- Inspect unfamiliar parts and actual connectors. Bounds and authored anchors do not prove mating surfaces. Reserve full openings, not only part centres.
- Use real physical `.dat` parts with proper rigid transforms; do not scale, shear or mirror complete parts. Group reusable assemblies in unique `.ldr` sections.
- Use named colours such as `@colours.Dark_Green` or inspected codes; 16 inherits and 24 is for edges. Preserve source authors/licences; do not invent attribution or manufacture availability.
- A plan's first section is its root; `steps` contains arrays of placements. IDs use letters, digits, underscores or hyphens. Choose exactly one position mode (`at`, `on`, `attach`, `snap`). See [complex models](docs/agent/complex-models.md) for includes, frames and assets.
- Bridge seams with real parts; check half-stud alignment. Unknown fits stay unresolved. Neither `free` nor `overlap` is a shortcut to accepting bad construction.

Generate first, then run dependent checks. Do not launch checks concurrently with the generation they consume. Check the actual parent after joining individually passing modules:

```sh
./ldraw-agent check output/my-model/model.mpd --report output/my-model/check.json
```

`check` reports PASS, FAIL or REVIEW for static construction. Only PASS returns zero. Investigate source-linked findings and coverage. Fix the responsible construction while preserving the brief; do not shrink or delete a promised feature merely to clear the checker. Legacy `build`, `validate --geometry` and contact counts provide different evidence and do not replace `check`.

**Review and deliver the exact revision**

For System models, use the existing stage route with the generated MPD or JSON plan:

```sh
./ldraw-agent stage prepare output/my-model/model.plan.json --outdir output/my-model/review --views home front right top
```

Add `--requirements FILE` for measurable retained relationships. Preparation checks the snapshot, renders it and compares Python/LeoCAD BOMs. Open every view; add rear, close-up and open-interior views where needed. Assess silhouette, proportions, palette, depth and character. Compare every core feature with the brief, including furnishings and access. A module name or connected parts do not prove a usable room.

Record actual observations using `stage review --images ... --note ... --decision accept|revise`. Reject an unattractive result even when geometry passes. Export an accepted exact revision with `stage export REVIEW_DIR --output FINAL.mpd`. Changed source, requirements, parts or evidence require preparing and viewing again. Preserve the separate mechanism review workflow.

`READY_FOR_REVIEW` means visual work is pending. `stage prepare --no-render` returns 1 even when `technical_checks_passed` is true: `review_state: pending_images` is not a broken construction. Use `check` for a static-only verdict; render and review before export. Input/execution errors return 2 with a diagnostic; inspect the JSON rather than treating all nonzero codes as the same failure.

Provide links to the MPD, reproducible source, reused-source manifests, brief/review, check report, BOM and previews. State unresolved features and evidence limits. Static PASS does not prove strength, assembly order, inventory or motion; visual review requires actually opening the images. Finish the requested work and its review artifacts without relabelling an unreviewed draft as final.
