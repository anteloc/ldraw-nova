# Sculpture model example

The web help image uses this [Pikachu model from BrickBuilderAI](https://brickbuilder.ai/generated-model?id=4121b49f-7e0a-482b-9e4e-7148a5250f04).
Open **Export → LDraw (.ldr)** on that page to download it. The example importer
recovers the exact coloured cell footprints from BrickBuilder's six rectangular
brick sizes, without an AI request or an added display base.

From the toolkit root, with the `sculpture` extra installed and `LDRAW_DIR` set:

```sh
.venv/bin/python examples/sculpture/generate.py ~/Downloads/Surpised_Pikachu.ldr
./ldraw-agent sculpture output/sculpture-example/pikachu.voxels.json --output output/sculpture-example/pikachu.mpd --title "Pikachu sculpture" --report output/sculpture-example/checks.json
./ldraw-agent render output/sculpture-example/pikachu.mpd --outdir output/sculpture-example/render --views home right
```

The same packing, support repair and connected instruction ordering run on the
recovered cells. The repaired JSON and matching revision manifest enable the web
Sculpture editor. These are connectivity checks, not a physical load certificate.
The download remains the original export; the rebuilt model may include support
cells added by the converter.
