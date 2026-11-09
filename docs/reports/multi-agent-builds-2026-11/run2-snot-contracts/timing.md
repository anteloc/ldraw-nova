# Timing log — Linden Row House, run 2 (SNOT + submodel contracts)

Orchestrator: Claude Opus 5.5. Workers: Claude Haiku 5.5. All times local, 2026-11-08.

| Time | Who | Event |
|---|---|---|
| 19:5x | Opus | plan mode: SNOT guide, Halcyon helpers, atlas SNOT entries; plan approved |
| 19:57:48 | Opus | Phase A starts: inspected 30414/11211/87087/4070/plates connectors |
| 19:59 | Opus | common.py SNOT helpers (Ry, panel_R, seat, side_studs, add_ldu) |
| 20:00 | Opus | kit/snot_kit.py: K1 side-stud wall, K2 seated 4x4 panel = 8 contacts, K3 4070+98138 = 1 contact; xray checked |
| 20:01 | Opus | contract_check.py written; verified PASS interface on kit, FAIL on 2 broken copies (moved panel → 0 contacts, floating, envelope) |
| 20:03 | Opus | contracts_src.py → contracts.json + CONTRACTS.md: 49 submodels across 5 modules; conventions.md; scene generate.py, integrate.sh |
| 20:05:03 | Opus | stub smoke test (scene + harness modes) OK; envelope stud tolerance fixed |
| 20:05:43 | Opus | Phase B: launching H1–H5 (Haiku 5.5) |
| 20:28:01 | H1 | **ground done** (20:05:46–20:28:01, 22.3 min; [1359 s, 59 tool uses, 363,424 tokens] 8 builds, 1 failed; 235 placements; 8/9 contract PASS; 11 self-found defects, 3 fixed, 3 open, 4 accepted) |
| 20:28:40 | Opus | contract gap #1 (mine): side-stud studs protrude 4 LDU past wall face → walls/parapet envelopes widened to z ±8.3; ground now re-checked |
| 20:30:41 | H5 | **street done** (20:05:46–20:30:41, 24.9 min; [1511 s, 92 tool uses, 405,472 tokens] 4+2 builds, 1 failed; 319 parts; 9/9 contract PASS; 6 self-found defects, all fixed; 4 visual limits open). Its folder cleanup was blocked by the safety check — left for the user |
| 20:30:50 | H2 | **floor2 done** (20:05:47–20:30:50, 25.1 min; 4+2 builds, 1 failed; 187 placements; 7/8 → 8/8 after gap #2; 10 defect rows, 3 visual limits open) [1512 s, 81 tool uses, 408,124 tokens] |
| 20:31:15 | Opus | contract gap #2 (mine): window-box envelope ignored the recessed 4070 stud → z max -7.5; floor2 re-checked |
| 20:38:24 | H4 | **roof done** (20:05:47–20:38:24, 32.6 min; [1977 s, 88 tool uses, 451,986 tokens] 5+1 builds, 1 failed; 366 parts; 13/13 contract PASS; 4 self-found defects, all fixed). Deviation: authored all submodels in one pass, then checked per submodel. Hit contract gap #1 independently (worked around with 4070) |
| 20:39:30 | Opus | H3 stuck investigating a stale walls FAIL (pre-widening); told it 10/10 PASS now. Phase C integration r1 starts |
| 20:39:42 | H3 | **floor3 done** (20:05:46–20:39:42, 33.9 min; 4 builds +1 failed rerun; 214 placements; 10/10 PASS; 14 defect rows: 5 fixed, 1 resolved by contract, several open (balcony cantilever, cornice gaps, single-leaf door)) [2049 s, 94 tool uses, 417,086 tokens] |
| 20:39:42 | — | **Phase B complete** (wall-clock 20:05:03→20:39:42 = 34.7 min) |
| 20:41:30 | Opus | r1 scripted integration done (1:47): build OK 1379 parts, **contract 49/49 PASS in scene**, main group 1339/1379 (all 40 outside = glass blind spots), 0 cross-module overlap errors |
| 20:42:58 | Opus | r1 visual review + classification done (9 findings: 0 structural; 3 worker-catchable unreported, 4 self-reported-but-open, 1 aesthetic, 1 my contract). D1 repairs → H1, H2, H3, H5 |
| 20:43:02 | Opus | D1 messages sent to H1, H2, H3, H5 (parallel) |
| 20:46 | H3 | D1 done (~20:42–20:46, ~4 min; 2 builds, 0 failed) [196 s, 18 tool uses, cumulative 460,126 tokens]: cornice now continuous band (16 contacts); windows: openings already existed — red was the room's BACK wall seen through the glass (my I3 diagnosis partly wrong); furniture added behind windows |
| 20:46:35 | H2 | D1 done (20:44:21–20:46:35, 2.2 min; 2 builds, 0 failed) [221 s, 11 tool uses, cumulative 450,514 tokens]: wall behind bay opened (it really was closed — I2 correct), corbels added, plants behind glass; scene 49/49 PASS |
| 20:48:28 | H5 | D1 done (20:43:05–20:48:28, 5.4 min; 2 builds, 0 failed) [337 s, 25 tool uses, cumulative 463,672 tokens]: brick garden wall + gate, trees to kerb line, lamps to X±6; kerb tiles blocked by envelope |
| 20:48:45 | Opus | contract gap #3 (mine): kerb envelope too low for side-stud brick + cap tile → h 0..32; asked H5 to finish I7 |
| ~20:50 | H1, H5 | **HTTP 429 '5-hour limit' (Haiku)** — H1 mid-D1 (awning slope test), H5 mid-I7 (harness 9/9 done, scene-check pending); resets 23:10 |
| 20:50–23:14 | — | **stall: rate limit + waiting for user** (~2 h 24 min, excluded from active time) |
| 23:14:23 | Opus | user said continue; resuming H1 and H5 |
| 23:14:39 | H5 | I7 done (resume leg <1 min; 1 harness + 1 scene build) [12 s + pre-stall leg, cumulative 469,517 tokens]: kerb cap tiles 2431, street 9/9 PASS |
| 23:15:59 | H1 | D1 done (20:43:05–~20:50 + 23:14:37–23:15:59 ≈ 8.5 min active; 3 builds, 0 failed) [92 s resume leg, cumulative 470,822 tokens]: rear studs removed, scalloped 35464 awning seated on side studs, word-block sign; 9/9 PASS |
| 23:15:59 | — | **Phase D1 complete** (active wall-clock ≈ 20:42→20:50 + 23:14→23:16 ≈ 10 min) |
| 23:16:08 | Opus | integration r2 starts |
| 23:18:02 | Opus | r2 done (3 min): 49/49, 97.5 % main group, all I1–I9 resolved/accepted → no D2. Phase E starts |
| 23:20:32 | Opus | final review passed (1427 = LeoCAD 1427), stud maps ×4 + cutaway inspected; writing COMPARISON/quality/README |

## Summary (active time excludes the 20:50→23:14 rate-limit/user-wait stall)

| Phase | Wall-clock | Who |
|---|---|---|
| Plan (research SNOT guide, Halcyon, atlas) | ≈10 min | Opus |
| A. Setup: SNOT helpers, verified kit, contract_check + tests, 49-submodel contracts | 19:57:48→20:05:03 · 7.3 min | Opus |
| B. Parallel module build (per-submodel loop + pre-delivery audit) | 20:05:03→20:39:42 · 34.7 min | H1–H5 |
| C. Integration r1 (scripted 1:47 + visual/classification) | 20:39:42→20:47 · ≈7.5 min | Opus |
| D1. Parallel repair (4 workers) | 20:42→20:50 + 23:14→23:16 · ≈10 min | H1, H2, H3, H5 |
| Integration r2 | 23:16→23:19 · 3 min | Opus |
| E. Final review + reports | 23:19→23:20:45 · ≈5 min | Opus |
| **Total active** | **≈ 77 min** (≈ 67 min excluding planning) | elapsed incl. stall ≈ 3 h 35 min |

### Per worker (Haiku 5.5)
| Worker | Module | Phase B | D1 | Builds (failed) | contract | Self-logged defect rows | Tokens (final context) |
|---|---|---|---|---|---|---|---|
| H1 | ground | 22.3 min | ≈8.5 min | 8+3 (1) | 9/9 | 11 (3 fixed in B) | 470,822 |
| H2 | floor2 | 25.1 min | 2.2 min | 6+2 (1) | 8/8 | 10 (3 fixed in B) | 450,514 |
| H3 | floor3 | 33.9 min | ≈4 min | 5+2 (1) | 10/10 | 14 (5 fixed in B) | 460,126 |
| H4 | roof | 32.6 min | — | 6 (1) | 13/13 | 4 (4 fixed in B) | 451,986 |
| H5 | street | 24.9 min | 5.4+0.3 min | 6+4 (1) | 9/9 | 6 (6 fixed in B) | 469,517 |
| **Σ** | | **138.8 min** | **≈20.5 min** | **≈51 (5)** | **49/49** | **45 rows, 21 fixed before delivery** | **≈2.30 M** |

- Worker-minutes ≈ 159 over ≈ 45 min parallel wall-clock (B + D1) → **≈3.5× parallelism**.
- All 5 failed builds were body-overlap refusals caught by the builder and fixed by the worker in the next build.
| 23:20:45 | Opus | **done** — COMPARISON.md, quality.md, README.md written |
