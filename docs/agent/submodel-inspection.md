# Inspect submodels with ldraw-xray

[ldraw-xray](https://github.com/anteloc/ldraw-xray) renders a source section with
LeoCAD:

- isolated, or highlighted inside its parent;
- step by step;
- see-through or cut away;
- coloured by stud direction;
- posed about an axis.

It then composes the views into a labelled board. Nova installs it as a core
dependency. `./ldraw-xray` runs it from the project environment, with the same
`LDRAW_DIR`, `LDRAW_SHADOW` and `LEOCAD` settings as `./ldraw-agent`. Like
`./ldraw-agent`, it defaults to the bundled `data/offLibShadow`.

xray only shows synthetic copies; it never judges a model, and it never changes
a source or the library. You decide what a picture means, and you check the
source before claiming a fit.

```sh
./ldraw-xray doctor        # library, shadow, LeoCAD and the available layers
```

## Workflow

```mermaid
stateDiagram-v2
  direction LR
  [*] --> Find: discover search, DB description, corpus scan
  Find --> Overview: ./ldraw-xray sections, then board overview
  Overview --> Find: wrong part, hidden, or a near-duplicate
  Overview --> Targeted: question still open
  Overview --> Record: construction and parent role are clear
  Targeted --> Record: board answers it
  Record --> Review: recipe and README row in examples/submodel-candidates
  Review --> Find: user drops it
  Review --> Promote: kept, then manual prepare, review, export and atlas
  Promote --> [*]
```

Start from the [discovery guide](reference-discovery.md) or a direct DB/corpus
query. Then list the sections, and render an overview of the candidate:

```sh
./ldraw-agent discover search submodels 'rear axle differential' --engine fts --limit 8
./ldraw-xray sections data/models-annotated/42075-1.mpd
./ldraw-xray board overview data/models-annotated/42075-1.mpd \
  --section '42075 - rearaxle.ldr' --steps 3,5 --output output/inspect/42075-rearaxle
```

The overview board shows:

- the section highlighted in its unique parent, with the rest ghosted;
- an isolated view;
- the requested source steps.

Open `mosaic.png` first, then the full-size `panels/*.png` for small connections.
The command prints each image with what it shows. `manifest.json` records:

- the source hash and the parent placements;
- each panel's camera, layers and LeoCAD arguments.

## Which board answers which question

```mermaid
flowchart TD
  Q{What do you need to see?}
  Q -->|where it sits, what it meets| A["board overview<br/>(parent: highlight + ghost)"]
  A -.->|parent is huge| A2["recipe panel with an explicit camera<br/>or a closeup layer"]
  Q -->|how it is built| B["board overview --steps 3,7<br/>render --steps"]
  Q -->|what a thin shell hides| X["board xray --select SHELL --highlight CORE"]
  X -.->|shell is thick or layered| C["board cutaway --view front<br/>or steps instead"]
  Q -->|SNOT: which way studs face| N["board stud-map<br/>(section coordinates + parent)"]
  Q -->|how a part turns| V["axes proposes lines;<br/>board pivot --point --direction --moving"]
  Q -->|whether parts touch| K["connections; recipe layers<br/>contacts, components, collisions"]
```

Every board writes a replayable `recipe.json`. Edit a copy to choose panels,
labels, layers or cameras, then render it with `./ldraw-xray board run
RECIPE --output DIR`. The [xray reference](https://github.com/anteloc/ldraw-xray/blob/master/docs/reference.md)
lists every layer and option. The `./ldraw-xray --help` and
`./ldraw-xray board TASK --help` outputs list the flags.

Selectors pick parts:

| Selector | Picks |
|---|---|
| `section` | the inspected section's placements inside its parent |
| `step:3-5` | source steps, numbered over every `0 STEP` and `0 ROTSTEP` |
| `line:12,15` | source-file line numbers |
| `part:3001*` | part references, by glob |
| `colour:15,4` | colour codes on placement lines |

`|` adds a term and `!` excludes one. For example, `'!part:3894'` picks
everything except the bearing bricks.

## Reading the images

| You see | It means |
|---|---|
| Magenta edges | Highlighted: new in this step, or selected. The fill keeps the part's colour |
| Pale grey, see-through parts | Ghosted context |
| Neon-green rod `#39FF14` | Synthetic axis marker, not a part |
| Lilac, rose, vermilion, electric blue, aqua, lime, violet | Stud map: up, +X, −X, +Z, −Z, down, odd angle |
| Small green / olive spheres | Detected contacts: confirmed / heuristic |
| Raspberry parts | Overlap candidates (box overlap without a detected contact) |
| Dark 2 px outline | Traced silhouette, added after rendering |

Every swatch is deliberately ΔE ≥ 16 from every `LDConfig.ldr` colour, so a
recoloured part is never mistaken for a real colour. LDraw −Y is up, and the
front view looks toward +Z. View names follow LeoCAD: `right` shows the model's
right side, from −X.

## What the candidate reviews taught

These come from the 30 reviewed [submodel candidates](../../examples/submodel-candidates/README.md):

- **Check the parent before trusting a description.**
  - Four of five DB descriptions were wrong in the second batch, and many SNOT
    descriptions were wrong or empty.
  - For example, "dashboard and headlight nacelle" is a motorcycle drive cover,
    and "radial engine" is a tail rudder.
- **The parent may supply parts.** The 8081 front axle's rack meets an 8T pinion
  that is placed in the frame, not in the axle.
- **Many walls and silhouettes are built flat and stood up by the parent's
  matrix.** A stud map in section coordinates then shows "all up". Read
  `parent_placements` in the manifest, or show the section in its parent.
- **Prefer steps to x-ray when a shell is thick or layered.** X-ray paid off for a
  thin shell over a few distinctively coloured parts: the V8 crank under its
  cylinder banks.
- **Pick panels that differ.** The last source step usually looks like the
  finished isolated view. Boards report near-identical pairs as
  `duplicate_panels`.
- **Moving parts get the three-pose sweep.** Mark the axis, and render 0°, 45°
  and 90° with one fixed camera in `analysis` mode.

## Record a candidate

Add a kept candidate to [`examples/submodel-candidates`](../../examples/submodel-candidates/README.md):

1. Copy the board's `recipe.json` to `recipes/<id>.json`.
   - Make `source` relative to the recipe, e.g.
     `../../../data/models-annotated/42075-1.mpd`.
   - Keep only the panels that taught something.
   - Write labels that say what to look at.
2. Add a `candidates.json` row with the source, section, SHA-256, parent, family,
   lesson and recipe paths.
3. Add a README entry: construction, what the parent supplies, the corrected
   description, and what remains unverified.

`tests/test_submodel_candidates.py` checks that every source still matches its
hash and that every recipe loads.

Promotion into an atlas follows [build manuals §4](build-manuals.md#4-review-export-and-add-to-an-atlas).
xray boards supplement that review; they do not replace it.

## Limits

- Renders show geometry. They do not prove clutch, clearance, travel or stability.
- xray's contact overlays use pyldraw3 with a subset of nova's connector adapter.
  - Technic pin/axle mating is not paired, so a pin-mounted part can appear as
    its own "floating" group.
  - Nova's fixes for 6014 wheel axes and deep stud sockets are missing.
  - Overlap candidates come from axis-aligned boxes.
  - Use nova's [validation](validation.md) for physical claims.
- Poses are rigid re-placements: clearance is not checked.
- A recipe cannot remove arbitrary parent placements. Show a selection in a
  ghosted parent with a close-up instead.
