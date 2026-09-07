# Snowbell Alpine Lodge

Seasonal and alpine buildings · minifigure scale · 489 physical placements · 8 FILE sections.

![Reviewed home view](home.png)

[MPD](winter-lodge.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A steep snow roof, warm timber walls and sheltered porch create a winter retreat.

**Place details:** Keep snow as broad roof/ground masses; warm accents cluster around the entrance.

**Avoid:** Do not scatter white studs indiscriminately or place foliage through the roof.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/alpine-lodge-10325) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `alpine-lodge.ldr` | 16 by 14 stud shell with reserved door/window openings and removable roof interface |
| `window4-19-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-19-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `alpine-lodge-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `lodge-porch-70-15-8-4-144.ldr` | Supported porch: base underside Y=0, entry at rear +Z; keep middle four studs clear |
| `leaf-tree-288-15.ldr` | Layered garden tree; bottom Y=0; foliage needs a nine-stud clearing |
| `bench-70.ldr` | Four-stud garden/platform bench; bottom Y=0; front -Z |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py winter-lodge --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/winter-lodge/scene.plan.json --output output/winter-lodge.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
