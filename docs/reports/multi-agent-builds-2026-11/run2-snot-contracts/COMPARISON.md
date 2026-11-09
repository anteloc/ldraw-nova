# Run 1 vs run 2 — does naming the submodels in the contract help?

Both runs build the same Linden Row brief (footprint, palette, storeys, features), with one Opus orchestrator and five parallel Haiku 5.5 workers, one module each.

- **Run 1** (`output/urban-house/`): System bricks only. The contract described *what* to build.
- **Run 2** (`output/urban-house-snot/`): SNOT façades. The contract also fixed **49 named submodels**: each with an envelope, build frame, interfaces and inspection duties, plus a per-submodel checker (`contract_check.py`) and a verified SNOT kit.

## Numbers

| | Run 1 | Run 2 |
|---|---|---|
| Orchestrator setup before launch | 2.6 min | 7.3 min (kit + checker + 49-row contract) |
| Phase B wall-clock (parallel build) | ≈19 min | 34.7 min |
| Worker-minutes (all phases) | ≈114 | ≈159 |
| Parallelism | ≈3.8× | ≈3.5× |
| Total active time | ≈43 min (+ 22.7 min roof self-audit afterwards) | ≈67 min (+ ≈10 min planning) |
| Worker tokens (final contexts) | ≈1.75 M (+0.41 M roof audit) | ≈2.30 M |
| Builds (failed) | 42 (0) | ≈51 (5 overlap refusals, each fixed next build) |
| Parts | 1390 | 1427 |
| Sideways (SNOT) parts | 0 | 205 (14.4 %) |
| Main contact group | 96.5 % | 97.5 % (rest = glass only) |
| Per-submodel contract checks | n/a | 49 / 49 PASS |
| Defects logged by workers before delivery | none tabulated | 45 rows, 21 fixed during the build |
| **Integration round 1 findings** | **12, incl. 4 structural** (floating slab centres in two storeys, props on tiles, floating strips) | **9, 0 structural**: 3 worker-catchable but unreported, 4 self-reported but left open, 1 aesthetic, 1 my contract |
| Repair rounds | 2 (5 workers, then 3) | 1 (4 workers) + a 1-line kerb follow-up |
| Contract gaps exposed (mine) | 1 (perimeter-only ring under the slabs), found only at integration | 3 (envelopes ignoring SNOT stud protrusion, recessed headlight studs, kerb cap height), **found by workers during the build** via the checker |
| Rate-limit stalls (5-hour quota) | 1 (3 h 44 min) | 1 (2 h 24 min) |

## Visual rubric (orchestrator, 1–5)
Images: run 1 `output/urban-house/review/previews/*`; run 2 `review/previews/*` and `integration/r2/whole/*`.

| | Run 1 | Run 2 |
|---|---|---|
| Silhouette | 4 | 4 |
| Façade richness | 4 | 4.5: SNOT rusticated piers, two-tone cornice band, pilasters, dentils, word-block sign, window boxes, corbelled bay |
| Cross-floor coherence | 3.5 | 4 |
| Interior | 4 | 4 |
| Street | 3.5 | 4: SNOT kerb face, capped kerb, garden wall + gate, plaque, shed |
| Rear / sides | 2.5 | 3: rear lintels, surrounds, lamps; sides still plain |
| **Mean** | **3.6** | **3.9** |

## What the experiment shows
1. **Structural defects moved from integration to build time.** In run 1 the orchestrator found 4 structural defect classes at integration. In run 2 it found none. The per-submodel checker made "is every part of *this* named unit connected, inside its box, and seated on its declared studs?" a question each worker answered for every submodel, every iteration.
2. **The contract itself got debugged early.** Three envelope rules of mine were wrong for SNOT: studs protrude, headlight studs are recessed, a kerb cap needs h32. Workers hit each one through a precise FAIL within minutes and reported it, instead of the gap surfacing as a defect in the finished house.
3. **What still reached integration was visual, not structural.** Of the 9 findings:
   - 3 were missed visual issues inside the worker's own submodels (bare rear studs, red wall seen through glass ×2);
   - 4 were found by the worker but left open because the constraints seemed hard (flat awning, dotted sign, cornice stubs, kerb studs);
   - all were fixed in one repair round once the orchestrator insisted or relaxed a rule.

   Naming submodels makes workers *see* local design problems. It does not make them insist on fixing them.
4. **The orchestrator also makes visual mistakes.** In run 2 I diagnosed floor3's red panes as an unopened wall; it was the back wall seen through the glass, and the worker corrected me. In the roof audit, 4 of my 8 suspicions came from the perspective top view. A cheap checker beats an eyeball for geometry claims, at both levels.
5. **Cost.** Run 2 took about 1.6× the active time of run 1, and about 30 % more worker tokens. Some of that is SNOT, which is harder than brick stacking. Some is the per-submodel inspection loop. The roof self-audit after run 1 suggests that adding audits afterwards costs about as much and finds fewer problems than building them into the contract.

## Recommendation
For multi-agent LDraw builds, put the submodel tree into the contract, with envelopes, interfaces and minimum contact counts, and give workers an automatic per-submodel checker. Validate the contract's numeric rules against a verified kit before launch: all three of run 2's contract gaps would have shown up in a 5-minute kit test of a full wall, slab and kerb. Keep one orchestrator integration round for visual judgement. Tell workers that design findings must be fixed or escalated, never just recorded.

## Cost
Why this run was slow and expensive, and how to fix it with subagents: [COST-ANALYSIS.md](COST-ANALYSIS.md).
