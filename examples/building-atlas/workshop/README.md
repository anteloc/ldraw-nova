# Copperworks Repair Yard

Industrial and workshops · minifigure scale · 475 physical placements · 10 FILE sections.

![Reviewed home view](home.png)

[MPD](workshop.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

Repeated glazed roof bays and a separate utility stack communicate a workshop.

**Place details:** Keep the working yard sparse, use darker materials low down, and group equipment to one side.

**Avoid:** Do not use domestic flower boxes or a ceremonial entrance.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/corner-garage-10264) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `workshop-shell.ldr` | 20 by 12 stud shell with reserved door/window openings and removable roof interface |
| `window4-72-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-72-70-glazed.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `rooflight-roof.ldr` | Three supported gable rooflight bays with contrasting trans-light-blue slope glazing |
| `roof-light-0.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `roof-light-1.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `roof-light-2.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `utility-stack.ldr` | Banded industrial chimney on a 4x4 stud equipment plinth |
| `landing-beacon.ldr` | Low blue landing beacon; functional industrial lighting |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py workshop --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/workshop/scene.plan.json --output output/workshop.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
