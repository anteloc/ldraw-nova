---
name: pivots-and-connections
description: 'Finds rotation axes and checks connections: ldraw-xray axes (candidate point/direction from coaxial pins, axles and holes), board pivot (--point, --direction, --moving, --hardware, --angles, fixed shared camera), connections (contacts, connected groups, box-overlap candidates), and the recipe layers pose, axis, contacts, collisions and components, with their limits (Technic pin/axle mating not paired, boxes overestimate rotated parts, shadow library improves coverage). Use when showing how a part moves, locating a hinge axis, or checking whether parts touch, float or overlap.'
---

# Pivots and connections

Locate where a part could rotate, show it posed through a range of angles, and check which parts touch, which float and which may overlap. Commands: `axes`, `board pivot`, `connections`, plus the recipe layers `pose`, `axis`, `contacts`, `collisions` and `components`. Everything here is **evidence, not proof**: confirm visually before claiming a fit, a gap or a motion. Selectors and the JSON contract are in the root [ldraw-xray](../SKILL.md) skill.

## Find a rotation axis

```sh
ldraw-xray axes 8071.mpd --section '8071 - crane.ldr'
```

`axes` proposes rotation axes from coaxial connectors (pins, axles, holes), with `point` and `direction` ready to paste into `board pivot`. Coordinates are the section's own, in LDraw units, with −Y up. Axis records also include the axes transformed into each parent placement.

## Show the motion

```sh
ldraw-xray board pivot 8071.mpd --section '8071 - crane.ldr' --point 0 -100 30 --direction 0 1 0 \
  --moving '!ref:craneBase.ldr' --angles 0 45 90 --output out/pivot/
```

| Option | Meaning |
|---|---|
| `--point X Y Z` | a point on the axis, section coordinates (LDU) |
| `--direction X Y Z` | axis direction; nonzero |
| `--moving SEL` | the parts that rotate (quote the selector) |
| `--hardware SEL` | optional selector for the joint hardware |
| `--angles A ...` | pose angles in degrees, e.g. `0 45 90` |

- The board shows the neon-green axis marker, then each pose. Pivot boards share **one fixed camera**, so poses are comparable (other boards frame each view independently).
- More than 12 images need `--no-mosaic`.
- The parent is added automatically when unique; pass `--parent NAME` otherwise.
- Choose angles the mechanism can actually reach. A rendered pose does not establish clearance or allowable travel.

## Check connections

```sh
ldraw-xray connections 8071.mpd --section '8071 - front-axle.ldr'
```

`connections` reports contacts between parts, connected groups and overlap candidates.

- **Several groups** can mean a loose part, or a joint the detector doesn't know: Technic pin/axle mating isn't paired yet.
- **Overlap candidates** come from axis-aligned bounding boxes, which overestimate rotated parts; check them in an image.
- Connector coverage improves with the LDCad shadow library (`--shadow` or `LDRAW_SHADOW`), but pyldraw3 1.7.0 still misses some joints.

## Connection and motion layers (recipes)

These layers go into a recipe panel's `layers` list ([recipes-and-python](../recipes-and-python/SKILL.md)):

| Layer | Options and defaults | Shows |
|---|---|---|
| `pose` | `select` required; `point: [0,0,0]`, `direction: [0,0,1]`, `angle: 0` (degrees); `scope: "section"` | the selection rotated about the axis |
| `axis` | `point: [0,0,0]`, `direction: [0,0,1]`; `length`, `radius` sized automatically | the synthetic neon-green rod |
| `contacts` | `radius: 2.5` | connector markers: green = confirmed, olive = heuristic |
| `collisions` | `min_depth: 2` LDraw units | overlap candidates recoloured raspberry |
| `components` | — | recolours connected groups other than the largest |

```json
{
  "source": "model.mpd",
  "section": "wing.ldr",
  "panels": [
    {"label": "Contacts behind the shell", "view": "home",
     "layers": [{"layer": "xray", "select": "colour:15"}, {"layer": "contacts"}]},
    {"label": "Loose groups", "view": "home", "layers": [{"layer": "components"}]},
    {"label": "Flap at 30 degrees", "camera": {"fixed": "home"},
     "layers": [{"layer": "axis", "point": [0, 0, 0], "direction": [1, 0, 0]},
                {"layer": "pose", "select": "ref:flap.ldr", "point": [0, 0, 0], "direction": [1, 0, 0], "angle": 30}]}
  ]
}
```

- Connection overlays require an **isolated section** (no `parent`) and inspect the **original** geometry: they ignore poses.
- Most contact markers sit between parts: apply `xray` before `contacts` to make them visible.
- Use `"camera": {"fixed": "home"}` for pose sweeps: fixed cameras frame the unposed block's bounding sphere and are shared for the same parent and view, keeping poses at one scale.

## Limits

Images and reports do not establish fit, clearance, travel or stability. Several groups, missing contacts or an overlap candidate are reasons to look closer, not verdicts. Unknown parts may be skipped for bounds; image notes identify them.

## Source docs

Verbatim copies, for details not covered above:

- [README.md](references/README.md)
- [AGENTS.md](references/AGENTS.md)
- [docs/reference.md](references/docs-reference.md)
