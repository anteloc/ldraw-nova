# Timing log — Linden Row House (subagent experiment)

Orchestrator: Claude Opus 5.5. Workers: Claude Haiku 5.5 (general-purpose subagents).
All times local, 2026-11-08.

| Time | Who | Event |
|---|---|---|
| 14:05:47 | Opus | t0 — request received, plan mode: exploration (repo, prior suburban-house run, architecture.py, ldraw-xray) |
| 14:07:20 | Opus | asked user about control run → "subagents only" |
| 14:08:30 | Opus | plan approved; Phase A setup starts |
| 14:10:00 | Opus | common.py (namespacing export) + stub 2-storey scene: builds, pitch 160 verified; xray --parent render verified |
| 14:10:58 | Opus | CONTRACTS.md + conventions.md written |
| 14:11:48 | Opus | Phase B: launched H1–H5 (Haiku 5.5) in parallel, background |
| 14:11:06 | Opus | scene generator + integrate.sh written while workers run; then idle |
| ~14:25–14:30 | H1–H5 | **all five workers terminated: HTTP 429 "5-hour limit" (Haiku), resets 17:10**. Last logged worker lines 14:23–14:25 (each had 1 build done) |
| 14:30–18:14 | — | **stall: rate-limit + waiting for user** (excluded from active time; ~3h44m) |
| 18:14:26 | Opus | user said "continue"; resuming workers via SendMessage |
| 18:14:49 | Opus | resumed H1–H5; early integration r0 on current snapshots |
| 18:15:01 | H5 | **street done** (2 builds, 0 failed, 280 physical parts). Resume leg: 22 s, 4 tool uses; cumulative subagent tokens 240,694. Active work ≈14:11:42–14:25 + 18:14–18:15 ≈ 14.5 min |
| 18:15:28 | Opus | r0 integration: build OK (1397 parts), whole renders inspected; notes in integration/notes.md |
| 18:16:35 | H4 | **roof done** (2 builds, 0 failed, 345 placements). Resume leg 121 s, 18 tool uses; cumulative tokens 265,699. Active ≈14:11:42–14:25 + 18:14:47–18:16:35 ≈ 15 min |
| 18:17:54 | H1 | **ground done** (4 builds, 0 failed, 257 parts). Resume leg 200 s, 28 tool uses; cumulative tokens 291,324. Active ≈14:11:43–14:26 + 18:14–18:17:54 ≈ 18 min |
| 18:18:11 | H3 | **floor3 done** (5 builds, 0 failed checks, 1 connectivity regression fixed, 208 placements). Resume leg 225 s, 22 tool uses; cumulative tokens 275,240. Active ≈14:11:43–14:26 + 18:14–18:18:11 ≈ 18 min |
| 18:18:46 | H2 | **floor2 done** (4 builds, 0 failed, 257 placements). Resume leg 248 s, 29 tool uses; cumulative tokens 273,805. Active ≈14:11:46–14:26 + 18:14:49–18:18:46 ≈ 18 min |
| 18:18:46 | — | **Phase B complete** (all 5 modules delivered) |
| 18:18:56 | Opus | Phase C integration r1 starts |
| 18:22:16 | Opus | r1 integration done (1 min scripted + ~3 min analysis/visual); launching repair round D1 to H1–H5 |
| 18:23:06 | Opus | D1 repair messages sent to H1–H5 (parallel) |
| 18:27:04 | H1 | D1 done (18:23:07–18:27:04, 4 min; 2 builds, 0 failed) [248 s, 18 tool uses, cumulative tokens 346,622]: 4 display windows (72 LDU, constrained by awning height), yellow sign, sloped 3298 awning |
| 18:27:47 | H4 | D1 done (18:23:06–18:27:47, 4.7 min; 3 builds, 0 failed) [289 s, 26 tool uses, cumulative tokens 328,481]: white deck edge, parapet pediment/dentils/urns, bushes on studs |
| 18:28:13 | H2 | D1 done (18:23:06–18:28:13, 5.1 min; 2 builds, 0 failed) [315 s, 26 tool uses, cumulative tokens 337,845]: 4×3027 slab spanning Z -8..8, glazed bay (3×4035 + sides), slope cap |
| 18:29:10 | H3 | D1 done (18:23:33–18:29:10, 5.6 min; 5 builds (1 over cap), 0 failed) [371 s, 25 tool uses, cumulative tokens 354,307]: 3027 slab + balcony deck integrated into slab, side + 2nd rear windows |
| 18:29:13 | H5 | D1 done (18:23:07–18:29:13, 6.1 min; 4 builds, 0 failed) [374 s, 21 tool uses, cumulative tokens 312,259]: stud-seated props, lamps to X±10, trees in plot |
| 18:29:13 | — | **Phase D1 complete** (wall-clock 18:22:16→18:29:13 = 7.0 min; sum of worker legs 4.1+4.8+5.2+6.2+6.2 = 26.5 min → 3.8× parallel speedup) |
| 18:29:25 | Opus | integration r2 starts |
| 18:32:00 | Opus | r2 integration done (~3 min); D2 messages to H2, H4, H5 |
| 18:32:38 | H4 | D2 done (18:31:35–18:32:38, 1.1 min; 1 build, 0 failed) [79 s, 12 tool uses, cumulative tokens 345,772]: side/back perimeter pads white |
| 18:33:12 | H5 | D2 done (18:31:56–18:33:12, 1.3 min; 1 build, 0 failed) [113 s, 10 tool uses, cumulative tokens 339,602]: slim fluted lamps restored (seated), closed back fence + shed |
| 18:33:35 | H2 | D2 done (18:31:41–18:33:35, 1.9 min; 2 builds, 0 failed) [137 s, 11 tool uses, cumulative tokens 363,550]: bay front = two window4 units, brick/tan solids |
| 18:33:35 | — | **Phase D2 complete** (wall-clock 18:32:00→18:33:35 = 1.6 min) |
| 18:33:46 | Opus | Phase E: final regen + integration r3 + whole-model review starts |
| 18:36:19 | Opus | orchestrator fix: street 3023→3023b alias (5 parts); rebuild + final review: checks_passed, BOM match |
| 18:37:27 | Opus | final renders inspected (review/previews home/front/back/top/bottom + final cutaway); writing quality.md / README |

## Summary (active time excludes the 14:26→18:14 rate-limit/user-wait stall)

| Phase | Wall-clock | Who | Notes |
|---|---|---|---|
| Plan (explore + question + plan) | 14:05:47→14:08:30 · 2.7 min | Opus | |
| A. Setup (common.py, stub pitch test, contracts, conventions) | 14:08:30→14:11:06 · 2.6 min | Opus | |
| B. Parallel module build | 14:11:06→~14:26 + 18:14:26→18:18:46 · ≈19 min active | H1–H5 | all 5 killed by HTTP 429 after ~14 min, resumed 3 h 48 min later |
| C. Integration r1 | 18:18:46→18:22:16 · 3.5 min | Opus | scripted pass 1 min, analysis + visual 2.5 min |
| D1. Parallel repair | 18:22:16→18:29:13 · 7.0 min | H1–H5 | |
| Integration r2 | 18:29:13→18:32:00 · 2.8 min | Opus | |
| D2. Parallel repair (3 workers) | 18:32:00→18:33:35 · 1.6 min | H2, H4, H5 | |
| E. Final review + reports | 18:33:35→18:37:46 · 4.2 min | Opus | incl. 1-line alias fix by orchestrator |
| **Total active** | **≈ 43 min** | | elapsed incl. stall: 4 h 32 min |

### Per worker (Haiku 5.5)

| Worker | Module | Phase B active | D1 | D2 | Builds (failed) | Final parts | Tokens (last reported context total) |
|---|---|---|---|---|---|---|---|
| H1 | ground | ≈18 min | 4.0 min | — | 4+2 (0) | 242 | 346,622 |
| H2 | floor2 | ≈18 min | 5.1 min | 1.9 min | 4+2+2 (0) | 236 | 363,550 |
| H3 | floor3 | ≈18 min | 5.6 min | — | 5+5 (0) | 197 | 354,307 |
| H4 | roof | ≈15 min | 4.7 min | 1.1 min | 2+3+1 (0) | ~381 | 345,772 |
| H5 | street | ≈14.5 min | 6.1 min | 1.3 min | 2+4+1 (0) | 282 | 339,602 |
| **Σ** | | **≈84 min** | **25.5 min** | **4.3 min** | **42 (0 failed)** | **1389** | |

- Worker-minutes ≈ 114 over ≈ 30 min of parallel wall-clock (B+D1+D2) → **≈3.8× parallelism**.
- Orchestrator (Opus) active ≈ 18 min: plan/setup 5.3 min, integration/analysis/visual 3 × ~3 min, final ≈ 4 min; the rest of the 43 min it idled while workers ran.
- Coordination overhead: 2 integration rounds + 2 repair rounds = 4 hand-offs, each costing ~3 min of orchestrator analysis; contracts/conventions took ~2.5 min to write up front.
| 18:37:46 | Opus | **done** — README, quality.md, timing.md written |
