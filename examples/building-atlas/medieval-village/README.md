# Hazelbridge Village

Historic vernacular villages · minifigure scale · 857 physical placements · 10 FILE sections.

![Reviewed home view](home.png)

[MPD](medieval-village.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A tall timber inn and a smaller smithy frame a shared working square.

**Place details:** Use shared timber/stone colours but different roof heights; put the stall on the square edge.

**Avoid:** Avoid identical paired façades and modern lighting.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/medieval-town-square-10332) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `inn-lower.ldr` | 12 by 10 stud shell with reserved door/window openings and removable roof interface |
| `window4-70-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-70-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `inn-upper.ldr` | 12 by 10 stud shell with reserved door/window openings and removable roof interface |
| `inn-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `smithy.ldr` | 8 by 10 stud shell with reserved door/window openings and removable roof interface |
| `smithy-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `village-stall.ldr` | Four-stud market stall; supported counter, posts and striped canopy |
| `bench-70.ldr` | Four-stud garden/platform bench; bottom Y=0; front -Z |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py medieval-village --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/medieval-village/scene.plan.json --output output/medieval-village.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
