# Independent wishbone suspension

Study four wheel corners, parallel wishbones, guide links, matching half-shafts and paired shocks with their mounting frame.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

Four independent wheel corners use equal parallel upper/lower wishbones and two shocks per corner.

- Fixed structure: The retained central frame and suspension pivots; some guide-link and Cardan boundary holders are absent.
- Moving elements: Wishbones, knuckles, hubs/wheels, guide links and articulating half-shafts; shock cylinders pivot and rods slide in the intended mechanism.
- Input: Independent wheel rise at each corner; the static source is at full droop, not normal ride height.
- Output: Wheel rise with lateral arc motion and shock compression. Steering, wheel spin and drivetrain motion are separate omitted systems.

This 259-part Mecha extract includes 117 moving-role pieces, 38 mounts and 104 frame pieces. Front inner tie-rod pins 74/75 lack their rack-side holders, and input Cardan yokes are omitted. Prescribed fixed positions do not make it self-supporting.

## Adaptation ideas

Preserve 100-LDU outer arms, 80-LDU inner coupler attachments, joint centres and shock eyes. Add the missing pin holders and shaft supports before integrating it. Keep the split rods/cylinders/springs as rigid source-pose parts; do not import animation spring scaling.

Use a measured corner as a starting point for a service rover or off-road chassis. Build its actual mounts first, then adapt track, frame and wheel arches while keeping travel space clear. Reconcile shared hubs before adding steering or drive.

## Source and build order

Unchanged Mecha extract `42110-suspension-standalone/source/42110-suspension-standalone.mpd` derived from Hurbain’s model. Its original occurrence comments and retained identity map preserve the selection history.

The source is a flat one-group selection: these pages show the retained assembly from several views, not a recovered insertion sequence.

The sibling flattened this selection into one source group and split shock shortcuts. The pages show the assembly and individual BOM, not a recovered assembly order. Keep the retained ID map with any corner extraction; count separate shock components only once.

The pinned input has SHA-256 `30c62143630438e51b3a6bfa83b78fffc4f8fe06b6b6898b3904944d5f33fc16`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [independent-suspension.provenance.json](provenance/independent-suspension.provenance.json) · [independent-suspension.idmap.json](provenance/independent-suspension.idmap.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/independent-suspension \
  --outdir output/my-independent-suspension
./ldraw-agent build output/my-independent-suspension/scene.plan.json --contacts none \
  --output output/my-independent-suspension/my-independent-suspension.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

259 physical placements; 1 nonempty source groups
across 1 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

The source contains deliberately incomplete fixed boundary interfaces. The source’s 30.5/40.5-LDU travel limits and spring deformation are animation-study choices, not verified limits for a new build. Source-pose geometric checks do not certify a loaded suspension.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
