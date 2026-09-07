# Copper Lane

Leaf and Letter is a botanical bookshop beside the quieter Rose House. This original parameterized streetscape demonstrates how composition, part selection and reusable details work together: green-and-white awnings, a gold BOOKS sign, arched flower windows, embossed masonry, a dormer, a stepped clock pediment, layered leaf trees and fluted lamps. Its five furnished storeys lift off for access. The default has 1,655 physical placements across nineteen FILE blocks.

[Generated MPD](copper-lane.mpd) · [Reviewed preview](preview.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json)

[Design brief](design-brief.json) · [Before/after review](visual-review.md) · [Front elevation](front.png) · [Window detail](window.png)

```sh
.venv/bin/python examples/modular-street/generate.py
./ldraw-agent build examples/modular-street/scene.plan.json --output output/copper-lane.mpd --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

Use `--force` on intentional rebuilds. `generate.py --floors 4 --outdir output/four-storeys` generates a four-storey shop and three-storey house without altering the supplied plans. Paths in `includes` are relative to their declaring plan. Edit the generator for persistent parameter/pattern changes; direct JSON edits are overwritten when regenerating.

`scene.plan.json` places the street and buildings; `buildings.plan.json` defines storeys/roofs; `details.plan.json` defines reusable windows, doors, furniture and landscaping. The generator uses the shared [detail recipes](../../ldraw_tools/details.py), [palette roles](../../ldraw_tools/data/design-palettes.json), and descriptive `@category.Symbol` / `@colours.Name` values resolved from the supplied categories. Edit the generator to change composition; edit the shared recipes to improve details across models. Export an individual starting recipe with `./ldraw-agent design details arched-window --output output/window.plan.json`.

A storey's `base` is its floor-plate underside at Y=8; `next` is the cornice top at Y=-160. Attachment therefore advances 168 LDU upwards. Each arch replaces reserved wall cells; the dormer replaces conflicting roof slopes. The awning's two-row support beam meets actual slope sockets. Interiors are visible when each storey is rendered separately. Floors lift off; no internal stairwell is represented.

Follow the [visual-design](../../docs/agent/visual-design.md) and [complex-model workflows](../../docs/agent/complex-models.md), and read [verification](../../docs/agent/verification.md). Full-scene contacts are explicitly skipped in auto mode; general shape collisions and connection/stability limits still require review. The generated model demonstrates tooling, not physical certification or inventory availability. It contains no copied OMR geometry.
