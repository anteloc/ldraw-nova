# Gear and axle module

Study gear stacks, axle joiners and the supports that register them to the surrounding gearbox.

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

A gear-and-axle module in the crawler crane transmission.

- Fixed structure: White crossbeam and bent support beams, once mounted in the parent gearbox.
- Moving elements: Geared shafts, inline axle links and the separate elevated clutch gear.
- Input: An exposed shaft driven by the parent gearbox; the isolated section does not identify a unique complete power path.
- Output: Gear and axle interfaces to the surrounding transmission.

Preserve gear positions, axle lengths, bushes and keyed orientations. Adapt the surrounding mounts and packaging first; retain the parent reference for exposed shafts.

## Parent context and source

42042 - gearbox.ldr supplies the rest of the multi-function gearbox and motor drive. The upper red clutch gear depends on that context.

Source: `42042-1.mpd` / `42042 - gearbox4.ldr`, SHA-256 `d53889036ecc71acb2d45de401e2b4d5e2875613a25a3c8959c2173c165c3b35`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank 1, relevance score 0.93). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export gear-reduction --outdir output/my-gear-reduction` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-gear-reduction/scene.plan.json --contacts none --output output/my-gear-reduction/my-gear-reduction.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

35 physical placements; 5 nonempty construction steps across 1 assembly section(s). Source checks pass. Python and LeoCAD BOMs match. See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
