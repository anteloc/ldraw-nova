# Steering rack carriage

A steering reference may contain the sliding rack and carrier while its driving pinion belongs to the parent.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

Rack carriage for the tractor steering system.

- Fixed structure: Carrier beam and cross blocks provide the surrounding mounting arrangement.
- Moving elements: Toothed rack and its associated steering connections; confirm the assembled relationships in the vehicle.
- Input: Mating pinion supplied by 9393 - vehicle.ldr; no pinion is included in this extracted section.
- Output: Lateral rack movement to the steering system, as interpreted from its intended role.

Treat this as a rack carriage, not a complete steering system. Include the matching pinion and parent supports when adapting it. Preserve the toothed side, axle stops and intended sliding space.

## Parent context and source

9393 - vehicle.ldr supplies the driving gear, vehicle mounts and the remaining wheel-steering connections.

Source: `9393-1.mpd` / `9393 - steering.ldr`, SHA-256 `6f62ffdb2eb3fd4d2ff8d4a2faba218ae2a435db83151cdbe14b6b85e936f19a`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 1, relevance score 0.92). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export steering-rack --outdir output/my-steering-rack` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-steering-rack/scene.plan.json --contacts none --output output/my-steering-rack/my-steering-rack.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

10 physical placements; 3 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
