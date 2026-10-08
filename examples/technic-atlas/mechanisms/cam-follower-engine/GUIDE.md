# Cam-driven inline-six followers

Combine phased liftarm cams with a separate guided follower block and preserve the source rest offset.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

A bank of liftarm cams is intended to lift six guided axle followers in sequence.

- Fixed structure: Engine-block guides, connector frame and camshaft supports retained in the two source sections.
- Moving elements: Camshaft axle, gear and phased cams; six follower axles moving through their guides.
- Input: Exposed camshaft gear/axle; the upstream engine-side shaft and idler are supplied by the original gearbox and are omitted.
- Output: Six short follower lifts. One follower already starts raised in the source pose.

These two source sections retain their mutual placements but omit the front-axle frame and upstream gear/idler route. Add physical mounts for both sections and an accessible drive.

## Adaptation ideas

Keep the cam phases, guides and stops, including the raised follower’s rest offset. Do not substitute crank-and-rod motion. Adapt the enclosing frame while reserving the space above the follower heads.

Use this compact arrangement in a tractor bonnet, pumping station or a visible sequence of industrial plungers. Expose the cams or make the cover removable so the action reads clearly.

## Source and build order

Engine block and camshaft from source type-1 indices 126 and 127 of `42110 - frontaxle.ldr`, placed in their original common frame. Source groups 23 and 24 become the two root groups; both child manuals retain their original steps.

Pages retain the source STEP groups; child assemblies have their own pages. These groups are source construction evidence, not a swept insertion check.

Study the block and camshaft child pages as well as the two parent groups. Insert/retain the camshaft before closing a new enclosure, and mount the follower block above the correct cam row.

The pinned input has SHA-256 `85ab5c80c58ce6c1b82db4c4fa2177d1bc3cab326f1cdac473b4b9b36e733b14`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [cam-follower-engine.provenance.json](provenance/cam-follower-engine.provenance.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/cam-follower-engine \
  --outdir output/my-cam-follower-engine
./ldraw-agent build output/my-cam-follower-engine/scene.plan.json --contacts none \
  --output output/my-cam-follower-engine/my-cam-follower-engine.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

55 physical placements; 9 nonempty source groups
across 3 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

Mecha’s lift law is a cam-contact hypothesis. Gravity return, full-cycle surface clearance and spring/loading behaviour remain unverified. The 55-part module is shown in its source pose.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
