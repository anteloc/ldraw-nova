# CLI and output contracts

For the normal modeling loop, follow [AGENTS.md](../../../AGENTS.md). Use `build` for fast iteration and `review` for the combined automatic checks and previews. Every existing command remains available.

## Setup

Run commands from the repository root. `./setup.sh` installs project-local uv, jev-rerank, ldraw-xray, ldraw-annotator and lsynth-nova, downloads the official `complete.zip` into `data/ldraw`, syncs pinned Python dependencies into `.venv`, builds a parts index and checks PDF extraction. Flex synthesis is always included. `doctor.synthesis` reports LSynth availability and version. Poppler and LeoCAD remain prerequisites. See [local setup](../../setup.md) for versions, environment variables, reruns and tool discovery. `bin/uv sync --locked --extra test` reproduces `uv.lock` after setup.

`./ldraw-agent --help` lists the executable interface. Global `--library` and repeatable `--shadow` options go **before** the command. Parts resolve from `--library`, then `LDRAW_DIR`, then `LDRAWDIR`, then project-local `data/ldraw` when present (empty variables are treated as unset). Reference models and descriptions always reside in `data/models-annotated/` and `data/ldraw-info.db`, resolved relative to this repository even when invoked from elsewhere. The local `.cache` directory can be deleted and rebuilt. Normal CLI commands do not download libraries or mutate the database; no global pyldraw configuration is needed.

The supplied `data/offLibShadow/` is loaded automatically. `LDRAW_SHADOW` overrides the default; explicit `--shadow` paths replace defaults, and `--no-shadow` disables external shadows. `doctor` reports selected sources. See the [shadow and snapping guide](connections.md) for coverage, connector discovery, candidate application and the pyldraw3 1.7 adapters.

## Review a model

Plans can [declare flexible sources and structural contracts](flex.md#generated-flexible-assets). Review prepares the sources and runs their checks automatically. For a standalone flexible asset:

```sh
./ldraw-agent flex guide TECHNIC_PNEUMATIC_HOSE_BEVELED
./ldraw-agent flex build CONSTRAINTS.ldr --output output/asset.mpd
```

`flex build` checks source and generated geometry, accepts the geometric options from `flex check --asset`, and reuses unchanged synthesis inputs. `--no-cache` reruns the engine. `flex hose` and `ldraw_tools.flex_authoring` supply endpoint, marker and wheel helpers. Standard `./setup.sh` includes the synthesis engine and `bin/lsynth`. Read [constraint authoring](../guides/flex.md) for choosing limits and repairing routes; [flexible parts](flex.md) covers installation and BOM boundaries.

```sh
./ldraw-agent review output/my-model.plan.json
./ldraw-agent review output/my-model.mpd --force
```

`review` accepts a JSON plan or an existing `.mpd`/`.ldr` assembly. A plan is built in memory through the same builder and checks as `build`; an existing assembly is copied before validation. The command then writes a Python BOM, renders LeoCAD views and compares reference/colour/quantity counts. It checks and renders the same frozen model bytes. It does not modify the input or claim to inspect images.

The default output is `NAME-review/` beside `NAME.plan.json`, `NAME.json`, `NAME.mpd` or `NAME.ldr`. Use `--outdir` to choose another dedicated directory. For an example without touching supplied assets:

```sh
./ldraw-agent review examples/plan-basics/bridge.plan.json --outdir output/bridge-review
```

| Artifact | Contents |
|---|---|
| `review.json` | Stage outcomes, diagnostics, physical count, source/model hashes and artifact hashes |
| `model.mpd` | Exact assembly reviewed; emitted only after source, geometry and declared checks pass |
| `validation.json` | Assembly/geometry diagnostics; declared flex and structure checks, coverage and truncation flags |
| `flex/`, `structure/` | Frozen constraints, generated assets/manifests and structural contracts when declared |
| `bom.json` | Python physical parts list and model hash |
| `bom-comparison.json` | Exact Python/LeoCAD comparison and model hash |
| `previews/` | Requested PNG views and `leocad-bom.csv` |

Open the images and record your visual observations beside the source. The generated directory is replaceable output: `--force` replaces only an unchanged review bundle. Extra files or edited artifacts are protected even with `--force`; use another directory or move your work out first. A rerun replaces the bundle as a unit, so old images and BOM comparisons cannot masquerade as new evidence. Validation, rendering or comparison failures publish the available reports and return nonzero; failed validation does not publish a model. Input/output preflight failures leave any existing bundle unchanged and report the error on stdout.

Useful variations:

```sh
# Intermediate checks without invoking LeoCAD; render/comparison are explicitly skipped.
./ldraw-agent review output/my-model.plan.json --no-render --outdir output/my-model-checks

# An MPD module with inherited colour resolved; source lines still refer to the input.
./ldraw-agent review output/my-model.mpd --section my-floor.ldr --colour 19 --outdir output/floor-review

# More views for final review, or full diagnostic rows for investigation.
./ldraw-agent review output/my-model.mpd --views home front back right top bottom --force
./ldraw-agent review output/my-model.mpd --no-render --detail full --contacts all --force
```

Section selection accepts JSON plans and existing MPD/LDR inputs; it reviews only the selected dependency closure. `--colour` requires `--section`. General geometry options are unchanged: `--contacts auto|all|none`, `--max-instances`, `--limit`, `--offset`, and `--detail summary|full`. Review defaults to summary; all selected checks still run. Auto contacts skip above 500 placements and report that limitation. `--timeout` defaults to 90 seconds per external command.

Exit 0 means the **selected automatic checks** passed; 1 means validation or BOM comparison failed; 2 means input/dependency/execution failure. `--no-render` can return 0 with rendering and comparison explicitly skipped. Full review still reports visual inspection as required and `physical_validity: not_proven`. Plans with section `structure` contracts run Technic checks automatically, even with `--contacts none`. Existing MPDs and old plans still need `technic check --contract`; run `vehicle check` when applicable. See [validation coverage](validation.md).

## Prepare and export construction manuals

```sh
./ldraw-agent manual prepare FILE --section NAME --outdir output/study --views home top --notes NOTES.json
bin/ldraw-xray mosaic output/study/panels.json --output output/study/mosaic.png
./ldraw-agent manual review output/study --images IMAGE ... --note 'What was inspected and learned'
./ldraw-agent manual export output/study --outdir output/my-example
./ldraw-agent spaceship list
./ldraw-agent spaceship details
./ldraw-agent spaceship brief starfighter --output output/starfighter-brief.json
./ldraw-agent spaceship export halcyon --outdir output/my-ship
```

`manual` shares the mechanism step renderer but uses construction notes: lesson, construction, interfaces, parent context and reuse notes. `--overview` renders completed-model views and retains source step data; `--no-render` leaves rendered evidence pending. Existing mechanism commands retain their operation-specific notes and review requirements. See [construction review](../guides/review-models.md) and [spaceship design](../guides/design-models.md). `ldraw-xray` renders inspection boards (parent context, x-ray, stud maps, pivots) and composes mosaics; see [submodel inspection](../guides/review-models.md).

## Reviewed real-set submodels

```sh
./ldraw-agent examples --family submodel --details 'curved roof'
./ldraw-agent examples --family submodel
./ldraw-agent examples --family aircraft --details 'landing gear'
./ldraw-agent manual export examples/10258-rounded-roof --outdir output/my-roof
```

Results come from the package README registrations. Each identifies its lesson, scope, guide, source and available evidence. `--details` selects legacy detail aliases. Default retrieval excludes inspiration, held and retired examples; `--scope inspiration` is explicit. Current manual export checks remain separate from search admission.

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

`prepare` creates source, provenance, normal source/geometry checks, per-section build pages, per-step parts, parent context, operation notes and a placement plan. It uses LeoCAD's step export with highlighted additions, a stable camera and embedded-DAT support. `--operation FILE` supplies the seven descriptive fields explained in the [mechanism guide](../guides/mechanisms.md). `--no-render` leaves rendering/BOM comparison pending. `review DIRECTORY --images ... --note ...` records only pages actually opened, binding all artifacts by hash. `export KEY_OR_DIRECTORY --outdir DIR` copies a current reviewed study with passing source checks and matching BOM. This export gate covers construction evidence; it does not certify motion.

## Discover and inspect

### Technic structures

```sh
./ldraw-agent technic list
./ldraw-agent technic parts 2780
./ldraw-agent technic plan frame-tower --levels 2 --output output/tower.plan.json
./ldraw-agent review output/tower.plan.json
./ldraw-agent examples --family technic
./ldraw-agent discover search submodels 'braced frame' --construction technic-structure --engine fts
```

The [Technic workflow](../guides/technic.md) covers supported ports, seated pins, axle intervals, structural restraints and contracts. Normal geometry checks remain required. Generated contracts bind to the model revision; `technic check` returns exit 1 for failed checks and exit 2 for invalid inputs. Use the [mechanism workflow](../guides/mechanisms.md) for moving assemblies and explicitly test requested motion. Use Jev only after its availability check; `fts` is the explicit offline alternative.

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
Example search has no default subject family; retired recipes are excluded from default retrieval.

`vehicle details` lists six dedicated fitting recipes or exports a named recipe
as a plan, using vehicle palettes and protecting existing files with `--force`.
`examples --family vehicle --details` finds their built and rendered counterparts.

`vehicle check` accepts `--profile road|motorcycle|watercraft|aircraft`, optional `--recipe`, `--section`, `--colour`, `--ground-y`, `--limit` and `--max-instances`. Mixed System/Technic construction is allowed. Road and motorcycle profiles check supported wheel layouts in their documented frame; unknown wheels remain unreviewed. Aircraft and watercraft profiles report interfaces as `not_checked` unless an exact recipe is requested.

Use `--recipe courier-jet` with `--profile aircraft`, `harbour-launch` with `watercraft`, or `touring-motorcycle` with `motorcycle` to require those recipes' particular parts and measured alignments. These requirements do not apply to other designs. All profiles retain `physical_validity: not_proven`; assembly validation and opened images remain necessary.

```sh
./ldraw-agent vehicle check output/jet.mpd --profile aircraft
./ldraw-agent vehicle check output/courier.mpd --profile aircraft --recipe courier-jet
```

### General discovery

Construction guidance and examples remain the starting point for model building.
Use the [part-information guide](../guides/part-information.md) to choose regex,
SQL, FTS/BM25, Jev, categories or dimensions for a specific question. Never read
or independently parse library `.dat` files. Identified parts may be passed to
existing geometry/connector tools and renderers.

```sh
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

`search parts` queries `PARTS_DESCRIPTIONS` read-only, without loading the installed
library. `--field part|description|both` defaults to both; `--match terms|exact|like`
defaults to literal AND terms. Exact mode accepts filenames with or without `.dat`;
LIKE exposes SQL `%`/`_`, while terms mode escapes them. Matching uses SQLite's
ASCII case-insensitive text behavior. Exact codes rank first, then description
length and filename. Duplicate descriptions retain distinct references. `--limit`
and `--offset` provide bounded pagination with total/truncation and provenance.

`--dimensions` enriches results with cached evidence. `--min-size X Y Z` and
`--max-size X Y Z` filter positive local-axis LDU extents, preferring complete DB
bounding boxes then category estimates. Missing sizes are excluded only when
filtering. `dimensions PART...` returns both sources separately with completeness
and missing-value evidence. Numeric words in descriptions are only text hints;
cached extents are not stacking heights or connection planes.

`export-parts-descriptions [--force]` creates the complete sorted UTF-8 TSV at
`data/parts-descriptions-full.tsv`, with `part`/`description` headers and standard
TSV quoting. The Git-ignored snapshot is reused unless explicitly refreshed.
Use bounded `rg` searches on the explicit file; do not print the full table.

```sh
./ldraw-agent search parts 3023 --field part --match exact
./ldraw-agent search parts 'Minifig Shield%' --field description --match like --limit 8
./ldraw-agent dimensions 3001 3023 3659
./ldraw-agent export-parts-descriptions
rg -i -m 20 -- 'minifig.*shield' data/parts-descriptions-full.tsv
```

Missing DBs or required indexes produce errors, never library scans. There is
no fixed hardcoded colour palette: `colours` reads `LDConfig.ldr` during explicit
library colour inspection; the DB `COLORS` table is also available as metadata.

Model/submodel search reuses the supplied `data/ldraw-info.db` **read-only**, with parameterized SQLite FTS5 queries: `wheel`, `wheel OR steering`, `"exact phrase"`, `hing*`. Reports identify the database, modification time, and whether each source exists. Read the actual annotated source before using a result. If the database is absent, a header scan uses simple AND terms instead; it reports this different query language explicitly. `sections` returns original source line numbers, descriptions, or a selected full block; it never strips attribution or packs dependencies for you.

`doctor` checks model-building setup; `index` refreshes the installed library index for geometry tools. Neither is required for database-only part queries.

`part` accepts a code with or without `.dat` and reports current part status/replacement, local coordinates, true expanded bounds, connector count, and a bounded connector list. Use a larger `--limit` if connectors are truncated. If `complete` is false, fix the missing library dependency before trusting its geometry. The generated index is a local symlink view of `parts`, `p`, and `LDConfig.ldr`; file size/mtime signatures automatically rebuild its titles as the library changes.

## Jev part discovery

First follow the [Jev availability check](cli.md#check-jev-availability-before-searching). Missing tooling/credentials, rejected API keys and service/network failures should lead the agent to `discover search parts|models|submodels ... --engine fts`. State the fallback and continue using local resources; the CLI does not switch engines automatically.

For the integrated parts/models/submodels workflow, use [reference discovery](../guides/find-references.md): `discover index`, `discover search`, `discover show`, `discover parts`, `discover prepare`, `discover catalog`, `discover review`, `discover example` and `discover recipe`. It consumes the three `full_description` views through a typed local index, repairs single-section header descriptions locally, filters actual contents, diversifies results and supplies measured image cards. The standalone CLI below also supports direct queries, but its original-table key instructions do not apply to the synthetic row keys returned by the new views.

Use the project-local `bin/jev-rerank` CLI (PATH fallback if absent) when the request describes a part's purpose or appearance. From this repository root:

```sh
bin/jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field parts_descriptions.description --top 10 \
  --query 'a wall decoration for a castle' --show --json
```

This requires `bin/jev-rerank` (or a PATH installation) and `TYPESAFE_API_KEY` in the environment. No Jev source checkout or `uv run` is needed. The source database is `data/ldraw-info.db` and stays read-only; the reranker maintains its own local index and score cache.

**Describe a single part in each query.** For example, `a wall decoration for a castle`, `a heraldic shield to hang above a castle gate`, or `a curved slope for the nose of a small spacecraft`. Query each intended role separately. The wording describes what one candidate should be; `--top 10` controls how many alternatives are returned. Do not ask the query to generate a model, list ten parts, or fill the entire model's BOM.

Read `results` in their returned rank order:

| JSON field | Use |
|---|---|
| `source.key.part` | Exact database part reference, including `.dat`; pass this to `ldraw-agent part`. |
| `text` | Matched description, included by `--show`. |
| `score` | Jev's 0–1 probability that the description matches the query; results are sorted descending. |
| `source` / `path` | Source identity; `path` is a SQLite locator, not a part filename. |
| `exhaustive` / `stats` | Search coverage, scored candidates, cache/API usage, and elapsed time. |

For a specific construction need, identify candidates from informational sources, then use existing inspection tools before putting them into a plan. Never inspect raw `.dat` source. The description table includes internal pattern segments, subparts, aliases, and sticker shortcuts as well as ordinary parts. Reject primitives/subparts as assembly placements, check status and replacements, and inspect a shortcut's physical meaning. Preserve the original ranks/scores when recording why a candidate was selected or rejected. A high score establishes neither geometric fit nor availability in a particular colour.

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

`--repair-bfc-comments` moves annotation comments before INVERTNEXT. `--normalize-rotations` explicitly projects nearly rigid assembly matrices to proper rotations within a small bounded tolerance. Both record changes; neither changes the original source. See the [Bookshop case study](../guides/compose-modules.md) for exact tolerances and known source defects.

## Generate from a plan

See the [plan guide](plans.md) for a complete example, placement modes, modules and the Python API. The [JSON schema](../../../ldraw_tools/data/plan.schema.json) remains the contract; existing plans and explicit output paths are unchanged.

```sh
./ldraw-agent build output/my-model.plan.json
./ldraw-agent build output/my-model.plan.json --output output/custom.mpd --report output/my-model.build.json
```

Without `--output`, `NAME.plan.json` or `NAME.json` builds to `NAME.mpd` beside the plan. `build` serializes with pyldraw3, validates the emitted source and analyzes geometry. It writes atomically only with no errors; `--force` permits replacing an existing output after successful checks. Failed builds preserve the previous MPD. Warnings remain visible. Keep fixes in the plan/generator so regeneration preserves them.

## Individual checks and exports

Use these commands for diagnosis, custom automation or legacy workflows. A normal `review` already runs assembly validation, geometry, BOM, rendering and BOM comparison; a separate `cad-check` repeats its renderer import/export smoke test.

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

`prepare-glb.sh` also retains `--part 3001.dat` and `--model 106-1.mpd`; outputs default to `parts-glb` or `models-glb`. `--model` reads `data/models-annotated/`; `--part` uses `LDRAW_DIR`, then `LDRAWDIR`, then project-local `data/ldraw`. `--file` accepts newly generated local models without copying them into OMR. It invokes the global `mpd2glb.sh` with real part descriptions and an optional default-colour preview mapping. GLB is a derived export; the MPD remains authoritative.

The global `ldraw-render-steps.sh` is also useful during construction. Read its current help with no arguments, select a submodel and step range, then render several viewpoints to expose misplaced parts, concealed gaps or awkward layering. Open the images, fix the source plan/generator and render again. The [build-page guide](../guides/review-models.md#read-source-steps-when-construction-is-unclear) covers this review loop and the richer `manual prepare` workflow for atlas studies. Nova's rendering calls resolve LeoCAD via `LEOCAD`, project-local paths, PATH, then the system macOS app; see [setup](../../setup.md#environment-and-tool-discovery). External helper scripts use their own discovery rules.

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

`catalog parts` and `catalog categories` are metadata-only by default. Categories
are optional, fallible hints; `--category minifig` includes its subgroups.
Part descriptions come from the DB and installed availability is unknown.
`--include-unavailable` includes legacy/internal hints without checking files.
`--measure` explicitly initializes the library to measure selected results;
`catalog colours` retains its installed-colour behavior. Category-dictionary
`--max-size` filtering remains a cached hint; `search parts` size filters use the
DB-first dimension-source selection described above.

`part-board` renders 1–12 candidates through LeoCAD and creates an offline `index.html` and `board.json`, measured bounds, individual MPDs and images. Cards are framed independently; compare listed dimensions to judge scale. Read the [visual design guide](../guides/design-models.md) and actually inspect the candidates. These tools support choices and visual iteration; they do not assign a beauty score.

## Named authoring and scoped plan review

`review PLAN --section NAME` now accepts JSON plans and checks only the selected
section dependency closure, including its declared contracts and flexible routes.
Its default output is `PLAN-SECTION-review/`; coverage explicitly requires a
whole-model review before delivery. `--colour` resolves inherited preview colours.

[Named authoring](../guides/build-model.md) adds inline structure contracts and flexible
placements. Reports retain named paths and original JSON locations; failed
flex checks retain structured measurements and repair guidance. Successful plan
reviews freeze declaring JSON sources under `sources/`, alongside the existing
flex and structural evidence. Public CLI exit meanings and legacy commands remain.

## Retrieve construction knowledge

Use local knowledge search before choosing an example. It searches current agent
guidance by heading and explicitly registered example lessons with SQLite FTS5
BM25. It needs no parts library, renderer, network, credentials or model service.

```sh
./ldraw-agent knowledge search 'bearing supports retained chain' --limit 5
./ldraw-agent examples 'pneumatic' --family flex
./ldraw-agent knowledge show technic:service-platform
./ldraw-agent knowledge search 'Y-wing' --scope inspiration
```

Results identify the source path, section/line for guidance, current source hash,
matched excerpt, scope and limitations. Open that source before adapting it.
Search rank is relevance, not geometry validation or export approval. Empty
results stay empty; broaden the construction role deliberately or use raw
[source discovery](../guides/find-references.md).

Default scope includes guidance, construction lessons and tutorials. Explicit
scopes include `inspiration`, `diagnostic`, `research`, `archive` and `hold`.
`all` is for auditing. Retired/held examples can be resolved by exact ID so their
reason is visible; this does not authorize reusable export. A changed registered
model is automatically held until its visual/evidence review is reconciled.

`examples` is the examples-only compatibility view. Omit `--family` to search
across families. Existing family/key aliases remain available through `knowledge
show FAMILY:KEY`; ambiguous short keys require qualification. `--details` selects
the legacy detail view. Family is a compatibility filter, not a requirement to
copy a subject's construction technique.

## Register or maintain an example

The package README owns one fenced `ldraw-knowledge` JSON list. Each entry has a
stable `id`, `title`, `scope`, `lesson`, qualified `aliases` and `families`.
`kind`, `subjects` and `techniques` describe independent dimensions. Paths such as
`model`, `plan`, `manual`, `visual_review` and `generator` are repository-relative.
`model_sha256` binds an entry to its reviewed model. The authored `limits` and
linked `audit` must retain missing parent interfaces and check coverage.

Keep one lesson entry per distinct construction. Colour variants and identical
copies share it; studies and cutaways identify their actual parent/selection.
Do not mark a new model construction-ready merely by filling in its hash. Review
its selected sections alone and in their parents, preserve provenance, and run
the appropriate checks first. After changing geometry, update the review and
identity together. Search never refreshes hashes or silently clears a hold.

The in-memory index is rebuilt from current README registrations and guidance on
each query. Legacy atlas catalogs are no longer admission authorities. Normal
manual/reference export freshness, source and BOM guards remain required.

## Check Jev availability before searching

Before the first Jev search in a task, check that `bin/jev-rerank` exists (or `jev-rerank` is on `PATH`), `data/ldraw-info.db` exists and `TYPESAFE_API_KEY` is nonempty. Check the key's presence without printing its value. If those prerequisites exist, verify authentication and service access with one bounded, uncached query from the repository root:

```sh
bin/jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field PARTS_DESCRIPTIONS_JEV.full_description \
  --query 'brick' --top 1 --candidates 1 --model jev-1.13.0 \
  --no-score-cache --timeout 10 --retries 0 --json
```

Require a successful exit, a nonempty result and a positive `stats.api_calls`; `--help` or a cached result alone does not verify the live service. The timeout applies to the API request, not local indexing.

If prerequisites are missing, the key is rejected, or the service/network fails, state the reason briefly and continue with **explicit offline FTS**. Apply the same fallback if Jev fails later in the task. Avoid repeatedly attempting an unavailable service; retry when configuration or availability changes. Local database/path errors need their own correction because FTS also requires the local resources.

```sh
./ldraw-agent discover search submodels 'street lamp' --engine fts \
  --max-parts 150 --limit 8 --report output/lamps.json
```

Select `parts`, `models` or `submodels` and suitable keywords for the current role. Record that results use keyword/BM25 ranking, not Jev semantic ranking. Continue with the existing catalogs, examples, part lookup and visual review; generation, rendering and validation do not require TypeSafe. This is an agent-directed fallback: the CLI does not switch engines automatically.

## Find a few distinct constructions

```sh
./ldraw-agent discover index
./ldraw-agent discover search models 'a passenger train with a locomotive and carriages' \
  --limit 5 --report output/train-inspiration.json
./ldraw-agent discover search submodels 'a street lamp for a minifigure town pavement' \
  --max-parts 150 --limit 8 --report output/lamps.json
./ldraw-agent discover search parts 'a cylindrical jet engine housing for a passenger plane' \
  --limit 6 --report output/engine-parts.json
./ldraw-agent discover parts output/lamps.json --limit 12
./ldraw-agent examples --family reference --limit 8
./ldraw-agent examples --family submodel --details 'side studs'
```

`discover search` invokes `bin/jev-rerank`, falling back to the PATH CLI with model `jev-1.13.0` and its configured credentials. Use `--engine fts` for an explicit offline BM25 search. There is no silent fallback. Natural-language FTS queries use token OR; the older `search models|submodels` commands retain their raw FTS5 syntax, now ranked and paginated with `--offset`.

Part discovery reads database descriptions and reuses `PARTS_DESCRIPTIONS_FTS`
for lexical ranking; Jev uses the existing eligible-snapshot reranking workflow.
`discover search parts` and `discover show part-ID` neither initialize the library
nor scan model sources. Part IDs remain stable; source existence/installed
availability, canonical identity and physical accounting remain unknown until
explicit inspection. Filename/description filters are metadata hints only.

Model/submodel discovery still uses the three description views and annotated
sources, correcting assembly descriptions against model headers and performing
its existing content/geometry checks. These are model sources, not permission
for agents to open library part definitions. The supplied database and sources
remain unchanged. Explicit geometry tools resolve the library from `--library`,
`LDRAW_DIR`, `LDRAWDIR`, then project-local `data/ldraw`.

Jev searches an eligible local snapshot with a real primary key. Results retain stable IDs and retrieval score/rank. Part rows provide exact filenames, DB descriptions and classification provenance; assembly rows additionally provide original/corrected text, source hashes and parent descriptions. This avoids persisting Jev's unstable view row numbers. Case/whitespace normalization must resolve unambiguously; paths must remain under the configured roots.

The defaults hide embedded part definitions, empty/raw-geometry-only sections, internal/legacy part candidates and identifiable incompatible product families. Submodel/model candidates are then inventoried to reject nonphysical accounting, apply part-count and Technic-share limits, group matching shapes and cap variants from one parent. Shape grouping ignores colour and global translation; it does not claim mirrored or rotated constructions are identical. Variants retain their own identities and scores.

Use `--min-parts`, `--max-parts`, `--max-technic-share` and `--parent-cap` deliberately. The default Technic title-prefix share is at most 0.5; this is a content filter, not a complete taxonomy. Inspect incidental pins and axles separately from a Technic mechanism. `--max-technic-share 0` requests no Technic-prefixed placements; `--all-families` disables family/share restrictions. Source names do not establish minifigure fit or physical scale.

For static Technic supports, use `--construction technic-structure`. It selects structural descriptions and inspects the selected assembly's BOM for obvious mechanism parts; parent themes do not exclude useful static sections. Part searches use the reviewed structural registry. Results still require parent-context, joint-role, restraint and insertion review: a shaft in a “chassis” can serve a mechanism. `--construction system` preserves System defaults; `--construction all` exposes all families. The same availability-first Jev/offline workflow applies. See [Technic structures](../guides/technic.md).

For mechanism discovery, use `--construction mechanism`. It selects mechanism vocabulary in the chosen description and checks the measured BOM for relevant parts. It includes useful partial assemblies, such as a steering rack whose pinion belongs to the parent. Use `mechanism prepare FILE --section NAME --outdir DIR` to create attributed source, step renderings, per-step parts and parent context, then follow the [mechanism workflow](../guides/mechanisms.md). Study and visual-review status are distinct from tested physical operation.

`--pool 60` asks Jev for enough ranked results to filter and diversify into the requested `--limit`. `--candidates 500` is the bounded lexical shortlist before scoring; `--candidates 3000` broadens it, and `0` scores all eligible records. If few useful results remain, refine the role or broaden this budget. Do not fill the list with poor matches just to reach ten. Returned `stats`, exclusions and original scores make those decisions visible.

For difficult roles, supply **both** `--yes` and `--no`, for example a criterion for a System aircraft engine pod and one rejecting car engines and spacecraft body slabs. Parent context is shown separately rather than silently added to the scored text. A semantic score is not an import approval.

