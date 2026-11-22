---
name: review-and-deliver
description: 'Reviews a built model visually and delivers it: review PLAN --outdir (BOM, previews, --views, --draft), opening and comparing images with the brief, the mandatory before/after silhouette boards for vehicles, rendering modules alone or in place with bin/ldraw-xray (boards, stud maps, cutaways, mosaic.png), then the delivery rules: metrics.md timing for every stage in seconds and hh:mm:ss, visual evidence, ai-NAME.mpd named after the model (ai- prefix, e.g. ai-ford-mustang.mpd) with [AI-GENERATED] title, Author, CC-BY-NC licence and keywords via finalize, and final review of the delivered bytes. Use after a build passes, when inspecting a warning in the render, and before handing a model to the user.'
---

# Review and deliver

Look at a built model, inspect anything a warning names with `bin/ldraw-xray`, then finalize and hand over exactly the three mandatory deliverables: timing metrics, visual evidence and `ai-NAME.mpd` (named after the model) with the required metadata. Checks cannot tell whether a model looks right; the images can. Neither checks nor images prove clutch, strength or motion. Fixing diagnostics: [fix-build-errors](../fix-build-errors/SKILL.md).

## Review the plan

```sh
./ldraw-agent review output/TASK/model.plan.json --outdir output/TASK/review
```

- `review` rebuilds the plan, runs every check (source, geometry, declared structural and flex checks), writes the BOM, renders previews (home, top and front by default; choose others with `--views home front back left right top bottom`) and compares the renderer's BOM with the model's, against frozen bytes.
- Rerunning on an unchanged plan reuses the bundle; a changed plan replaces it; `--force` recomputes anyway.
- **Files you add to the bundle stop the review**: keep notes outside it.
- `--draft` renders a failing model; `--no-render` runs checks only (skipped stages are not passing evidence); `--section NAME` reviews one module (excluding parent and sibling interactions).

## Look at the model

1. Open the previews and compare silhouette, proportions and colours with the brief, at thumbnail size and full size.
2. Look closely at every placement a warning names. Render one module alone, or in its parent:

   ```sh
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --view home -o output/TASK/xray/NAME
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --parent model.ldr --highlight section --ghost --view home -o output/TASK/xray/NAME-in-place
   ```

3. Fix what you see in the plan, then review again.
4. **Vehicles:** do the mandatory silhouette pass ([design-models](../design-models/SKILL.md)). Render the outline before and after rounding the blocky edges with SNOT curves, and keep both boards:

   ```sh
   bin/ldraw-xray render output/TASK/review/model.mpd --view front --view right --view top -o output/TASK/xray/silhouette-before
   bin/ldraw-xray mosaic output/TASK/xray/silhouette-before/manifest.json --output output/TASK/xray/silhouette-before/mosaic.png
   ```

   A plain `render` writes no `mosaic.png`; the `mosaic` command adds the one every delivered board needs. Repeat as `silhouette-after`, and say in the final response which edges were rounded and which were left square.

Open the whole model from useful sides, the underside and hidden joins. Check every module in isolation **and** in its parent context (every distinct parent where reused). A JSON report cannot establish visual review.

## Inspect with ldraw-xray

Set `LDRAW_DIR`, `LDRAW_XRAY_CACHE` and, if needed, `LEOCAD` (see the root [ldraw-nova](../SKILL.md) setup), then run `bin/ldraw-xray doctor`: `renders: true` means rendering works; otherwise read `errors`. Xray needs `--shadow data/offLibShadow` to use Nova's connector shadows. `sections`, `palette` and `mosaic` work without LeoCAD. Check current `--help` for options.

```sh
bin/ldraw-xray sections output/task/model.mpd
bin/ldraw-xray board overview output/task/model.mpd --section 'wing.ldr' \
  --output output/task/xray/overview
bin/ldraw-xray render output/task/model.mpd --section 'wing.ldr' \
  --parent --highlight section --ghost --view front \
  --output output/task/xray/mount
bin/ldraw-xray render output/task/model.mpd --section 'wing.ldr' \
  --stud-map --view home --view bottom --output output/task/xray/studs
```

Read the JSON's `images`, `notes` and `warnings`, then open `mosaic.png` and the individual PNGs (full size for small joins). An empty selection can succeed with a warning; `--section` needs the exact name, so list sections first. Bare `--parent` needs a unique parent; otherwise name it.

| Question | Command/options |
| --- | --- |
| Hidden parts | `render MODEL --xray 'colour:15' --highlight 'part:3647' -o OUT` |
| Build sequence | `render MODEL --section NAME --steps 3,7-9 -o OUT` |
| Shell cross-section | `board cutaway MODEL --section NAME --view front --depths 0.35 0.5 0.65 -o OUT` |
| Candidate pivots | `axes MODEL --section NAME` |
| Contacts and groups | `connections MODEL --section NAME` |
| Replay inspection | `board run recipe.json -o NEW_OUT` |
| Stud directions (SNOT) | `render MODEL --section NAME --stud-map --view home --view bottom -o OUT` |

- **Selectors** (quote them): `all`, `section`, `line:12,20-24`, `step:3-5`, `part:3001*`, `colour:15,4`, `ref:wing.ldr`. `|` unions; `!` removes (applied last; removals alone start from all placements). Line and step numbers belong to the source.
- **Constraints:** `--ghost` requires `--highlight`. `--steps` cannot combine with `--parent`, `--highlight` or `--ghost`. `--stud-map` and `--xray` are mutually exclusive. More than 12 panels needs `--no-mosaic`, so **split evidence into boards of at most 12 panels** so every board has its `mosaic.png`. Existing results need a new output directory or `--force`.
- **Motion:** get candidate axes with `axes`, then `board pivot --point X Y Z --direction X Y Z --moving 'SELECTOR' --angles ...` (section frame, -Y up). Choose plausible angles for the actual range with a fixed camera; a generic 0/45/90 sweep can show impossible poses.
- **Reading boards:** magenta marks highlights or new steps; pale grey is ghosted context; a neon-green rod is a synthetic axis marker. Stud maps recolour by stud direction (up lilac, +X rose, −X vermilion, +Z electric blue, −Z aqua, down lime, odd angle violet). They show orientation, not verified mating. Contacts and box overlaps are clues with incomplete coverage.
- Commands emit one JSON object; exit 2 = bad input/setup, 1 = execution failure.

When construction order is unclear, `manual prepare FILE --section NAME --outdir DIR` makes attributed source steps with per-step parts (`--overview` adds final views; `--no-render` prepares data only). `mechanism prepare` adds operation notes. A one-group source has no invented build sequence.

## Deliver

For **each model**, give the user only these three deliverables under `output/TASK/`, with direct links in the final response:

1. **Metrics** in `metrics.md`: total generation wall time and a breakdown for every stage (below), each duration in seconds and `hh:mm:ss`.
2. **Visual evidence:** every `xray/<board>/mosaic.png`, plus stills and previews from different perspectives. Include every board produced during research, construction and review; label reference studies and intermediate revisions so they cannot be mistaken for the final model. Include final home, front, back, left, right, top and bottom views, and close-ups of hidden joins. For a vehicle, include the `silhouette-before` (labelled as an intermediate revision) and `silhouette-after` boards. Preview PNGs can serve as stills.
3. **`ai-NAME.mpd`**, named after the model: `ai-` plus the model's name in lowercase words joined by hyphens (`ai-wanderer.mpd`, `ai-ford-mustang.mpd`, `ai-mecha-invader.mpd`), with the metadata below in every AI-generated model/submodel section. Never the generic `ai-generated.mpd`: `finalize` refuses it and any name without the prefix. Use a separate directory per model. The tool's internal `review/model.mpd` is not the user-facing file.

Keep plans, generators, review reports, BOMs, xray recipes/manifests and notes internal. Do not attach or package them, or produce `.blend`, `.glb`, videos, README handoffs or other extras unless explicitly requested. Briefly state unresolved warnings or skipped checks in the final response.

### Timing (`metrics.md`)

- Start a timing log **before planning** and update it throughout.
- Record start/end timestamps, elapsed time and measurement source for: planning, construction/part research, plan or generator authoring, build/check execution, repairs, rendering/xray, visual inspection, metadata/finalization. Include setup or other stages when used, plus retries and failed commands. Mark unused stages `not run`.
- **Write every duration, per stage and in total, in seconds followed by its `hh:mm:ss` translation**: `4523.4 s (01:15:23)`, `42 s (00:00:42)`. Round `hh:mm:ss` to the nearest whole second, pad each field to two digits and do not wrap hours past 24 (`93784 s (26:03:04)`); show no unit smaller than seconds. Keep the seconds value as measured.
- For each stage distinguish **wall time, tool execution time and agent/model thinking time**. Report total elapsed time, total tool time and per-agent/model thinking time where available, with the actual agent/model names and versions.
- `LDRAW_AGENT_TRACE` records `ldraw-agent` command durations to an internal JSONL file: create its parent directory first and verify entries were written. Time other tools separately.
- If a measurement is not exposed, write `unavailable` with the reason. **Never** equate elapsed minus tool time with thinking time. Label estimates and their method. State units, boundaries and overlaps; parallel durations are cumulative and must not be added to wall time as if sequential. Metrics describe durations, not reasoning transcripts.

### MPD metadata

In the plan: set `author` to the actual contributing agent/model names and versions, `license` to `CC-BY-NC`, and prefix the root section's `description` with `[AI-GENERATED] ` exactly once. Override section authors when contributions differ; the root header lists all contributors. Use the runtime's model identifier; record `version unavailable` if not exposed, never invent one. Keep the `ai-NAME.mpd` filename, section names, `Name:` fields and references unchanged; renaming after finalizing means finalizing and reviewing again.

Each AI-generated section's header must contain, before its geometry:

```text
0 Author: <agent name and version; model name and version; other contributors as applicable>
0 !LICENSE CC-BY-NC
0 Allows sharing and adapting for noncommercial purposes only, with attribution to the AI that authored the current model.
0 !KEYWORDS AI, AI-generated
```

These are section headers inside the MPD, not comments before its first `0 FILE`. The main title line becomes `0 [AI-GENERATED] <model title>` right after its `0 FILE` line. Preserve existing authors/licences in imported third-party blocks; do not relabel them as AI-created. The plan has no keywords or licence-comment field: keep `license` single-line and add no unsupported keys.

### Finalize and verify the delivered bytes

```sh
./ldraw-agent build output/TASK/model.plan.json --output output/TASK/ai-NAME.mpd
./ldraw-agent finalize output/TASK/ai-NAME.mpd
./ldraw-agent review output/TASK/ai-NAME.mpd --outdir output/TASK/final-review --views home front back left right top bottom
bin/ldraw-xray board overview output/TASK/ai-NAME.mpd --output output/TASK/xray/final-overview
```

- `finalize` adds the licence comment below each generated `0 !LICENSE CC-BY-NC` line and the keywords after it, keeps CRLF, and checks the filename (`ai-NAME.mpd`), the title prefix and the authors. Run it again after every rebuild (it never duplicates a line). Do not write your own script for this or edit the managed review bundle.
- Keep the successful **plan** review for declared structural/flex checks; an MPD review does not replace them. Then review the finalized MPD so final images and reports match the delivered bytes.
- Open the final previews and mosaics. Verify: the filename; a single `[AI-GENERATED]` prefix; the exact licence/comment pair and other headers in every generated section; **byte equality with `final-review/model.mpd`**. Never deliver an old model after a failed rebuild. If the finalized MPD changes, refresh affected evidence.
- Check every board has a nonempty `mosaic.png` and every required file is linked. Report any missing evidence explicitly rather than claiming delivery is complete.

## Record conclusions

Record image paths, source identity, findings, corrections and unresolved limits (internally). `manual review DIR --images IMAGE ... --note TEXT` records review for prepared manuals; changing geometry needs fresh checks and images, changing descriptions does not. Reuse images only when source hashes and selections match. Physical validity remains `not_proven` outside the documented checks.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/cards/review.md](references/docs-agent-cards-review.md)
- [docs/agent/guides/review-models.md](references/docs-agent-guides-review-models.md)
- [docs/agent/guides/xray.md](references/docs-agent-guides-xray.md)
