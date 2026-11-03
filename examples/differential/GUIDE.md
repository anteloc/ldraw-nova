# Differential in an axle frame

Inspect the internal bevel gear arrangement through the open carrier and source part list; preserve both axle outputs and their supports.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

Differential and drive gearing for the front axle of a car.

- Fixed structure: Open rectangular frame and its beam mounts form the supporting structure.
- Moving elements: Differential carrier, internal bevel gears, axle outputs and mating drive gears.
- Input: Drive gear arrangement at the differential carrier, interpreted from source placement.
- Output: Two axle shafts leading to the front-wheel drivetrain.

Retain the differential internals, axle insertion depths and surrounding frame. Place the complete axle module first and adapt its exterior supports; input/output behavior has not been analytically verified.

## Parent context and source

42083 - frontaxle.ldr supplies the surrounding axle, wheel connections and chassis context.

Source: `42083-1.mpd` / `42083 - frontaxlediff.ldr`, SHA-256 `72df8a1a852d6584eeba935320de411b9dc9dc23582177336341af68156469db`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 1, relevance score 0.92). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export differential --outdir output/my-differential` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-differential/scene.plan.json --contacts none --output output/my-differential/my-differential.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

29 physical placements; 4 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
