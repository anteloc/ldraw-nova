# Compose models from inspected modules

Partition by purpose, interfaces and repair boundaries: chassis/body, core/skin, frame/tool, floor/roof or figure limbs as appropriate. MPD hierarchy is authoring structure; it does not by itself establish rigid bodies or physical connections.

Before filling a module, record its local origin, envelope, mating parts, attachment frames, palette inheritance and review status. Reserve openings and expose the connectors that neighbouring modules need. Keep a parent section readable. [Plan anchors and includes](../reference/plans.md#3-define-module-contracts) compose full frames; aligned anchors are intentions that still need real joints.

Use `study FILE --detail full` for hierarchy, reachability, actual parts and source diagnostics. Section names and counts can be misleading: see the preserved [Bookshop source audit](../../reports/bookshop-source-audit.md). `study` is informational, so read `source_checks_passed`. Use [reference discovery](find-references.md) for attributed extraction and dependency boundaries.

## 5. Review at three scales

1. **Detail:** inspect windows/glass, door hinges, furniture, or a single angled roof connection. Use local occurrence indices with `snap`; render the selected section. Record connector residuals and unresolved coverage.
2. **Module:** inspect a complete floor/roof with `--section` and `--colour`, checking clearances, support, step order, and boundary interfaces. Renders of extracted floors expose rooms that a closed exterior hides.
3. **Scene:** validate the complete assembly, check cross-module duplicates/body overlaps, compare BOMs, and render home/top/front plus relevant rear/side views. Module checks alone cannot detect collisions introduced when composing modules.

```sh
.venv/bin/python examples/modular-street/generate.py
./ldraw-agent build examples/modular-street/scene.plan.json --output output/copper-lane.mpd \
  --detail summary --report output/copper-lane.build.json
./ldraw-agent inspect output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --contacts all --detail summary --report output/ground-inspection.json
./ldraw-agent render output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --outdir output/ground-review --views home top
./ldraw-agent validate output/copper-lane.mpd --geometry --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

Default contact mode is `auto`: compute contacts through 500 physical placements; above that, explicitly report skipped coverage. Request `--contacts all` for a deliberate full analysis, or scope to modules. `--contacts none` still checks all resolved bounds and curated rectangular overlaps. It reports no connected-component conclusion. Missing connector metadata produces fragmented groups even for apparently mated parts; investigate the reported parts and do not equate group count with a buildability verdict.

`--detail summary` suppresses instance/contact/pair lists while retaining totals, errors and coverage. `--detail full --limit 30 --offset 60` shows physical occurrences 60–89. Limits truncate report detail, not validation checks. Scope changes restart occurrence indices; section/source-line paths identify the original source. The default physical expansion budget is 100,000 (`--max-instances`).

The LeoCAD adapter materializes embedded DAT definitions and their library dependencies in a temporary library, restoring original embedded names in the CSV. The supplied LeoCAD otherwise omits these placements. `compare-bom` checks actual `(reference, colour, quantity)` equality and returns 1 on differences. Images still need to be opened and reviewed; inspect uncertain interfaces in close views and [step sequences](review-models.md#read-source-steps-when-construction-is-unclear), and record unresolved material intersections.

## Example scope

Copper Lane has a three-storey tan/green bookshop beside a two-storey sand-green townhouse. Arched flower windows, striped awnings, a gold BOOKS sign, a dormer and stepped clock pediment distinguish their façades. It includes exposed-side glazing, localized masonry, layered leaf trees, two lamps and five furnished removable floors. The [design guide](design-models.md) explains how category symbols, palette roles and reusable details express these choices. Floor/roof interfaces are studded; levels are accessed by lifting them off, and the example does not include a minifigure stairwell. This is an original modular construction example, not a recreation of set 10270 or a guarantee of retail part/colour availability. See the [verification record](../../reports/tooling-verification-history.md) for measured coverage and remaining physical review limits.

