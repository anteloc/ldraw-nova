# Seabreeze Community Clinic

Healthcare · minifigure scale · 426 physical placements · 12 FILE sections.

![Reviewed home view](home.png)

[MPD](clinic.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A low horizontal wing, a taller glazed reception and a clear medical marker distinguish a clinic.

**Place details:** A broad level approach leads to reception; a quiet planted side court balances the sign.

**Avoid:** No stairs at the main entrance; the cross is a functional identifier, not scattered decoration.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/heartlake-city-hospital-42621) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `clinic-wing.ldr` | 18 by 10 stud shell with reserved door/window openings and removable roof interface |
| `window4-3-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-3-70-glazed.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `clinic-wing-roof.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `clinic-reception.ldr` | 6 by 10 stud shell with reserved door/window openings and removable roof interface |
| `door4-15-70-glazed.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `window4-15-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `reception-cap.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `medical-marker.ldr` | Upright red medical cross on a white pedestal; bottom Y=0 |
| `bench-15.ldr` | Four-stud garden/platform bench; bottom Y=0; front -Z |
| `flower-box-5.ldr` | Four by two stud planter with flowers; bottom Y=0 |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py clinic --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/clinic/scene.plan.json --output output/clinic.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
