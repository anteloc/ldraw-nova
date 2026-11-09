# Quality report — Linden Row House (subagent experiment)

Model revision: `review/model.mpd` sha256 `dd55d1d56b073290dd7deb74b2050ac4222ebacd5878fbc006f84109ee10ae1e` (same bytes as `linden-row.mpd` built from `scene.plan.json`).

## Measured checks (final, `review/`)

| Check | Result |
|---|---|
| Build / validation | `checks_passed: true`; 0 errors; remaining warnings `assembly.disconnected_evidence`, `coverage.collision_review` |
| Physical placements | 1390 (5 modules + helper submodels) |
| BOM: Python vs LeoCAD | match, 1389 = 1389, no differences |
| Contacts (`--contacts all`) | 4364 contacts; 48 groups; **main group 1338 / 1389 (96.3 %)** |
| Parts outside main group | 51, all analyzer blind spots or trivial: clipped glass panes (60608/3854/60797c04 ≈ 33), 1×1 round plates (stool seats, urn caps), slim lamp-head stacks on 2039 posts |
| Failed builds (whole process) | 0 of 42 worker builds; 0 orchestrator build errors |
| Cross-module collisions | none reported at any integration round |
| Bounds | X ±320, Z ±320 (inside the 32×32 plate), height 684 LDU |

## Defects found at integration, by round

| Round | Found by orchestrator | Fixed by |
|---|---|---|
| r1 (after phase B) | floating centre slab plates in floor2 + floor3 (storey below only provides a perimeter ring — a **contract gap of mine**); street props on studless tiles; weak café front; bay window a blank white box; lamps hiding the shopfront; tree canopy past plot edge; grey roof-deck edge band; floor3 blank sides | D1 (all five workers in parallel) |
| r2 | bay window still mostly white; **new regression**: H5 rebuilt lamps as heavy black columns; grey strip on roof sides; odd open back fence | D2 (H2, H4, H5) |
| r3 / final | `3023` alias part in street (orchestrator one-line fix) | Opus |

Every module passed its own isolated checks in phase B, yet 2 of 5 had real structural defects that only appeared in the composed scene (slabs over a perimeter-only ring, props on tiles). Workers' self-reports were accurate about what they had and had not checked.

## Visual rubric (orchestrator, 1–5; images: `review/previews/{home,front,back,top,bottom}.png`, `integration/final-cutaway/panels/02-*.png`)

| Criterion | Linden Row (subagents) | Maple Court suburban house (earlier single agent) |
|---|---|---|
| Silhouette | 4 — tall terrace block, stair-house + chimney + pergola break the roofline | 3 — simple gambrel block + garage box |
| Façade richness | 4 — shopfront, sign, striped awning, bay, balcony, dentilled parapet, quoins | 3 — shutters, portico |
| Cross-floor coherence | 3.5 — consistent palette and string courses; ground floor stone vs brick upper works; each floor's slab + ring shows as a brown/white band on sides/back | 4 — single hand, very uniform |
| Interior | 4 — café counter/tables, living room, bedroom, furnished roof terrace | 1 — not furnished |
| Street scene | 3.5 — lamps, trees, hydrants, bin, bench, café seating, alley, hedge, fenced garden | 2.5 — path, tree, mailbox |
| Rear / sides | 2.5 — plain brick, few windows | 3 |
| **Mean** | **3.6** | **2.8** |

Main weaknesses that remain: plain rear façade; ground-floor display glazing only 72 LDU tall (an awning-height constraint in my contract); stair-house is a plain grey box; trees are the stylized atlas pinwheel type; no bike rack.

## Process observations (subagents vs single agent)

- **Speed:** ≈114 worker-minutes of building ran in ≈30 min wall-clock (≈3.8× parallelism). The whole active process took ≈43 min for 1389 parts, about 2× the size of the earlier single-agent house, which has no timing record. Wall-clock was dominated by phase B (≈19 min). Each round-trip through the orchestrator cost ≈3 min.
- **Biggest risk:** shared quota. All five workers hit the 5-hour usage limit at the same moment (≈14 min in), which stalled the run for 3 h 48 min. Parallelism multiplies the burn rate.
- **Quality:** strong. Haiku workers followed the contracts precisely (footprints, anchors, h=160 interface, projection zones, palette). No cross-module collision occurred in any round, and no build failed. They used ldraw-xray well, including `--parent`, cutaways and isolated sub-tests, fixed what they saw, and wrote honest timing logs.
- **What workers could not see:** defects in the composed scene (support coming from another module) and aesthetic judgement across the whole model. One D1 fix (the lamps) satisfied the letter of the request but regressed visually. Orchestrator integration rounds were essential: 2 rounds found 12 distinct issues.
- **Contract design is the leverage point:** the floating-slab defect came from my storey contract, which specified a perimeter ring only. One sentence there ("slab plates must span between ring cells") would have saved most of D1.
- **Tokens:** each worker's context was ≈340–365 k tokens, mostly re-read docs and images. Five workers carry ≈1.75 M tokens of context, against roughly a single context for a solo agent. That trades cost for wall-clock time.

## Update 2026-11-08 19:45 — roof self-audit
The roof was re-audited by a fresh Haiku agent: split into 15 submodels, then 7 defects found and 6 fixed (see `roof-audit-eval/EVALUATION.md`). The audited roof replaced the original (old copy in `modules/roof.pre-audit/`). Final model: 1390 parts, sha256 `dd55d1d5…`, review passed, BOM 1390 = 1390, contacts main group 1341/1390. The roof now has no parts outside the main group.
