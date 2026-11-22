---
name: render-views
description: 'Renders a model or section with ldraw-xray render: --section, --view (home front back left right top bottom), --parent to see where a section is mounted, --highlight and --ghost to pick out parts, --xray to see through a shell, --steps for one image per source build step, --stud-map to colour parts by stud direction, plus --output, --force, --keep-intermediates and building a mosaic from render panels. Use when you need images of a section from given sides, its mounting in the parent, specific highlighted parts, what is hidden behind a shell, its build sequence or which way its studs point.'
---

# Render views

`ldraw-xray render` produces images of a model or one section: from chosen sides, inside its parent, with parts highlighted or ghosted, with a shell x-rayed, one image per build step, or coloured by stud direction. The JSON contract, selectors and image legend are in the root [ldraw-xray](../SKILL.md) skill. The examples use `8071.mpd`, a Technic bucket truck with sections such as `8071 - cabin.ldr`, `8071 - front-axle.ldr` and `8071 - crane.ldr`.

## Basic render

```sh
ldraw-xray sections 8071.mpd                         # names, steps and parents
ldraw-xray render 8071.mpd --output out/             # the whole (root) model
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --view home --view front --output out/cabin/
```

Open `out/cabin/panels/*.png`. The JSON result lists what it wrote:

```json
{
  "output": "/home/me/out/cabin",
  "recipe": "/home/me/out/cabin/recipe.json",
  "manifest": "/home/me/out/cabin/manifest.json",
  "images": [
    {"image": "/home/me/out/cabin/panels/01-home-view.png", "shows": "home view", "view": "home", ...},
    {"image": "/home/me/out/cabin/panels/02-front-view.png", "shows": "front view", "view": "front", ...}
  ]
}
```

| Option | Meaning |
|---|---|
| `--section NAME` | a name from `sections` (quote it); omitted = root model |
| `--view V` (repeat) | `home` (LeoCAD's 3/4 view), `front`, `back`, `left`, `right`, `top`, `bottom` |
| `--output DIR` / `-o DIR` | result directory; an existing result is refused |
| `--force` | overwrite an existing result |
| `--keep-intermediates` | also keep the raw LeoCAD images and generated models, for debugging |

Each image takes a few seconds: request only the views that answer your question. `right` shows the model's right side, seen from −X; `front` looks toward +Z.

## Highlight and ghost

Magenta edges on the selected parts; `--ghost` fades the rest.

```sh
# the steering parts of the front axle, everything else ghosted
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' \
  --highlight 'ref:8071 - steering-shaft.ldr|ref:steerArm.ldr' --ghost --output out/

# the parts added in step 3
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --highlight 'step:3' --output out/
```

`--ghost` needs `--highlight`.

## A section in its parent

`--parent` renders the parent model so you see where the section sits. Highlight `section` to pick it out:

```sh
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --parent --highlight section --ghost --output out/

# a section used in several places: name the parent
ldraw-xray render 8071.mpd --section '8071 - headlight-lamp.ldr' --parent headLightLeft.ldr \
  --highlight section --output out/
```

Bare `--parent` works only with a unique parent; otherwise the error lists them:

```
{"error": "Multiple parents of '8071 - headlight-lamp.ldr'; choose --parent NAME: headLightLeft.ldr, headLightRight.ldr"}
```

In a parent render, `--highlight` selects the **parent's** placements: `section` picks the whole submodel; you cannot highlight individual parts inside it there.

## X-ray: see through a shell

`--xray` makes the selected parts transparent. Select the shell by submodel, colour, part, step or line.

```sh
# the cabin turned to clear glass, seen from the top
ldraw-xray render 8071.mpd --xray 'ref:8071 - cabin.ldr' --view top --output out/

# x-ray the cabin and highlight the front axle under it
ldraw-xray render 8071.mpd --xray 'ref:8071 - cabin.ldr' --highlight 'ref:8071 - front-axle.ldr' --output out/

# x-ray the whole cabin except the seats and steering wheel
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --xray '!ref:chair.ldr|!ref:steeringWheel.ldr' --output out/
```

For a before/after comparison from three sides use the `xray` board ([inspection-boards](../inspection-boards/SKILL.md)).

## Build steps

One image per source step, parts new in that step edged in magenta:

```sh
# every step with parts
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --steps --output out/steps/

# just these, then side by side on one image
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --steps 3,6,10,15 --output out/some-steps/
ldraw-xray mosaic out/some-steps/manifest.json --output out/steps.png
```

- Steps keep the numbering of the source file, empty steps included (`sections` reports `empty_leading_steps`).
- They render the section on its own: no `--parent`, `--highlight` or `--ghost`.
- More than 12 images on a board need `--no-mosaic`; split large step sets.
- Steps of a panel share a camera and scale.

## Stud directions

Colours each part by where its studs point (up, ±X, ±Z, down, odd angle). Handy for SNOT (studs-not-on-top) building:

```sh
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --stud-map --output out/
ldraw-xray palette          # what each colour means
```

`--stud-map` and `--xray` are alternatives: one per render. Stud directions are in the section's coordinates; a parent may rotate the whole section, so check the parent placement (in the manifest, or with `board stud-map`, which adds the parent view).

## Mosaic from any render

`ldraw-xray mosaic out/manifest.json --output board.png` composes a labelled board from any render's manifest (works without LeoCAD). `--columns` and `--panel-width` set the layout.

## Source docs

Verbatim copies, for details not covered above:

- [README.md](references/README.md)
- [AGENTS.md](references/AGENTS.md)
