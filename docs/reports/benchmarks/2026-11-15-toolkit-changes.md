# Toolkit changes of 2026-11-15: measured effects

This record covers the implementation of the improvement plan on branch `fable-optimizations`. Tool-level numbers below compare the starting commit `c2068cf2` with the changed working tree, run on the same machine. **The agent benchmark has not been run yet**, so nothing here shows that agents now build better models; that is the next step.

## Agent benchmark: pending

Run from a terminal (a Claude Code session cannot launch headless workers):

```sh
.venv/bin/python bench/run.py --suite baseline --ref c2068cf2 --model haiku --model opus --repeats 2
.venv/bin/python bench/run.py --suite candidate --model haiku --model opus --repeats 2
.venv/bin/python bench/score.py sheets output/bench/baseline output/bench/candidate --out output/bench/blind
# fill output/bench/blind/rubric.json without opening key.json, then:
.venv/bin/python bench/score.py unblind output/bench/blind
.venv/bin/python bench/score.py table output/bench/baseline output/bench/candidate
```

Score the blind sheets with [the rubric](../../../bench/RUBRIC.md) before opening the table. The baseline revision predates `LDRAW_AGENT_TRACE`, so its tool-trace columns stay empty; compare it on transcript metrics (turns, tokens, images, cost) and model scores.

## What an agent reads and receives

| Measure | Before | After |
|---|---:|---:|
| Required reading before the first part (tokens, `bench/reading_cost.py`) | 9,006 | 2,899 |
| `build` stdout, airliner plan, 314 placements (bytes) | 930,010 | 2,373 |
| `build --quiet` stdout (bytes) | — | 224 |
| `part 3001` (bytes) | 44,847 | 1,126 |
| `part 87087` (bytes) | 8,819 | 661 |
| `knowledge search 'side stud bracket'` (bytes) | 9,452 | 2,254 |
| `examples 'steering rack'` (bytes) | 13,411 | 2,210 |
| `--help` (bytes) | 4,337 | 2,168 |

The complete reports remain available through `--report`, `--full` and the review bundle. The `docs/agent` corpus grew from about 66,700 to 77,500 tokens. The growth is on-demand material: cards, the generated SNOT interface table and the generated command reference.

## Time

| Operation, airliner plan | Before | After |
|---|---:|---:|
| `build` (seconds) | 7.6 | 7.8 |
| `review` with three views (seconds) | 11.6–12.2 | 10.0 |
| LeoCAD render of three views and BOM alone (seconds) | 5.2 | 2.2 |
| `review` rerun with unchanged inputs (seconds) | full review | 1.1 |
| `knowledge search` (seconds) | 0.26 | 0.32–0.37 |

The appearance checks cost about 1 second on a cold part cache and about 0.2 seconds warm; parallel rendering more than pays for them in `review`.

## Placement without arithmetic

`on: {to, face, stud, socket}` and `orient` reproduce hand-derived SNOT placements. The parrot head's sideways jumper and rear plate, and Halcyon's two flank modules seated on side studs inside the hull module, build byte-identical MPD output; the cat's 45° ear matches to 1e-8 (tests in `tests/test_placement.py`). The same mode seats reviewed Technic pins and axles by port name (`on: {to, hole, pin}`), checked against the Technic fit rules, and `under` hangs parts by their studs from sockets above. Nine recipes in `examples/recipes/` use only seats (stud, hanging and Technic). All nine pass review with matching BOMs, the Technic frame passes `technic check` with eight pin joints, and each preview was opened and checked.

## Checks that see what people see

New warnings on models built before this change:

| Model | Deep overlaps | Bare side studs | Obstructed glass |
|---|---:|---:|---:|
| Parrot (reviewed reference) | 0 | 0 | 0 |
| Cat (reviewed reference) | 0 | 0 | 0 |
| Halcyon | 3 | 12 | 0 |
| Airliner (output/airliner-boarding) | 6 | 4 | 8 |
| Copper Lane | 2 | 0 | 2 |
| Linden Row run 2 | 5 | 16 | 1 |
| Linden Row run 3 (final) | 0 | 16 | 4 |

Confirmed by inspecting coordinates:

- The airliner's 1 x 2 deck plate sits inside a 1 x 8 plate at the same height; the old body check skipped it because `3023` has no profile.
- Halcyon's windscreen rim shares space with two tiles.
- The Linden Row bare studs are the sideways flowers and the uncovered headlight-brick studs that the run audits criticised.

An earlier box-based version of the overlap check flagged 86 airliner pairs (hulls containing interiors) and 17 parrot pairs. The vertex test removed those; the remaining flags are listed above.

## Tests

The full suite passed with 731 tests before the change and 798 after it, with no failures. One existing review test changed meaning: an unchanged rerun now reuses its bundle instead of demanding `--force`. New test files: `test_appearance.py`, `test_placement.py`, `test_report.py`, `test_knowledge_ranking.py`, `test_cards.py`, `test_cli_reference.py`, `test_construction_recipes.py` and `test_bench.py`.
