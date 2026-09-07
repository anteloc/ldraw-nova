# Red Barn Farmstead

Agriculture · minifigure scale · 531 physical placements · 10 FILE sections.

![Reviewed home view](home.png)

[MPD](farmstead.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A tall barn, smaller granary, fenced yard and crop patch make a working cluster.

**Place details:** Leave a broad barn approach; use fences to describe the yard rather than enclose every edge.

**Avoid:** Avoid urban paving and lampposts; the crops belong in rows away from vehicle access.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/barn-farm-animals-60346) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `red-barn.ldr` | 14 by 14 stud shell with reserved door/window openings and removable roof interface |
| `door4-15-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `window4-15-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `red-barn-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `granary.ldr` | 6 by 8 stud shell with reserved door/window openings and removable roof interface |
| `door4-70-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `window4-70-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `granary-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `fence-8-70.ldr` | Supported garden fence; underside Y=0; do not cross circulation routes |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py farmstead --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/farmstead/scene.plan.json --output output/farmstead.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
