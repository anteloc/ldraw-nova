# Willow Porch Cottage

Detached homes and gardens · minifigure scale · 442 physical placements · 10 FILE sections.

![Reviewed home view](home.png)

[MPD](cottage.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A low gable, deep porch and asymmetrical garden make a modest house inviting.

**Place details:** The porch is centred on the door; a tree frames the left edge and a bench faces the garden.

**Avoid:** Do not put a lamppost in the small front garden or cover the porch approach with planting.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/cozy-house-31139) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `cottage-shell.ldr` | 16 by 12 stud shell with reserved door/window openings and removable roof interface |
| `window4-15-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-15-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `cottage-shell-roof.ldr` | Removable gabled roof: supported slope courses, contrasting gable core and tiled ridge |
| `porch-15-72-8-4-144.ldr` | Supported porch: base underside Y=0, entry at rear +Z; keep middle four studs clear |
| `leaf-tree-288-5.ldr` | Layered garden tree; bottom Y=0; foliage needs a nine-stud clearing |
| `bench-70.ldr` | Four-stud garden/platform bench; bottom Y=0; front -Z |
| `flower-box-5.ldr` | Four by two stud planter with flowers; bottom Y=0 |
| `fence-8-15.ldr` | Supported garden fence; underside Y=0; do not cross circulation routes |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py cottage --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/cottage/scene.plan.json --output output/cottage.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
