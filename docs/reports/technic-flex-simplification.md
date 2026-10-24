# Technic and LSynth workflow simplification

Implemented and verified locally on 2026-10-24. This extends the [earlier workflow consolidation](workflow-simplification.md) to the manual work around flexible assets and fixed Technic structures.

## The shorter workflow

Keep the existing plan format and run `review PLAN`. Two optional declarations replace the extra orchestration:

- An asset can declare `source`, `namespace`, optional `checks` and `timeout`. The builder checks the constraints, synthesizes, packages, validates and measures the asset before embedding it.
- A section can link its `structure` contract. `build` and `review` check that section's required joints, seating, restraints and insertion order. `technic plan` writes this link automatically. Included modules keep their own contract indices and paths.

`flex build` now performs the complete source/synthesis/measurement sequence and infers its output name. Existing manual commands, string MPD assets and the lower-level Python synthesis adapter remain available, including for diagnostic experiments. Prebuilt assets do not require LSynth.

The [plan guide](../agent/plans.md), [agent instructions](../../instructions.md), [Technic guide](../agent/technic.md) and [flex guide](../agent/flex-constraints.md) lead with this path. The pneumatic press generator's `--automatic` mode declares its hose source and limits. Its default mode still reproduces the original fixtures. Endpoint/lead expansion and marker-frame calculations now use the shared authoring helpers while preserving those fixtures' bytes.

## Correctness and provenance

Only raw LSynth output is cached. The key covers original constraints, configuration, engine version and Python source files, and Python version. Cache payloads have a checksum; missing or damaged entries regenerate. Packaging uses current bundled geometry, and library validation and chosen geometric limits run on every build. `--no-cache` reruns synthesis; it does not bypass checks.

The complete flexible-asset operation stages its output. Failed source checks, synthesis, validation or measurements leave the previous MPD and manifest intact. Publication rolls back if either file cannot be replaced. Edits to constraints during measurement prevent publication.

A review freezes generated constraints, assets and manifests under `flex/`, and declared contracts under `structure/`. Their reports are in `validation.json`; all copied artifacts are hashed by `review.json`. The final MPD embeds its generated geometry and remains portable. This is not a full snapshot of the installed parts library or every editable generator dependency.

Technic contact discovery now filters impossible distances before applying the unchanged exact seating rules. Contact order remains stable. Geometry review reuses its computed contacts instead of calculating them again for seating checks. Exhaustive comparisons cover rotated structures, partial engagement and misplaced connectors; the existing negative tests still reject incomplete grips, conflicting occupation and invalid keyed seating.

## Local performance measurements

These measurements exclude initial library loading. They describe the supplied fixtures, not every model or rendering workload.

| Fixture | Contact search speedup | Complete structural review speedup |
|---|---:|---:|
| Box chassis | 11.2× | 1.21× |
| Three-level frame tower | 45.5× | 1.45× |
| Service platform | 19.8× | 1.10× |

The before/after runs produced identical complete structural reports. The contact timings compare a single local run before and after the change.

For the three-hose pneumatic press, the complete checked asset build took a median **0.342 s uncached** and **0.049 s cached**, approximately **7× faster**. Each median covers three runs after one warm-up, using `min_radius=15` and `min_separation=10`. Both paths produced the same MPD hash and ran source, assembly and generated-geometry checks. These measurements do not include rendering.

## Regression and rendering evidence

Final full suite: **427 passed in 125.69 seconds**, with no failures or skips. `git diff --check` and local Markdown link checks also passed.

Tests cover relative paths through includes, schema mistakes, source/config cache invalidation, corrupted caches, current library validation on cache hits, stricter geometric limits, stale contracts, embedded part hashes, module-local indices, failed publication and source edits during checks. Existing System, SNOT, mechanisms, all installed LSynth method fixtures and example-byte regressions remain in the suite.

The automatic pneumatic press reproduces the supplied reviewed MPD byte for byte, including its three seated hoses. The final real LeoCAD runs passed validation and exact Python/LeoCAD BOM comparison:

| Model | Physical placements | MPD SHA-256 |
|---|---:|---|
| Pneumatic press | 41 | `5537de112c1b85a4f63111225018ef197aadb125d651516b342414bec5469f8e` |
| Box chassis | 18 | `939934608f422cd4cab8aecb1232f392f33d39282eb51da04c2c3672e84fd708` |

Press home/front and chassis home/top previews were opened. The press retains its seated red/blue cylinder hoses, separate supply route and supported rigid frame. The chassis retains its two side frames, crossmembers and upper rails; no missing geometry was apparent in these views. These are rendering regressions, not new claims of strength, motion, general collision freedom or physical validity.

Reproduce the main workflows from the repository root:

```sh
.venv/bin/python -m pytest -q
./ldraw-agent technic plan box-chassis --output output/chassis.plan.json
./ldraw-agent review output/chassis.plan.json
.venv/bin/python examples/flex/pneumatic-press/generate.py --automatic \
  --output output/press/press.plan.json --hoses output/press/hoses.ldr
./ldraw-agent review output/press/press.plan.json --contacts all
```

Use `--force` to replace existing generated outputs. Local rendered bundles are under ignored `output/workflow-simplification/press-review/` and `chassis-review/`; test logs and timing samples are under `.cache/simplification/`.
