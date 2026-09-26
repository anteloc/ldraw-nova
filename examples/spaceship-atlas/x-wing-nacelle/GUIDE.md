# UCS X-wing engine nacelle

Use genuine cylinders and concentric round parts to give an engine a convincing layered profile.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

A single source STEP group combines the cylindrical shell, red round inner pieces and axle core. Read the part list because there are no intermediate insertions in the source.

Keep the coaxial core and cylinder spacing; inspect its parent mounting shaft and the full pod envelope.

7191-1.mpd supplies the surrounding wing and fore/aft engine context.

Change external mounts and hull palette carefully while preserving the concentric stack and dedicated engine shapes.

## Source and evidence

Source: `7191-1.mpd` / `7191 - nacelle-2.ldr`. Original SHA-256: `51454fee78072d22bcf9bdcd735901adea09d183a3c5072acce5e37fa510f9ca`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. No additional position repairs were made.

41 physical placements. The manual preserves source STEP groups, with highlighted additions and per-step parts. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export x-wing-nacelle --outdir output/my-x-wing-nacelle`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
