# Worm-drive support module

Keep a worm shaft, its driven gear and retaining pieces together with their supporting layers.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

Worm-drive module for a tower-crane winding function.

- Fixed structure: Liftarms and cross blocks provide the mounting structure.
- Moving elements: Worm shaft and the separate axle carrying the eight-tooth gear.
- Input: Axle carrying the worm gear, interpreted from the source arrangement.
- Output: Eight-tooth gear axle; the winding drum and cable belong to the parent assembly.

Preserve the worm/gear placement, bush stack and the thin-beam layer. Copy the support geometry as a unit before designing a new external mount; no load-holding claim is made.

## Parent context and source

42042 - tower.ldr supplies the surrounding tower and remaining winding assembly.

Source: `42042-1_Tower-Crane.mpd` / `42042 - spoolwormgear.ldr`, SHA-256 `418b1b235c01b58a199e34953b5ff55f459188c73f5a4d45c6e8ad62149dee27`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 5, relevance score 0.93). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export worm-drive --outdir output/my-worm-drive` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-worm-drive/scene.plan.json --contacts none --output output/my-worm-drive/my-worm-drive.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

14 physical placements; 3 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
