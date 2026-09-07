# Sunbeam Learning Courtyard

Education · minifigure scale · 530 physical placements · 10 FILE sections.

![Reviewed home view](home.png)

[MPD](school.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A classroom wing, clock block and courtyard create a small campus with an obvious entrance.

**Place details:** Use the courtyard for gathering and the quieter side for a garden bench.

**Avoid:** Keep trees outside the classroom window band and the entrance axis.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/heartlake-international-school-41731) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `classrooms.ldr` | 20 by 10 stud shell with reserved door/window openings and removable roof interface |
| `window4-15-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-15-70-glazed.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `classrooms-roof.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `school-clock-tower.ldr` | 6 by 8 stud shell with reserved door/window openings and removable roof interface |
| `school-clock-cap.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `school-clock.ldr` | Printed civic clock, standing on a two-stud support surface |
| `bench-15.ldr` | Four-stud garden/platform bench; bottom Y=0; front -Z |
| `leaf-tree-2-14.ldr` | Layered garden tree; bottom Y=0; foliage needs a nine-stud clearing |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py school --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/school/scene.plan.json --output output/school.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
