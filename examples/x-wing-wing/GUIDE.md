# UCS X-wing lower port wing

A long spacecraft wing can carry an engine pod and a slender tip feature while retaining a layered, readable silhouette.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

Read the plate sandwich, local bracing, nacelle and tip assembly as linked submodels. Whole-section views are supplied; prepare its source sections separately for build pages.

Retain the source wing-root stack and inspect the exact mating parts before attaching it to a new spine.

7191-1.mpd supplies the other wings, central fuselage and wing articulation. This is one lower port wing, not a mirrored pair.

Use a real opposite-hand construction or rebuild it with matching left/right parts; never mirror physical part matrices. Keep the nacelle and long projecting details clear of neighbouring wings.

## Source and evidence

Source: `7191-1.mpd` / `7191 - bottom-port-wing.ldr`. Original SHA-256: `51454fee78072d22bcf9bdcd735901adea09d183a3c5072acce5e37fa510f9ca`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. No additional position repairs were made.

125 physical placements. The images show completed-model views; source step data identifies smaller sections to study. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export x-wing-wing --outdir output/my-x-wing-wing`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
