---
name: recipes-and-python
description: 'Reference for ldraw-xray recipes and the Python API: recipe.json fields (source, section, title, mosaic, mode, columns, panel_width, legend, style, panels), ordered layers and their options (highlight, ghost, steps, xray, recolour, stud_map, pose, axis, closeup, cutaway, components, contacts, collisions), scope, colours and swatches, views and explicit cameras (fixed, position/target/up/fov/orthographic, zplanes), pinned style defaults, stud-map colours, renderer limits, board run, and Session.render / Session.board with Style, Camera, XrayConfig and compose_mosaic. Use when a CLI flag cannot express the composition, when editing or replaying a saved recipe.json, or when scripting renders from Python.'
---

# Recipes and Python

Use a recipe when CLI flags cannot express what you need: ordered layer compositions, custom cameras, close-ups, recolouring, contact overlays or style changes. Every render and board saves a `recipe.json` that reproduces it; edit it or write one, then replay it. `board run recipe.json --output out/` and Python `Session.board(recipe, output="out")` share the same validation and renderer. Selector syntax is in the root [ldraw-xray](../SKILL.md) skill.

```sh
ldraw-xray board run out/overview/recipe.json --output out/overview-v2/
```

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

Only `source` and a nonempty `panels` list are required. **Unknown fields are errors; options are JSON values, not strings.** Relative `source` paths resolve beside the recipe (or from the current directory for Python mappings); written recipes use an absolute path. Omitted `section` means the root model.

| Recipe field | Default / meaning |
|---|---|
| `title` | `Inspection`; at most 120 characters |
| `mosaic` | `true`; plain renders save `false` |
| `mode` | `views`; `analysis` requires identical cameras, subject frames, and image dimensions |
| `columns`, `panel_width` | 2 columns, 800 pixels; allowed ranges 1–4 and 320–1600 |
| `legend` | Extra legend lines; the mosaic displays up to four lines including generated entries |
| `style` | Overrides to the pinned style settings below |

Each panel has optional `label` (≤180 characters; default `Panel N`), `parent` (an explicit section name; omit or `null` for an isolated render), `view` (default `home`), `layers` (default empty) and `camera`. A steps layer expands into labelled images for its nonempty source steps.

## Layers

Layers apply **in order**.

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

- `scope` is `section` or `parent`. Colours accept LDraw codes, swatch names such as `Xray_Glass`, or `group:A` … `group:F`. Vectors are three finite numbers; directions nonzero; dimensions and step numbers positive.
- Recolouring and x-ray flatten selected child models, so explicit colours inside them also change. Later operations can replace earlier colours.
- Highlighting moves the selection to a synthetic final step. Ghosting replaces other parts' colours, so inspection colours survive only on highlighted parts. Steps cannot combine with highlight or ghost.
- Content layers edit the section, which also changes its appearance inside a parent. Parent highlighting works on parent placements; it cannot highlight leaves inside the child.
- Connection overlays and source-step renders need an isolated section; connection overlays ignore poses. Apply `xray` before `contacts` to see markers between parts ([pivots-and-connections](../pivots-and-connections/SKILL.md)).

Example close-up composition:

```json
{
  "source": "model.mpd",
  "section": "wing.ldr",
  "title": "Wing: shell and hidden gear",
  "panels": [
    {"label": "As built", "view": "home"},
    {"label": "Shell x-rayed, gear highlighted", "view": "front",
     "layers": [{"layer": "xray", "select": "colour:15"}, {"layer": "highlight", "select": "part:3647"}]},
    {"label": "Close-up of the gear", "view": "home",
     "layers": [{"layer": "highlight", "select": "part:3647"}, {"layer": "closeup", "select": "part:3647"}]}
  ]
}
```

## Views and cameras

Views: `home`, `front`, `back`, `left`, `right`, `top`, `bottom`, named as in LeoCAD (`right` shows the model's right side from −X, `left` from +X). LDraw −Y is up; front looks toward +Z. Normal views fit the part bounds. Cutaways need an axis-aligned view (depth 0 = nearest face, 1 = farthest; cut surfaces are not capped).

A panel may replace `view` with `camera`:

```json
{"label": "Fixed camera", "camera": {"fixed": "home"}, "layers": []}
```

Fixed cameras frame the unposed block's bounding sphere and are shared for the same parent and view, keeping pose sweeps at one scale. Explicit camera:

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

- Explicit cameras need both `position` and `target`. Optional `zplanes: [near, far]` with `1 <= near < far`.
- A panel cannot combine `camera` with a `closeup` or `cutaway` layer. Without a camera, the last `closeup` supplies the camera unless a `cutaway` is present; the last cutaway wins.

## Style

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

LeoCAD 25.09 needs stud style 6 or 7 for its high-contrast edge options. It writes transparent PNGs; ldraw-xray flattens them onto the backdrop and traces an outline from opaque pixels. Rendering uses a temporary library wrapper with extended colours and materialized embedded parts (direct and model-local colours are unreliable in LeoCAD); the real library stays read-only.

Stud-map colours: up `#EDD4F7`, +X `#FF0078`, −X `#FF5500`, +Z `#0500FF`, −Z `#00FFE0`, down `#BCF747`, odd angle `#7C49FF`, in the chosen scope's coordinates (a parent may rotate the section; the manifest records parent placements). `ldraw-xray palette` lists every swatch; `palette --check` checks their distance from the installed LDraw colours.

## Python

```python
from pathlib import Path
from ldraw_xray import Session

session = Session()  # reads LDRAW_DIR, LEOCAD, LDRAW_SHADOW
manifest = session.render(
    "model.mpd",
    section="wing.ldr",
    output="out",
    layers=[{"layer": "xray", "select": "colour:15"}, {"layer": "highlight", "select": "step:3"}],
    views=["home", "front"],
)
images = [Path(manifest["output"]) / panel["image"] for panel in manifest["panels"]]

session.board("out/recipe.json", output="replay")
```

| Call | Extra options |
|---|---|
| `Session.render(...)` | `cameras=[Camera(...)]`, `style=Style(...)`, `force=True`, `keep_intermediates=True` |
| `Session.board(recipe, output=...)` | `force=True`, `keep_intermediates=True`, `mosaic=False` (overrides the recipe) |

`XrayConfig`, `Style`, `Camera` and `compose_mosaic` are also public. The docs do not list their constructor fields beyond what is shown here; check `help()` on the installed package before relying on other arguments.

## Source docs

Verbatim copies, for details not covered above:

- [docs/reference.md](references/docs-reference.md)
- [README.md](references/README.md)
