# Catalog, export and evidence compatibility plan

Planning only, 2026-11-03. Read with the [example ledger](example-migration-ledger.md), [documentation ledger](document-migration-ledger.md) and [target diagram](target-structure.md). This specifies the remaining implementation work; it does not advertise a new command that already exists.

## One authored package, generated discovery views

Use the package README as the authored lesson and metadata owner. It names the package's stable ID, scope, subject, techniques, purpose, usable source/section, parent-supplied interfaces, limitations and provenance. Focused lesson headings support small fittings, variants and selected children. Keep measured reports and native visual evidence as separate artifacts, linked from the README. Do not copy their full contents into metadata.

Generate the local catalog/search index and optional galleries from those packages. Preserve existing `examples` and `details` callers through generated projections while migrating them: their old distinction is a compatibility view, not two authored copies of the same lesson. Family filters become explicit mappings to independent metadata, rather than discovering every `*-atlas/catalog.json` as a category. Do not infer default eligibility by recursively scanning everything under `examples/`.

Default search covers admitted construction/tutorial content and current agent guides/reference. Inspiration, diagnostics, archive and research need explicit scopes. A partial construction study may be returned when relevant, but its missing supports and actual check coverage must be visible in the excerpt. A family label is neither a construction technique nor a validation profile. No-match stays no-match.

An alias record maps `(legacy family, legacy key)` to a canonical package and optional lesson/section. The ledger resolves **138 unique existing catalog aliases**, including **27 retired entries**. Old short keys stay valid within their existing command namespace. Ambiguous unqualified names must request a namespace or return alternatives; never select the first similarly named directory. Aliases do not override hold/inspiration/export restrictions.

Examples:

| Existing lookup | Canonical destination | Behavior |
|---|---|---|
| `technic:mounted-frame-named`, `technic:service-platform` | `examples/mounted-service-frame/` | One lesson and named plan; preserve old numeric-contract fixtures as history/compatibility inputs |
| `reference:classic-truck-cab` | `examples/6594-tractor-unit/` | Correct whole-vehicle description; retain legacy key |
| `reference:rounded-cockpit-shell` | `examples/10212-rounded-side-covers/` | Return paired body covers, with parent context |
| `reference:spacecraft-wheel-module` | `examples/5980-buggy-chassis/` | Return separate buggy chassis; no spacecraft-landing claim |
| `reference:classical-arch-bay`, `reference:arcade-bay` | `examples/classical-arch-bay/` | One package, distinct source-study and adjustable-recipe lessons |
| `spaceship:b-wing` | `examples/75050-b-wing/` | Keep distinct from `examples/b-wing-6208/` |
| `building:conservatory` | `examples/glasshouse-walls/` | Explicitly resolve to a reduced wall-shell selection; state that the former whole scene is retired |
| `vehicle:grand-tourer` | Archived source and retirement reason | Excluded from recommendations; never silently substitute another vehicle |

Halcyon remains directly addressable. It loses automatic insertion, the `default: true` designation and mandatory SNOT policy. An explicit request for Halcyon can still export it after the normal package checks.

## Runtime and generator changes

| Current consumer | Required implementation change | Concrete acceptance |
|---|---|---|
| `ldraw_tools/examples.py`, CLI `examples` parser | Replace atlas globbing and building default with generated package discovery; preserve explicit old family filters and bounded result shape | An unfiltered query can find boombox and mounted flex; a vehicle query does not return architectural motifs because of the default family |
| `ldraw_tools/spaceships.py` | Remove injected Halcyon/default-construction instructions; resolve explicit keys through aliases | Starfighter, freighter and capital-ship briefs do not all require the same example or technique |
| `ldraw_tools/cli.py` mechanism export branch | Replace fallback into `examples/mechanism-atlas` with canonical resolver; keep explicit directory exports | Old six mechanism keys and the moved imported-study directories reach their intended package; unsafe/ambiguous paths fail |
| `ldraw_tools/manuals.py` and `reference_catalog.py` | Read the authoritative lesson fields while preserving source/BOM/visual freshness gates and confined output paths | Missing context, stale source or review, failing source checks or mismatched BOM still prevents normal reusable export |
| Existing per-atlas catalog/gallery generators | Generate compatibility catalogs from package metadata; stop maintaining multiple lesson summaries | No duplicate results from examples/details or colour variants; retired entries do not reappear after regeneration |
| Per-package `generate.py` shims and shared `workshop`, `technic_recipes`, `reference_recipes`, `vehicles`, `architecture` helpers | Keep useful geometry helpers; fix relative root assumptions and shims that currently call a parent atlas generator | Exported editable plans work from a new output directory; generators reproduce the selected source or report an intentional reviewed change |
| `ldraw_tools/discovery.py` and new KB index integration | Keep raw corpus discovery distinct from curated KB admission; local retrieval works without network; optional reranking cannot silently broaden eligibility | Unavailable Jev does not block KB search; an empty curated search does not fall back to held/raw scenes |
| `ldraw_tools/vehicle_review.py` | Separate current recipe-specific part checks from general subject checks; preserve measured wheel/part relationships | An-225 does not fail general aircraft classification merely for omitting courier-jet pieces; an incompatible claimed courier recipe still fails |

Preserve existing output protection and `--force` semantics, diagnostics and meaningful exit behavior. Determine any new CLI options during implementation against the parser and tests. Do not introduce a second authoring format, model parser, renderer or geometry solver.

The existing manual exporter requires every image named by its manual to have an opened-image review. Preserve that gate for existing manuals. A minimal native xray evidence bundle can be a separate supported package-evidence form; do not fake a complete manual review or pad the image list to satisfy the old exporter. For a retained source-step manual, retain its actual reviewed pages.

## Content-preserving moves and evidence

Keep MPD FILE names, transforms and dependency names stable during a pure package relocation. Copy source attribution/licences and extraction manifests; do not reconstruct unchanged imports as thousands of Python placement calls. Preserve historical hashed reports byte-for-byte. A relocation record can map original paths and digests to new paths without pretending that a check was rerun. Update mutable README links, generator paths and replay recipes separately; keep the original recipe/manifest when needed to explain the old artifact hashes.

For many-to-one packages, place source variants and existing evidence under distinct subdirectories. Never overwrite two `source.mpd`, `scene.plan.json` or `manual.json` files with one another. Consolidate prose and search entries, not distinct geometry or provenance. Preserve independent FILE namespaces; shared definitions or explicit namespaced extraction handle eventual model composition.

Pure path/prose changes require dependency/link/export checks, not a new visual campaign. Changed geometry, source selection, reconstruction or lost provenance requires the relevant new checks and opened isolated/actual-parent views. Shared dependencies changing invalidate every affected model. Existing static review does not become motion or strength evidence through relocation.

### Origin-hash discrepancies found during this ledger

For **21 reference-atlas entries**, the card/extraction manifest's recorded upstream source hash differs from the current source corpus. The **frozen package artifacts checked against those cards all still match**, including extracted geometry and previews. These are distinct identities: the old extraction is not the current upstream model.

Keep the recorded original hash and frozen extraction. Do not update the hash to the current corpus and claim an unchanged extraction. Migration can preserve the reviewed frozen package; any fresh extraction or replacement of its parent/source context must reconcile that lineage, rerun affected checks and review the changed geometry. The JSON ledger lists every mismatch and each frozen-artifact comparison. This is not an instruction to rerender all 21 packages now. The current `reference_catalog.export_example` also rejects a card whose source identity differs from the current discovery index. Keep that export block until provenance is reconciled; frozen-artifact agreement is not permission to bypass the guard. These candidates remain conditional, not immediately export-ready.

## Exact promotion bundles from ignored output

| Candidate | Promote during implementation | Keep outside default retrieval |
|---|---|---|
| Boombox | `boombox.mpd`, `boombox.plan.json`, `generate.py`, brief; concise package README; scoped visual notes; source-matched `output/boombox-review` evidence and the reviewed child boards | Exploratory shortlists and chronological process report; preserve a report link if it explains a retained limitation |
| An-225 | MPD, plan, generator, README/brief corrected to audit findings; validation/BOM/profile reports, manifest, retained final review and child boards; the check helpers and exact inputs required to reproduce cited clearance/hinge claims | Iterations, broad research and shortlists; preserve cited original experiment evidence under history rather than deleting it |
| Pneumatic press | Named plan, generator path that emits it, named-review source/evidence, relevant upstream constraints and declared dependencies | Old compatibility variants stay available as historical fixtures but do not create duplicate lessons |
| Tutorials | Reviewed bridge MPD/plan, Python API example and shadow-snap plan in one package; synthesized flex examples with source/manifests in their separate basics package | No aesthetic-template or mounted-mechanism claim from tutorial smoke tests |

An output-to-example promotion must include executable dependencies. Merely copying the final MPD or a README that points to ignored files is incomplete. Rewrite absolute workspace paths where safe; preserve them as historical provenance where required. Do not copy secrets, caches or unrelated output directories. These bundles still need their normal reproducibility checks during implementation; no regeneration occurred while writing this plan.

## Selective extraction and holds

The selected Atlas frame/outrigger/boom become three lessons in `examples/atlas-crane-studies/`, each with the selected section's dependency closure and actual parent evidence. The original whole crane belongs in a dated archive destination distinct from the already existing archive. Do not copy all 774 current crane files into the curated excerpt package.

The glasshouse package contains the retained glazing shell and its actual dependencies; it does not advertise the old roof or whole-scene design. Cottage remains conditional on repairing its nested weak tree/bench as well as updating the standalone catalog. F40/B-wing parent sources can remain package provenance without turning every unselected section into an indexed lesson.

Titan, Goliath, Jaguar, Stadium, the whole Atlas and the full cathedral remain outside default construction recommendations. Their hold/archive reasons and the absence of new visual approval remain explicit. The raw LSynth corpus remains in place for optional family research; the constraint lab and turntable failure case move to diagnostic fixtures. Retain expected failures, not just successful examples.

## Implementation batches and validation

1. **Metadata, resolver and search scaffold.** Define the small package metadata contract and explicit scopes; implement generated views and aliases against existing locations first. Verify all 138 alias decisions and non-admission of all 27 retired keys. Keep the old path resolvers until the next batch can use the new ones.
2. **Documentation migration.** Apply the 103-source ledger; move historical verification, correct routing, update the 267 recorded incoming links and check anchors. Validate command examples against local help/schema. Do not run model trials at this stage.
3. **Move and consolidate unchanged packages.** Preserve source bytes, attributed dependency closures and existing reviewed images. Repair generators/export paths and compare rebuilt output/BOM where an executable path changed. Exercise manual, reference, spaceship and mechanism exports from a separate directory. Use existing relevant tests (`test_manuals`, `test_submodel_atlas`, `test_ferrari_reference`, `test_cat_reference`, `test_spaceships`, `test_technic_atlas`, `test_vehicles`) plus focused resolver/search regressions.
4. **Repair and promote conditional selections.** Rework cottage dependencies and selective extractions; package boombox/An-225 and mounted flex; reconcile any source refresh. Reinspect only affected geometry with global `ldraw-xray` and retain scoped failures. Held candidates can remain held; they do not block the lean corpus.
5. **Evaluate the actual overhaul.** Run the agreed Terra/Luna retrieval comparison, then three construction pilots, followed by the larger matrix only if pilots justify it. Preserve before/after snapshots, equal budgets, failures, image review and no-expert-rescue policy. Compare diverse unseen briefs, not copies of the promoted examples.

The planning inventories are complete for the stated sources and visual selections. Implementation remains unstarted. Exact source relocation, command compatibility and generation improvement will be demonstrated by those implementation checks and trials, not inferred from the plan.
