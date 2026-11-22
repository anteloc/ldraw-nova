# ldraw-xray

Look inside LDraw models (`.ldr` / `.mpd`). ldraw-xray renders a model, or one of its submodels,
with [LeoCAD](https://www.leocad.org) and adds what plain renders don't show:

- **highlight** parts with magenta edges and **ghost** everything else;
- **x-ray** a shell to see the mechanism behind it;
- show a submodel **in its parent**, where it is mounted;
- replay the **build steps** of a submodel, one image per step;
- colour parts by **stud direction**, mark **axes**, **pose** moving parts, **cut** the model open;
- put several views on one labelled **inspection board** (`mosaic.png`).

Your model and parts library are never modified. Every command prints JSON, so it's equally easy
to use by hand, from scripts, or by AI agents (see [AGENTS.md](AGENTS.md)).

## Install

You need three things the tool can't install for you, then the tool itself.

### 1. LeoCAD

ldraw-xray drives LeoCAD to render. Download it from [leocad.org](https://www.leocad.org)
(tested with **25.09**).

- **macOS:** move `LeoCAD.app` to `/Applications`; it's found there automatically.
- **Linux / Windows:** put `leocad` on your `PATH`, or point to it:

  ```sh
  export LEOCAD=/opt/leocad/LeoCAD-Linux-25.09-x86_64.AppImage
  ```

### 2. The LDraw parts library

```sh
mkdir -p ~/ldraw-lib && cd ~/ldraw-lib
curl -LO https://library.ldraw.org/library/updates/complete.zip
unzip complete.zip                      # creates ~/ldraw-lib/ldraw

export LDRAW_DIR=~/ldraw-lib/ldraw      # e.g. in ~/.zshrc
```

`LDRAWDIR` works too, if you already use it for other LDraw tools.

### 3. Python 3.12+ and uv

[uv](https://docs.astral.sh/uv/) (or `pipx`) installs the tool in its own environment.

### Install ldraw-xray

The [latest release](https://github.com/anteloc/ldraw-xray/releases/latest) shows the exact
command; for version `X.Y.Z` it is:

```sh
uv tool install https://github.com/anteloc/ldraw-xray/releases/download/vX.Y.Z/ldraw_xray-X.Y.Z-py3-none-any.whl

# or, with pipx
pipx install https://github.com/anteloc/ldraw-xray/releases/download/vX.Y.Z/ldraw_xray-X.Y.Z-py3-none-any.whl
```

### Check the setup

```sh
ldraw-xray doctor
```

`doctor` lists what it found and what's missing. You're ready when it says `"renders": true`.

### Optional: LDCad shadow library

`connections`, `axes` and the connection overlays find more joints with the shadow library that
ships with [LDCad](https://www.melkert.net/LDCad): a directory with `parts/`, or a ZIP / CSL file.

```sh
export LDRAW_SHADOW=~/LDCad/shadow      # several: separate with ':' (';' on Windows)
```

### All settings

Flags win over environment variables. Set the variables once, in your shell profile.

| Setting | Flag | Environment | Default |
|---|---|---|---|
| Parts library | `--library` | `LDRAW_DIR`, then `LDRAWDIR` | required for rendering |
| LeoCAD | `--leocad` | `LEOCAD` | `leocad` on `PATH`, then `/Applications/LeoCAD.app` |
| Shadow libraries | `--shadow` (repeat), `--no-shadow` | `LDRAW_SHADOW` | built-in connector detection |
| Index cache | `--cache-dir` | `LDRAW_XRAY_CACHE` | your user cache directory |

## Quick start

The examples and pictures below use `8071.mpd`, a Technic bucket truck whose sections include
`8071 - cabin.ldr`, `8071 - front-axle.ldr` and `8071 - crane.ldr`. Quote names with spaces.

```sh
# what's in the model: sections (submodels), their steps and parents
ldraw-xray sections 8071.mpd

# render the whole model
ldraw-xray render 8071.mpd --output out/

# render one section, from two sides
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --view home --view front --output out/cabin/
```

![The whole 8071 truck, home view](img/render.png)

Open `out/cabin/panels/*.png`. Every command prints a JSON result with the paths of what it
wrote:

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

`--section` takes a name from `sections`. Without it you get the root model. Views are `home`
(LeoCAD's default 3/4 view), `front`, `back`, `left`, `right`, `top` and `bottom`.

## Ways to look inside a model

### Highlight and ghost

Magenta edges on selected parts; `--ghost` fades the rest so they stand out.

```sh
# the steering parts of the front axle, everything else ghosted
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' \
  --highlight 'ref:8071 - steering-shaft.ldr|ref:steerArm.ldr' --ghost --output out/

# the parts added in step 3
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --highlight 'step:3' --output out/
```

![Front axle: steering shaft and arms highlighted, the rest ghosted](img/highlight-ghost.png)

### A section in its parent

`--parent` renders the parent model, so you see where the section sits. Highlight `section` to
pick it out:

```sh
# the front axle inside the truck, everything around it ghosted
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --parent --highlight section --ghost --output out/

# a section used in several places: name the parent
ldraw-xray render 8071.mpd --section '8071 - headlight-lamp.ldr' --parent headLightLeft.ldr \
  --highlight section --output out/
```

![The front axle highlighted inside the ghosted truck](img/parent.png)

Bare `--parent` works when there's only one parent; otherwise the error lists them:

```
{"error": "Multiple parents of '8071 - headlight-lamp.ldr'; choose --parent NAME: headLightLeft.ldr, headLightRight.ldr"}
```

### X-ray: see through a shell

`--xray` makes the selected parts transparent, to see what's behind them. Select the shell by
submodel, colour, part, step or line ([selectors](#select-parts)).

```sh
# the cabin turned to clear glass, seen from the top
ldraw-xray render 8071.mpd --xray 'ref:8071 - cabin.ldr' --view top --output out/

# x-ray the cabin and highlight the front axle under it
ldraw-xray render 8071.mpd --xray 'ref:8071 - cabin.ldr' --highlight 'ref:8071 - front-axle.ldr' --output out/

# x-ray the whole cabin except the seats and steering wheel
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --xray '!ref:chair.ldr|!ref:steeringWheel.ldr' --output out/
```

For a side-by-side comparison, the `xray` board shows the model as built, then x-rayed from
three sides. `--colour` picks the glass: `47` (Trans-Clear, default), any LDraw colour code, or
`Xray_Glass`, a tinted glass that stands out more:

```sh
ldraw-xray board xray 8071.mpd --select 'ref:8071 - cabin.ldr' --colour Xray_Glass --output out/xray/
```

![X-ray board: the truck as built, then with the cabin as blue glass from three sides](img/board-xray.png)

### Build steps

One image per source step, with the parts new in that step edged in magenta:

```sh
# every step with parts
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --steps --output out/steps/

# just these, side by side on one image
ldraw-xray render 8071.mpd --section '8071 - front-axle.ldr' --steps 3,6,10,15 --output out/some-steps/
ldraw-xray mosaic out/some-steps/manifest.json --output out/steps.png
```

![Front axle, source steps 3, 6, 10 and 15](img/steps.png)

Steps keep the numbering of the source file. They render the section on its own (no `--parent`)
and can't be combined with `--highlight` or `--ghost`.

### Stud directions

Colours each part by where its studs point (up, ±X, ±Z, down, at an odd angle). Handy for SNOT
(studs-not-on-top) building:

```sh
ldraw-xray render 8071.mpd --section '8071 - cabin.ldr' --stud-map --output out/
ldraw-xray palette          # what each colour means
```

![Cabin coloured by stud direction](img/stud-map.png)

`--stud-map` and `--xray` are alternatives: use one per render.

## Inspection boards

A board is a ready-made set of views on one labelled `mosaic.png`. Each task has its own options;
see `ldraw-xray board TASK --help`.

```sh
# where it sits, what it looks like; --steps adds build steps
ldraw-xray board overview 8071.mpd --section '8071 - crane.ldr' --output out/overview/

# stud directions, plus the section in its parent
ldraw-xray board stud-map 8071.mpd --section '8071 - cabin.ldr' --output out/studs/

# as built vs. x-rayed (pictured above)
ldraw-xray board xray 8071.mpd --select 'ref:8071 - cabin.ldr' --output out/xray/

# the crane slewing on its turntable: axis marker, then poses with one fixed camera
ldraw-xray board pivot 8071.mpd --section '8071 - crane.ldr' --point 0 -100 30 --direction 0 1 0 \
  --moving '!ref:craneBase.ldr' --angles 0 45 90 --output out/pivot/

# slices through the cabin at 35%, 50% and 65% depth, seen from the front
ldraw-xray board cutaway 8071.mpd --section '8071 - cabin.ldr' --view front --depths 0.35 0.5 0.65 --output out/cuts/
```

`overview`, `stud-map` and `pivot` add the parent automatically when it's unique; pass
`--parent NAME` when there are several. `--no-mosaic` writes the panels without `mosaic.png`.

![Overview board: the crane in the truck, then on its own from two sides](img/board-overview.png)

![Pivot board: the turntable axis, then the boom at 0, 45 and 90 degrees](img/board-pivot.png)

![Cutaway board: the cabin uncut, then sliced at three depths](img/board-cutaway.png)

### Finding a pivot

Not sure where a hinge axis is? `axes` proposes rotation axes from coaxial connectors (pins,
axles, holes), with `point` and `direction` ready to paste into `board pivot`:

```sh
ldraw-xray axes 8071.mpd --section '8071 - crane.ldr'
```

Coordinates are the section's own, in LDraw units, with −Y up.

### Recipes: tweak and replay

Every render and board saves a `recipe.json` that reproduces it. Edit it (labels, views, layers,
colours, cameras, image size) and run it again:

```sh
ldraw-xray board overview 8071.mpd --section '8071 - crane.ldr' --output out/overview/
$EDITOR out/overview/recipe.json
ldraw-xray board run out/overview/recipe.json --output out/overview-v2/
```

Recipes can do more than the flags: recolour selections, close-ups, contact markers, overlap
candidates, connected groups, custom cameras. The full format is in the
[reference](docs/reference.md).

## Select parts

`--highlight`, `--xray`, `--select`, `--moving` and `--hardware` take a selector. Quote it in
the shell, especially when it has `*`, `!` or `|`.

| Selector | Selects |
|---|---|
| `all` | every part |
| `section` | the submodel itself, when rendered in its parent |
| `line:12,15,20-24` | the parts on these lines of the file |
| `step:3-5` | the parts added in these steps |
| `part:3001*` | parts by number; `*` is a wildcard and `.dat` is optional |
| `colour:15,4` | parts by LDraw colour code |
| `ref:chair.ldr` | an exact part or submodel name |

Combine them: `|` adds, `!` removes. Removals apply last; a selector with only removals starts
from `all`.

```sh
--highlight 'part:3001*|colour:15'      # 2x4 bricks, plus anything white
--xray 'colour:15|!step:1'              # white parts, except those from step 1
--xray '!ref:8071 - cabin.ldr'         # everything except the cabin
```

An empty selection doesn't fail: the image notes say so.

## Check connections

```sh
# contacts between parts, connected groups and overlap candidates
ldraw-xray connections 8071.mpd --section '8071 - front-axle.ldr'

# proposed rotation axes
ldraw-xray axes 8071.mpd --section '8071 - front-axle.ldr'
```

Several groups can mean a loose part, or a joint the detector doesn't know (Technic pin/axle
mating isn't paired yet). Overlap candidates come from bounding boxes and need a visual check.
These reports are clues, not proof of fit or stability.

## Output

```
out/
├── panels/          # one PNG per image: 01-home-view.png, 02-front-view.png, ...
├── mosaic.png       # boards with 2-12 images
├── recipe.json      # replay with `ldraw-xray board run`
└── manifest.json    # what each image shows, notes, versions, source hash
```

- An existing output is not overwritten: add `--force`. Unrelated files in the folder are kept.
- `--keep-intermediates` also keeps the raw LeoCAD images and generated models, for debugging.
- `ldraw-xray mosaic out/manifest.json --output board.png` builds a mosaic from any render.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | done; the JSON result is on stdout |
| 1 | rendering failed (LeoCAD, files); the error is JSON on stderr |
| 2 | bad input or setup: missing file, unknown section, bad selector, no library |

`sections`, `palette` and `mosaic` work without LeoCAD or a parts library. `python -m ldraw_xray`
is the same as `ldraw-xray`.

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

`XrayConfig`, `Style`, `Camera` and `compose_mosaic` are public too; see the
[reference](docs/reference.md).

## Development

```sh
git clone https://github.com/anteloc/ldraw-xray && cd ldraw-xray
uv sync --extra test              # .venv with the package installed in editable mode
uv run ldraw-xray doctor
uv run pytest                     # LeoCAD / library / shadow tests skip when those are missing
uv build --wheel                  # dist/ldraw_xray-<version>-py3-none-any.whl
```

To publish a release, tag a commit on `master` and push the tag:

```sh
git tag v0.9.0
git push origin v0.9.0
```

The `release` workflow runs the tests, builds the wheel (its version comes from the tag, so there
is nothing to bump), and attaches it to the `v0.9.0` release. Tags on commits that aren't on
`master` are refused.

## License

Code: [AGPL-3.0](LICENSE). Documentation: [CC BY-SA 4.0](CC-BY-SA-4.0). The mosaic composer and
pyldraw3 connection-frame adapter are adapted from ldraw-nova by the same author.
