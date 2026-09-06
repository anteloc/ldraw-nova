# Copper Lane

An original parameterized streetscape demonstrating included plans, repeated submodels, running brick bonds, inherited colours, and named floor/roof interfaces. The default has 1,544 physical placements across ten FILE blocks, including five furnished storeys, windows/glass, two hinged doors, supported red/blue roofs, two trees and two lamps.

[Generated MPD](copper-lane.mpd) · [Reviewed preview](preview.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json)

```sh
.venv/bin/python examples/modular-street/generate.py
./ldraw-agent build examples/modular-street/scene.plan.json --output output/copper-lane.mpd --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

Use `--force` on intentional rebuilds. `generate.py --floors 4 --outdir output/four-storeys` generates a four-storey shop and three-storey house without altering the supplied plans. Paths in `includes` are relative to their declaring plan. Edit the generator for persistent parameter/pattern changes; direct JSON edits are overwritten when regenerating.

`scene.plan.json` places the street and buildings; `buildings.plan.json` defines storeys/roof; `details.plan.json` defines reusable windows, doors, furniture and landscaping. A storey's `base` is its floor-plate underside at Y=8; `next` is the cornice top at Y=-152. Attachment therefore advances 160 LDU upwards. Interiors are visible when each storey is rendered separately. Floors lift off; no internal stairwell is represented.

Follow the [complex-model workflow](../../docs/agent/complex-models.md) and read [verification](../../docs/agent/verification.md). Full-scene contacts are explicitly skipped in auto mode; general shape collisions and connection/stability limits still require review. The generated model demonstrates tooling, not physical certification or inventory availability. It contains no copied OMR geometry.
