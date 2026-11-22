# Recipes and rendering reference

Use ordinary CLI flags for common tasks; use a recipe for ordered compositions,
custom cameras, or style changes. `board run recipe.json --output out/` and
`Session.board(recipe, output="out")` share the same validation and renderer.

## Recipe structure

```json
{
  "source": "model.mpd",
  "section": "wing.ldr",
  "title": "Wing inspection",
  "mosaic": true,
  "style": {"width": 1200, "height": 900},
  "panels": [
    {
      "label": "Shell transparent, step 3 highlighted",
      "view": "home",
      "layers": [
        {"layer": "xray", "select": "colour:15"},
        {"layer": "highlight", "select": "step:3"}
      ]
    },
    {
      "label": "Stud directions from the front",
      "view": "front",
      "layers": [{"layer": "stud_map"}]
    }
  ]
}
```

Only `source` and a nonempty `panels` list are required. Relative source paths
are resolved beside the input recipe, or from the current directory for Python
mappings. Written recipes use an absolute source path. Omitted `section` means
the root model. Unknown fields are errors.

| Recipe field | Default / meaning |
|---|---|
| `title` | `Inspection`; at most 120 characters |
| `mosaic` | `true`; plain renders save `false` |
| `mode` | `views`; `analysis` requires identical cameras, subject frames, and image dimensions |
| `columns`, `panel_width` | 2 columns, 800 pixels; allowed ranges 1–4 and 320–1600 |
| `legend` | Extra legend lines; the mosaic displays up to four lines including generated entries |
| `style` | Overrides to the pinned settings below |

Each panel has an optional `label` (at most 180 characters), `parent`, `view`,
`layers`, and `camera`. A missing label becomes `Panel N`; the default view is
`home`; the default layers list is empty. `parent` is an explicit model section
name; omit it or use `null` for an isolated render. A steps layer expands into
labelled images for its nonempty source steps.

## Ordered layers

Layer options use JSON numbers, booleans, and arrays, not strings containing
options. Selectors retain the [small selection language](../README.md#select-parts).

| Layer | Options and defaults |
|---|---|
| `highlight` | `select` required when isolated; defaults to `section` in a parent panel. `scope` defaults to the rendered block |
| `ghost` | No options; requires a highlight |
| `steps` | All nonempty steps by default. Use `numbers: [3, 7]` or inclusive `first` / `last` bounds |
| `xray` | Required `select`; `colour: 47` (Trans-Clear); `scope: "section"` |
| `recolour` | Required `select`; `colour: "group:A"`; `scope: "section"` |
| `stud_map` | `select: "all"`; `scope: "section"` |
| `pose` | Required `select`; `point: [0,0,0]`, `direction: [0,0,1]`, `angle: 0` degrees; `scope: "section"` |
| `axis` | `point: [0,0,0]`, `direction: [0,0,1]`; `length` and `radius` sized automatically |
| `closeup` | `select: "section"`, `scope` defaults to the rendered block, `view: "home"`, `margin: 1.25`. Use `select: "all"` when isolated |
| `cutaway` | `view: "front"`, `depth: 0.5` between 0 and 1 |
| `components` | Recolour connected groups other than the largest |
| `contacts` | Connector markers; `radius: 2.5` |
| `collisions` | Recolour overlap candidates; `min_depth: 2` LDraw units |

`scope` is `section` or `parent`. Colour values accept LDraw codes, swatch names
such as `Xray_Glass`, or `group:A` through `group:F`. Vectors contain three finite
numbers; directions must be nonzero. Dimensions and source step numbers are
positive. Source steps retain their original numbering, including empty steps.

Layers apply in order. Recolouring and x-ray flatten selected child models so
explicit colours inside those children also change. Selection then operates on
the current placements; later operations can replace earlier colours.
Highlighting moves the selection to a synthetic final step. Ghosting replaces
the other parts' colours, so inspection colours survive only on highlighted
parts. Steps cannot combine with highlight or ghost.

Content layers edit the section, which also changes its appearance inside a
parent. Parent highlighting operates on parent placements; it cannot highlight
individual leaves inside the child. Connection overlays and source-step renders
require an isolated section. Connection overlays inspect original geometry and
ignore poses. Most contact markers are between parts; apply x-ray before
contacts to make them visible.

## Coordinates and cameras

LDraw −Y is up; the front view looks toward +Z. Axis points, directions, and
lengths use section coordinates and LDraw units. Axis records include the axes
transformed into each parent placement.

Views are `home`, `front`, `back`, `left`, `right`, `top`, and `bottom`, named
as in LeoCAD: `right` shows the model's right side from −X, `left` its left side
from +X. Normal views fit the part bounds. Steps of a panel share a camera and scale. Cutaways
require an axis-aligned view: depth 0 is the nearest face, depth 1 the farthest.
Cut surfaces are not capped.

A panel may replace `view` with `camera`:

```json
{"label": "Fixed camera", "camera": {"fixed": "home"}, "layers": []}
```

Fixed cameras frame the unposed block's bounding sphere and are shared for the
same parent and view, keeping pose sweeps at one scale. For an explicit camera:

```json
{
  "label": "Custom camera",
  "camera": {
    "position": [200, -200, -200],
    "target": [0, 0, 0],
    "up": [0, -1, 0],
    "fov": 30,
    "orthographic": false
  }
}
```

Optional `zplanes: [near, far]` must satisfy `1 <= near < far`. Explicit cameras
need both position and target. A panel cannot combine `camera` with a `closeup`
or `cutaway` layer. In layer-only compositions, the last closeup supplies the
camera unless a cutaway is present; the last cutaway takes precedence.

Python accepts `Camera` objects through `Session.render(..., cameras=[...])`.
`Session.render` also accepts `style=Style(...)`, `force=True`, and
`keep_intermediates=True`. `Session.board` accepts the latter two options and
`mosaic=False` to override a recipe's mosaic setting.

## Style and image interpretation

Defaults are pinned so saved LeoCAD GUI preferences do not change renders:

| Style fields | Defaults |
|---|---|
| `width`, `height` | 1200, 900 |
| `stud_style`, `auto_edges` | 6, `true` |
| `edge_contrast`, `light_dark` | 1.0, 0.5 |
| `line_width`, `aa_samples`, `shading` | 2, 4, `full` |
| `highlight`, `fade` | `#FFFF00FF`, `#40C0C0C0` in LeoCAD's `#AARRGGBB` format |
| `backdrop` | `#EEF1F4` |
| `outline`, `outline_width` | `#2A2F36`, 2 pixels; `outline: null` disables it |

Magenta edges mean highlighted or newly added parts. Pale grey means ghosted
context. The neon-green axis rod is synthetic. Green and olive contact markers
mean confirmed and heuristic detections. Raspberry marks box-overlap candidates.
Dark stud sides and the postprocessed silhouette outline are rendering aids.

Stud-map colours: up `#EDD4F7`, +X `#FF0078`, −X `#FF5500`, +Z `#0500FF`,
−Z `#00FFE0`, down `#BCF747`, odd angle `#7C49FF`. They describe the chosen
scope's coordinates; a parent may rotate the whole section. The manifest records
parent placements. `palette` lists every swatch and `palette --check` checks their
distance from the installed LDraw colours.

## Renderer details and limits

LeoCAD 25.09 requires stud style 6 or 7 for its high-contrast edge options. It
writes transparent PNGs; ldraw-xray flattens them onto the backdrop and traces an
outline from opaque pixels. Direct colours and model-local colour definitions
are unreliable in LeoCAD, so rendering uses a temporary library wrapper with
extended colours and materialized embedded parts. The real library stays read-only.

Unknown parts may be skipped for bounds; image notes identify them. Connector
coverage improves with LDCad shadows, but pyldraw3 1.7.0 still misses some joints,
including Technic pin/axle mating. Separate groups can indicate missed connections.
Overlap candidates use axis-aligned boxes, which can overestimate rotated parts.
Images and reports do not establish fit, clearance, travel, or stability.
