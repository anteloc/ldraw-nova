# Run 3 integration notes (orchestrator)

## First terminal run (user, 01:17–01:34)
- 16 worker tasks: all finished, $0.37 total, 245 turns, max prompt 73.7 k (< 100 k Haiku tier), 85–376 s each.
- Integration FAILED to produce linden-row.mpd: `ldraw-agent build` refuses to write on body-overlap errors (219).
  The Opus review therefore got no images and returned 0 tickets ($0.03 wasted); no repairs ran.
- Root causes, all in the orchestrator setup (not worker mistakes):
  1. check.py built each task in isolation, so collisions with sibling tasks of the same module were invisible
     (street-base vs street-alley 88, floor2-facade vs bay/window-box ~100, roof corner piers vs parapet 6, ...).
  2. Layout gaps in my briefs: who paves the alley; front parapet vs corner piers; lamps at X ±6 in front of the shop.
  3. Stale roof envelopes (run-2 deck height 16 vs run-3 deck 8).
  4. contract_check took the largest component as "main group": a big floating facade passed its harness check.
  5. Glass check false positive on the horizontal skylight.

## Fixes (orchestrator, deterministic, 01:40–02:05)
- Integration builds through the Python API (MPD always written; errors to errors.json).
- auto_tickets(): overlap pairs → the submodel with the larger envelope; contract FAILs; part-file errors;
  exposed wall-mount studs → the task that owns that mount; glass/visual rows → owner.
- check.py builds all existing parts of the module (siblings included), reports only the task's own errors.
- Layout briefs fixed (alley, parapet/piers, slim lamps at X ±10); roof envelopes h ≥ 8; core-anchored main group;
  horizontal glass skipped.
- Dry integration r1c (no LLM): 35/55 contract PASS, 219 overlaps, 38 auto tickets over 12 tasks.

## Quality pass preparation (after the user's verdict "the end result is a mess")
- AUDIT.md: module close-ups confirmed blocked floor-2 windows (trans-clear 2x2 plates over them), bare studs on facades,
  chaotic awning, parts inside parts, crude interiors/props. My earlier "clean" verdict was wrong.
- New automatic checks (contract_check module/scene mode): window blocked from outside (accumulated coverage, studded
  trans plates count as blockers), bare studs facing out of a facade, deep oriented-bounds interpenetration (frame/glass/leaf
  excluded). On the pass-1 model they report exactly the defects seen by eye (19 FAIL rows).
- Briefs: QUALITY RULES block; shopfront must fit h8..104 (proven window4 layout); slim lamps; per-task models
  (Sonnet 5.5 for T02 sign/awning, T05 floor-2 facade, T11 roof front; Haiku for the rest) with --max-budget-usd caps
  (0.60 / 0.12 per task, 0.25 / 0.06 per repair, 0.60 Opus review).
- check.py now prints each task's own VISUAL rows; Opus review gets 1024 px home-view close-ups of every module.
