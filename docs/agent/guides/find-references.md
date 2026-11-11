# Find a relevant construction and inspect its evidence

Search current local knowledge first:

```sh
./ldraw-agent knowledge search 'sideways glazing attachment' --limit 5
./ldraw-agent examples 'retained chain' --family flex
./ldraw-agent knowledge search 'spacecraft silhouette' --scope inspiration
```

Retrieve a few role-specific lessons, open their construction documentation/model source paths (not library part definitions), and compare interfaces, scale and limits. Default search includes current guides, construction lessons and tutorials. Inspiration, diagnostics, holds, archives and research need explicit scopes. No match is useful information; do not silently fill the list from a weaker source. See the [search and registration contract](../reference/cli.md#retrieve-construction-knowledge).

## Targeted part information within a construction

Retrieve and adapt documented construction principles first. Use part search
when a lesson or design decision needs a particular reference, variant,
substitute, accessory, dimension or interface detail. Do not replace the
construction workflow with piece-by-piece searches or ad-hoc geometry tools.

Choose the method that fits the question: [SQL, regex, FTS/BM25, Jev,
categories or cached dimensions](part-information.md). These methods are
complementary and have no mandatory order. Never directly read, search or parse
library `.dat` contents. Get exact filenames from informational sources before
rendering or explicit tool inspection. A missing lesson calls for the reference
workflow below and explicit unresolved limits, not an invented construction claim.

## Broader raw-source discovery

When curated knowledge lacks a role, use explicit offline FTS over parts, models or submodels. Whole models can inform proportions; submodels reveal construction; parts supply shapes and interfaces. These raw results are not admitted examples.

```sh
./ldraw-agent discover index
./ldraw-agent discover search submodels 'rack steering' --construction all --engine fts --limit 5
./ldraw-agent discover search parts 'jet engine housing' --engine fts --limit 6
```

Choose the intended construction filter deliberately; raw discovery retains its existing System filter unless overridden. Do not infer a technique from subject. Jev reranking is optional; its prerequisites and failure handling are in the [CLI reference](../reference/cli.md#check-jev-availability-before-searching).

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

## Prefer the actual assembly over its label

Names, family categories and search ranks shortlist references. Expand the
selected section's physical inventory and read its source before assigning
mechanical roles. The W16's V8 label, double-bevel gears used on parallel axes,
and cam-driven Defender engine are concrete counterexamples to name-based
inference. Embedded DATs with numeric-only descriptions may still be important
gears; preserve their geometry and inspect their provenance/variant.

A whole shock DAT and a split rod/cylinder/spring assembly have different
physical boundaries. Do not count its internal primitives as loose parts, replace
an embedded definition with a guessed current part, or silently change the BOM.
Categories and bounding-box snapshots help select candidates; measured geometry
and connector frames locate real pivots and mounting interfaces.

## Keep selection, frame and occurrence identity together

Record original model hash, exact `FILE` section, selected physical occurrence
paths, composed transforms and effective colours. Mecha's hierarchical paths
such as `84/16` are not Nova's flattened `--occurrence` indices. Obtain current
Nova indices with `inspect`/`connectors` for the same selection before snapping
or writing a structural contract.

Extracting a section changes its frame relative to the outer scene. A flat
world-coordinate extract and a section-local extract therefore need different
placement transforms. Keep the extraction manifest and any old-to-new identity
map; do not copy occurrence IDs across them by appearance or filename.
If changing frames, transform axes and anchors as well as parts.

Use `extract`/`mechanism prepare` to preserve dependency sections, embedded DATs,
author and licence headers. Record permitted rotation/BFC repairs to the copy.
The source models, supplied categories and part library remain unchanged.

## A visible support may still be an incomplete interface

List fixed supports, moving members, input/output parts and omitted neighbours.
The suspension extract has floating tie-rod boundary pins; the W16 preview
hides its fixed heads and frame; the local rack and worm examples need parent
parts. Add the actual missing holders, drive parts or retained stack before
treating a study as a new self-contained model.

Trace keyed axle holes separately from round bearings and loose clutch gears.
Coaxial proximity or a connector contact does not mean rigid coupling, torque
transfer or axial retention. MPD sections describe source organization, not
rigid groups. Check bushes, axle stops and insertion access on both sides of
each new stack using the [structural workflow](technic.md) where supported.

## Missing evidence is a reason to inspect

In the Mustang audit, tiny rounded source rotations suppressed many connector
results: raw analysis found 29 contacts and axle-hole evidence for 0/25 straight
axles; Mecha's bounded analysis correction found 921 contacts and 25/25 axles.
Those figures describe its historical analysis policy. Nova does not acquire
that policy by importing this guide.

When a plausible drivetrain appears disconnected, inspect transform validity,
embedded parts, shadow support, selection size and skipped-contact diagnostics.
Use Nova's recorded extraction normalization for permitted rounded rotations;
never silently normalize real scale/shear or introduce reflected physical parts.
Several contact records may describe one joint. Neither a dense graph nor a
zero-error report establishes complete mechanical coverage.

The Mustang's worm/crank route ends at a possible surface contact with beams.
Record that unresolved coupling rather than inventing a connector or deleting
the mechanism from the design notes. Distinguish an intentionally fixed member,
an intended moving one, and an unknown role.

## Keep observation and qualification together

For each reused core, retain: what was directly counted/measured, what the source
report checked, what was inferred or approximated, and what changes in this
model. A source sweep is not a new-model test; a rendered cutaway is not proof
of assembly order; sampled surface crossings do not test bore containment.

Mecha-specific spring scaling, hub projection, fixed boundary points, selector
cam profiles, prescribed paddle timing and added reconstruction gears must not
quietly become Nova construction rules. Preserve the useful physical pattern
and its limits. Continue the normal generation/review workflow with analytical
mechanism verification deferred.

## Admit an example

The package README owns its lesson, scope, entry points, interfaces, reproduction, limits and provenance. Register only distinct constructions; colour variants and identical copies share an entry. Retain original names as qualified aliases. Review each retained model/submodel alone and in every actual parent, checking that prose and metadata match what is visible.

Preserve source hashes, exact selections and opened-image evidence. Any geometry edit invalidates affected visual acceptance and checks. Reuse unchanged hash-matched evidence. Source/BOM/export gates remain mandatory for reusable exports; search registration does not waive them. See [review models](review-models.md) and [metadata fields](../reference/cli.md#register-or-maintain-an-example).

