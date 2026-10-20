# Workflow simplification

The default path is now **edit a plan → review → inspect images → repair**. A simple model needs one JSON source file. Python remains available for calculations and procedural patterns. All existing commands and plan features remain available.

## Changes

- Added `review PLAN.json|MODEL.mpd`: build when needed, validate source and geometry, write the Python BOM, render views, and compare the LeoCAD BOM. Results share one directory and one manifest. `--no-render` supports intermediate checks with explicit skipped stages.
- Made `build --output` optional: `name.plan.json` and `name.json` default to `name.mpd`. Existing explicit paths, overwrite protection and failure behavior are retained.
- Shared source/geometry orchestration between build, review and individual inspection/validation. The geometry algorithms, schema, parser and serializer remain the existing implementations.
- Consolidated duplicate manual/mechanism CLI setup and dispatch while preserving their notes, study kinds and export behavior.
- Updated the Python example to use the shared checked build and save its editable plan. Failures use an explicit check rather than an assertion that disappears under `python -O`.
- Rewrote the README around a runnable local example and the modeling loop. Moved the project history to [background](../background.md), retaining the Docker instructions and acknowledgements.
- Reduced the main [agent instructions](../../instructions.md) from 2,957 to 1,029 whitespace-delimited words (65%). Specialized guides remain linked by task. The [plan guide](../agent/plans.md) consolidates authoring guidance; the [tool reference](../agent/tooling.md#review-a-model) documents review artifacts and options.

There is one plan format and one set of validators. Reusing those implementations avoids maintaining a second modeling language or weakening checks to make the workflow appear easier.

## Compatibility and correctness

A structural comparison of argparse interfaces against the original revision found all 31 existing commands retained their options, defaults, types and subcommands. The intentional changes are the new `review` command and optional `build --output`. Direct before/after execution of `build`, `validate --geometry`, `inspect` and `bom` on the bridge produced equal JSON reports, exit codes and MPD bytes.

A review uses a frozen model copy for validation, rendering and BOM comparison. Reports include the model hash; the manifest includes the input hash and hashes of every produced artifact. Plan includes and assets still resolve relative to their declaring source. Input provenance identifies the root source; the resolved MPD hash identifies the reviewed geometry, including imported assets. It is not a complete snapshot of the source dependency tree or the installed library.

Output is staged and replaces a previous generated bundle only with `--force`. Additional files, edited artifacts and symlinks are protected. Failed validation publishes diagnostics without a model. Rendering failures retain completed checks and discard partial previews. Reruns cannot inherit stale previews or BOM comparisons; publication failures restore the previous bundle. Invalid input/output preflight requests leave existing output unchanged and return an error.

Summary output limits display rows, not checks. Contact limits, geometry budgets, unsupported geometry, inherited colours, source-line attribution and embedded DAT boundaries keep their existing behavior. Family-specific checks remain separate. `physical_validity: not_proven` and required image inspection remain explicit.

## Verification

Verified in the supplied workspace on 2026-10-20:

- Baseline: 226 tests passed with the configured official parts library.
- Final full suite: **246 passed in 82.99 seconds**, with no skips or failures.
- Added 20 regressions for plan/MPD review, command compatibility, source hashes, relative includes, scoped colours/source lines, embedded parts, budget failures, skipped contacts, BOM mismatches, renderer failure, stale outputs, edited-file protection and publication rollback.
- The complete two-part example in the new plan guide built, rendered and matched both BOMs. The Python example produced its plan and MPD.
- The bridge review reproduced the checked-in MPD exactly: SHA-256 `7f9a0a9e808d8b6e6dcf3ddff1ac24b007d0e2b74f4bfc577642b1f6be252138`. Five physical placements, complete geometry, no diagnostics and matching BOMs. Home/front previews were opened and show the expected two pillars and deck.
- The existing Alder Court v19 MPD passed source/geometry checks and the real LeoCAD render/BOM comparison at 2,979 physical placements. SHA-256 `70f99635d77f93f621d0f654910f9843abfd03d55760bc819330cd44aa330521`. Its bytes were unchanged. Whole-scene contacts remain explicitly skipped and partial collision coverage remains a warning. Home/front previews were opened to check rendering and framing; this was a tooling regression, not a new physical certification or design review.
- Documentation links, shell syntax and `git diff --check` passed.

Run `.venv/bin/python -m pytest -q` to reproduce the automated suite. Local reports, previews, compatibility results and test output from this run are under ignored `output/workflow-simplification/`.
