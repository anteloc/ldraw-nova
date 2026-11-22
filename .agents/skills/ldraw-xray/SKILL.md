---
name: ldraw-xray
description: 'Gives agents eyes on LDraw models (.ldr/.mpd): the ldraw-xray CLI renders a model or one of its sections with LeoCAD, with highlighting, ghosting, x-ray, build steps, stud maps, poses and cutaways, and lays images out on a labelled board (mosaic.png). Covers install and settings (LeoCAD, LDRAW_DIR, LDRAW_SHADOW, LDRAW_XRAY_CACHE, doctor), the JSON output contract and exit codes, the sections → overview → specific question workflow, the selector language (all, section, line:, step:, part:, colour:, ref:, |, !), rules that trip agents and how to read the images. Use when you need to look at, inspect or render an LDraw model or submodel, check how a section is mounted or built, or before running any ldraw-xray command (doctor, sections, render, board, axes, connections, palette, mosaic).'
---

# ldraw-xray

ldraw-xray gives you eyes on LDraw models (`.ldr` / `.mpd`). It renders a model, or one of its sections (submodels), with LeoCAD and adds what plain renders don't show: highlighting, ghosting, x-ray, the section in its parent, build steps, stud maps, axes, poses and cutaways. It lays the images out on a labelled inspection board (`mosaic.png`). **Then you open the PNGs and look.** Source files and the parts library are never modified.

## Before you start

```sh
ldraw-xray doctor          # "renders": true means you can render
```

- If `renders` is false, read `errors`: LeoCAD, the LDraw library (`LDRAW_DIR`) or both are missing. Ask the user to install or configure them (see [Install](#install)). Don't download the library or install LeoCAD yourself unless asked.
- `sections`, `palette` and `mosaic` work without LeoCAD or a library.
- Inside the ldraw-xray source checkout, prefix commands with `uv run` (or use `.venv/bin/ldraw-xray`). Projects that install it locally call that path instead (ldraw-nova uses `bin/ldraw-xray`). `python -m ldraw_xray` is the same as `ldraw-xray`.

## The contract

- Every command prints **one JSON object** on stdout. Paths in it are absolute.
- Errors are JSON on stderr: `{"error": "..."}`. Error messages say what to change.

| Exit | Meaning |
|---|---|
| 0 | done; the JSON result is on stdout |
| 1 | execution failed (LeoCAD, files); the error is JSON on stderr |
| 2 | bad input or setup: missing file, unknown section, bad selector, no library; fix the command |

- Renders and boards return `images[]` (each with `image`, `shows`, `view`, `step`, `notes`, `warnings`) and, for boards with 2–12 images, `mosaic`. **Open those files to see the result.** Read `notes` and `warnings`: empty selections and skipped parts are reported there, not as failures.
- An output directory that already holds results is refused: use a new one or `--force`. Unrelated files in the folder are kept.
- Each image takes a few seconds. Ask for the views you need, not all seven.

Output layout:

```
out/
├── panels/          # one PNG per image: 01-home-view.png, 02-front-view.png, ...
├── mosaic.png       # boards with 2-12 images
├── recipe.json      # replay with `ldraw-xray board run`
└── manifest.json    # what each image shows, notes, versions, source hash
```

## Workflow

1. **List sections:** `ldraw-xray sections model.mpd`. Each has `name`, `kind`, `placements`, `steps` and `parents`. Pass the exact `name` to `--section`, single-quoted (names often have spaces). Without `--section` you get the root model.
2. **Get oriented:** one overview board shows the section in its parent and on its own.

   ```sh
   ldraw-xray board overview model.mpd --section 'wing.ldr' --output out/overview/
   ```

3. **Ask a specific question** with the command that answers it:

| Question | Command |
|---|---|
| What does it look like from X? | `render M --section S --view front --view top -o OUT` |
| Where is it mounted? | `render M --section S --parent --highlight section --ghost -o OUT` |
| Which parts are these? | `render M --section S --highlight 'part:3647' --ghost -o OUT` |
| What's behind the shell? | `render M --section S --xray 'colour:15' [--highlight SEL] -o OUT` |
| Before/after x-ray, 3 sides | `board xray M --section S --select 'colour:15' --colour Xray_Glass -o OUT` |
| How is it built? | `render M --section S --steps [3,7-9] -o OUT` |
| Which way do studs point? | `render M --section S --stud-map -o OUT` or `board stud-map ...` |
| What's inside? | `board cutaway M --section S --view front --depths 0.35 0.5 0.65 -o OUT` |
| Where could it rotate? | `axes M --section S` → candidate `point` / `direction` |
| How does it move? | `board pivot M --section S --point X Y Z --direction X Y Z --moving SEL [--hardware SEL] [--angles 0 45 90] -o OUT` |
| Is it connected? | `connections M --section S` → contacts, groups, overlap candidates |

4. **Anything else:** edit the `recipe.json` saved next to any result (or write one) and run `ldraw-xray board run recipe.json -o OUT`. See [recipes-and-python](recipes-and-python/SKILL.md).

## Selectors

`--highlight`, `--xray`, `--select`, `--moving` and `--hardware` take a selector. **Always single-quote it** (`*`, `!`, `|` are shell characters).

| Selector | Selects |
|---|---|
| `all` | every part |
| `section` | the submodel itself, when rendered in its parent |
| `line:12,15,20-24` | the parts on these lines of the source file |
| `step:3-5` | the parts added in these steps |
| `part:3001*` | parts by number; `*` is a wildcard and `.dat` is optional |
| `colour:15,4` | parts by LDraw colour code |
| `ref:chair.ldr` | an exact part or submodel name |

`|` adds, `!` removes; removals apply last; a selector with only removals starts from `all`.

```sh
--highlight 'part:3001*|colour:15'      # 2x4 bricks, plus anything white
--xray 'colour:15|!step:1'              # white parts, except those from step 1
--xray '!ref:8071 - cabin.ldr'          # everything except the cabin
```

Step numbers are the file's own, empty steps included (`sections` reports `empty_leading_steps`). An empty selection doesn't fail: the image notes say so.

## Rules that trip agents

- `--ghost` needs `--highlight`. `--xray` and `--stud-map` are exclusive.
- `--steps` needs an isolated section: no `--parent`, no `--highlight`, no `--ghost`.
- Bare `--parent` needs a unique parent; with several, the error lists them: pass one by name.
- Boards with more than 12 images need `--no-mosaic` (many `--steps`, many `--angles`).
- In a parent render, `--highlight` selects the parent's placements: use `section` to pick the whole submodel, not parts inside it.

## Reading the images

- **Magenta edges:** highlighted parts, or parts new in that step. **Pale grey:** ghosted context.
- **Neon-green rod:** the synthetic axis (not a part). **Green / olive dots:** confirmed / heuristic contacts. **Raspberry:** box-overlap candidates. Stud-map colours: `ldraw-xray palette`.
- LDraw −Y is up; `front` looks toward +Z; `right` shows the model's right side (from −X). Coordinates for `--point` / `--direction` are section coordinates in LDraw units.
- Views are framed independently: compare shapes across panels, not sizes. Pivot boards share one camera, so poses are comparable.
- `connections` and overlap candidates are evidence, not proof: Technic pin/axle mating isn't paired, and boxes overestimate rotated parts. Confirm visually before claiming a fit or a gap. Images and reports do not establish fit, clearance, travel or stability.

## Install

ldraw-xray needs three things it can't install for you:

1. **LeoCAD** (tested with 25.09) from [leocad.org](https://www.leocad.org). macOS: move `LeoCAD.app` to `/Applications`. Linux/Windows: put `leocad` on `PATH` or `export LEOCAD=/opt/leocad/LeoCAD-Linux-25.09-x86_64.AppImage`.
2. **The LDraw parts library:**

   ```sh
   mkdir -p ~/ldraw-lib && cd ~/ldraw-lib
   curl -LO https://library.ldraw.org/library/updates/complete.zip
   unzip complete.zip                      # creates ~/ldraw-lib/ldraw
   export LDRAW_DIR=~/ldraw-lib/ldraw      # e.g. in ~/.zshrc
   ```

3. **Python 3.12+ and [uv](https://docs.astral.sh/uv/)** (or `pipx`).

Then install the wheel from the [latest release](https://github.com/anteloc/ldraw-xray/releases/latest) (for version `X.Y.Z`):

```sh
uv tool install https://github.com/anteloc/ldraw-xray/releases/download/vX.Y.Z/ldraw_xray-X.Y.Z-py3-none-any.whl
# or
pipx install https://github.com/anteloc/ldraw-xray/releases/download/vX.Y.Z/ldraw_xray-X.Y.Z-py3-none-any.whl
```

Optional: the LDCad shadow library (a directory with `parts/`, or a ZIP / CSL file) makes `connections`, `axes` and connection overlays find more joints: `export LDRAW_SHADOW=~/LDCad/shadow` (several: separate with `:`, `;` on Windows).

| Setting | Flag | Environment | Default |
|---|---|---|---|
| Parts library | `--library` | `LDRAW_DIR`, then `LDRAWDIR` | required for rendering |
| LeoCAD | `--leocad` | `LEOCAD` | `leocad` on `PATH`, then `/Applications/LeoCAD.app` |
| Shadow libraries | `--shadow` (repeat), `--no-shadow` | `LDRAW_SHADOW` | built-in connector detection |
| Index cache | `--cache-dir` | `LDRAW_XRAY_CACHE` | your user cache directory |

Flags win over environment variables. Check the result with `ldraw-xray doctor`: it lists what it found and the versions in use.

## Which subskill

| Task | Subskill |
|---|---|
| Images of a section: views, in its parent, highlighted, x-rayed, build steps, stud map | [render-views](render-views/SKILL.md) |
| Ready-made labelled boards: overview, stud-map, xray, pivot, cutaway | [inspection-boards](inspection-boards/SKILL.md) |
| Rotation axes, poses, contacts, connected groups, overlaps | [pivots-and-connections](pivots-and-connections/SKILL.md) |
| Custom compositions, cameras, style, `board run`, Python `Session` | [recipes-and-python](recipes-and-python/SKILL.md) |

## Subskills

Read the one that matches your task:

- [render-views](render-views/SKILL.md): Renders a model or section with ldraw-xray render: --section, --view (home front back left right top bottom), --parent to see where a section is mounted, --highlight and --ghost to pick out parts, --xray to see through a shell, --steps for one image per source build step, --stud-map to colour parts by stud direction, plus --output, --force, --keep-intermediates and building a mosaic from render panels. Use when you need images of a section from given sides, its mounting in the parent, specific highlighted parts, what is hidden behind a shell, its build sequence or which way its studs point.
- [inspection-boards](inspection-boards/SKILL.md): Builds ready-made inspection boards with ldraw-xray board: overview (section in its parent and alone, optional --steps), stud-map, xray (as built vs x-rayed from three sides, --select, --colour Xray_Glass), pivot (axis marker and poses with one fixed camera) and cutaway (--view, --depths), plus mosaic.png layout, --no-mosaic, the 2-12 image limit and ldraw-xray mosaic. Use when you want several labelled views of a section on one image, a first orientation board, or a board to hand over as visual evidence.
- [pivots-and-connections](pivots-and-connections/SKILL.md): Finds rotation axes and checks connections: ldraw-xray axes (candidate point/direction from coaxial pins, axles and holes), board pivot (--point, --direction, --moving, --hardware, --angles, fixed shared camera), connections (contacts, connected groups, box-overlap candidates), and the recipe layers pose, axis, contacts, collisions and components, with their limits (Technic pin/axle mating not paired, boxes overestimate rotated parts, shadow library improves coverage). Use when showing how a part moves, locating a hinge axis, or checking whether parts touch, float or overlap.
- [recipes-and-python](recipes-and-python/SKILL.md): Reference for ldraw-xray recipes and the Python API: recipe.json fields (source, section, title, mosaic, mode, columns, panel_width, legend, style, panels), ordered layers and their options (highlight, ghost, steps, xray, recolour, stud_map, pose, axis, closeup, cutaway, components, contacts, collisions), scope, colours and swatches, views and explicit cameras (fixed, position/target/up/fov/orthographic, zplanes), pinned style defaults, stud-map colours, renderer limits, board run, and Session.render / Session.board with Style, Camera, XrayConfig and compose_mosaic. Use when a CLI flag cannot express the composition, when editing or replaying a saved recipe.json, or when scripting renders from Python.

## Source docs

Verbatim copies, for details not covered above:

- [AGENTS.md](references/AGENTS.md)
- [README.md](references/README.md)
