# Benchmark

Toolkit changes are accepted or reverted on these numbers. Earlier attempts measured the tooling (test counts, byte equality, word counts) and never the models agents produced, so they could not tell whether a change helped.

## What a run is

One fresh headless agent, one frozen brief from [briefs.json](briefs.json), one model tier, a time and cost budget, and an isolated workspace: a git worktree of the toolkit revision under test, so earlier models in `output/` are invisible. The agent receives the harness prompt plus the brief and must deliver its plan or generator, `model.mpd` and a review bundle.

## Protocol

1. **Baseline first.** Run round 1 (four briefs) with two tiers and two repeats on the current revision before changing anything:

   ```sh
   .venv/bin/python bench/run.py --suite baseline --ref HEAD --model haiku --model opus --repeats 2
   ```

   Run it from a terminal. A session inside Claude Code cannot launch headless workers. Use `--jobs 1`: parallel heavy runs exhausted the usage quota in earlier experiments.
2. **Change, then rerun the same suite** with a new `--suite` name. Without `--ref`, the workspace is HEAD plus the uncommitted working tree.
3. **Score the visuals blind** with [RUBRIC.md](RUBRIC.md).
4. **Compare**:

   ```sh
   .venv/bin/python bench/score.py table output/bench/baseline output/bench/candidate
   ```

Each suite's workspace is a git worktree in the system temp directory with links to `.venv`, `bin/`, the parts library and `.cache`. Remove it with `.venv/bin/python bench/run.py --suite NAME --clean`, which unlinks the shared resources before removing the worktree; results under `output/bench/` stay.

The two repeats of a brief define its noise band. A change that does not move its target metric beyond that band is reverted, even if every test passes. Round 2 (`--round 2`) adds the Technic steering and pneumatic briefs.

## What is measured

| Group | Metrics | Source |
|---|---|---|
| Model | build passes, placements, distinct parts, main connected group share, deep overlaps, bare sideways studs, obstructed glass | delivered MPD, scored with the current toolkit |
| Brief | size, connectivity, required parts, extents, proportions, wheels on one ground plane | `checks` in briefs.json |
| Authoring | share of absolute `at` placements, hand-written matrices, connector placements | delivered plans |
| Cost | turns, prompt tokens, largest context, images opened, tool calls, USD, minutes | stream-json transcript |
| Tools | commands, tool seconds, stdout bytes, failures | `LDRAW_AGENT_TRACE`; revisions before 2026-11-15 (including the `c2068cf2` baseline) do not write it |
| Visual | five rubric dimensions | human, blind |

`bench/reading_cost.py` measures the entry document and the reading it requires before the first part.
