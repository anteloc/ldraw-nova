# Reference atlas

Start with the [offline example gallery](index.html): **21 inspected source constructions**, with seven rendered views each, editable placement plans, measured cards and specific adaptation notes. Two [parameterized recipes](#parameterized-recipes) demonstrate rebuilding a construction for a different height and palette.

The broader [library manifest](library.manifest.json) selects **200 submodels and 20 whole models** across architecture, street fittings, foliage, vehicles, aircraft, boats and trains. Its generated [220-reference gallery](../../output/reference-library/index.html) uses home/front/right/top by default. The large gallery is generated into ignored `output/`; the curated examples and their images are retained here.

```sh
./ldraw-agent examples --family reference --limit 8
./ldraw-agent examples --family reference 'aircraft' --limit 5
./ldraw-agent examples --family reference --scale microscale
.venv/bin/python examples/reference-atlas/generate.py --jobs 3
```

The shared generator resumes completed cards. Use `--views home front back right left top bottom` for seven views of the library, or `--manifest curated.manifest.json` with a separate `--outdir` for the smaller selection. Run from the repository root and use the complete manifest path, for example `examples/reference-atlas/curated.manifest.json`. Preparing the library requires the original annotated sources, the installed parts and LeoCAD; rebuilding a retained example plan uses its local attributed source copy.

## Choose a useful construction

| Need | Examples | What to learn |
|---|---|---|
| Street details | [Winter lamp](winter-lamp/README.md), [globe lamp](ornamental-lamp/README.md), [bench](park-bench/README.md) | Thin posts, transparent lights, decorative part reuse and shaped seating |
| Organic shapes | [Small tree](small-ornamental-tree/README.md), [woodland tree](layered-tree/README.md) | Tapered trunks, angled foliage and canopy clearance |
| Architecture | [Stairs](moulded-staircase/README.md), [window](shuttered-window/README.md), [timbered wall](timbered-wall/README.md), [arch](classical-arch-bay/README.md) | Dedicated moulds, open profiles, shutters and cornice shadow lines |
| Exterior interfaces | [Clip panel](arched-clip-panel/README.md), [railing](fire-escape-railing/README.md), [loading ramp](truck-loading-ramp/README.md) | Small clips, bars and hinges; inspect the adjoining construction |
| Aircraft | [Engine](airliner-engine/README.md), [wing](hinged-wing/README.md), [fin](sloped-tail-fin/README.md), [wheel bogie](airliner-wheel-bogie/README.md) | Turbine detail, tapered planforms, thin fins and compact wheel fittings |
| Road and space vehicles | [Classic truck](classic-truck-cab/README.md), [mini truck](mini-truck-cab/README.md), [wheel module](spacecraft-wheel-module/README.md), [cockpit shell](rounded-cockpit-shell/README.md) | Distinct scales, dedicated glazing, open chassis and curved bodywork |
| Boats | [Research-ship bow](faceted-ship-bow/README.md) | Sideways slopes and coordinated colour bands around a small hull |

Open the images, then read the guide and `card.json`. Each source example includes its actual part inventory, local bounds, parent placement matrices, source hash, author/licence headers, repair log, connection analysis and visual review. The recorded review names only the views actually inspected; rendering seven images does not mean seven were reviewed.

```sh
./ldraw-agent build examples/reference-atlas/airliner-engine/scene.plan.json \
  --output output/airliner-engine-example.mpd
./ldraw-agent inspect output/airliner-engine-example.mpd --contacts all
```

To integrate a reference, include its plan and place its first section, or import its namespaced `source.mpd` as a plan asset. The `source_origin` frame is a positioning aid. It is not an inferred mechanical connector. Preserve the source author and licence; measure any new attachment and check the combined model. Images are framed independently, so compare dimensions rather than apparent image size.

All 21 exported plans were rebuilt, passed assembly and geometry error checks, and matched the recorded LeoCAD BOM. Eleven have one optimistic connection group; ten retain multiple groups that their guides explicitly identify. These examples teach construction and visual design; contact coverage, material clearance, strength and stability still need review in the new model. See [verification.json](verification.json).

The broad gallery also retains problematic sources for inspiration: 26 of its 220 entries need preparation, and three have a Python/LeoCAD BOM discrepancy. Their cards show these failures. Eight of the 36 candidates inspected with contacts had geometry errors and were excluded from the curated atlas. This keeps useful visual precedents available without presenting them as ready assemblies.

## Parameterized recipes

- [Arcade bay](recipes/arcade-bay/README.md): change the pier height and cornice colours, preserving a four-stud arch and a shared foot plate.
- [Street lantern](recipes/street-lantern/README.md): change round-brick post courses and palette, retaining the centred base, open-stud collar and transparent light.

```sh
.venv/bin/python examples/reference-atlas/recipes/arcade-bay/generate.py \
  --height 5 --render --outdir output/taller-arcade
.venv/bin/python examples/reference-atlas/recipes/street-lantern/generate.py \
  --height 7 --colour 0 --accent 71 --render --outdir output/taller-lantern
```

The default, two-course and seven-course forms pass geometry error checks with one optimistic connection group. Their plans retain the construction-source credits. Unchanged OMR submodels use the shared extractor and placement plans; only selected adaptable constructions need their own generator.

For new searches, preparation and review/export commands, follow the [agent workflow](../../docs/agent/reference-discovery.md).
