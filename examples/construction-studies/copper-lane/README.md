# Copper Lane construction reuse study

This experiment adapts the existing Copper Lane generator to examine construction reuse, local repairs and scaling. It is not an original building design, another Sol run, or a measurement of design time. The original example, parts library and checker remain unchanged.

```sh
.venv/bin/python examples/construction-studies/copper-lane/reproduce.py
.venv/bin/python examples/construction-studies/copper-lane/evidence.py \
  output/construction-approach-study/reuse/3-floors \
  output/construction-approach-study/reuse/4-floors \
  output/construction-approach-study/reuse/5-floors
.venv/bin/python examples/construction-studies/copper-lane/controls.py \
  output/construction-approach-study/reuse/3-floors
```

The reproducible repair moves the lamps and their exposed pavement mounting openings forward by two studs. It raises the BOOKS tile by half a stud so its lower socket row engages the four side studs. No parts or features are removed from the study models.

The 1,655-, 2,153- and 2,651-part copies report zero collisions, seating errors and duplicates. Their raw verdict remains **FAIL**: fitted panes produce overlap reviews or unrecognized connections. `evidence.py` corroborates every remaining finding using four exact relative poses present in the repository's annotated Bookshop reference, with source hashes and part identities. It does not suppress findings, change checker tolerances, infer acceptance from a part family, or certify physical fit.

The controls establish a PASS for a diagnostic copy without window inserts, and FAIL for a restored sign offset, a one-plate roof gap, and a displaced pane. The displaced pane also fails reference-pose matching. The actual study models retain all glazing.

After generating, render and compare the exact revision:

```sh
./ldraw-agent render output/construction-approach-study/reuse/3-floors/copper-lane-study.mpd \
  --outdir output/construction-approach-study/reuse/3-floors/preview --views home front right back top
./ldraw-agent compare-bom output/construction-approach-study/reuse/3-floors/copper-lane-study.mpd \
  --csv output/construction-approach-study/reuse/3-floors/preview/leocad-bom.csv
```

The generated and checked variants took 4.4–5.4 seconds each in the recorded warm-cache run. This excludes design, reference research, library initialization, rendering, manual inspection and writing the repair code.

See the [assessment and proposed architecture](../../../docs/reports/construction-led-evolution.md) and the [large-model workflow](../../../docs/agent/construction-workflow.md). Artifacts are under ignored `output/construction-approach-study/`; these scripts remain in version control for reproduction.
