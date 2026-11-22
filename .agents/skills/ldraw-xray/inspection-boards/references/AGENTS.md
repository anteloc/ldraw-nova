# AGENTS.md — ldraw-xray

Gives you eyes on LDraw models (`.ldr` / `.mpd`): renders a model or one of its sections
(submodels) with LeoCAD, with highlighting, ghosting, x-ray, build steps, stud maps, poses and
cutaways, and lays the images out on a labelled board. Then you look at the PNGs.

Source files and the parts library are never modified. Human docs: [README.md](README.md). Recipe
format, layers, cameras, style: [docs/reference.md](docs/reference.md).

## Before you start

```sh
ldraw-xray doctor          # "renders": true means you can render
```

- In this repo, prefix commands with `uv run` (or use `.venv/bin/ldraw-xray`).
- If `renders` is false, read `errors`: LeoCAD, the LDraw library (`LDRAW_DIR`) or both are
  missing. Ask the user to install or configure them (README, "Install"). Don't download the
  library or install LeoCAD yourself unless asked.
- `sections`, `palette` and `mosaic` work without LeoCAD or a library.

## The contract

- Every command prints **one JSON object** on stdout. Paths in it are absolute.
- Errors are JSON on stderr: `{"error": "..."}`. Exit 2 = bad input or setup (fix the command);
  exit 1 = execution failed (LeoCAD, files). Error messages say what to change.
- Renders and boards return `images[]` (each with `image`, `shows`, `view`, `step`, `notes`,
  `warnings`) and, for boards with 2-12 images, `mosaic`. **Open those files to see the result.**
  Read `notes` and `warnings`: empty selections and skipped parts are reported there.
- An output directory that already holds results is refused; use a new one or `--force`.
- Each image takes a few seconds. Ask for the views you need, not all seven.

## Workflow

1. **List sections**: `ldraw-xray sections model.mpd`. Each has `name`, `kind`, `placements`,
   `steps` and `parents`. Pass the exact `name` to `--section` (quote it: names often have spaces).
2. **Get oriented**: one overview board shows the section in its parent and on its own.

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

4. **Anything else**: edit the `recipe.json` saved next to any result, or write one, and run
   `ldraw-xray board run recipe.json -o OUT`. Panels take ordered layers (`highlight`, `ghost`,
   `steps`, `xray`, `recolour`, `stud_map`, `pose`, `axis`, `closeup`, `cutaway`, `components`,
   `contacts`, `collisions`) and an optional `parent`, `view` or `camera`:

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

   Unknown fields are errors; options are JSON values, not strings. Details: docs/reference.md.

## Selectors

`all`, `section` (the section inside its parent), `line:12,20-24`, `step:3-5`, `part:3001*`
(glob, `.dat` optional), `colour:15,4`, `ref:wing.ldr` (exact part or submodel). `|` adds, `!`
removes; removals apply last; only-removals starts from `all`. Always single-quote them.

Line numbers are lines of the source file. Step numbers are the file's own, empty steps included
(`sections` reports `empty_leading_steps`).

## Rules that trip agents

- `--ghost` needs `--highlight`. `--xray` and `--stud-map` are exclusive.
- `--steps` needs an isolated section: no `--parent`, no `--highlight`, no `--ghost`.
- Bare `--parent` needs a unique parent; with several, the error lists them: pass one by name.
- Boards with more than 12 images need `--no-mosaic` (many `--steps`, many `--angles`).
- In a parent render, `--highlight` selects the parent's placements: use `section` to pick the
  whole submodel, not parts inside it.

## Reading the images

- Magenta edges: highlighted parts, or parts new in that step. Pale grey: ghosted context.
- Neon-green rod: the synthetic axis (not a part). Green / olive dots: confirmed / heuristic
  contacts. Raspberry: box-overlap candidates. Stud-map colours: `ldraw-xray palette`.
- LDraw −Y is up; `front` looks toward +Z; `right` shows the model's right side (from −X).
  Coordinates for `--point` / `--direction` are section coordinates in LDraw units.
- Views are framed independently: compare shapes across panels, not sizes. Pivot boards share one
  camera, so poses are comparable.
- `connections` and overlap candidates are evidence, not proof: Technic pin/axle mating isn't
  paired, and boxes overestimate rotated parts. Confirm visually before claiming a fit or a gap.

## Working on the code

```sh
uv sync --extra test
uv run pytest -q          # LeoCAD / library / shadow tests skip when those are unavailable
```

| Module | Role |
|---|---|
| `cli.py` | argparse commands → layers / presets → `Session` |
| `render.py`, `board.py` | `Session.render` / `Session.board`: validate, render, stage, publish |
| `recipe.py`, `presets.py` | recipe validation; recipes behind the `board` tasks |
| `layers.py`, `select.py` | layer operations; selector language |
| `mpd.py` | sections, steps, placements, parents |
| `leocad.py`, `camera.py`, `post.py` | LeoCAD calls, cameras, backdrop + outline |
| `library.py`, `config.py` | read-only library wrapper and cache; settings discovery |
| `connections.py`, `geometry.py` | contacts, groups, overlaps, axes |
| `mosaic.py`, `manifest.py`, `palette.py` | board image, provenance, inspection colours |

Releases are a pushed `vX.Y.Z` tag on `master` (see README, "Development"); don't tag or push
unless the user asks.
