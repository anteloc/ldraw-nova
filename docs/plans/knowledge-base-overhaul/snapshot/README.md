# Knowledge-base visual audit progress

Planning evidence only. Repository content has not been refactored. All keep/improve decisions remain conditional on the specified metadata corrections, retained check scopes and fresh review of later edits.

| Collection | Candidate entries reviewed | Model/route sections or cutaways reviewed | Findings |
|---|---:|---:|---|
| Submodel atlas | 30 | 96 | [Findings](submodel-findings.md) |
| Reference atlas + recipes | 29 | 29 | [Findings](reference-findings.md) |
| Mechanism + imported Technic studies | 12 | 15 | [Findings](mechanical-findings.md) |
| Structural + workshop starters | 7 | 18 | [Findings](structural-findings.md) |
| Selected vehicles + fittings | 9 | 11 | [Findings](vehicle-findings.md) |
| Selected buildings + details | 16 | 33 | [Findings](building-findings.md) |
| Parrot, cat and Halcyon | 3 | 30 | [Findings](snot-findings.md) |
| Selected F40 studies | 5 | 5 | [Findings](f40-findings.md) |
| 6208 B-wing studies + nested band | 13 | 14 | [Findings](bwing6208-findings.md) |
| Spaceship atlas | 8 | 48 | [Findings](spaceship-findings.md) |
| Standalone scenes, fittings and tutorials | 9 | 89 | [Findings](standalone-findings.md) |
| Atlas selections and turntable diagnostic | 5 | 6 | [Findings](remaining-standalone-findings.md) |
| Legacy LSynth scenes | 26 | 26 | [Findings](lsynth-legacy-findings.md) |
| Constraint lab cases | 8 | 9 | [Findings](constraint-lab-findings.md) |
| Mounted press + minimal flex tutorials | 4 | 11 | [Findings](mounted-flex-findings.md) |
| Replacement candidates + held Titan root | 3 | 25 | [Findings](replacement-findings.md) |

Coverage so far: **187 candidate entries and 465 sections/selections**. The latest completed batch adds seven candidates and 36 sections, including the held Titan root (not its children). Standalone animal head/leg copies reuse verified identical section geometry and are not counted again.

These counts include duplicates, colour variants, synthesized routes and candidates now downgraded. They are inspection coverage, not a count of unique recommended lessons. Nested model sections are reviewed both alone and in actual parents; repeated instances appear in parent views. Embedded library/mesh DAT primitives are retained dependencies, not independently curated assemblies.

## Selection changes from visual evidence

- Correct rounded-cockpit-shell to paired rounded body-side covers; correct spacecraft-wheel-module to small vehicle chassis. Their original parent scenes refute the old identities.
- Retain imported mechanical selections as construction studies with missing supports/interfaces prominent in search excerpts. The suspension source is two separated axle assemblies, not a complete chassis.
- Consolidate byte-identical service-platform and named mounted-frame examples.
- Limit motorcycle/launch/jet examples to purpose-made-part composition; no broad default template.
- Replace the whole conservatory candidate with its repeated-glazing wall-shell lesson; do not recommend the thick roof or sparse whole-scene composition.
- Correct battlement square/rectangle and skyline three-towers/two-towers-plus-pavilion metadata.
- Apply previously recorded submodel corrections across every generated description, including tree panel counts, Buckbeak head closure, helmet mouth support and Tantive child roles.

- Retain Halcyon as one core-and-skin lesson; remove the universal spaceship default and label its canopy-only section accurately.
- Distinguish actual child assemblies, unreferenced F40 callouts and B-wing visibility cutaways in retrieval.
- Preserve the 6208 LDCad band as a dependency with deferred mechanism verification; do not classify it as an LSynth recipe.

- Correct UCS Y-wing child roles from parent evidence: outriggers, engine body, nozzle, rear cage, forward housing, dorsal cannon and plaque supports. Keep the complete package opt-in inspiration only.
- Correct spaceship cockpit glazing and nacelle-armour descriptions; expose contacts-skipped scope for all eight atlas entries.

## Current visual gate and next planning work

The currently selected examples in this audit have completed their visual pass, subject to the individual findings. Workshop routes reuse earlier complete, source-matched evidence. No additional candidate is silently admitted by closing this batch.

Stadium remains on source-reconciliation hold; Atlas whole-model/unselected research children, Titan, Goliath and Jaguar remain outside the proposed construction corpus. Their held/unreviewed children do not have visual approval. Any later admission or geometry change reopens the corresponding visual gate.

[Consolidated target structure and migration sequence](target-structure.md) incorporates the visual decisions. The [documentation migration ledger](document-migration-ledger.md) now assigns all 103 tracked documentation/evidence files, proposes 21 agent documents and records 267 incoming Markdown links. The [example-package ledger](example-migration-ledger.md) now covers all 187 audited entries, 138 legacy catalog aliases (27 retired), and 5,089 tracked example/LSynth files. The [catalog/export compatibility plan](catalog-export-migration.md) completes the planning handoff. Implementation and after-overhaul agent trials have not started.

No new agent generation trials were run. Existing Terra/Luna retrieval baselines remain retrieval evidence only. Future evaluation uses the agreed staged retrieval, pilot and expanded generation protocol.

## Review efficiency

Use one clear view per distinct selected assembly plus its parent context, reuse source-matched evidence for identical geometry, and add views only for unresolved questions. Triage before rendering. Preserve the requirement to visually review every retained/improved model and submodel. Use the globally installed `ldraw-xray` CLI and its native boards/mosaics. Read `../ldraw-xray/README.md` and `../ldraw-xray/AGENTS.md` before first use; both have been read in this session.

Latest completed batch: 60 fresh native xray panels across 30 jobs (press 14, boombox 10, An-225 36). All were opened via their native mosaics/single view. Existing press, boombox, minimal-flex and Titan previews were reused with matching hashes. No new synthesis, reproduction or agent generation trials. This continuation only opened the remaining aircraft boards and recorded decisions; it rendered no additional panels.

## Planning handoff — 2026-11-03

The documentation, example and compatibility ledgers are complete for the stated inventory. Shared atlas orchestration is explicitly tracked separately from curated package content; no file is implicitly admitted by a recursive move. Start implementation with the resolver/metadata scaffold, then documentation, unchanged package moves, conditional repairs/promotions, and staged Terra/Luna evaluation.

A provenance check found 21 reference-atlas upstream hashes no longer matching the current corpus; all frozen package artifacts checked against their cards still match. Preserve those exact reviewed snapshots and original lineage. Fresh extraction/context replacement requires reconciliation and affected checks; do not silently refresh source hashes. Details and per-file comparisons are in the example ledger and compatibility plan.

No models were rendered, synthesized or changed in this planning continuation.
