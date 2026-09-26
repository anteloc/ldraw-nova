# B-wing starfighter

Build a distinctive asymmetric starfighter around a narrow spine and separate wing masses.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

Study cockpit mass, long blade, smaller side wings, engine block and detailed wing ends as separate design roles.

Preserve wing-root and engine attachments; the model is delivered in its source pose, with no claim of working articulation.

Full model includes the supplied parent assembly.

Adapt the silhouette and module interfaces deliberately; keep real canopy, engine and wing parts rather than replacing their forms with rectangular slabs.

## Source and evidence

Source: `75050-1.mpd` / `75050 - Main.ldr`. Original SHA-256: `09e942934e480c12f92ffc90533060c1ceaa789c7b99d92598ff925244473123`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. Resolve tiny rounded-coordinate body-envelope penetrations in the posed wing plate/tile stack; maximum displacement is under 0.00033 LDU. Part identity, colour and orientation are unchanged. Strict collision tolerances remain unchanged.

434 physical placements. The images show completed-model views; source step data identifies smaller sections to study. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export b-wing --outdir output/my-b-wing`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
