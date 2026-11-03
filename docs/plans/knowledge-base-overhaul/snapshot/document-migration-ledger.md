# Documentation migration ledger

Planning only, 2026-11-02. **103 tracked sources mapped:** instructions, 30 agent Markdown documents, one agent evidence resource, and 71 report/evidence files. All source hashes are recorded in [the complete ledger](document-migration-ledger.json). No source has been moved or rewritten.

The proposed agent documentation has **21 files**, plus the short entry point. This reduces duplicate ownership, not just file count. Search should retrieve headings/sections with parent context rather than loading an entire guide. Proposed paths are destinations, not currently available files.

## Entry and agent documents

| Existing source | Action and proposed destination | Required editorial work |
|---|---|---|
| `instructions.md` | **rewrite in place**<br/>`instructions.md` | Keep setup, brief → retrieve → build → review → repair → deliver, essential coordinates and evidence rules. Link task guides and current CLI. Remove family default, copied hose schema, universal Halcyon/SNOT mandate, historical permission rules and project-local xray invocation. Target roughly 400–600 words; make it useful before adding extra rules. |
| `docs/agent/advanced-mechanisms.md` | **merge**<br/>`docs/agent/guides/mechanisms.md` | Keep rigidity versus MPD hierarchy, keyed/bearing roles, carrier frames, finite engagement and non-rest tests. Separate construction-only from requested animation. Link the gear-drive package and upstream Mecha contract; do not copy an entire sibling API into Nova. |
| `docs/agent/authoring.md` | **split**<br/>`docs/agent/guides/build-model.md`<br/>`docs/agent/reference/plans.md`<br/>`docs/agent/guides/flex.md`<br/>`docs/agent/reference/flex.md`<br/>`docs/agent/reference/technic.md` | Lead the build guide with named authoring. Put precise path expansion, structure fields, inline flex transforms and scope rules in their single reference owners. Preserve numeric-contract and external-asset compatibility; avoid repeating the full pneumatic example in every guide. |
| `docs/agent/build-manuals.md` | **merge**<br/>`docs/agent/guides/review-models.md`<br/>`docs/agent/guides/find-references.md`<br/>`docs/agent/reference/cli.md` | Keep actual source steps, final unterminated group, empty-step handling, no-render/overview distinctions and evidence freshness. Replace per-atlas promotion instructions with one package admission process. Use global ldraw-xray; source-step manuals are for construction questions, not mandatory duplicate render sets. |
| `docs/agent/complex-models.md` | **split**<br/>`docs/agent/guides/compose-modules.md`<br/>`docs/agent/reference/plans.md`<br/>`docs/agent/guides/find-references.md`<br/>`docs/reports/bookshop-source-audit.md` | Keep detail/module/scene review and parent-supplied interfaces. Move includes/anchors/repeat math to plan reference. Move Bookshop inventory, exact duplicate and rounded-transform history to a dated report with its resource. Keep Copper Lane as one linked worked example; use subject-neutral module guidance. |
| `docs/agent/flex-constraints.md` | **split**<br/>`docs/agent/guides/flex.md`<br/>`docs/agent/reference/flex.md` | Use this as the main flex procedure. Preserve actual-fitting endpoints, outward versus travel directions, wheel ownership, shared coordinate frames, fixed-length multi-pose limits and actual synthesized measurements. Put exact helper/flag semantics in reference. Link the lab as diagnostics, raw LSynth as optional research, press/chain as mounted examples. |
| `docs/agent/flexible-parts.md` | **merge**<br/>`docs/agent/guides/flex.md`<br/>`docs/agent/reference/flex.md`<br/>`docs/agent/reference/cli.md` | Merge the duplicate workflow into flex. Keep posed-item versus rigid-link BOM boundaries, atomic failed-build behavior, recorded compatibility repairs and generated-asset portability. Keep installed-version restrictions in reference. Replace the raw 26-scene corpus as the primary rigid-construction starting point with admitted mounted packages. |
| `docs/agent/geometry.md` | **split**<br/>`docs/agent/guides/place-parts.md`<br/>`docs/agent/reference/ldraw.md`<br/>`docs/agent/reference/connections.md`<br/>`docs/agent/reference/validation.md` | Keep inspect-before-place, upper-body stacking height, local frames, seam bonding and actual mating surfaces. Centralize dimensions in LDraw reference and report meanings/limits in validation. Do not turn source-case offsets into universal dimensions. |
| `docs/agent/ldraw-reference.md` | **retain and relocate**<br/>`docs/agent/reference/ldraw.md` | Keep type records, transforms, colours 16/24, MPD boundaries, attribution and distinction between legal primitive transforms and rigid physical placements. Merge the specification page map as a source appendix; link the supplied PDF without copying it. |
| `docs/agent/mechanisms.md` | **merge**<br/>`docs/agent/guides/mechanisms.md`<br/>`docs/agent/reference/cli.md` | Retain construction workflow, parent-supplied pinions/supports and intended-operation versus tested-motion distinction. Merge advanced workflow as an explicit animation branch. Remove historical authorization language as a current rule; keep fixed-support checks scoped. |
| `docs/agent/plans.md` | **split**<br/>`docs/agent/guides/build-model.md`<br/>`docs/agent/reference/plans.md` | Keep one minimal plan tutorial in build-model. Make reference/plans the owner of placement modes, includes/assets, anchors, repeats, symbols, schema links and Python builder semantics. Cross-link flex/technic field references. Preserve build_plan versus build_checked distinction and no second parser rule. |
| `docs/agent/reference-discovery.md` | **split**<br/>`docs/agent/guides/find-references.md`<br/>`docs/agent/reference/cli.md` | Lead with local curated knowledge search, then exact source/parts discovery. Jev is optional reranking with explicit availability/failure handling, not a network prerequisite to reading the KB. Preserve stable identities, raw/corrected text, source hashes, parent transforms, variant grouping, attribution and copy-versus-adapt decisions. Document defaults as current behavior until code changes land. |
| `docs/agent/snapping.md` | **split**<br/>`docs/agent/guides/place-parts.md`<br/>`docs/agent/reference/connections.md`<br/>`docs/agent/reference/plans.md` | Merge the operational snap loop with placement. Keep shadow precedence, feature/occurrence identity, world/local frames, path cloning, adapter provenance and collision status meanings in connections reference. Put plan snap fields in plans. Do not assume global xray inherits Nova shadow configuration. |
| `docs/agent/snot.md` | **retain and relocate**<br/>`docs/agent/guides/snot.md` | Keep real attachment first, origin = target - R*socket, off-grid single-stud details and articulation boundaries. Link audited parrot/cat/boombox/F40/B-wing lessons by scope. Remove universal Halcyon/spaceship mandates and copy-heavy coordinates that belong in their example package. |
| `docs/agent/spaceships.md` | **merge**<br/>`docs/agent/guides/design-models.md` | Keep silhouettes, local surface grids, wing/root support, engine/cockpit proportions and underside/display mounts as a spacecraft section. Remove mandatory SNOT, automatic Halcyon export and atlas-wide recommendation. Link Halcyon only for core/skin construction; whole spacecraft inspiration stays opt-in. |
| `docs/agent/specification-map.md` | **merge**<br/>`docs/agent/reference/ldraw.md` | Preserve the 171-page snapshot identity, 1-based PDF page convention, content ranges and spec-search cache behavior. Update relative links after relocation. Do not promote dated snapshot statements to claims about the latest external standard. |
| `docs/agent/submodel-inspection.md` | **merge**<br/>`docs/agent/guides/review-models.md`<br/>`docs/agent/guides/find-references.md`<br/>`docs/agent/reference/cli.md` | Use globally installed ldraw-xray and its mandatory upstream README/AGENTS guidance. Remove project-wrapper/default-shadow assumptions. Keep synthetic-copy/overlay limits and scale/framing cautions. Replace fixed 0/45/90 sweeps with task-appropriate valid poses; no motion claim from posed renders. Replace selections.json plus five duplicated note fields with the common package contract and generated index. |
| `docs/agent/technic-catalog.md` | **split**<br/>`docs/agent/reference/technic.md`<br/>`docs/agent/reference/cli.md` | Keep aliases, variant transforms, geometry fingerprints, provenance and unknown motion profiles. Move the dated 5,643-reference snapshot count to history or generate it on demand. Catalog membership must not imply validated seating or animation support. |
| `docs/agent/technic-design.md` | **merge**<br/>`docs/agent/guides/technic.md`<br/>`docs/agent/guides/design-models.md` | Merge actual support/mount design into Technic and general composition into design-models. Retain the functional pattern routing table. Keep hypothetical rover/crane/stand prompts explicitly unbuilt; do not index them as executable recipes. |
| `docs/agent/technic-patterns/engines.md` | **retain and relocate**<br/>`docs/agent/guides/mechanism-patterns/engines.md` | Keep separate focused pattern page. Preserve W16 three-crankshaft correction, source-local phase and cam-lift assumptions; link source-specific measurements to audited package evidence. Do not turn cutaways into freestanding engine claims. |
| `docs/agent/technic-patterns/industrial-assemblies.md` | **merge**<br/>`docs/agent/guides/flex.md`<br/>`docs/agent/guides/technic.md` | Distill carrier bearings/retention, accessible controls, cable terminations and coherent structure. Replace broad raw-corpus recommendations with per-family audited limits. Keep missing hardware and optical/electrical distinctions explicit; no promotion of incomplete LSynth scenes. |
| `docs/agent/technic-patterns/lifts-and-linkages.md` | **retain and relocate**<br/>`docs/agent/guides/mechanism-patterns/lifts-and-linkages.md` | Keep in-plane versus spatial dimensions, moving-parent pivots and surrounding clearance. Retain unresolved 90-degree indexing, detent/return and prescribed timing qualifications. Source-specific values stay attached to the studied construction. |
| `docs/agent/technic-patterns/source-reuse.md` | **merge**<br/>`docs/agent/guides/find-references.md` | Generalize its strongest lessons beyond Technic: names are hypotheses, selection changes frames/indices, source support can be incomplete, and observed versus inferred evidence stays together. Move example-specific historical counts to package/report links rather than duplicating them. |
| `docs/agent/technic-patterns/suspension-steering.md` | **retain and relocate**<br/>`docs/agent/guides/mechanism-patterns/suspension-steering.md` | Keep separate motions and one occurrence per shared physical hub. Preserve parent-supplied rack pinion, missing boundary mounts and the fact that separate steering/suspension rigs do not verify a combined axle. No load or full chassis claim from partial studies. |
| `docs/agent/technic-patterns/transmissions.md` | **retain and relocate**<br/>`docs/agent/guides/mechanism-patterns/transmissions.md` | Keep role-based pattern sections and finite engagement/phase/support limits. Preserve unresolved Mustang output connection and selector source offsets. Link exact source geometry and distinguish catalog part names from shaft arrangement. |
| `docs/agent/technic.md` | **split**<br/>`docs/agent/guides/technic.md`<br/>`docs/agent/reference/technic.md` | Keep seating, occupied spans, retaining stops, assembly order and body mounts in the procedure. Move registry/contract fields, fingerprints and solver boundaries to reference. Remove stage authorization gates; moving assemblies use joint scope and explicit motion workflow when requested. |
| `docs/agent/tooling.md` | **retain and relocate**<br/>`docs/agent/reference/cli.md` | Reorganize by task and keep setup, exits, report artifacts, current flags, explicit scopes and informational-command exceptions. Replace long duplicate design tutorials with guide links. Document global xray with upstream help/docs and explicit environment. Add proposed KB search only when implemented; do not advertise fictional flags. |
| `docs/agent/validation.md` | **split**<br/>`docs/agent/reference/validation.md`<br/>`docs/agent/guides/review-models.md` | Keep diagnostic/coverage table authoritative in reference; put the repair loop in review-models. Preserve unsupported-versus-invalid, strict warnings, contacts-skipped, heuristic groups, material-overlap limits and whole-model review requirements. Remove historical blanket contacts-none authorization; scope checks by task and state what was skipped. |
| `docs/agent/vehicles.md` | **split**<br/>`docs/agent/guides/design-models.md`<br/>`docs/agent/reference/connections.md` | Keep stance, shape-defining parts, wheel wells, glazing, bodylines and boat/aircraft/motorcycle review questions in design sections. Preserve classic/touring measured wheel contracts in connections. Rename bounded part-family checks as recipe-specific evidence; different designs and mixed System/Technic builds must not fail solely for differing from atlas parts. |
| `docs/agent/verification.md` | **archive and extract**<br/>`docs/reports/tooling-verification-history.md`<br/>`docs/reports/bookshop-source-audit.md` | Remove this historical result aggregator from agent instructions/default retrieval. Preserve dates, counts, hashes, coverage and links in reports. Extract the Bookshop audit with its JSON; current behavior belongs in reference and current evidence in example packages, not old test totals. |
| `docs/agent/visual-design.md` | **split**<br/>`docs/agent/guides/design-models.md`<br/>`docs/agent/reference/cli.md`<br/>`docs/agent/reference/plans.md` | Keep general identity/silhouette/palette/scale principles; move building-specific motifs under an explicit architecture section alongside vehicles/spacecraft/animals/objects. Correct flower-planter to the audited tree/plinth description. Put catalog flags and symbol grammar in references; details link to their single package owner. Local retrieval first, optional Jev, no aesthetic score from numeric checks. |
| `docs/agent/resources/bookshop-study.json` | **relocate evidence**<br/>`docs/reports/resources/bookshop-study.json` | Preserve bytes/hash and connect to bookshop-source-audit; do not embed this source-specific inventory in default retrieval. Update the new report links and existing historical backlinks. |

## Reports: preserve history, extract narrowly

Reports and evidence remain outside default construction retrieval. Extract a durable lesson only if its destination does not already teach it; link the report for provenance. Historical permissions, prices, test totals and measured timings do not become current instructions.

| Report | Lesson destination | Action |
|---|---|---|
| `docs/reports/authoring-simplification.md` | `docs/agent/guides/build-model.md`, `docs/agent/guides/flex.md`, `docs/agent/guides/technic.md` | Named paths, first-failed-prerequisite repair and corrected-starter lesson. Preserve the original six trials and separate corrected-starter rerun; no claim of Terra/Luna effectiveness from these historical agents. |
| `docs/reports/jev-assembly-discovery-assessment.md` | `docs/agent/guides/find-references.md` | Inspect source classification, distinct constructions, scale and parent supply after ranking; semantic rank is not admission. Keep historical query results and measured limits in the report. |
| `docs/reports/jev-submodel-discovery-evaluation.md` | `docs/agent/guides/find-references.md` | Separate model/submodel/part roles and stable source lookup. Retain proposed versus observed improvements and historical costs; do not treat retrospective judgments as a controlled generation benchmark. |
| `docs/reports/lsynth-constraints.md` | `docs/agent/guides/flex.md`, `docs/agent/reference/flex.md` | Measure synthesized geometry, inspect fittings/context, preserve the deliberately failing lab case and unproven stock/motion properties. |
| `docs/reports/lsynth-integration.md` | `docs/agent/reference/flex.md` | Keep physical BOM boundaries and recorded legacy compatibility repairs. Old sweep counts remain historical and are superseded for selection by the visual audit. |
| `docs/reports/mechanism-workflow.md` | `docs/agent/guides/mechanisms.md` | Use keyed/bearing roles and off-rest/asymmetric checks for requested motion. Preserve the original gear-drive evidence and sampled-check limits; do not rerun Blender for a documentation move. |
| `docs/reports/reference-discovery-implementation.md` | `docs/agent/guides/find-references.md`, `docs/agent/reference/cli.md` | Stable IDs, attributed extraction, resumable evidence and explicit FTS behavior. Do not recopy already documented command details. |
| `docs/reports/spaceship-support-implementation.md` | `docs/agent/guides/review-models.md`, `docs/agent/guides/design-models.md` | Source-step handling and inspiration-versus-reuse distinction. Preserve unresolved source errors and old image/test counts in history. |
| `docs/reports/technic-flex-simplification.md` | `docs/agent/reference/plans.md`, `docs/agent/reference/flex.md`, `docs/agent/reference/technic.md` | Automatic assets/contracts, cache invalidation and atomic publication; retain fixture-specific timings as dated local measurements, not promised speedups. |
| `docs/reports/technic-knowledge-transfer.md` | `docs/agent/guides/mechanisms.md`, `docs/agent/guides/find-references.md` | Preserve source identities, corrections, missing mounts and observation qualifications. Most lessons already exist in pattern pages: link them rather than extracting duplicate prose. |
| `docs/reports/technic-stage1-implementation.md` | `docs/agent/guides/technic.md`, `docs/agent/reference/technic.md` | Retain registry and finite seating/retention boundaries. Historical stage-2 permission gate remains only as dated history, not current agent policy. |
| `docs/reports/technic-stage2-implementation.md` | `docs/agent/guides/mechanisms.md` | Construction studies and intended-operation evidence are distinct from tested motion. The old deferral is historical scope, not a prohibition on present animation tasks. |
| `docs/reports/technic-structure-readiness.md` | `docs/agent/guides/technic.md` | Extract only still-applicable spacing, connector-role and support lessons absent from the guide. Pre-implementation capability gaps remain historical. |
| `docs/reports/typesafe-jev-ldraw-assessment.md` | None; historical provenance/research only | Keep the dated research assessment and proposed use cases outside default retrieval. Do not import old vendor pricing, availability, speculative savings or unimplemented product features as current guidance. |
| `docs/reports/typesafe-jev-reading-audit.md` | None; historical provenance/research only | Keep the historical reading manifest with its companion JSON and source-cache links. It is provenance, not construction knowledge; no vendor-document mirror or new fetch is needed for this migration. |
| `docs/reports/workflow-simplification.md` | `docs/agent/guides/build-model.md`, `docs/agent/guides/review-models.md`, `docs/agent/reference/cli.md` | Retain the single review loop, skipped-stage semantics and atomic-output behavior. Preserve historical compatibility/test counts and Alder Court scope without promoting its geometry as a new exemplar. |

## Every companion and trial record

The following files each have their own source hash and retain-in-place decision in the JSON ledger. Preserve each bundle as a unit; no new visual acceptance is implied for its historical generated models.

| File | Role |
|---|---|
| `docs/reports/authoring-trials/baseline-complete-machine/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-complete-machine/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-complete-machine/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/baseline-complete-machine/repair-log.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-complete-machine/result.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-complete-machine/visual-notes.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/repair-log.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/result.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-frame-drive/visual-review.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/repair-log.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/result.json` | Trial evidence |
| `docs/reports/authoring-trials/baseline-pneumatic-passage/visual-review.md` | Trial evidence |
| `docs/reports/authoring-trials/baseline-toolkit.json` | Trial evidence |
| `docs/reports/authoring-trials/briefs.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-complete-machine/NOTES.md` | Trial evidence |
| `docs/reports/authoring-trials/candidate-complete-machine/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-complete-machine/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-complete-machine/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/candidate-complete-machine/result.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-frame-drive/NOTES.md` | Trial evidence |
| `docs/reports/authoring-trials/candidate-frame-drive/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-frame-drive/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-frame-drive/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/candidate-frame-drive/result.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/NOTES.md` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/repair-log.md` | Trial evidence |
| `docs/reports/authoring-trials/candidate-pneumatic-passage/result.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-toolkit.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-v2-complete-machine/artifacts.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-v2-complete-machine/audit.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-v2-complete-machine/commands.jsonl` | Trial evidence |
| `docs/reports/authoring-trials/candidate-v2-complete-machine/result.json` | Trial evidence |
| `docs/reports/authoring-trials/candidate-v2-toolkit.json` | Trial evidence |
| `docs/reports/authoring-trials/results.json` | Trial evidence |
| `docs/reports/jev-assembly-discovery-evidence.json` | Report evidence or reproduction aid |
| `docs/reports/reference-discovery-implementation.json` | Report evidence or reproduction aid |
| `docs/reports/spaceship-support-evidence.json` | Report evidence or reproduction aid |
| `docs/reports/technic-knowledge-transfer.json` | Report evidence or reproduction aid |
| `docs/reports/technic-stage1-evidence.json` | Report evidence or reproduction aid |
| `docs/reports/technic-stage2-evidence.json` | Report evidence or reproduction aid |
| `docs/reports/technic-structure-evidence.json` | Report evidence or reproduction aid |
| `docs/reports/technic-structure-probe.py` | Report evidence or reproduction aid |
| `docs/reports/typesafe-jev-costs.csv` | Report evidence or reproduction aid |
| `docs/reports/typesafe-jev-costs.json` | Report evidence or reproduction aid |
| `docs/reports/typesafe-jev-costs.py` | Report evidence or reproduction aid |
| `docs/reports/typesafe-jev-reading-audit.json` | Report evidence or reproduction aid |

## Link and contract migration

267 inline Markdown references to these sources were found across tracked Markdown. The JSON records source file, line, target and fragment for each. This is a rewrite inventory, not a declaration that all existing anchors are valid.

After the destination text exists, rewrite inbound paths and heading anchors, including example READMEs and preserved reports. For moved relative links, compute against the new directory; do not merely replace the basename. Use temporary redirect stubs only for externally used old paths, exclude stubs from search, and keep each claim authored in one place. No permanent duplicate guide is required.

Update runtime/test consumers in the same migration as their docs: CLI family default in `ldraw_tools/cli.py`; hardcoded atlas routing in `ldraw_tools/examples.py`; Halcyon insertion/default policy in `ldraw_tools/spaceships.py`; bounded family-part checks in `ldraw_tools/vehicle_review.py`; filters and corpus scope in `ldraw_tools/discovery.py`; per-atlas generators and tests. Preserve explicit recipe checks while separating them from general subject classification.

Before publication, check exact command examples against the local parser/help/schema; exercise changed retrieval/default behavior and the affected example export/build paths. A document-only move does not justify rerendering unchanged models or rerunning all historical experiments. Do not present proposed KB-search flags before implementation.

For `ldraw-xray`, use the global executable, inspect its actual environment, and link upstream usage documentation. The existing Nova wrapper remains a compatibility implementation detail until separately changed; this plan does not assume it configures the global CLI.

## Remaining planning boundary

This closes the per-document mapping. The individual visual findings already determine candidate dispositions. The [example-package ledger](example-migration-ledger.md) and [catalog/export compatibility plan](catalog-export-migration.md) now complete that consolidation. No new render sweep or agent trial was needed to prepare the handoff.
