---
name: inspection-boards
description: 'Builds ready-made inspection boards with ldraw-xray board: overview (section in its parent and alone, optional --steps), stud-map, xray (as built vs x-rayed from three sides, --select, --colour Xray_Glass), pivot (axis marker and poses with one fixed camera) and cutaway (--view, --depths), plus mosaic.png layout, --no-mosaic, the 2-12 image limit and ldraw-xray mosaic. Use when you want several labelled views of a section on one image, a first orientation board, or a board to hand over as visual evidence.'
---

# Inspection boards

A board is a ready-made set of views on one labelled `mosaic.png`. `ldraw-xray board TASK` builds one for a common question; each task has its own options (`ldraw-xray board TASK --help`). Single renders are in [render-views](../render-views/SKILL.md); the contract and selectors in the root [ldraw-xray](../SKILL.md) skill.

## Tasks

```sh
# where it sits, what it looks like; --steps adds build steps
ldraw-xray board overview 8071.mpd --section '8071 - crane.ldr' --output out/overview/

# stud directions, plus the section in its parent
ldraw-xray board stud-map 8071.mpd --section '8071 - cabin.ldr' --output out/studs/

# as built vs. x-rayed from three sides
ldraw-xray board xray 8071.mpd --select 'ref:8071 - cabin.ldr' --output out/xray/

# the crane slewing on its turntable: axis marker, then poses with one fixed camera
ldraw-xray board pivot 8071.mpd --section '8071 - crane.ldr' --point 0 -100 30 --direction 0 1 0 \
  --moving '!ref:craneBase.ldr' --angles 0 45 90 --output out/pivot/

# slices through the cabin at 35%, 50% and 65% depth, seen from the front
ldraw-xray board cutaway 8071.mpd --section '8071 - cabin.ldr' --view front --depths 0.35 0.5 0.65 --output out/cuts/
```

| Task | Shows | Key options |
|---|---|---|
| `overview` | the section in its parent, then on its own from two sides | `--section`, `--parent NAME`, `--steps` |
| `stud-map` | parts coloured by stud direction, plus the section in its parent | `--section`, `--parent NAME`, `--steps` |
| `xray` | the model as built, then x-rayed from three sides | `--select SEL`, `--colour` (`47` Trans-Clear by default, any LDraw code, or `Xray_Glass`, a tinted glass that stands out more), `--highlight SEL`, `--section` |
| `pivot` | the axis marker, then the moving parts posed at each angle with one shared camera | `--point X Y Z`, `--direction X Y Z`, `--moving SEL`, `--hardware SEL`, `--angles ...` |
| `cutaway` | the section uncut, then sliced at each depth | `--view` (axis-aligned), `--depths` between 0 (nearest face) and 1 (farthest) |

- `overview`, `stud-map` and `pivot` add the parent automatically when it is unique; pass `--parent NAME` when there are several.
- Start an inspection with `overview`: it orients you before you ask a narrower question.
- Pivot details (finding the axis with `axes`, choosing angles): [pivots-and-connections](../pivots-and-connections/SKILL.md).
- Cut surfaces are not capped.

## Mosaic rules

- A mosaic is written for boards with **2–12 images**. More than 12 (many `--steps`, many `--angles`) needs `--no-mosaic`, which writes only the panels. To keep a mosaic for every board, split the evidence into several boards of at most 12 images.
- `ldraw-xray mosaic out/manifest.json --output board.png` builds a mosaic from any render or board manifest, without LeoCAD (`--columns`, `--panel-width` set the layout).
- Every board task also accepts `--force`, `--keep-intermediates`, `--no-mosaic` and the setting flags (`--library`, `--leocad`, `--shadow`, `--no-shadow`, `--cache-dir`); `board TASK --help` lists them.
- Views on a board are framed independently, so compare shapes across panels, not sizes. Pivot boards share one camera, so poses are comparable.

## Results

Each board writes `panels/`, `mosaic.png`, `recipe.json` and `manifest.json` (what each image shows, notes, versions, source hash). Open `mosaic.png`, then the full-size panels for small details, and read each image's `notes` and `warnings`. An existing output directory is refused unless you pass `--force`.

To change a board (labels, views, layers, colours, cameras, image size), edit its `recipe.json` and replay it:

```sh
ldraw-xray board overview 8071.mpd --section '8071 - crane.ldr' --output out/overview/
$EDITOR out/overview/recipe.json
ldraw-xray board run out/overview/recipe.json --output out/overview-v2/
```

Recipe format: [recipes-and-python](../recipes-and-python/SKILL.md).

## Source docs

Verbatim copies, for details not covered above:

- [README.md](references/README.md)
- [AGENTS.md](references/AGENTS.md)
