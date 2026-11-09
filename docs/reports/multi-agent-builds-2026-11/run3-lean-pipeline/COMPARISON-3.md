# Runs 1, 2 and 3 compared

The same Linden Row brief was built three times by an Opus orchestrator working with Haiku 5.5 agents:

| Run | Agent setup | Construction |
|---|---|---|
| 1 | 5 in-process module workers | System bricks |
| 2 | 5 workers, contract of 49 named submodels | SNOT |
| 3 | 16 short headless tasks, scripted driver, deterministic structure | SNOT, same 49-submodel contract |

## Cost and time

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Worker context at the end | 270–365 k | 450–470 k | 25–74 k (one repair reached 105 k) |
| Agent cost | not measured (about 1.75 M context tokens; Haiku mostly on the > 100 k tier) | not measured (about 2.3 M context tokens) | **$0.99 measured** |
| Orchestrator (Opus) | about 150 turns in a long session | about 150 turns | about 23 execution turns (about $3, estimate) |
| Active wall-clock | about 43 min | about 67 min | about 37 min of pipeline, plus about 25 min of my fixes |
| Quota stall | 3 h 44 min | 2 h 24 min | none |
| Solo-Opus estimate for the same work | — | — | $4.50 lower bound, $10.21 realistic |

## Quality

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Parts | 1390 | 1427 | 1517 |
| Build errors at the end | 0 | 0 | 0 |
| Contract checks | n/a | 49/49 | 48/51 (3 documented) |
| Main contact group | 96.5 % | 97.5 % | 97.6 % |
| SNOT parts | 0 | 205 | 162 |
| Integration round 1 findings | 12 (4 structural) | 9 (0 structural) | 219 overlaps, 20 contract FAILs. All came from setup gaps: worker checks were isolated, the layout had gaps, and two checker bugs. All were fixed by automatic tickets and 2 repair rounds. |
| Visual (orchestrator, 1–5) | 3.6 | 3.9 | about 3.7 |

## Lessons from run 3
1. **The cost goals were met, by about 10× against a realistic solo Opus.** Small headless Haiku tasks under 100 k tokens, deterministic structure and a scripted orchestrator did it. Measured spend was $0.99. The human-facing Opus session became the largest cost item.
2. **Isolating tasks costs integration.** Splitting a module into 2–4 parallel tasks created sibling collisions that no task could see. The fix was to have `check.py` build the sibling parts too. With that, plus automatic overlap tickets, two cheap repair rounds took the house from 219 errors to 0 for $0.36.
3. **Most defects were in my contracts, not in the workers' work.** Workers followed briefs literally. The defects came from:
   - layout gaps: who paves the alley; the parapet against the corner piers; lamp positions;
   - stale envelopes;
   - an interface mismatch: the base laid tiles where the garden expected studs;
   - a checker bug: "main group" picked the largest component, not the structure.

   A preflight that builds the whole module skeleton with *placeholder* parts for every task, run once before launch, would catch most of this.
4. **The Opus review was the most expensive single call:** $0.22, against $0.36 for all 16 repair calls together. Most tickets came from the deterministic checks. Opus is worth keeping for visual judgement, but with fewer images.

## What to change next time
- Run the orchestrator from a fresh, short session, or fully headless, so it doesn't carry a long context.
- Add a placeholder preflight: one stub part per task, built together, checked for overlaps and envelope gaps.
- Make sibling-aware checks the default from the first task round, and give layout zones explicit owners in one shared map.
- Cap any repair prompt at 90 k, so no request crosses the 100 k tier.
