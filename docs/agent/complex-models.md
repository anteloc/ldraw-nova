# Building complex models with small, verifiable modules

Use this workflow for multi-building scenes, vehicles, [advanced spaceships](spaceships.md), structural frames, figures, and models with hundreds or thousands of placements. Use the [structural workflow](technic.md) for fixed Technic supports and the [mechanism workflow](mechanisms.md) for mechanisms studied from source and build pages; analytical mechanism verification is deferred. Complexity comes from composing inspected modules; a single enormous list of coordinates is difficult to repair. The original [Copper Lane generator](../../examples/modular-street/generate.py) and [modular plans](../../examples/modular-street/scene.plan.json) demonstrate a complete 1,655-placement, nineteen-section streetscape. Start with its [visual brief and review](../../examples/modular-street/visual-review.md): complexity should serve an attractive, readable design.

## 1. Study structure before geometry

```sh
./ldraw-agent study data/models-annotated/10270-1.mpd --report output/bookshop-study.json
```

`study --detail full` reports the FILE hierarchy, direct versus expanded physical counts, reuse counts, reachability, local steps, authors/licences, frequently used parts, BOM, source hash, and validation findings. The default `study` summary limits section/diagnostic rows to 30 (`--limit`); use full detail when saving a complete inventory. It is an **informational** command: exit 0 does not mean `source_checks_passed` is true. A `.dat` definition is a physical-part boundary for scene traversal; its primitives contribute geometry, not separate BOM pieces. A library shortcut can still represent several manufactured elements.

The measured [Bookshop inventory](resources/bookshop-study.json) is tied to the supplied source's SHA-256. It contains 42 definitions: 25 assemblies and 17 embedded DAT definitions. The main scene reaches 39 definitions and 2,456 physical placements of 245 distinct reference names. Two minifigure blocks are empty and unreachable; the aeroplane is also unreachable. The descriptive annotation mentioning two minifigures is therefore not evidence that the main scene contains them.

Useful starting modules, with their exact FILE names:

| FILE name | Physical placements | What to study |
|---|---:|---|
| `10270 - Stair Step.ldr` | 4, instantiated 17 times | Repeat a small local construction with different rigid transforms. |
| `10270 - Window-1.ldr` | 14, instantiated twice | A framed window as a reusable façade detail. |
| `10270 - Bookshelf-1.ldr` | 15 | Small interior module and part palette. |
| `10270 - Pendulum_Clock.ldr` | 27 | A detailed object inspected independently from its room. |
| `10270 - Building-1_Second_Floor.ldr` | 342 | Floor envelope, furnishings, stairs, and their shared coordinate frame. |
| `10270 - Building-1_Roof.ldr` | 242 | Roof modules, decorative subassemblies, and orientation. |
| `10270 - Building-2_First_Floor_Balcony.ldr` | 86 | An interface with a separately placed building storey. |

Read a section with `sections FILE --section NAME`. Retrieve a bounded geometry report with `inspect FILE --section NAME --colour 15 --detail full --limit 30`. Some source sections have validation errors; extract an explicitly repaired review copy when needed.

## 2. Learn from references without inheriting their problems

This annotated Bookshop has 18 comments between `BFC INVERTNEXT` and its target line, violating PDF p.96. It also has 215 nearly rigid placement matrices rounded to three decimals, exceeding the new-assembly tolerance. Its embedded part quads are within the ordinary **less than 1 degree** tolerance; both diagonals must be measured (PDF p.142). These are different issues and require different handling.

Create a dependency-closed copy of a useful module:

```sh
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Pendulum_Clock.ldr' --namespace ref-clock \
  --output output/assets/clock.mpd
```

Read the returned `root`; use that exact reference when importing the asset. The adjacent `.manifest.json` records the original source/hash, FILE renames, authors/licences, edits, and output hash. Original bytes remain unchanged. Repeated imports need distinct namespaces. Keep the manifest beside the asset, and preserve copied authorship/licences.

For a review copy of the entire Bookshop:

```sh
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Complete.ldr' --namespace bookshop \
  --repair-bfc-comments --normalize-rotations \
  --output output/bookshop-reference.mpd
./ldraw-agent inspect output/bookshop-reference.mpd --detail summary --contacts none \
  --report output/bookshop-inspection.json
```

`--repair-bfc-comments` only moves annotation comments ahead of INVERTNEXT. `--normalize-rotations` uses an SVD projection to a proper rotation only for assembly matrices whose maximum orthogonality error is above 1e-4 and at most 0.002, with positive determinant. Every before/after matrix is recorded. This is an explicit approximation for reviewing rounded legacy rotations, not proof of original design intent; inspect the result. Larger scale/shear and reflections remain unchanged and fail the assembly check.

Extraction writes a review artifact even when syntax checks fail and then returns 1. It does not silently delete bad placements. In this Bookshop, the repaired copy exposes a duplicated `3010.dat` at world `(148,-129,0)` in the townhouse ground floor. Its geometry check correctly fails. Do not treat this reference as a golden physically valid fixture.

## 3. Define module contracts

Before populating parts, record each module's purpose, approximate envelope, local origin, attachment frames, inherited palette, construction steps, and review status. For a building, start with the street/base, then separate each floor, façade detail, roof, interior and landscaping. Keep the main section short enough to read in one screen.

In JSON plans, a section can expose named **anchor frames**:

```json
"anchors": {
  "base": {"at": [0, 8, 0]},
  "next": {"at": [0, -160, 0]}
}
```

These match Copper Lane's floor plate: its underside is at +8, while its cornice top is at -160. The resulting storey pitch is 168 LDU. Frames may have an explicit proper `matrix`; omitted matrices are identity. Keep the interface clear of decorative geometry and leave actual attachment studs/sockets accessible.

A containing section can place a floor and attach another:

```json
[
  {"id":"lower", "ref":"lane-ground.ldr", "colour":19, "at":[0,-8,0]},
  {"id":"upper", "ref":"lane-upper.ldr", "colour":19,
   "attach":{"to":"lower", "anchor":"next", "using":"base"}}
]
```

The builder solves `T_moving = T_support × A_support × T_offset × inverse(A_moving)`. All matrices act on column vectors. Optional `attach.offset` is in the supporting anchor's axes. The target ID must already exist in this section, including earlier steps. `attach` sets both position and orientation: do not combine it with `at`, `on`, `yaw`, `matrix`, or `repeat`. Anchors are authored assembly interfaces, **not inferred mechanical connectors**. Check the parts at each interface.

## 4. Compose plans and repeat structure

A main plan can use `"includes": ["buildings.plan.json"]`; that plan can include `details.plan.json`. Paths resolve relative to the file declaring them, each file loads once, cycles fail, and duplicate section names fail. The first section of the root plan remains the MPD main. Each module retains its own author/licence unless it explicitly supplies section-level values.

Use `"assets": ["assets/clock.mpd"]` to embed an extracted MPD's definitions. Assets resolve relative to their declaring plan and retain original headers. Names must not collide with generated sections, other assets, or the official library. Final validation checks the combined source and inherited colours. Imported assets use inspected `at` placements; named anchors are currently declared on generated JSON sections.

For a regular row:

```json
{"id":"roof-slope", "ref":"3039.dat", "colour":320,
 "at":[-140,-24,-130], "repeat":{"count":8,"step":[40,0,0]}}
```

This expands to IDs `roof-slope-0` through `roof-slope-7`. `step` is a translation in the containing section's axes, in LDU; it does not rotate with `yaw`. Repetition is supported with `at` only. Use an included submodel for a repeated multi-part construction. Use a small Python generator for conditional openings, different floor counts, brick bonds and parameterized patterns; serialize through `build_plan`, not a handwritten LDraw parser.

## 5. Review at three scales

1. **Detail:** inspect windows/glass, door hinges, furniture, or a single angled roof connection. Use local occurrence indices with `snap`; render the selected section. Record connector residuals and unresolved coverage.
2. **Module:** inspect a complete floor/roof with `--section` and `--colour`, checking clearances, support, step order, and boundary interfaces. Renders of extracted floors expose rooms that a closed exterior hides.
3. **Scene:** validate the complete assembly, check cross-module duplicates/body overlaps, compare BOMs, and render home/top/front plus relevant rear/side views. Module checks alone cannot detect collisions introduced when composing modules.

```sh
.venv/bin/python examples/modular-street/generate.py
./ldraw-agent build examples/modular-street/scene.plan.json --output output/copper-lane.mpd \
  --detail summary --report output/copper-lane.build.json
./ldraw-agent inspect output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --contacts all --detail summary --report output/ground-inspection.json
./ldraw-agent render output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --outdir output/ground-review --views home top
./ldraw-agent validate output/copper-lane.mpd --geometry --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

Default contact mode is `auto`: compute contacts through 500 physical placements; above that, explicitly report skipped coverage. Request `--contacts all` for a deliberate full analysis, or scope to modules. `--contacts none` still checks all resolved bounds and curated rectangular overlaps. It reports no connected-component conclusion. Missing connector metadata produces fragmented groups even for apparently mated parts; investigate the reported parts and do not equate group count with a buildability verdict.

`--detail summary` suppresses instance/contact/pair lists while retaining totals, errors and coverage. `--detail full --limit 30 --offset 60` shows physical occurrences 60–89. Limits truncate report detail, not validation checks. Scope changes restart occurrence indices; section/source-line paths identify the original source. The default physical expansion budget is 100,000 (`--max-instances`).

The LeoCAD adapter materializes embedded DAT definitions and their library dependencies in a temporary library, restoring original embedded names in the CSV. The supplied LeoCAD otherwise omits these placements. `compare-bom` checks actual `(reference, colour, quantity)` equality and returns 1 on differences. Images still need to be opened and reviewed; inspect uncertain interfaces in close views and [step sequences](build-manuals.md#inspect-a-model-during-construction), and record unresolved material intersections.

## Example scope

Copper Lane has a three-storey tan/green bookshop beside a two-storey sand-green townhouse. Arched flower windows, striped awnings, a gold BOOKS sign, a dormer and stepped clock pediment distinguish their façades. It includes exposed-side glazing, localized masonry, layered leaf trees, two lamps and five furnished removable floors. The [design guide](visual-design.md) explains how category symbols, palette roles and reusable details express these choices. Floor/roof interfaces are studded; levels are accessed by lifting them off, and the example does not include a minifigure stairwell. This is an original modular construction example, not a recreation of set 10270 or a guarantee of retail part/colour availability. See the [verification record](verification.md) for measured coverage and remaining physical review limits.
