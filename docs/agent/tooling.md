# Tool reference

Run commands from the repository root. `./setup.sh` installs the pinned Python tools into `.venv`, checks source paths, builds a local parts index, and extracts a PDF page to verify Poppler. It needs Python 3.12+ and `pdftotext`; LeoCAD must be available for rendering. `uv sync --locked --extra test` reproduces `uv.lock`. The pip fallback pins direct dependencies; transitive dependencies may differ.

`./ldraw-agent --help` lists the executable interface. Global `--library`, `--models`, and repeatable `--shadow` options go **before** the command. Default directories are relative to this repository, not `$HOME`; `LDRAW_DIR` and `MODELS_DIR` override them. The local `.cache` directory can be deleted and rebuilt. No library download, database mutation, or global pyldraw configuration is needed.

## Discover and inspect

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
./ldraw-agent sections '../ldraw-lib/models-annotated/106-1.mpd'
./ldraw-agent sections '../ldraw-lib/models-annotated/106-1.mpd' --section '106 - car.ldr'
```

Part search uses case-insensitive plain AND terms over actual filenames/descriptions; whitespace within terms is not significant. Numeric dimensions are search hints, not a geometry API. Exact codes rank first; aliases/internal parts rank later. There is no fixed hardcoded palette: `colours` reads `LDConfig.ldr`.

Model/submodel search reuses the supplied `../ldraw-lib/scripts/ldraw-info.db` **read-only**, with parameterized SQLite FTS5 queries: `wheel`, `wheel OR steering`, `"exact phrase"`, `hing*`. Reports identify the database, modification time, and whether each source exists. Read the actual annotated source before using a result. If the database is absent, a header scan uses simple AND terms instead; it reports this different query language explicitly. `sections` returns original source line numbers, descriptions, or a selected full block; it never strips attribution or packs dependencies for you.

`part` accepts a code with or without `.dat` and reports current part status/replacement, local coordinates, true expanded bounds, connector count, and a bounded connector list. Use a larger `--limit` if connectors are truncated. If `complete` is false, fix the missing library dependency before trusting its geometry. The generated index is a local symlink view of `parts`, `p`, and `LDConfig.ldr`; file size/mtime signatures automatically rebuild its titles as the library changes.

## Generate from a plan

Copy the structure of [examples/bridge.plan.json](../../examples/bridge.plan.json), then design a new assembly. The machine-readable contract is [plan.schema.json](../../ldraw_tools/data/plan.schema.json). Unknown keys, malformed vectors, mixed position modes, duplicate IDs, missing references, nonfinite numbers, invalid transforms, and invalid colours fail explicitly.

```sh
./ldraw-agent build output/my-model.plan.json --output output/my-model.mpd --report output/my-model.build.json
```

Top-level keys: `version: 1`, `author`, optional `license`, and ordered `sections`. The **first section is the main model**. Each section has `name` ending in `.ldr`, a descriptive `description`, and `steps`, an array of arrays of placements. Every placement has a unique section-local `id`, `ref`, `colour`, optional `purpose`, and either `at` or `on`.

| Field | Meaning |
|---|---|
| `at: [x,y,z]` | Translation in LDU, in the containing section's coordinate system. Required unless using `on`. |
| `yaw: degrees` | Optional right-handed rotation about that section's +Y axis; default zero. |
| `matrix: [[a,b,c],[d,e,f],[g,h,i]]` | Optional explicit proper rotation; mutually exclusive with `yaw`. |
| `on: "earlier-id"` | Stack a curated upright brick/plate on an earlier placement in the same section. Computes Y from the upper body's height and checks stud-grid alignment. |
| `offset_studs: [x,z]` | Only with `on`: offset in the support's local X/Z axes, multiplied by 20 LDU. Default `[0,0]`. |
| `colour: 16` | Permitted within reusable submodels; explicit ancestor colours must resolve every visible leaf. |

All refs are flat official `.dat` filenames or embedded `.ldr` names. Inline custom parts, loose external model files, primitive scaling, mirrored physical parts, raw polygons, textures/data, and local colour definitions are outside this generation plan. They require a separate advanced authoring/review workflow. Arbitrary **rigid** orientations of real parts are supported with `matrix` and explicit `at`; physical checks have more limited coverage.

`build` serializes using pyldraw3, validates the emitted MPD, runs geometry analysis, and writes atomically only if there are no errors. Existing output needs `--force`; failed builds preserve it. Warnings remain in the report. A successful build does not complete visual/physical review. Keep both plan and generated MPD so fixes are reproducible. Never hand-edit the MPD and then overwrite those fixes by rerunning an old plan.

For loops, procedural repetition, or matrix composition, use the [Python example](../../examples/python_api.py): `.venv/bin/python examples/python_api.py`. `ldraw_tools.builder.rotation(axis, degrees)`, `build_plan(plan, parts)`, `get_parts()`, and `analyze_geometry(model, parts)` are the small supported Python API. `ldraw.Model`, `Piece`, `Matrix`, and `Vector` remain available from pyldraw3. Run validation on serialized bytes before accepting custom Python output.

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

`validate` defaults to the new-model `assembly` profile. `--profile syntax` permits general transformations and type 2–5 geometry for examining existing sources; it still does not claim complete coverage of all extensions. `inspect` uses this syntax profile before analysing placements, so it can investigate legacy nonrigid OMR transforms; the **final generated model must pass the assembly profile**. `--strict` makes warnings fail; it does not expand coverage or prove buildability. Geometry traversal has a 5,000-leaf limit; inspect smaller assemblies when exceeded. Pair details are limited to 200 candidates with an explicit total/truncation flag; all rectangular body overlaps are still checked.

`check-model.sh` now runs Python syntax/reference checks and a **LeoCAD** snapshot/BOM import test. It returns one JSON object, and its exit status reflects failure. It no longer uses LDView. LeoCAD import success supplements the Python checks; it is not the equivalent of LDView's error diagnostics. Geometry analysis remains the separate `validate --geometry` step.

`render` saves `home.png`, `top.png`, `front.png`, and `leocad-bom.csv`. Override `--views` with any of `home front back left right top bottom`. Supported assemblies use cameras framed from their resolved bounds; other inputs use LeoCAD's preset view framing. Outputs are rendered to unique temporary files first, so stale files cannot count as a successful export. Existing destination images are replaced on successful export. Open the images and inspect them; merely producing a PNG is not visual review. Compare the Python BOM with LeoCAD's part/colour counts. Commands use explicit library paths and per-process timeouts (`--timeout`, default 90 seconds).

`prepare-glb.sh` also retains `--part 3001.dat` and `--model 106-1.mpd`; outputs default to `parts-glb` or `models-glb`. `--file` accepts newly generated local models without copying them into OMR. It invokes the existing semantic converter with real part descriptions and an optional default-colour preview mapping. It does not import into Blender or alter the MPD. See [geometry.md](geometry.md) for Blender review.

## Automation contract

Reports are JSON. Exit **0** means the selected command/checks completed successfully; **1** means validation/coverage failed (or warnings failed under `--strict`); **2** means bad input, dependency, I/O, conversion, budget, or execution failure. Read `diagnostics`, `complete`, truncation flags, and `physical_validity`, not just the exit code. Empty search results are a successful empty query. `--report` writes a report in addition to stdout. Do not use a shell pipeline that loses the first command's exit status.

Shell examples that redirect output intentionally retain the command's exit status. Paths with spaces must be shell quoted. For local development, run `.venv/bin/python -m pytest -q`. Tests cover malformed syntax, transforms, MPD references/cycles, colour inheritance, nested duplicates, polygon degeneracy, failed writes, normal stud overlap, floating parts, and the real-library example. Official-library integration tests skip explicitly if that resource is absent; a skipped integration test is not evidence of working library geometry.
