# Review card

```sh
./ldraw-agent review output/TASK/model.plan.json --outdir output/TASK/review
```

`review` rebuilds the plan and runs every check. It writes the BOM, renders previews (home, top and front; choose others with `--views home front back left right top bottom`) and compares the renderer's BOM with the model's. Rerunning on an unchanged plan reuses the bundle, and a changed plan replaces it; `--force` recomputes anyway. Files you add to the bundle stop the review, so keep notes outside it.

## Look at the model

1. Open the previews and compare silhouette, proportions and colours with the brief, at thumbnail size and full size.
2. Look closely at every placement a warning names. To render one module alone, or in its parent:

   ```sh
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --view home -o output/TASK/xray/NAME
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --parent model.ldr --highlight section --ghost --view home -o output/TASK/xray/NAME-in-place
   ```

   The [xray guide](../guides/xray.md) has more views, including stud maps and cutaways.
3. Fix what you see in the plan, then review again.
4. **Vehicles:** do the mandatory [silhouette pass](../guides/design-models.md#soften-blocky-vehicle-silhouettes). Render the outline before and after rounding the blocky edges with SNOT curves, keep both boards, and say in the final response what was rounded and what was left square.

Checks cannot tell whether a model looks right; the images can. Neither checks nor images prove clutch, strength or motion.

## Deliver

For **each model**, give the user only these three deliverables under `output/TASK/`, with direct links in the final response:

1. **Metrics** in `metrics.md`: total generation wall time and a breakdown for every stage, as specified below, each duration in seconds and `hh:mm:ss`.
2. **Visual evidence**: every `xray/<board>/mosaic.png`, plus stills and previews showing different perspectives. Include every board produced during research, construction and review; label reference studies and intermediate revisions so they cannot be mistaken for the final model. Include final home, front, back, left, right, top and bottom views, and close-ups of hidden joins. Preview PNGs can serve as stills; duplicate files are unnecessary.
3. **`ai-NAME.mpd`**, named after the model: `ai-` plus the model's name in lowercase words joined by hyphens, such as `ai-wanderer.mpd`, `ai-ford-mustang.mpd` or `ai-mecha-invader.mpd`. It carries the metadata below in every AI-generated model/submodel section. Never use the generic `ai-generated.mpd`; `finalize` refuses it and any name without the prefix. Use a separate task/model directory for each model.

Keep plans, generators, review reports, BOMs, xray recipes/manifests and working notes internally for reproducibility. Do not attach or package them, or produce `.blend`, `.glb`, videos or other extra deliverables, unless explicitly requested. The tool's internal `review/model.mpd` is not the user-facing filename. Briefly state unresolved warnings or skipped checks in the final response; do not add a README deliverable.

### Timing

Start a timing log before planning, and update it throughout the task. Record start/end timestamps, elapsed time and measurement source for planning, construction/part research, plan or generator authoring, build/check execution, repairs, rendering/xray, visual inspection and metadata/finalization. Include setup or other stages when used, plus retries and failed commands. Mark unused stages `not run`.

Write every duration, per stage and in total, in seconds followed by its `hh:mm:ss` translation, so nobody has to convert by hand: `4523.4 s (01:15:23)`, `42 s (00:00:42)`. Round `hh:mm:ss` to the nearest whole second, pad each field to two digits and do not wrap hours past 24 (`93784 s (26:03:04)`); show no unit smaller than seconds. Keep the seconds value as measured.

For each stage, distinguish wall time, tool execution time and agent/model thinking time. Use tool/runtime telemetry for measured durations. `LDRAW_AGENT_TRACE` can record `ldraw-agent` command durations to an internal JSONL file; create its parent directory first and verify entries were written. Time other tools separately. Include total elapsed generation time, total tool execution time and per-agent/model thinking time where available. Report the actual agent/model names and versions used.

If the runtime does not expose thinking time or another measurement, write `unavailable` with the reason. Do not equate elapsed time minus tool time with thinking time: it can include scheduling, waiting and other overhead. Label any estimates and their method. State units, timing boundaries and overlaps; parallel tool/agent durations are cumulative and must not be added to wall time as if sequential. Metrics describe durations, not private reasoning transcripts.

### MPD metadata and final verification

Set the plan's `author` to the actual contributing agent/model names and versions, and `license` to `CC-BY-NC`. Override section authors when contributions differ; include all contributors in the root header. Use the runtime's supplied version/model identifier, never an invented version; explicitly record `version unavailable` if it is not exposed.

Prefix the root section's `description` with `[AI-GENERATED] ` exactly once. This writes the internal main-model title as `0 [AI-GENERATED] <model title>` immediately after its `0 FILE` line. Keep the `ai-NAME.mpd` filename, section names, `Name:` fields and references unchanged; renaming the file after finalizing means finalizing and reviewing it again.

Each AI-generated section's header must contain, before its geometry:

```text
0 Author: <agent name and version; model name and version; other contributors as applicable>
0 !LICENSE CC-BY-NC
0 Allows sharing and adapting for noncommercial purposes only, with attribution to the AI that authored the current model.
0 !KEYWORDS AI, AI-generated
```

These are section headers inside the MPD, not comments before its first `0 FILE`. Preserve existing authors/licences in imported third-party model or part blocks; do not relabel them as AI-created. The main model and newly generated submodels always receive the required metadata.

The plan schema has `author`, `license` and section `description`, but no field for keywords or the licence comment. Keep `license` a single-line value and add no unsupported plan keys. After the final successful build, run `./ldraw-agent finalize output/TASK/ai-NAME.mpd`. It adds the comment below each generated section's `0 !LICENSE CC-BY-NC` line and the keywords after it, keeps the CRLF line endings, and checks the filename, the title prefix and the authors. Run it again after every rebuild; it never duplicates a line. Do not write your own script for this or edit the managed review bundle.

Keep the successful plan review for declared structural/flex checks, then review the finalized MPD itself so the final images and reports correspond to the delivered bytes:

```sh
./ldraw-agent review output/TASK/ai-NAME.mpd --outdir output/TASK/final-review --views home front back left right top bottom
bin/ldraw-xray board overview output/TASK/ai-NAME.mpd --output output/TASK/xray/final-overview
```

An MPD review does not replace plan-declared checks. Open the final previews and mosaics. Verify the `ai-NAME.mpd` filename, the single `[AI-GENERATED]` prefix on the internal main-model title, the exact licence/comment pair and other headers in every generated section, and byte equality with `final-review/model.mpd`; never deliver an old successful model after a failed rebuild. If the finalized MPD changes, refresh affected evidence before handoff. Check that every board has a nonempty `mosaic.png` and every required file is linked; explicitly report any missing evidence rather than claiming delivery is complete.
