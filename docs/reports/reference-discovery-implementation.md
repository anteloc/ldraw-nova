# Reference discovery implementation — 2026-09-25

The assessment is now implemented as an agent workflow: search whole models, submodels or parts; inspect actual contents; compare rendered candidates; reuse an attributed construction or rebuild its technique at the required scale. The [workflow guide](../agent/reference-discovery.md), [curated atlas](../../examples/reference-atlas/README.md) and [machine-readable evidence](reference-discovery-implementation.json) retain the commands and results.

## Delivered

- `discover index/search/show/parts` connects all three `*_DESCRIPTIONS_JEV.full_description` fields to stable identities, source paths, parent context, actual dependencies and BOMs. Jev runs against a filtered local primary-key table with its original field/text provenance retained. The source SQLite database is opened read-only. Explicit offline FTS uses BM25 ordering; the existing model searches also gain ranked pagination.
- Candidate filtering separates physical parts from internal/legacy records and assemblies from embedded DAT definitions, empty blocks and raw geometry. Measured part limits and Technic share complement family filtering. Translation/colour-independent shape grouping and a parent cap diversify results; rotated and mirrored constructions retain distinct identities.
- `discover prepare/catalog` creates measured cards, namespaced attributed MPDs, recorded source repairs, explicit preview colour, Python/LeoCAD BOM comparisons and an offline searchable gallery. Default views are home/front/right/top; all seven views are supported. Independent renderer processes and artifact hashes provide bounded parallelism and resumable rendering.
- `discover review/example` records only views actually opened, checks source/artifact freshness, and requires a matching BOM, passing assembly/geometry checks, contact inspection and a reuse/adapt review before example export. The resulting plan imports the source through a positioning wrapper and includes an authored lesson and placement guide.
- `examples --family reference` exposes 21 curated source examples and two adjustable recipes. The arcade bay and street lantern change brick courses and palette, preserving physical part dimensions. Regeneration invalidates stale images and visual reviews.
- Agent instructions now call for whole-model inspiration, role-specific submodel comparison and discovery of dedicated fittings from actual construction BOMs before adaptation. Single-section files and trailing whitespace in source section identities are handled without discarding attribution or original line mappings.

## Measured result

The final full regression suite passed: **181 tests in 72.15 seconds**. This includes source identity and extraction regressions, filtered Jev snapshots, cache/artifact freshness, review/export gates, all curated plans and their attributed BOMs, both adjustable recipes, and stale-preview invalidation. `git diff --check` passed; all 239 checked local Markdown links resolve.

| Resource | Result |
|---|---|
| Indexed fields | 35,257 parts; 1,821 models; 28,451 submodels |
| Corrected source headers | 38 descriptions corrected only in the derived index |
| Broad visual library | 200 submodels + 20 whole models; 880 images; no preparation exceptions |
| Candidate inspection | 36 submodels with all seven views and contact analysis; 252 images |
| Curated source atlas | 21 examples; 147 retained images; home plus one relevant orthographic view inspected for each |
| Adjustable recipes | Two default examples with four views each; home/front inspected; two-course and seven-course variants checked |
| Artifact and source audit | All recorded hashes match; all 140 distinct broad-library source files still match their selection hashes |
| Gallery links | 1,980 broad-library, 432 candidate-gallery and 252 curated-gallery links resolve |
| Resume check | All 220 cached cards reused; zero images regenerated |

The broad catalog distinguishes **194 prepared references** from **26 needing adaptation**. Three of the latter have Python/LeoCAD BOM disagreements. It intentionally retains these visual precedents with their diagnostics. Contact analysis is deferred until selection in the broad catalog; eight of the 36 separately inspected candidates had geometry errors and were excluded from the curated atlas.

All 21 curated placement plans rebuild with no assembly or geometry errors and match their saved LeoCAD BOM. Eleven have one optimistic connection group; ten have multiple groups, recorded in their guides. The two recipe defaults and both tested height variants have one optimistic group. These checks establish the recorded computational results, not complete connection legality, material clearance, stability or successful integration into a new model.

Three live queries through the new command exercised all three fields with `jev-1.13.0`, 500 scored candidates each:

| Query | Eligible records | Jev elapsed time |
|---|---:|---:|
| Street lamp for a minifigure pavement | 20,823 | 8.98 s |
| Passenger train with locomotive and carriages | 1,720 | 8.17 s |
| Cylindrical passenger-plane engine housing | 17,422 | 8.51 s |

These are retrieval smoke tests, not exhaustive corpus searches or an A/B benchmark of final model aesthetics. Actual inspection remains necessary: the tray returned for a ramp query did not clearly establish that function, and its visual review is recorded as technique-only. The original database still matches assessment SHA-256 `5472f2479da929c06d4a39dd94c04aa58c3065306441e1746fc6cc4a8bd49e02`.

## Reproduce

```sh
./ldraw-agent discover index
./ldraw-agent discover search submodels 'a street lamp for a minifigure town pavement' \
  --limit 8 --report output/lamps.json
./ldraw-agent discover parts output/lamps.json --limit 12
.venv/bin/python examples/reference-atlas/generate.py --jobs 3
./ldraw-agent examples --family reference aircraft --limit 5
./ldraw-agent build examples/reference-atlas/airliner-engine/scene.plan.json \
  --output output/airliner-engine-example.mpd
.venv/bin/python -m pytest -q
```

Open [the generated broad gallery](../../output/reference-library/index.html) or [the retained example gallery](../../examples/reference-atlas/index.html). The large catalog lives in ignored `output/`; its reproducible manifest and the inspected examples live under `examples/reference-atlas/`. No generator is required for each unchanged source: the shared extractor and editable placement plan already reproduce it.
