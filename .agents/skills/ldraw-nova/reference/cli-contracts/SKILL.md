---
name: cli-contracts
description: 'CLI and output contracts: setup, review artifacts and failure behaviour, construction manuals (manual prepare/export), reviewed real-set submodels, mechanism studies, discovery and inspection, studying and extracting complex references, generating from a plan, individual checks and exports, the automation contract (JSON output, exit codes), knowledge retrieval and registering examples. Use when scripting the toolkit, interpreting a command''s output files or exit codes, or using a specialist workflow beyond build and review.'
---

# CLI and output contracts

What each part of the `./ldraw-agent` interface writes, what its exit codes mean, and how to script it: review bundles, build output, individual checks, manuals, discovery, knowledge registration and the Jev availability check. Flags are listed in [commands](../commands/SKILL.md). The normal modelling loop is in the root [ldraw-nova](../../SKILL.md) skill.

## Automation contract

- Reports are JSON. `--report FILE` writes the complete report in addition to stdout.
- Exit **0**: the selected command/checks completed successfully. **1**: validation or coverage failed (or warnings under `--strict`). **2**: bad input, dependency, I/O, conversion, budget or execution failure.
- Read `diagnostics`, `complete`, truncation flags and `physical_validity`, not just the exit code.
- `study` is informational: read `source_checks_passed`. `extract` can write a failing review artifact with exit 1. Empty search results are a successful empty query.
- **Do not use a shell pipeline that loses the first command's exit status.** Quote paths with spaces.
- Run from the repository root. Global `--library` and `--shadow` go before the command. Reference models and descriptions always come from `data/models-annotated/` and `data/ldraw-info.db`. Normal commands never download libraries or mutate the database; `.cache` can be deleted and rebuilt.

## `build`

```sh
./ldraw-agent build output/my-model.plan.json
./ldraw-agent build output/my-model.plan.json --output output/custom.mpd --report output/my-model.build.json
```

- Without `--output`, `NAME.plan.json` or `NAME.json` builds to `NAME.mpd` beside the plan.
- Serializes with pyldraw3, validates the emitted source and analyzes geometry. Writes atomically **only with no errors**; `--force` permits replacing an existing output after successful checks.
- A failed build preserves the previous MPD and writes `NAME.draft.mpd` when the plan produced a model.
- Stdout is a few-kilobyte summary: `checks_passed`, errors with placement paths (plus `separation`, `gap`, or a schema `pointer` and `example`), warnings grouped by code, geometry counts including appearance checks, and `next`. `--report` adds the per-placement `source_map` and connector `seats`.

## `review`

```sh
./ldraw-agent review output/my-model.plan.json
./ldraw-agent review output/my-model.plan.json --draft
./ldraw-agent review output/my-model.mpd --force
./ldraw-agent review output/my-model.plan.json --no-render --outdir output/my-model-checks
./ldraw-agent review output/my-model.mpd --section my-floor.ldr --colour 19 --outdir output/floor-review
./ldraw-agent review output/my-model.mpd --no-render --detail full --contacts all
```

A plan is built in memory with the same builder and checks as `build`; an existing MPD/LDR is copied first. Review then writes a Python BOM, renders LeoCAD views and compares reference/colour/quantity counts, all on the same frozen bytes. It never modifies the input or claims to inspect images. Default output: `NAME-review/` beside the input (`PLAN-SECTION-review/` with `--section`).

| Artifact | Contents |
|---|---|
| `review.json` | Stage outcomes, diagnostics, physical count, source/model hashes, artifact hashes and the `inputs` fingerprint used for reuse |
| `model.mpd` | Exact assembly reviewed; emitted only after source, geometry and declared checks pass |
| `draft.mpd` | With `--draft` only: the failing model that the previews show |
| `connectivity.json` | Placements outside the main group, used for `assembly.became_floating` next time |
| `validation.json` | Assembly/geometry diagnostics; declared flex and structure checks, coverage, truncation |
| `flex/`, `structure/`, `sources/` | Frozen constraints, generated assets/manifests, structural contracts, declaring JSON sources |
| `bom.json` | Python physical parts list and model hash |
| `bom-comparison.json` | Exact Python/LeoCAD comparison and model hash |
| `previews/` | Requested PNG views and `leocad-bom.csv` |

These are internal artifacts, not the delivery list; the internal `model.mpd` name never replaces the delivered `ai-NAME.mpd`, named after the model ([review-and-deliver](../../review-and-deliver/SKILL.md)).

- **Reuse:** same inputs (source and dependency hashes, options, toolkit, library) return the existing manifest with `reused: true`; `--force` recomputes. Changed inputs replace the bundle as a unit. Plans with inline flex routes always recompute.
- **Extra files or edited artifacts stop the review**: use another directory or move your work out.
- Validation, rendering or comparison failures publish available reports and return nonzero; failed validation does not publish a model. Preflight failures leave an existing bundle unchanged.
- Exit 0 means the **selected automatic checks** passed; `--no-render` can return 0 with rendering skipped. Visual inspection is still required and `physical_validity: not_proven`.
- Plans with section `structure` contracts run Technic checks automatically, even with `--contacts none`. Existing MPDs and old plans need `technic check --contract`; run `vehicle check` when applicable.
- A section review covers only its dependency closure and requires a whole-model review before delivery.

## Individual checks and exports

A normal `review` already runs these; use them for diagnosis or automation.

```sh
./ldraw-agent validate output/my-model.mpd --geometry --report output/my-model.validation.json
./ldraw-agent inspect output/my-model.mpd --report output/my-model.inspection.json
./ldraw-agent bom output/my-model.mpd --report output/my-model.bom.json
./ldraw-agent snap output/my-model.mpd --moving 1 --fixed 0 --limit 5
./check-model.sh output/my-model.mpd
./ldraw-agent render output/my-model.mpd --outdir output/my-model-review
```

- `validate` defaults to the new-model `assembly` profile; `--profile syntax` permits general transforms and type 2–5 geometry for existing sources. `inspect` uses the syntax profile. **The final generated model must pass the assembly profile.** `--strict` makes warnings fail without expanding coverage.
- `--contacts auto` computes contacts through 500 placements and skips above (null component counts, not a disconnected graph). Truncation never skips overlap checks.
- `render`, `cad-check`, `validate`, `inspect`, `bom`, `compare-bom`, `connectors` and `snap` accept `--section NAME` and `--colour CODE`; a selected section has its own occurrence indices (pass the same selection to `snap`).
- `compare-bom FILE --csv leocad-bom.csv` checks exact reference/colour/quantity equality; exit 1 on differences.
- `render` saves `home.png`, `top.png`, `front.png` and `leocad-bom.csv` (override with `--views home front back left right top bottom`). Producing a PNG is not visual review: open it. Embedded DAT parts are rendered through a temporary library so LeoCAD does not omit them.
- `check-model.sh` runs Python syntax/reference checks plus a LeoCAD snapshot/BOM import test and returns one JSON object.
- `prepare-glb.sh --file MODEL OUT.glb` (and `glb`) are derived exports, only on explicit user request.
- LeoCAD resolves via `LEOCAD`, project-local `bin/` paths, PATH, then the macOS app.

## Manuals and real-set studies

```sh
./ldraw-agent manual prepare FILE --section NAME --outdir output/study --views home top --notes NOTES.json
bin/ldraw-xray mosaic output/study/panels.json --output output/study/mosaic.png
./ldraw-agent manual review output/study --images IMAGE ... --note 'What was inspected and learned'
./ldraw-agent manual export output/study --outdir output/my-example
./ldraw-agent examples --family submodel --details 'curved roof'
./ldraw-agent manual export examples/10258-rounded-roof --outdir output/my-roof
```

- `manual` notes: lesson, construction, interfaces, parent context, reuse notes. `--overview` renders completed views; `--no-render` leaves evidence pending.
- `mechanism prepare` creates source, provenance, checks, per-section build pages, per-step parts, parent context, operation notes (`--operation FILE`, seven fields) and a placement plan. `review DIRECTORY --images ... --note ...` records only pages actually opened, binding artifacts by hash. `export` copies a current reviewed study with passing checks and matching BOM; it does not certify motion.
- `spaceship list`/`details` return eight lessons by default, interleaved across sources; `brief` and these do not initialize the library. No ship is a default template.

```sh
./ldraw-agent mechanism prepare "data/models-annotated/42042-1_Tower-Crane.mpd" \
  --section '42042 - spoolwormgear.ldr' --outdir output/worm-study \
  --views home top --normalize-rotations --repair-bfc-comments
./ldraw-agent mechanism export worm-drive --outdir output/my-winch
./ldraw-agent build output/my-winch/scene.plan.json --contacts none --output output/my-winch/my-winch.mpd
```

## Study and extract

- `study` inventories hierarchy, counts, reuse/reachability and diagnostics (summary limit 30 rows; `--detail full` adds section metadata and BOM). Exit 0 even if `source_checks_passed` is false.
- `extract` copies a dependency closure, namespaces every embedded reference, preserves geometry and author/licence headers, and writes an adjacent manifest. Read the returned `root`. It writes review copies even with diagnostics (exit 1 on syntax errors). Existing output needs `--force`; overwriting the source is prohibited. `--repair-bfc-comments` and `--normalize-rotations` record every change.

## Discovery

- `search parts` queries `PARTS_DESCRIPTIONS` read-only without loading the library. `search models|submodels` uses parameterized FTS5 over `data/ldraw-info.db`: `wheel`, `wheel OR steering`, `"exact phrase"`, `hing*` (header scan with AND terms if the DB is absent).
- `sections FILE [--section NAME]` returns source line numbers, descriptions, or a full block; it never strips attribution.
- `part CODE` reports status/replacement, local coordinates, expanded bounds and connectors. If `complete` is false, fix the missing dependency before trusting its geometry.
- `discover search` defaults to Jev (`bin/jev-rerank`, model `jev-1.13.0`); `--engine fts` is the explicit offline BM25 alternative. **There is no silent fallback.** Natural-language FTS uses token OR.
- `--construction technic-structure` for static Technic supports; `--construction mechanism` for mechanisms (includes partial assemblies such as a rack whose pinion is in the parent); `system` and `all` otherwise.
- `--pool 60` asks Jev for enough results to filter and diversify; `--candidates 500` is the lexical shortlist (`3000` broadens, `0` scores all). For difficult roles supply both `--yes` and `--no` criteria. A semantic score is not import approval.
- Defaults hide embedded part definitions, empty sections, internal/legacy parts and incompatible families, then apply `--min-parts`, `--max-parts`, `--max-technic-share` (0.5), `--parent-cap` (2). `--all-families` disables family/share limits.
- `catalog parts` and `catalog categories` are metadata-only; `--measure` initializes the library to measure; `--max-size` is a coarse snapshot filter. Plans accept `@category.Symbol` and `@colours.Name`. `part-board` renders 1–12 candidates with `index.html`, `board.json` and measured bounds.

### Check Jev availability before the first Jev search

Check `bin/jev-rerank` (or PATH), `data/ldraw-info.db`, and that `TYPESAFE_API_KEY` is nonempty **without printing it**. Then run one bounded uncached query:

```sh
bin/jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field PARTS_DESCRIPTIONS_JEV.full_description \
  --query 'brick' --top 1 --candidates 1 --model jev-1.13.0 \
  --no-score-cache --timeout 10 --retries 0 --json
```

Require a successful exit, a nonempty result and positive `stats.api_calls`. If anything fails, state the reason and continue with explicit offline FTS (and say results are BM25, not semantic); do not retry an unavailable service repeatedly.

```sh
./ldraw-agent discover search submodels 'street lamp' --engine fts \
  --max-parts 150 --limit 8 --report output/lamps.json
```

Standalone Jev: describe **one part per query**; read `results` in rank order (`source.key.part` is the exact reference to pass to `part`; `score` is 0–1; `exhaustive`/`stats` show coverage). `--top 10` scores a BM25 shortlist of up to 500 values, not the whole library. Reject primitives/subparts as placements; inspect shortcuts.

## Knowledge retrieval and registration

- `knowledge search` uses SQLite FTS5 BM25 over current guidance headings and registered example lessons; it needs no library, renderer, network or credentials. Results give source path, section/line, hash, excerpt, scope and limits. Rank is relevance, not validation.
- Default scope: guidance, construction lessons, tutorials. Explicit scopes: `inspiration`, `diagnostic`, `research`, `archive`, `hold`; `all` is for auditing. A changed registered model is held until its evidence review is reconciled.
- `--diversify source` (default for `--family spaceship`) interleaves the best match per source; `none` keeps relevance order. `source_group` (e.g. `ldraw:6208-1`) groups lessons from one source.
- Registering an example: the package README owns one fenced `ldraw-knowledge` JSON list. Each entry has `id`, `title`, `scope`, `lesson`, qualified `aliases`, `families`; optional `kind`, `subjects`, `techniques`, repository-relative `model`, `plan`, `manual`, `visual_review`, `generator`; `model_sha256` binds the reviewed model; `limits` and `audit` keep missing interfaces and coverage. One entry per distinct construction. Search never refreshes hashes or clears a hold.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/reference/cli.md](references/docs-agent-reference-cli.md)
