# Four-speed driving-ring gearbox

Study constant-mesh gear trains, two alternating driving rings and the separate rotary selector.

[Build pages](index.html) · [Source assembly](source.mpd) · [Editable plan](scene.plan.json) · [Operation notes](operation.json)

## Construction and interfaces

A compact transmission selects among four gear routes using two driving rings and a rotary catch.

- Fixed structure: The retained beam/cross-block gearbox frame and bearing supports.
- Moving elements: Input/output shafts, intermediate shafts, loose gears, sliding driving rings and the rotary selector.
- Input: The source gearbox input shaft; the adjacent propshaft and its support belong to the parent.
- Output: The selected output shaft route, with the rotary catch as a separate user-controlled interface.

The selector knob/dial, adjacent propshafts and range/direction gearbox are omitted. This is the four-speed core, not a complete vehicle transmission or self-contained control station.

## Adaptation ideas

Keep gear centres, tooth planes, shaft stacks, free-versus-keyed gear roles and ring travel. Ring A starts engaged toward first gear in the source; preserve that offset and space for the catch and forks.

Use it as the core of a cutaway transmission exhibit or a vehicle drivetrain. Add an accessible selector and supporting chassis, with a removable panel that reveals the ring positions.

## Source and build order

Selected four-speed topology of `42110 - reargearbox.ldr` from Hurbain’s 42110 model. Mecha identifies it as the sequential four-speed core at full-model occurrence `0/1/133`; its surrounding shafts and external selector control are outside this section. One exact coincident 4519.dat axle duplicate (source index 43, identical to retained index 39) is removed in this derived copy; the original model remains unchanged.

Pages retain the source STEP groups; child assemblies have their own pages. These groups are source construction evidence, not a swept insertion check.

Follow the source’s eleven groups before adapting the case. Fit internal gears and retaining stacks before the closing frame members; identify hidden gear additions in the per-step lists.

The pinned input has SHA-256 `e5fdf0c10388c3e66bdeb70851b7ab412dd7f1c02ee702cb878f0547fbd7a93b`. Original authorship and
CCAL notices remain in the MPD. The upstream selection records travel with this
study: [four-speed-gearbox.provenance.json](provenance/four-speed-gearbox.provenance.json). Nova's [extraction.json](extraction.json) records any
rotation normalization or BFC repair to the study copy.

## Reuse in a new model

From the repository root, export this reviewed directory:

```sh
./ldraw-agent mechanism export examples/technic-atlas/mechanisms/four-speed-gearbox \
  --outdir output/my-four-speed-gearbox
./ldraw-agent build output/my-four-speed-gearbox/scene.plan.json --contacts none \
  --output output/my-four-speed-gearbox/my-four-speed-gearbox.mpd
```

Export requires current visual review and a matching rendered BOM. The exported
`generate.py` rebuilds the placement from local files. Position the module through
`scene.plan.json`; its `source_origin` is a frame, not an asserted connector.
Adapt internal parts in the bundled MPD, preserve provenance, then review the
combined model. Apply fixed-member structural contracts only to fixed supports.

## Current evidence and scope

66 physical placements; 13 nonempty source groups
across 2 assembly section(s). Source checks pass.
Python and LeoCAD BOMs match.
See [source checks](source-checks.json), [manual data](manual.json) and the separate
`visual-review.json` recorded after every generated image is opened.

The selector cam profile and engagement windows in Mecha are approximations. This source has no added Chiron reconstruction gears. Clutch contact, tooth phase and shifting under load are not certified.

Analytical mechanism verification remains **deferred**. Operation is intended or
inferred from the source. The study does not certify motion, loads or physical
buildability. Rebuilding pages clears their visual review.
