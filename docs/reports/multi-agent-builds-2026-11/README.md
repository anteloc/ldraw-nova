# Multi-agent LDraw builds: research record (2026-11-08 → 09)

This is a research line on branch `multi-agents`, kept unmerged on purpose. The question: how does delegating to subagents change the speed, quality and cost of building a large LDraw model, compared with a single high-end agent? The test subject is the same brief every time: "Linden Row House", an original 3-storey urban townhouse with a café, two apartments, a roof terrace and a street plot.

The full working folders, with MPDs, logs and every render, are local and gitignored: `output/urban-house/`, `output/urban-house-snot/` and `output/urban-house-run3/`. This folder keeps the reports, the reusable tooling and a few key images.

## Experiments

| | Setup | Result |
|---|---|---|
| [Run 1](run1-system/) | Opus orchestrator plus 5 in-process Haiku 5.5 module workers. System bricks; contracts say *what* to build. | About 43 min active, 1390 parts, 96.5 % in the main contact group. Integration round 1 found 12 issues (4 structural). 3 h 44 min quota stall. Visual score 3.6. |
| [Roof self-audit](roof-self-audit/) | A fresh Haiku splits the finished roof into 15 submodels, audits them and fixes what it finds. | 7 defects found, 6 fixed, in 22.7 min. Weak on taste. |
| [Run 2](run2-snot-contracts/) | SNOT façades. The contract fixes **49 named submodels**, checked per submodel by `contract_check.py`, with a verified SNOT kit. | 49/49 PASS, 0 structural findings at integration, visual 3.9 (the best). Cost was **unacceptable**: about 67 min, about 2.3 M worker-context tokens, 2 h 24 min quota stall. See [COST-ANALYSIS.md](run2-snot-contracts/COST-ANALYSIS.md). |
| [Run 3](run3-lean-pipeline/) | Deterministic storey core, 16 headless `claude -p` tasks with ~2 k-token briefs, scripted driver, automatic tickets, one Opus review. | Pass 1 was cheap ($0.99) but a mess, as the user judged. The quality pass added new visual checks, quality rules and Sonnet on 3 façade tasks. Final: **agents $1.96 measured**, against a solo-Opus estimate of $6.7–16; 0 build errors, 48/49 contract, no visual-check fails; visual about 3.5. |

Final images are in [images/](images/):
- runs 1, 2 and 3 final views: `run1-*`, `run2-*`, `run3-final-*`;
- run 3 before and after the quality pass: `run3-pass1-*` against `run3-final-*`.

## Main findings
1. **Naming submodels in the contract, plus a per-submodel checker, moves structural defects from integration to build time.** Run 2 had 0 structural findings at integration; run 1 had 4.
2. **Run 2's cost came from agent turns, not tools.** Builds take about 4 s, checks about 3 s, renders about 4 s, while worker contexts grew to about 450 k tokens. The breakdown:
   - **onboarding:** about 53 % of each worker's time;
   - **images:** 337 renders;
   - **build output:** builds print about 350 KB of JSON.

   Haiku 5.5 costs about 5× more per token above 100 k tokens of prompt, so the long contexts also cost more per token.
3. **Lean tasks met the cost goal but lost quality.** Small headless Haiku tasks with deterministic structure brought agent cost to about $1–2. With only a cheat-sheet and about 20 turns, though, Haiku builds structurally valid but crude designs.
4. **Structural checks are blind to appearance.** The builder's "0 errors" only covers curated rectangular overlaps. The `collision_review` warning means "look". Three checks catch most of what a human sees as a mess:
   - windows blocked from outside;
   - bare studs facing out of a façade;
   - deep oriented-bounds interpenetration.

   They are implemented in [`tooling/contract_check.py`](run3-lean-pipeline/tooling/contract_check.py).
5. **The human-facing Opus session became the largest cost item.** About $6 was estimated for supervision in a very long conversation. Run orchestration headless or from a fresh session, and review only the final close-ups. Always audit module close-ups before declaring success.
6. **Most integration defects in run 3 were orchestrator gaps, not worker errors:**
   - worker checks isolated from sibling tasks;
   - layout areas with no owner;
   - stale envelopes;
   - a "main group" bug in the checker.

   A placeholder preflight, with one stub part per task built together, would catch most of them.
7. **Examples drive both quality and variety.** Agents read short generator code and READMEs, not MPDs. See [agent-reading.md](agent-reading.md).

## Reusing the run-3 pipeline
The [`run3-lean-pipeline/tooling/`](run3-lean-pipeline/tooling/) folder is a copy of `output/urban-house-run3/` code. The scripts resolve paths relative to that location, so to rerun, copy them back there. The run-3 pipeline consists of:
- the storey core, `lib/storey_core.py`;
- the assembler, `lib/assemble.py`;
- brief and skeleton generation, `make_skeletons.py`;
- the quiet per-task check, `check.py`;
- the checker with visual checks, `contract_check.py`;
- the driver, `orchestrate.py`;
- the cost model, `cost_model.py`.

The run-3 README explains how to launch it. The Claude Code auto-mode classifier blocks an interactive session from spawning `claude -p` workers, so run `orchestrate.py` from a terminal.

## Open follow-ups
- Add short, verified, task-specific examples to the briefs: a sign, an awning, furniture, slim lamps.
- Run a placeholder preflight and use sibling-aware checks from the first round.
- Cap repair prompts below 100 k tokens.
- Run a real solo-Opus baseline, since the solo figures so far are only estimates.
