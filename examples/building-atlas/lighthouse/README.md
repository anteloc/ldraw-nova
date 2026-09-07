# Saltwind Light and Keeper Cottage

Coastal and maritime · minifigure scale · 368 physical placements · 7 FILE sections.

![Reviewed home view](home.png)

[MPD](lighthouse.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A slender banded tower and low cottage balance a waterside composition.

**Place details:** The beacon is the skyline focus; the cottage stays lower and the water remains uncluttered.

**Avoid:** Do not imply a working Fresnel lens or motor; this is a static architectural study.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/motorised-lighthouse-21335) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `striped-light.ldr` | Round lighthouse tower; 4x4 drum, wide gallery, transparent lantern and cap |
| `keeper-cottage.ldr` | 10 by 10 stud shell with reserved door/window openings and removable roof interface |
| `door4-72-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `window4-72-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `keeper-cottage-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `fence-8-72.ldr` | Supported garden fence; underside Y=0; do not cross circulation routes |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py lighthouse --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/lighthouse/scene.plan.json --output output/lighthouse.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
