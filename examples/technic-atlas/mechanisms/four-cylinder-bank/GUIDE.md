# Four-cylinder crank engine bank

Repeat a compact piston/rod/crank construction while preserving cylinder guides, phase and the geared input.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

Four dedicated pistons reciprocate through connecting rods around a shared crankshaft.

- Fixed structure: Cylinder heads and the bank’s static connectors; a new model must provide a supporting frame.
- Moving elements: Crank pieces, axle and 24T input gear; four separate connecting rods and four pistons.
- Input: The 24T gear/crankshaft interface, normally driven by the parent engine’s central 24T gear.
- Output: Four guided piston strokes with alternating source phases.

The parent supplies the central driving gear, frame and opposite banks. This 34-part extract is an engine core, not a freestanding supported engine.

## Adaptation ideas

Preserve the nominal 10-LDU throw, 40-LDU rods, head positions and source phase. Adapt the mounts and input route before changing the internals; use proper rotations for another bank.

Use it in an engine stand, compact compressor or exposed machinery bay. Pair two instances at measured angles for a wider engine, providing separate supports and one deliberate drive interface.

## Source and build order

Lower four-cylinder bank from Philippe Hurbain’s 42083 model, selected from `42083 - enginelower.ldr`. This is one repeated bank of the W16 studied in Mecha; the surrounding engine and its central drive are omitted.

Pages retain the source STEP groups; child assemblies have their own pages. These groups are source construction evidence, not a swept insertion check.

Read all four source groups. The first group already contains heads and parts of the crank mechanism together; inspect the part list for hidden rods and pistons. Pin-to-ball joints must remain seated while the bank is installed.

The pinned input has SHA-256 `08be58bada85635d22bdf4480541a788ba5e420967c4967474694a1c9c743748`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [four-cylinder-bank.provenance.json](provenance/four-cylinder-bank.provenance.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/four-cylinder-bank \
  --outdir output/my-four-cylinder-bank
./ldraw-agent build output/my-four-cylinder-bank/scene.plan.json --contacts none \
  --output output/my-four-cylinder-bank/my-four-cylinder-bank.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

34 physical placements; 4 nonempty source groups
across 1 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

The slider-crank construction is centred and planar. Source phase is LEGO mechanism geometry, not combustion timing; bore clearance and load capacity are not certified.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
