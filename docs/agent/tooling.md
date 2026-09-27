# Tool reference

## Build manuals for any atlas

```sh
./ldraw-agent manual prepare FILE --section NAME --outdir output/study --views home top --notes NOTES.json
./ldraw-agent manual review output/study --images IMAGE ... --note 'What was inspected and learned'
./ldraw-agent manual export output/study --outdir output/my-example
./ldraw-agent spaceship list
./ldraw-agent spaceship details
./ldraw-agent spaceship brief starfighter --output output/starfighter-brief.json
./ldraw-agent spaceship export b-wing --outdir output/my-ship
```

`manual` shares the mechanism step renderer but uses construction notes: lesson, construction, interfaces, parent context and reuse notes. `--overview` renders completed-model views and retains source step data; `--no-render` leaves rendered evidence pending. Existing mechanism commands retain their operation-specific notes and review requirements. See [build manuals and atlas additions](build-manuals.md) and [spaceship design](spaceships.md).

## Mechanism studies and reuse

```sh
./ldraw-agent mechanism list
./ldraw-agent discover search submodels 'a small worm drive' --construction mechanism --engine fts
./ldraw-agent mechanism prepare "data/models-annotated/42042-1_Tower-Crane.mpd" \
  --section '42042 - spoolwormgear.ldr' --outdir output/worm-study \
  --views home top --normalize-rotations --repair-bfc-comments
./ldraw-agent mechanism export worm-drive --outdir output/my-winch
./ldraw-agent build output/my-winch/scene.plan.json --contacts none --output output/my-winch/my-winch.mpd
```

`prepare` creates source, provenance, normal source/geometry checks, per-section build pages, per-step parts, parent context, operation notes and a placement plan. It uses LeoCAD's step export with highlighted additions, a stable camera and embedded-DAT support. `--operation FILE` supplies the seven descriptive fields explained in the [mechanism guide](mechanisms.md). `--no-render` leaves rendering/BOM comparison pending. `review DIRECTORY --images ... --note ...` records only pages actually opened, binding all artifacts by hash. `export KEY_OR_DIRECTORY --outdir DIR` copies a current reviewed study with passing source checks and matching BOM. Analytical mechanism verification is deferred and is not an export prerequisite.


Run commands from the repository root. `./setup.sh` installs the pinned Python tools into `.venv`, checks source paths, builds a local parts index, and extracts a PDF page to verify Poppler. It needs Python 3.12+ and `pdftotext`; LeoCAD must be available for rendering. `uv sync --locked --extra test` reproduces `uv.lock`. The pip fallback pins direct dependencies; transitive dependencies may differ.

`./ldraw-agent --help` lists the executable interface. Global `--library` and repeatable `--shadow` options go **before** the command. Parts resolve from `--library`, then `LDRAW_DIR`, then `LDRAWDIR` (empty variables are treated as unset). Reference models and descriptions always reside in `data/models-annotated/` and `data/ldraw-info.db`, resolved relative to this repository even when invoked from elsewhere. The local `.cache` directory can be deleted and rebuilt. No library download, database mutation, or global pyldraw configuration is needed.

The supplied `data/offLibShadow/` is loaded automatically. `LDRAW_SHADOW` overrides the default; explicit `--shadow` paths replace defaults, and `--no-shadow` disables external shadows. `doctor` reports selected sources. See the [shadow and snapping guide](snapping.md) for coverage, connector discovery, candidate application and the pyldraw3 1.7 adapters.

## Discover and inspect

### Technic structures (stage 1)

```sh
./ldraw-agent technic list
./ldraw-agent technic parts 2780
./ldraw-agent technic plan frame-tower --levels 2 --output output/tower.plan.json
./ldraw-agent build output/tower.plan.json --output output/tower.mpd
./ldraw-agent technic check output/tower.mpd --contract output/tower.plan.structure.json
./ldraw-agent examples --family technic
./ldraw-agent discover search submodels 'braced frame' --construction technic-structure --engine fts
```

The [Technic workflow](technic.md) covers supported ports, seated pins, axle intervals, structural restraints and contracts. Normal geometry checks remain required. Generated contracts bind to the model revision; `technic check` returns exit 1 for failed checks and exit 2 for invalid inputs. Use the authorized [mechanism workflow](mechanisms.md) for moving assemblies; analytical mechanism verification is deferred. Use Jev only after its availability check; `fts` is the explicit offline alternative.

### System vehicles

```sh
./ldraw-agent vehicle list
./ldraw-agent vehicle wheels touring
./ldraw-agent vehicle details driver-cockpit --output output/cockpit.plan.json
./ldraw-agent examples --family vehicle --details
./ldraw-agent vehicle plan pickup --palette desert-utility --output output/pickup.plan.json
./ldraw-agent examples --family vehicle --limit 3
./ldraw-agent vehicle check output/pickup.mpd --report output/pickup.vehicle.json
```

`vehicle plan` writes an ordinary editable plan and a sibling `.brief.json`,
resolving parts before writing; use `--force` to replace either. Run normal
`build`/`validate --geometry` afterwards. Vehicle palettes also appear under
`design palettes`; architectural detail recipes require architectural palettes.
The building example search remains the default.

`vehicle details` lists six dedicated fitting recipes or exports a named recipe
as a plan, using vehicle palettes and protecting existing files with `--force`.
`examples --family vehicle --details` finds their built and rendered counterparts.

`vehicle check` accepts `--profile road|motorcycle|watercraft|aircraft`, `--section`, `--colour`, `--ground-y`, `--limit` and
`--max-instances`. The default road profile checks supported separate wheel/tyre
pairs. Motorcycle checks use the dedicated frame and two centreline wheels;
watercraft/aircraft profiles check their documented hull/cockpit or nose/wing/engine
assemblies and mark road-wheel checks inapplicable. Diagnostics distinguish layout errors, unknown-wheel
coverage and conservative wheel-space warnings. It does not replace assembly
validation, material clearance inspection or visual review. Full usage and
limitations are in the [vehicle guide](vehicles.md).

### General discovery

```sh
./ldraw-agent doctor
./ldraw-agent index
./ldraw-agent search parts 'brick 2 x 4' --limit 8
./ldraw-agent search parts '3001' --limit 1
./ldraw-agent part 3001 --limit 30
./ldraw-agent colours 'blue'
./ldraw-agent colours '148'
./ldraw-agent profiles
./ldraw-agent spec --page 65
./ldraw-agent spec 'INVERTNEXT' --limit 4
./ldraw-agent search models 'car' --limit 5
./ldraw-agent search submodels 'wheel OR steering' --limit 5
./ldraw-agent sections 'data/models-annotated/106-1.mpd'
./ldraw-agent sections 'data/models-annotated/106-1.mpd' --section '106 - car.ldr'
```

Part search uses case-insensitive plain AND terms over actual filenames/descriptions; whitespace within terms is not significant. Numeric dimensions are search hints, not a geometry API. Exact codes rank first; aliases/internal parts rank later. There is no fixed hardcoded palette: `colours` reads `LDConfig.ldr`.

Model/submodel search reuses the supplied `data/ldraw-info.db` **read-only**, with parameterized SQLite FTS5 queries: `wheel`, `wheel OR steering`, `"exact phrase"`, `hing*`. Reports identify the database, modification time, and whether each source exists. Read the actual annotated source before using a result. If the database is absent, a header scan uses simple AND terms instead; it reports this different query language explicitly. `sections` returns original source line numbers, descriptions, or a selected full block; it never strips attribution or packs dependencies for you.

`part` accepts a code with or without `.dat` and reports current part status/replacement, local coordinates, true expanded bounds, connector count, and a bounded connector list. Use a larger `--limit` if connectors are truncated. If `complete` is false, fix the missing library dependency before trusting its geometry. The generated index is a local symlink view of `parts`, `p`, and `LDConfig.ldr`; file size/mtime signatures automatically rebuild its titles as the library changes.

## Jev part discovery

First follow the [Jev availability check](reference-discovery.md#check-jev-availability-before-searching). Missing tooling/credentials, rejected API keys and service/network failures should lead the agent to `discover search parts|models|submodels ... --engine fts`. State the fallback and continue using local resources; the CLI does not switch engines automatically.

For the integrated parts/models/submodels workflow, use [reference discovery](reference-discovery.md): `discover index`, `discover search`, `discover show`, `discover parts`, `discover prepare`, `discover catalog`, `discover review`, `discover example` and `discover recipe`. It consumes the three `full_description` views through a typed local index, repairs single-section header descriptions locally, filters actual contents, diversifies results and supplies measured image cards. The global CLI below also supports direct queries, but its original-table key instructions do not apply to the synthetic row keys returned by the new views.

Use the global `jev-rerank` CLI when the request describes a part's purpose or appearance. From this repository root:

```sh
jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field parts_descriptions.description --top 10 \
  --query 'a wall decoration for a castle' --show --json
```

This requires `jev-rerank` on `PATH` and `TYPESAFE_API_KEY` in the environment. No Jev source checkout or `uv run` is needed. The source database is `data/ldraw-info.db` and stays read-only; the reranker maintains its own local index and score cache.

**Describe a single part in each query.** For example, `a wall decoration for a castle`, `a heraldic shield to hang above a castle gate`, or `a curved slope for the nose of a small spacecraft`. Query each intended role separately. The wording describes what one candidate should be; `--top 10` controls how many alternatives are returned. Do not ask the query to generate a model, list ten parts, or fill the entire model's BOM.

Read `results` in their returned rank order:

| JSON field | Use |
|---|---|
| `source.key.part` | Exact database part reference, including `.dat`; pass this to `ldraw-agent part`. |
| `text` | Matched description, included by `--show`. |
| `score` | Jev's 0–1 probability that the description matches the query; results are sorted descending. |
| `source` / `path` | Source identity; `path` is a SQLite locator, not a part filename. |
| `exhaustive` / `stats` | Search coverage, scored candidates, cache/API usage, and elapsed time. |

Inspect candidates before putting them into a plan. The description table includes internal pattern segments, subparts, aliases, and sticker shortcuts as well as ordinary parts. Reject primitives/subparts as assembly placements, check status and replacements, and inspect a shortcut's physical meaning. Preserve the original ranks/scores when recording why a candidate was selected or rejected. A high score establishes neither geometric fit nor availability in a particular colour.

For example, after selecting these references from the castle query:

```sh
./ldraw-agent part 4444p09.dat --limit 20
./ldraw-agent part 3068bd09.dat --limit 20
./ldraw-agent part-board 4444p09.dat 3068bd09.dat 3069bpt5.dat \
  --colour 71 --outdir output/castle-decoration-shortlist
```

Open the board images, compare measured dimensions, and check origins/connectors before placement. A score ranks relevance from description text; it does not replace this review.

With `--top 10`, the current reranker normally scores a BM25 shortlist of up to 500 field values. The ten results are therefore not an exhaustive search of the whole library. If suitable parts are missing, refine the single-part description or supplement it with category searches; see `jev-rerank --help` for larger candidate budgets. Progress goes to stderr, so stdout can be saved as JSON; preserve and check the command's exit status before consuming it. If the reranker is unavailable, report that and use the existing catalog/search tools without claiming Jev ranking.

## Study and extract complex references

```sh
./ldraw-agent study data/models-annotated/10270-1.mpd --report output/bookshop-study.json
./ldraw-agent extract data/models-annotated/10270-1.mpd --section '10270 - Pendulum_Clock.ldr' --namespace ref-clock --output output/assets/clock.mpd
```

`study` inventories hierarchy, physical counts, reuse/reachability and source diagnostics. Its default summary limits section/diagnostic rows to 30 (`--limit`); `--detail full` includes complete section metadata and BOM. It returns 0 for a completed inventory even if `source_checks_passed` is false. `extract` copies only a dependency closure, namespaces every embedded reference, preserves raw geometry and author/licence headers, and writes an adjacent attribution/change manifest. Read the returned `root` for the new reference name. It writes review copies even with diagnostics (exit 1 on syntax errors); successful extraction is not a successful assembly build. Existing output or manifest requires `--force`, and source overwrite is prohibited.

`--repair-bfc-comments` moves annotation comments before INVERTNEXT. `--normalize-rotations` explicitly projects nearly rigid assembly matrices to proper rotations within a small bounded tolerance. Both record changes; neither changes the original source. See the [Bookshop case study](complex-models.md) for exact tolerances and known source defects.

## Generate from a plan

Copy the structure of [examples/bridge.plan.json](../../examples/bridge.plan.json), then design a new assembly. The machine-readable contract is [plan.schema.json](../../ldraw_tools/data/plan.schema.json). Unknown keys, malformed vectors, mixed position modes, duplicate IDs, missing references, nonfinite numbers, invalid transforms, and invalid colours fail explicitly.

```sh
./ldraw-agent build output/my-model.plan.json --output output/my-model.mpd --report output/my-model.build.json
```

Top-level keys: `version: 1`, `author`, optional `license`, ordered `sections`, and optional `includes` (relative JSON plan paths) / `assets` (relative MPD paths). `load_plan(path)` resolves nested includes once and preserves each module's headers; cycles and namespace collisions fail. The **first section is the main model**. Each section has `name` ending in `.ldr`, a descriptive `description`, and `steps`, an array of arrays of placements. Every placement has a unique section-local `id`, `ref`, `colour`, optional `purpose`, and exactly one of `at`, `on`, `attach`, or `snap`. Sections may declare named `anchors` and their own `author`/`license`. See the complete [module contract examples](complex-models.md).

| Field | Meaning |
|---|---|
| `at: [x,y,z]` | Translation in LDU, in the containing section's coordinate system. Required unless using `on`, `attach`, or `snap`. |
| `yaw: degrees` | Optional right-handed rotation about that section's +Y axis; default zero. |
| `matrix: [[a,b,c],[d,e,f],[g,h,i]]` | Optional explicit proper rotation; mutually exclusive with `yaw`. |
| `on: "earlier-id"` | Stack a curated upright brick/plate on an earlier placement in the same section. Computes Y from the upper body's height and checks stud-grid alignment. |
| `offset_studs: [x,z]` | Only with `on`: offset in the support's local X/Z axes, multiplied by 20 LDU. Default `[0,0]`. |
| `attach: {"to":"earlier-id","anchor":"seat","using":"base"}` | Align named frames on generated modules, including orientation. Optional `offset` is in the support anchor frame. Mutually exclusive with explicit position/orientation and repeats. |
| `snap: {"to":"earlier-id","near":[0,-8,0]}` | Mate a selected leaf interface and move the complete part/submodel. Optional leaf and feature selectors; see [snapping](snapping.md). |
| `repeat: {"count":8,"step":[40,0,0]}` | Repeat an `at` placement in containing-section axes; generated IDs are `id-0` etc. |
| `colour: 16` | Permitted within reusable submodels; explicit ancestor colours must resolve every visible leaf. |

Generated refs are flat official `.dat` names, generated `.ldr` names, or namespaced definitions imported through `assets`. Imported classified DAT parts retain their raw geometry, internal primitive transforms, BFC and attribution; they are single physical leaves during assembly/BOM traversal. Loose external models, mirrored/scaled physical parts, model-level raw polygons, textures/data and local colours remain outside the standard generation profile. New part authoring still needs additional geometry/BFC review. Arbitrary **rigid** orientations of real parts are supported with `matrix` and explicit `at`; physical checks have more limited coverage.

`build` serializes using pyldraw3, validates the emitted MPD, runs geometry analysis, and writes atomically only if there are no errors. Existing output needs `--force`; failed builds preserve it. Warnings remain in the report. A successful build does not complete visual/physical review. Keep both plan and generated MPD so fixes are reproducible. Never hand-edit the MPD and then overwrite those fixes by rerunning an old plan.

For loops, procedural repetition, or matrix composition, use the [Python example](../../examples/python_api.py): `.venv/bin/python examples/python_api.py`. `ldraw_tools.builder.load_plan(path)`, `rotation(axis, degrees)`, `build_plan(plan, parts)`, `get_parts()`, and `analyze_geometry(model, parts)` are the small supported Python API. `ldraw.Model`, `Piece`, `Matrix`, and `Vector` remain available from pyldraw3. Run validation on serialized bytes before accepting custom Python output.

## Validate and review

```sh
./ldraw-agent validate output/my-model.mpd --geometry --report output/my-model.validation.json
./ldraw-agent inspect output/my-model.mpd --report output/my-model.inspection.json
./ldraw-agent bom output/my-model.mpd --report output/my-model.bom.json
./ldraw-agent snap output/my-model.mpd --moving 1 --fixed 0 --limit 5
./check-model.sh output/my-model.mpd
./ldraw-agent render output/my-model.mpd --outdir output/my-model-review
./prepare-glb.sh --file output/my-model.mpd output/my-model.glb
```

`validate` defaults to the new-model `assembly` profile. `--profile syntax` permits general transformations and type 2–5 geometry for examining existing sources; it still does not claim complete coverage of all extensions. `inspect` uses this syntax profile before analysing placements, so it can investigate legacy nonrigid OMR transforms; the **final generated model must pass the assembly profile**. `--strict` makes warnings fail; it does not expand coverage or prove buildability. The physical expansion budget defaults to 100,000 (`--max-instances`). `--section NAME --colour CODE` selects a dependency closure with original source-line attribution. `--detail summary` retains counts/diagnostics while omitting long lists; full detail uses `--limit` (default 200) and instance `--offset`. Truncation never skips overlap checks. `--contacts auto` computes contacts through 500 placements and explicitly skips them above that; choose `all` or `none` deliberately. Skipped contacts have null component counts, not a fabricated disconnected graph.

`check-model.sh` now runs Python syntax/reference checks and a **LeoCAD** snapshot/BOM import test. It returns one JSON object, and its exit status reflects failure. It no longer uses LDView. LeoCAD import success supplements the Python checks; it is not the equivalent of LDView's error diagnostics. Geometry analysis remains the separate `validate --geometry` step.

`render`, `cad-check`, `validate`, `inspect`, `bom`, `compare-bom`, `connectors` and `snap` accept `--section NAME` and optional `--colour CODE`. A selected section has its own occurrence indices; pass the same selection to `snap`. `compare-bom FILE --csv leocad-bom.csv` checks exact reference/colour/quantity equality and returns 1 on differences.

`render` saves `home.png`, `top.png`, `front.png`, and `leocad-bom.csv`. Override `--views` with any of `home front back left right top bottom`. Supported assemblies use cameras framed from their resolved bounds; other inputs use LeoCAD's preset view framing. Outputs are rendered to unique temporary files first, so stale files cannot count as a successful export. Existing destination images are replaced on successful export. Open the images and inspect them; merely producing a PNG is not visual review. For MPDs with embedded DAT geometry, the adapter writes a temporary dependency library and model view for LeoCAD, then restores original embedded names in the CSV. The originals and installed library remain unchanged. This avoids the supplied LeoCAD omitting embedded parts. Compare the Python BOM with LeoCAD using `compare-bom`. Commands use explicit library paths and per-process timeouts (`--timeout`, default 90 seconds).

`prepare-glb.sh` also retains `--part 3001.dat` and `--model 106-1.mpd`; outputs default to `parts-glb` or `models-glb`. `--model` reads `data/models-annotated/`; `--part` uses `LDRAW_DIR` or its fallback `LDRAWDIR`. `--file` accepts newly generated local models without copying them into OMR. It invokes the global `mpd2glb.sh` with real part descriptions and an optional default-colour preview mapping. GLB is a derived export; the MPD remains authoritative.

The global `ldraw-render-steps.sh` is also useful during construction. Read its current help with no arguments, select a submodel and step range, then render several viewpoints to expose misplaced parts, concealed gaps or awkward layering. Open the images, fix the source plan/generator and render again. The [build-page guide](build-manuals.md#inspect-a-model-during-construction) covers this review loop and the richer `manual prepare` workflow for atlas studies. All rendering calls use the `leocad` CLI on `PATH`.

## Automation contract

Reports are JSON. Exit **0** means the selected command/checks completed successfully; **1** means validation/coverage failed (or warnings failed under `--strict`); **2** means bad input, dependency, I/O, conversion, budget, or execution failure. Read `diagnostics`, `complete`, truncation flags, and `physical_validity`, not just the exit code. `study` is informational: read `source_checks_passed`. `extract` can write a failing review artifact with exit 1. Empty search results are a successful empty query. `--report` writes a report in addition to stdout. Do not use a shell pipeline that loses the first command's exit status.

Shell examples that redirect output intentionally retain the command's exit status. Paths with spaces must be shell quoted. For local development, run `.venv/bin/python -m pytest -q`. Tests cover malformed syntax, transforms, MPD references/cycles, colour inheritance, nested duplicates, polygon degeneracy, failed writes, normal stud overlap, floating parts, and the real-library example. Official-library integration tests skip explicitly if that resource is absent; a skipped integration test is not evidence of working library geometry.

## Category discovery and visual design

```sh
./ldraw-agent catalog categories
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
./ldraw-agent catalog parts 'leaves' --category plants --max-size 110 40 130
./ldraw-agent catalog colours 'sand'
./ldraw-agent part @arches.Arch1X6X2WithThickTopAndReinforcedUnderside
./ldraw-agent design palettes botanical-bookshop
./ldraw-agent design details arched-window --palette rose-townhouse --output output/window.plan.json
./ldraw-agent part-board @plants.PlantLeaves6X5 @plants.PlantTreeOval4X4X6 --colour @colours.Green --outdir output/plant-shortlist
```

`catalog` reads the provided Python categories as static metadata, without importing `py4bricks` or executing generated modules. Results include source symbols, file/line provenance, installed availability, and dimension hints. Missing/legacy/internal entries are hidden by default (`--include-unavailable` exposes them). `--measure` expands selected results and flags disagreement with the dimension snapshot; `--max-size` is a coarse **snapshot** filter, not a fit guarantee. `LDRAW_CATEGORIES` overrides the category directory. Numeric plans still work without it.

Plans accept `@category.Symbol` refs (including nested categories such as `@minifig.heads.Symbol`) and `@colours.Name`. Resolution checks the installed library and leaves editable plans intact. Current `LDConfig.ldr` controls colour properties. `design palettes` exposes roles and composition guidance; it is not an inventory compatibility database. `design details` lists authored recipes, or writes an ordinary JSON plan with `--output`; existing output requires `--force`. Include the resulting sections using the usual module workflow.

`part-board` renders 1–12 candidates through LeoCAD and creates an offline `index.html` and `board.json`, measured bounds, individual MPDs and images. Cards are framed independently; compare listed dimensions to judge scale. Read the [visual design guide](visual-design.md) and actually inspect the candidates. These tools support choices and visual iteration; they do not assign a beauty score.
