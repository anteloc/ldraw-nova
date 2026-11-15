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

Checks cannot tell whether a model looks right; the images can. Neither checks nor images prove clutch, strength or motion.

## Deliver

For **each model**, give the user only these three deliverables under `output/TASK/`, with direct links in the final response:

1. **Metrics** in `metrics.md`: total generation wall time and a breakdown for every stage, as specified below.
2. **Visual evidence**: every `xray/<board>/mosaic.png`, plus stills and previews showing different perspectives. Include every board produced during research, construction and review; label reference studies and intermediate revisions so they cannot be mistaken for the final model. Include final home, front, back, left, right, top and bottom views, and close-ups of hidden joins. Preview PNGs can serve as stills; duplicate files are unnecessary.
3. **`ai-generated.mpd`**, with the metadata below in every AI-generated model/submodel section. Use a separate task/model directory for each model, never a subject-specific MPD filename at handoff.

Keep plans, generators, review reports, BOMs, xray recipes/manifests and working notes internally for reproducibility. Do not attach or package them, or produce `.blend`, `.glb`, videos or other extra deliverables, unless explicitly requested. The tool's internal `review/model.mpd` is not the user-facing filename. Briefly state unresolved warnings or skipped checks in the final response; do not add a README deliverable.

### Timing

Start a timing log before planning, and update it throughout the task. Record start/end timestamps, elapsed seconds and measurement source for planning, construction/part research, plan or generator authoring, build/check execution, repairs, rendering/xray, visual inspection and metadata/finalization. Include setup or other stages when used, plus retries and failed commands. Mark unused stages `not run`.

For each stage, distinguish wall time, tool execution time and agent/model thinking time. Use tool/runtime telemetry for measured durations. `LDRAW_AGENT_TRACE` can record `ldraw-agent` command durations to an internal JSONL file; create its parent directory first and verify entries were written. Time other tools separately. Include total elapsed generation time, total tool execution time and per-agent/model thinking time where available. Report the actual agent/model names and versions used.

If the runtime does not expose thinking time or another measurement, write `unavailable` with the reason. Do not equate elapsed time minus tool time with thinking time: it can include scheduling, waiting and other overhead. Label any estimates and their method. State units, timing boundaries and overlaps; parallel tool/agent durations are cumulative and must not be added to wall time as if sequential. Metrics describe durations, not private reasoning transcripts.

### MPD metadata and final verification

Set the plan's `author` to the actual contributing agent/model names and versions, and `license` to `Redistributable under CCAL version 2.0 : see CAreadme.txt`. Override section authors when contributions differ; include all contributors in the root header. Use the runtime's supplied version/model identifier, never an invented version; explicitly record `version unavailable` if it is not exposed.

Each AI-generated section's header must contain, before its geometry:

```text
0 Author: <agent name and version; model name and version; other contributors as applicable>
0 !LICENSE Redistributable under CCAL version 2.0 : see CAreadme.txt
0 !KEYWORDS AI, AI-generated
```

These are section headers inside the MPD, not comments before its first `0 FILE`. Preserve existing authors/licences in imported third-party model or part blocks; do not relabel them as AI-created. The main model and newly generated submodels always receive the required metadata.

The current plan schema supports `author` and `license`, but not `keywords`. Do not add an unsupported plan key. After the final successful build, insert the keywords meta into the generated section headers in `ai-generated.mpd`. Make this finalization repeatable after each rebuild, which otherwise overwrites the added metadata. Do not edit the managed review bundle.

Keep the successful plan review for declared structural/flex checks, then review the finalized MPD itself so the final images and reports correspond to the delivered bytes:

```sh
./ldraw-agent review output/TASK/ai-generated.mpd --outdir output/TASK/final-review --views home front back left right top bottom
bin/ldraw-xray board overview output/TASK/ai-generated.mpd --output output/TASK/xray/final-overview
```

An MPD review does not replace plan-declared checks. Open the final previews and mosaics. Verify the filename, headers in every generated section, and byte equality with `final-review/model.mpd`; never deliver an old successful model after a failed rebuild. If the finalized MPD changes, refresh affected evidence before handoff. Check that every board has a nonempty `mosaic.png` and every required file is linked; explicitly report any missing evidence rather than claiming delivery is complete.
