# Mesa Crossing Trading Post

Western and frontier · minifigure scale · 381 physical placements · 12 FILE sections.

![Reviewed home view](home.png)

[MPD](frontier.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A false-front shop, boardwalk and small stable establish a frontier settlement.

**Place details:** Timber porches and a dusty open yard belong here; keep the false front above the lower roof.

**Avoid:** Do not rely on lettering alone to distinguish the building from a modern shop.

This is an original teaching model. The [LEGO example](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/4585106.pdf) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `trading-post.ldr` | 14 by 10 stud shell with reserved door/window openings and removable roof interface |
| `window4-19-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-19-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `trading-post-roof.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `false-front.ldr` | Supported stepped false front with a central sign field |
| `boardwalk-porch-70-19-14-4-144.ldr` | Supported porch: base underside Y=0, entry at rear +Z; keep middle four studs clear |
| `stable.ldr` | 6 by 8 stud shell with reserved door/window openings and removable roof interface |
| `door4-70-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `window4-70-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `stable-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `fence-8-70.ldr` | Supported garden fence; underside Y=0; do not cross circulation routes |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py frontier --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/frontier/scene.plan.json --output output/frontier.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
