# Geared turntable mount

Keep the two turntable halves, the driving gear and the base supports together while exposing the rotating attachment face.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

Geared rotating attachment in the rescue-vehicle assembly.

- Fixed structure: Open-centre beam frame and the supported lower turntable half.
- Moving elements: Driving gear shaft and the upper turntable half with its mounting ears.
- Input: Axle carrying the twelve-tooth gear.
- Output: Rotating upper turntable attachment face.

Preserve the matching turntable halves and driving gear position. Attach the stationary base and moving upper assembly to different surrounding components; review their appearance in the intended pose.

## Parent context and source

42068 - main.ldr supplies the external drive and attached structure.

Source: `42068-1.mpd` / `42068 - turntable.ldr`, SHA-256 `d9e5e14335324cebdf2204d998cc089ae15b4150193323813b4511d22d8c8239`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 1, relevance score 0.88). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export driven-turntable --outdir output/my-driven-turntable` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-driven-turntable/scene.plan.json --contacts none --output output/my-driven-turntable/my-driven-turntable.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

25 physical placements; 3 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
