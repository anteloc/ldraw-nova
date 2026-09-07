# Aster Museum Pavilion

Civic and cultural · minifigure scale · 376 physical placements · 9 FILE sections.

![Reviewed home view](home.png)

[MPD](museum.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

Symmetry, a columned portico and a stepped pediment establish a civic focal point.

**Place details:** Pair lamps beside the central approach; reserve the central axis for the portico.

**Avoid:** Avoid striped shop awnings and random bright accents on the classical front.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/product/natural-history-museum-10326) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `museum-hall.ldr` | 22 by 12 stud shell with reserved door/window openings and removable roof interface |
| `window4-19-47.ldr` | Four-stud glazed bay; bottom Y=0, body height 72 LDU, front -Z |
| `door4-19-70-traditional.ldr` | Four-stud closed hinged entrance; bottom Y=0, height 144 LDU; front -Z |
| `museum-roof.ldr` | Flat lift-off roof with a low parapet and recessed quiet roof surface |
| `portico-19-19-12-6-144.ldr` | Supported porch: base underside Y=0, entry at rear +Z; keep middle four studs clear |
| `museum-clock.ldr` | Printed civic clock, standing on a two-stud support surface |
| `fluted-lamp.ldr` | Fluted lamppost with warm lantern; bottom Y=0, 2x2 stud foot |
| `flower-box-14.ldr` | Four by two stud planter with flowers; bottom Y=0 |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py museum --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/museum/scene.plan.json --output output/museum.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
