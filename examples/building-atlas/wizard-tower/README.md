# Moonflower Observatory

Fantasy and enchanted buildings · minifigure scale · 459 physical placements · 9 FILE sections.

![Reviewed home view](home.png)

[MPD](wizard-tower.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

Offset tower masses, a pointed roof and restrained magical colour create a fantasy silhouette.

**Place details:** Use the high spire as the focal feature; keep magical accents small and repeat the same palette.

**Avoid:** Do not use arbitrary floating geometry or add a different bright colour to every tier.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/hogwarts-castle-and-grounds-76419) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `observatory.ldr` | 12 by 12 stud shell with reserved door/window openings and removable roof interface |
| `window4-72-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `observatory-conical-roof.ldr` | Two complementary tiled half-cones form a supported circular spire |
| `study.ldr` | 8 by 10 stud shell with reserved door/window openings and removable roof interface |
| `door4-72-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `study-spire.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `leaf-tree-288-5.ldr` | Layered garden tree; bottom Y=0; foliage needs a nine-stud clearing |
| `flower-box-5.ldr` | Four by two stud planter with flowers; bottom Y=0 |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py wizard-tower --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/wizard-tower/scene.plan.json --output output/wizard-tower.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
