# Maintaining ldraw-nova

This page is for changing the toolkit or the knowledge base. Agents that build models start at [AGENTS.md](../../AGENTS.md).

## Measure changes to what agents produce

A change to tools, documents or lessons is accepted on [benchmark](../../bench/README.md) results, not on passing tests alone. Run the baseline before the change and the same suite after it; revert changes that do not move their target metric beyond the noise of the repeats. `bench/reading_cost.py` measures the reading the entry document requires; keep it under 6,000 tokens.

## Change the tooling

Work in `ldraw_tools/` with the related tests in `tests/`:

```sh
.venv/bin/python -m pytest tests/test_<area>.py -q
.venv/bin/python -m pytest -q          # broad changes; about 12 minutes
```

`./setup.sh` installs test dependencies, including LSynth for flex tests. Keep CLI help, the [cards](../agent/cards/) and the `docs/agent/` references aligned with behaviour. After changing arguments, regenerate the command reference (`tests/test_cli_reference.py` fails while it is stale):

```sh
.venv/bin/python scripts/cli_reference.py
```

The card examples are built by `tests/test_cards.py`, and `tests/test_knowledge_ranking.py` holds golden queries that must keep an acceptable answer in the top three. `build` and `review` print summaries (`ldraw_tools/report.py`); complete reports go to `--report` files and review bundles. Regenerate the SNOT interface table after connector or library changes:

```sh
.venv/bin/python scripts/snot_interfaces.py
```

Model generation is validated by its own review artifacts and the benchmark, not by rerunning the software test suite.

### Technic data

The Technic tables are generated from the installed library, its LDCad shadow data and the official sets in `data/models-annotated`. After a library or shadow update, or a change to the port rules in `ldraw_tools/technic_ports.py`, regenerate them in this order:

```sh
.venv/bin/python scripts/technic_ports.py                 # derived ports -> ldraw_tools/data/technic-ports.json
.venv/bin/python scripts/technic_corpus.py ports --apply  # seat rates in official sets; records usage and withheld ports
.venv/bin/python scripts/technic_ports.py                 # applies the withheld ports
.venv/bin/python scripts/technic_gears.py                 # gear facts and mesh geometries -> technic-gears.json
.venv/bin/python scripts/technic_parts_reference.py       # docs/agent/reference/technic-parts.md
```

`ldraw_tools/data/technic-parts.json` holds the hand-reviewed parts. The scripts never regenerate it, and it overrides derived ports. `tests/test_technic_ports.py` fails when the derived table is stale or no longer reproduces every reviewed port.

Before you add a Technic check or change a threshold, measure it on the official sets:

```sh
.venv/bin/python scripts/technic_corpus.py checks
```

An error must fire less than once per 1,000 official placements; anything noisier ships as a warning. The command writes its rates and examples to `docs/reports/benchmarks/technic-corpus.json`. The mutation test in `tests/test_technic_checks.py` and the Walker1 cross-check in `tests/test_mechanism_crosscheck.py` must keep passing. The cross-check reads `../LegoTechnicSimulation` and skips when that checkout is absent.

## Change the knowledge base

Package READMEs own `ldraw-knowledge` registrations. Edit those owners and regenerate compatibility catalogs with each atlas README's command. Keep scopes, aliases, source attribution and source, BOM and visual freshness gates. `docs/reports/` holds historical findings; `data/` and `lsynth-examples/` hold source research, not admitted construction lessons. Preserve the planning baseline in `docs/plans/knowledge-base-overhaul/snapshot/` and record later decisions in the implementation record.

Lessons are most useful as recipes: a small plan that `review` builds, using `on` and `orient` placements an agent can copy, plus one paragraph on when to use it. A lesson made only of a finished MPD and prose forces the agent to re-derive coordinates.

## Visual evidence for admitted lessons

New or changed geometry needs matching visual evidence before admission. Inspect every retained or improved model and submodel, both isolated and in its actual parent placement, with `bin/ldraw-xray` ([xray workflow](../agent/guides/xray.md)); text and JSON alone are insufficient. Reuse existing images only when their source hashes and selections match. Record skipped coverage: automatic contacts stop above 500 placements, a section review excludes parent and sibling interactions, and BOM agreement, connectivity, rendered poses and material clearance are distinct evidence. None alone proves strength or motion. For annotation, read the [annotator workflow](../agent/guides/annotate-models.md) and use `bin/ldraw-annotator` with the supplied database read-only.
