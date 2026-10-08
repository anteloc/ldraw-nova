# Orientation-preserving four-bar lift

Use equal cranks and matched pivot spacing to lift a panel while retaining its orientation.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

A paired-crank parallelogram raises the wing/payload along a shallow arc without tilting it in the studied arrangement.

- Fixed structure: Retained mounting frame and axis-spacing links; the upper pivot is assumed fixed by the sibling rig.
- Moving elements: Upper/lower cranks, struts and wing panel, with two closing rear rods and short links.
- Input: The lower crank/axle rotation; the complete key-driven tilt actuator is not retained or solved.
- Output: A level payload carried through a shallow arc, including a small sideways displacement.

The 119-part selection is a standalone study with partial surrounding mounts. It assumes a fixed upper pivot and omits the complete key-driven wing mechanism and nearby bodywork obstacles.

## Adaptation ideas

Preserve the nominal 40-LDU sides in the YZ linkage plane, real axis spacing and roughly 120-LDU rear rods. Do not mistake an off-plane spatial diagonal for a crank radius. Add a frame that physically fixes both pivots.

Adapt it into a service deck, cargo platform or retractable equipment tray. Broaden the payload only after adding lateral support and clearance for its curved path.

## Source and build order

Unchanged Mecha extract `42083-mechanisms/wing/source/42083-wing.mpd` derived from Hurbain’s model. Its original occurrence comments and retained identity map preserve the selection history.

The source is a flat one-group selection: these pages show the retained assembly from several views, not a recovered insertion sequence.

The sibling source is flattened into one group. It supplies identities and final placement, not a recovered build sequence. Insert pins and rods before closing a new paired support frame.

The pinned input has SHA-256 `e978e97ddb0fb19aa67856b09879abebea8e39f5c97b391649bbae905530c686`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [four-bar-lift.provenance.json](provenance/four-bar-lift.provenance.json) · [four-bar-lift.idmap.json](provenance/four-bar-lift.idmap.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/four-bar-lift \
  --outdir output/my-four-bar-lift
./ldraw-agent build output/my-four-bar-lift/scene.plan.json --contacts none \
  --output output/my-four-bar-lift/my-four-bar-lift.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

119 physical placements; 1 nonempty source groups
across 1 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

The upper-axis restraint is an assumption; key-driven tilt is not established. Source clearance limits belong to the original bodywork, and this source-pose study does not demonstrate motion.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
