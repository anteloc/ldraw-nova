# Learn from models, submodels and their actual parts

Use whole models for proportions, palettes and a module checklist; use submodels for construction ideas and details. Compare the source images and measured contents before choosing a construction. The [reference atlas](../../examples/reference-atlas/README.md) contains a reproducible 220-reference catalog manifest, curated examples and selected parameterized recipes.

## Check Jev availability before searching

Before the first Jev search in a task, check that the global `jev-rerank` executable is on `PATH`, `data/ldraw-info.db` exists and `TYPESAFE_API_KEY` is nonempty. Check the key's presence without printing its value. If those prerequisites exist, verify authentication and service access with one bounded, uncached query from the repository root:

```sh
jev-rerank \
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
```

`discover search` invokes the global `jev-rerank` CLI with model `jev-1.13.0` and its configured credentials. Use `--engine fts` for an explicit offline BM25 search. There is no silent fallback. Natural-language FTS queries use token OR; the older `search models|submodels` commands retain their raw FTS5 syntax, now ranked and paginated with `--offset`.

The source is the three `*_DESCRIPTIONS_JEV.full_description` fields in `data/ldraw-info.db`, with annotated sources in `data/models-annotated/`. A local index resolves their pipe-prefixed identifiers, corrects descriptions against source headers and classifies records. The supplied database and source files remain untouched. Only the parts library is configured externally: `--library`, then `LDRAW_DIR`, then `LDRAWDIR`.

Jev searches an eligible local snapshot with a real primary key. Each result returns a stable `id`, exact `model`/`section` or `part`, original indexed text, corrected source text, original field name, source hash, parent description and retrieval score/rank. This avoids persisting Jev's unstable view row numbers. Case/whitespace normalization must resolve unambiguously; paths must remain under the configured roots.

The defaults hide embedded part definitions, empty/raw-geometry-only sections, internal/legacy part candidates and identifiable incompatible product families. Submodel/model candidates are then inventoried to reject nonphysical accounting, apply part-count and Technic-share limits, group matching shapes and cap variants from one parent. Shape grouping ignores colour and global translation; it does not claim mirrored or rotated constructions are identical. Variants retain their own identities and scores.

Use `--min-parts`, `--max-parts`, `--max-technic-share` and `--parent-cap` deliberately. The default Technic title-prefix share is at most 0.5; this is a content filter, not a complete taxonomy. Inspect incidental pins and axles separately from a Technic mechanism. `--max-technic-share 0` requests no Technic-prefixed placements; `--all-families` disables family/share restrictions. Source names do not establish minifigure fit or physical scale.

For stage-1 Technic work, use `--construction technic-structure`. It selects structural descriptions and inspects the selected assembly's BOM for obvious mechanism parts; parent themes do not exclude useful static sections. Part searches use the reviewed structural registry. Results still require parent-context, joint-role, restraint and insertion review: a shaft in a “chassis” can serve a mechanism. `--construction system` preserves System defaults; `--construction all` exposes all families. The same availability-first Jev/offline workflow applies. See [Technic structures](technic.md).

For the authorized Stage 2, use `--construction mechanism`. It selects mechanism vocabulary in the chosen description and checks the measured BOM for relevant parts. It includes useful partial assemblies, such as a steering rack whose pinion belongs to the parent. Use `mechanism prepare FILE --section NAME --outdir DIR` to create attributed source, step renderings, per-step parts and parent context, then follow the [mechanism workflow](mechanisms.md). Analytical mechanism verification is deferred; study and visual-review status are distinct from physical operation.

`--pool 60` asks Jev for enough ranked results to filter and diversify into the requested `--limit`. `--candidates 500` is the bounded lexical shortlist before scoring; `--candidates 3000` broadens it, and `0` scores all eligible records. If few useful results remain, refine the role or broaden this budget. Do not fill the list with poor matches just to reach ten. Returned `stats`, exclusions and original scores make those decisions visible.

For difficult roles, supply **both** `--yes` and `--no`, for example a criterion for a System aircraft engine pod and one rejecting car engines and spacecraft body slabs. Parent context is shown separately rather than silently added to the scored text. A semantic score is not an import approval.

## Study the construction steps

A completed snapshot can hide the useful construction. Follow the [build-manual workflow](build-manuals.md) to turn the returned exact model/section into consecutive pages with highlighted additions and per-step parts. Use `manual prepare` for any family and `mechanism prepare` for mechanism operation notes. Read the parent interfaces, record the actual pages opened and export reviewed constructions into the appropriate atlas. `--overview` provides completed-model views and source section metadata for choosing smaller studies. The [spaceship atlas](../../examples/spaceship-atlas/README.md) demonstrates both routes.

## Compare actual images and dimensions

```sh
./ldraw-agent discover catalog output/lamps.json --outdir output/lamp-references --jobs 2
./ldraw-agent discover show submodel-2bd03fab63ff8deee3a007d0
./ldraw-agent discover prepare submodel-2bd03fab63ff8deee3a007d0 \
  --outdir output/lamp-references --contacts all \
  --views home front back right left top bottom
```

Open the catalog's `index.html`. Search and filter the cards, then open the relevant views. The default views are home/front/right/top; all seven viewpoints are supported. Images are framed independently and preserve source-local orientation, so compare the listed dimensions and parent transforms rather than apparent image size. Front in a reference file may differ from the new model's front.

Each card directory contains:

- `source.mpd`: a dependency-closed, namespaced extraction, preserving source authorship and licences.
- `preview.mpd`: an explicit-colour root wrapper; it does not recolour explicitly coloured source parts.
- `extraction.json`: source hash, original/parsed identities, renamed references, attribution and recorded repairs.
- `card.json`: actual BOM and dedicated fittings, bounds, parent placements, dependencies, mesh coverage, assembly diagnostics, optional contacts, BOM comparison and review status.
- `renders/`: the requested images and LeoCAD BOM.

Preparation applies the existing bounded rotation repair and annotation-comment/BFC repair to the copy and records every edit. Raw diagnostic counts remain visible. Larger scale/shear defects stay invalid. Single-section sources without `FILE` blocks receive a wrapper; their first description, author and original source-line mapping survive extraction.

Mesh expansion, physical-part accounting, assembly checks, connector coverage and visual review are separate evidence. In particular, generated ropes/hoses can contain primitive placements that are not physical BOM parts. Such sources are excluded from normal reusable search results; a catalog can retain them as inspiration with explicit preparation failures. `contacts none` is the economical catalog default; request `all` on a selected assembly before reuse.

Rendering is resumable and content checked. Cached cards depend on the source, library/connection metadata, explicit preview colour and inspection mode; altered artifacts invalidate the cache. A changed source hash in a saved catalog manifest fails that entry instead of silently replacing its provenance. `--jobs 2` or `3` uses independent processes with separate geometry and CAD state. Failures are recorded, progress goes to stderr, and a partially completed catalog remains available.

## Reuse, adapt or study the technique

Record a review only after opening the actual images:

```sh
./ldraw-agent discover review submodel-2bd03fab63ff8deee3a007d0 \
  --catalog output/lamp-references --decision adapt --viewed-views home front right top \
  --note 'The globe and tall moulded post suit this pavement; reserve the post base and check its connection to the scene.'
```

Choose `reuse`, `adapt`, `technique` or `reject`, and list only the views actually opened. For a useful reference with passing assembly and geometry checks, a matching BOM, a contact inspection and a reuse/adapt review, `discover example` exports an editable plan and source copy with an authored lesson and placement guide. Changed artifacts invalidate the review/export step. It does not certify buildability. Inspect remaining diagnostics and uncertain connections in the composed model.

```sh
./ldraw-agent discover example submodel-2bd03fab63ff8deee3a007d0 \
  --catalog output/lamp-references --output output/my-lamp-example \
  --title 'Globe street lamp' --scale minifigure \
  --lesson 'Use a dedicated post and globe to keep a narrow street fitting legible.' \
  --placement-notes 'Preserve source orientation and measure the exposed base; reserve the complete globe envelope above the pavement.'
```

The plan uses `assets` and a positioning wrapper. Its `source_origin` anchor is explicitly not a mechanical connector. For repeated imports, extract with distinct namespaces or share one definition; do not merge colliding source names. Author attachment frames only after inspecting the actual support/connector surfaces. Remove conflicting tiles or bodywork before placing a fitting.

If the reference is the wrong scale or invalid, rebuild its useful technique using real parts and the new model's own interfaces. Selected recipes demonstrate this approach:

```sh
./ldraw-agent discover recipe
./ldraw-agent discover recipe arcade-bay --height 5 --colour 19 --accent 28 \
  --output output/tall-arch.plan.json
./ldraw-agent discover recipe street-lantern --height 7 --colour 0 --accent 71 \
  --output output/lamp.plan.json
```

These change brick courses and palette, not physical-part scale. Build and check the plans normally. A separate generator for every unchanged source submodel adds little: the shared extractor, source manifest and editable placement plan already provide reproducibility.

In the build process notes, identify the chosen model precedent, the modules studied, what was copied or rebuilt, and what visual improvement each contributes. Keep enough quiet surfaces and coherent palette roles that added details improve the design rather than overwhelm it.
