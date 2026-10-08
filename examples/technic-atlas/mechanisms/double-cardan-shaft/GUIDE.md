# Paired Cardan drive shaft

Route an offset drive through two yokes-and-crosses joints while retaining the intermediate fork phase.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

Two universal joints connect parallel end axes through an angled intermediate axle.

- Fixed structure: No fixed bearings are retained in this seven-part selection; end supports belong to the two parent gearboxes.
- Moving elements: Four yokes, two crosses and the intermediate axle. Crosses and yokes have distinct joint axes.
- Input: The first end yoke, originally source index 199 in the selected rear-axle section.
- Output: The opposite end yoke, originally source index 194, leading into the sequential gearbox.

Both gearbox supports, adjoining input/output axles and their retention are omitted. A new frame must hold the end axes at the measured locations without obstructing fork swing.

## Adaptation ideas

Preserve joint centres, matched bend angles and fork phase. Use the source frame as a positioning reference, then inspect actual axle sockets before adding new supports. Never treat coaxial bearings as axle-locked parts.

Use it to pass a drive around a crossmember or between offset machinery modules. Make the drive path visible through an open side of the frame; size the supports around the joint centres.

## Source and build order

Seven source placements 194–200 from `42110 - rearaxle.ldr`, corresponding to Mecha full-model paths `0/1/194` through `0/1/200`. The section frame is preserved; these indices are not Nova’s later flattened occurrence indices.

The source is a flat one-group selection: these pages show the retained assembly from several views, not a recovered insertion sequence.

All seven placements belong to one source group, so no substep insertion sequence is claimed. Study the two crosses and the axle engagement before adding the external bearings and end retainers.

The pinned input has SHA-256 `64923a35383837e8748e94878b7aae70806688ed9ecd8edaa9198df08aee8d96`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [double-cardan-shaft.provenance.json](provenance/double-cardan-shaft.provenance.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/double-cardan-shaft \
  --outdir output/my-double-cardan-shaft
./ldraw-agent build output/my-double-cardan-shaft/scene.plan.json --contacts none \
  --output output/my-double-cardan-shaft/my-double-cardan-shaft.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

7 physical placements; 1 nonempty source groups
across 1 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

The sibling’s equal-speed far-end relation depends on equal bends, parallel end axes and corrected fork phase. This static source extract is not a moving-suspension or universal constant-velocity solution.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
