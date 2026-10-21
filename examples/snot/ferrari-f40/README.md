# Ferrari F40: SNOT bodywork reference

The supplied `10248 Ferrari F40.ldr` adds useful vehicle constructions: narrow bracket-supported trim, perpendicular lamp/grille faces, repeated window louvers and compact body mounts. Its part comments identify pieces but do not explain those assembly roles. This reference adds **semantic labels to all 74 sections**, using the existing extraction, gallery and build-manual tools.

Start with the [searchable section gallery](index.html), or open the [annotated complete MPD](ferrari-f40.mpd). The original FILE names remain stable. Search the gallery for `door`, `louver`, `bracket`, `engine` or another role; each card links its isolated source, checks and provenance.

## Understand the source structure

The complete car in `main.ldr` contains **1,156 direct parts in 83 nonempty source steps**. It does **not** reference any of the other 73 sections. Those sections are saved construction callouts, some with their own declared children.

The saved callouts and the flattened car also differ. For example, the body-mount callout uses a `60897` clip where main step 13 uses `4085c`. The saved windscreen/cowl has 25 pieces with multipart glazing; the corresponding main step 41 adds 15 pieces, including the dedicated printed `19212p01` windscreen. These are construction precedents, not interchangeable occurrences of identical geometry.

[sections.json](sections.json) therefore separates **declared parents/children** from **main construction context**. Context step numbers point to the corresponding body area; they do not assert exact matches or create hierarchy. Only the main section is reachable from the car's root. Role names and lessons are curated interpretations of the source, step context and rendered views, not original author labels.

## Five small build studies

These retain the source's construction stages and include home/back views, final previews, editable placement plans and recorded image reviews.

| Study | Parts / stages | Lesson | Source section |
|---|---:|---|---|
| [Body mount](studies/body-mount/index.html) · [plan](studies/body-mount/scene.plan.json) | 5 / 4 | Combine bracket, side-stud and clip interfaces in one compact mount | `subModel-6.ldr` |
| [Door rail](studies/door-rail/index.html) · [plan](studies/door-rail/scene.plan.json) | 6 / 2 | Repeat brackets behind a thin visible trim strip | `subModel-35.ldr` |
| [Rear lamp](studies/rear-lamp/index.html) · [plan](studies/rear-lamp/scene.plan.json) | 8 / 4 | Put a lamp and grille on perpendicular faces | `subModel-53.ldr` |
| [Window louver](studies/window-louver/index.html) · [plan](studies/window-louver/scene.plan.json) | 5 / 3 | Repeat a small glazing module on stepped mounting planes | `subModel-57.ldr` |
| [Fascia core](studies/fascia-core/index.html) · [plan](studies/fascia-core/scene.plan.json) | 6 / 3 | Separate sideways panel mounts from structural support | `subModel-63.ldr` |

Each study's `GUIDE.md` and `study-notes.json` explain its interfaces, parent context and reuse limits. For the louver, the saved clamshell declares three placements with a 40 LDU longitudinal and 8 LDU vertical progression. That is a measured construction choice for this source, not a universal louver pitch.

```sh
./ldraw-agent build examples/snot/ferrari-f40/studies/rear-lamp/scene.plan.json \
  --output output/ferrari-rear-lamp.mpd
./ldraw-agent inspect output/ferrari-rear-lamp.mpd --contacts all
```

Import a study's attributed `source.mpd` as a plan asset, or include its placement plan. The `source_origin` anchor is a coordinate frame, not a verified connector. Inspect the actual receiving parts and review the combined assembly after adapting it.

## What passed, and what still needs work

- All **73 isolated saved callouts** pass source and geometry error checks after the existing bounded rotation normalization where needed. Overview contact analysis was not run. All **74** overview Python/LeoCAD BOM comparisons match.
- The complete car retains **25 body-overlap errors**, with reported penetration up to approximately **2.504 LDU**. Its gallery entry is explicitly marked as needing preparation. Some smaller overlaps involve rounding; the larger ones must not be dismissed as rounding. This is useful whole-car inspiration, not a validated reusable complete car.
- The five exported studies pass source/geometry checks and rendered BOM comparison. Additional all-contact checks find **one optimistic connection group in each**. All **37** step/view and final images were inspected. Nonrectangular material collision coverage remains incomplete, and isolated checks do not establish parent clearance or physical strength. See [verification.json](verification.json) and [visual-review.md](visual-review.md).

The annotated complete MPD changes descriptions and headers only. It deliberately retains the original geometry, including 14 rounded non-rigid matrices in sections 42, 68 and 69. The isolated catalog copies record bounded normalization in `extraction.json`; the largest changed coefficient is less than 0.0001. The five focused studies require no rotation repairs. Use their checked extractions for reuse rather than assuming the annotated complete MPD passes validation.

## Reproduce or extend the reference

[original.ldr](original.ldr) is a byte-identical copy of the supplied file. Its original `Author: LEGO` header and contact comment remain intact; no independent author or licence is inferred. Uncredited child sections are explicitly marked unspecified. Source hashes and extraction manifests preserve the provenance chain through the annotated copy and exported studies.

[annotations.json](annotations.json) is the editable role/lesson map. [studies.json](studies.json) selects the five lessons and supplies their interface notes. [prepare.py](prepare.py) checks the pinned source hash and requires exactly one annotation per FILE section. It delegates parsing, extraction, checking, rendering and gallery generation to the existing toolkit; it does not reconstruct the flattened main model or add a search database.

From the repository root:

```sh
# Refresh semantic metadata and the annotated MPD; no rendering needed.
.venv/bin/python examples/snot/ferrari-f40/prepare.py

# Rebuild all overview evidence and the searchable gallery.
.venv/bin/python examples/snot/ferrari-f40/prepare.py \
  --render-overviews output/ferrari-f40-assessment/sections

# Prepare the five source-step studies for image inspection.
.venv/bin/python examples/snot/ferrari-f40/prepare.py \
  --studies-out output/ferrari-f40-studies
```

`--catalog-root output/ferrari-f40-assessment/sections` refreshes the gallery from existing overview evidence without rendering again. After regenerating studies, inspect every image and use the existing [manual review/export workflow](../../../docs/agent/build-manuals.md#4-review-export-and-add-to-an-atlas). A new preparation invalidates the previous image review; the script never records an automatic visual approval.
