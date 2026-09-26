# Single-cylinder piston and crank

Use dedicated piston, connecting-rod, crankshaft and cylinder parts; read the source and per-step parts list for internals hidden within a grouped step.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

Display engine intended to turn shaft rotation into piston reciprocation.

- Fixed structure: Cylinder and mounting cross blocks connect the engine to the chassis.
- Moving elements: Crankshaft pieces, connecting rod and piston.
- Input: External geared shaft connected to the parent kart drivetrain.
- Output: Reciprocating piston visible at the cylinder opening; this is a display-engine role.

Keep the crank, rod and piston together and preserve their phase in the source pose. Retain the embedded cylinder definition and inspect the internal steps before mounting the complete engine.

## Parent context and source

42048 - Race Kart.ldr supplies the surrounding drivetrain and chassis mounting. The extracted cylinder is an embedded DAT definition and must travel with the assembly.

Source: `42048-1.mpd` / `42048 - engine.ldr`, SHA-256 `b1da23cd1ebfa574d233e0ee042828fb83cdbcb15a967e071a29b5e6738e390d`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 1, relevance score 0.89). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export piston-crank --outdir output/my-piston-crank` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-piston-crank/scene.plan.json --contacts none --output output/my-piston-crank/my-piston-crank.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

19 physical placements; 4 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
