# Sunwell Desert Sanctuary

Adventure ruins and ancient monuments · minifigure scale · 260 physical placements · 3 FILE sections.

![Reviewed home view](home.png)

[MPD](desert-sanctuary.mpd) · [Editable plan](scene.plan.json) · [Front](front.png) · [Top](top.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json) · [Review](visual-review.json)

## What to learn

A stepped platform, open colonnade and paired pylons express an archaeological adventure setting.

**Place details:** Use a clear ceremonial axis and sparse warm stone accents; leave the ruins visually open.

**Avoid:** Do not invent historical accuracy or place unrelated medieval/gothic decoration on the sanctuary.

This is an original teaching model. The [LEGO example](https://www.lego.com/en-us/service/building-instructions/5988) establishes the building family; its source geometry was not copied. The family labels are the atlas's practical classification, not an exhaustive official LEGO taxonomy.

## Construction

The root section places the site and named modules. `base` anchors describe underside contact planes; `roof` anchors use body-top heights. The [shared helpers](../../../ldraw_tools/architecture.py) author X/Z in studs and upward height in LDU, then emit `[20*x, -h, 20*z]`. The [generator](../generate.py) contains the composition and every reserved footprint. Inspect unfamiliar parts with `ldraw-agent part` before changing their interfaces.

| Submodel | Construction purpose |
|---|---|
| `colonnaded-shrine.ldr` | Open inner shrine with paired columns and a complete lintel deck |
| `stairs-6-3.ldr` | Supported steps, 8 LDU rise and one-stud tread; front -Z |

Render and inspect one submodel with `--section NAME --colour CODE`; replace NAME with a FILE name from this table. The [detail library](../details/README.md) supplies isolated modules with measured envelopes, local anchors and placement advice. Use the [placement guide](../../../docs/agent/building-atlas.md) when composing a different scene.

```sh
.venv/bin/python examples/building-atlas/generate.py desert-sanctuary --outdir output/atlas-study --render
./ldraw-agent build examples/building-atlas/desert-sanctuary/scene.plan.json --output output/desert-sanctuary.mpd --detail summary
```

Change the generator for reproducible structural edits; changing only the emitted MPD loses the change on regeneration. The examples focus on exterior composition and interfaces. Most rooms have no furniture or internal stairs; the skyline is explicitly microscale. No vehicles, minifigures, moving mechanisms or manufacturing inventory are implied. Read the per-view observations and physical scope in the [collection review](../visual-review.md).
