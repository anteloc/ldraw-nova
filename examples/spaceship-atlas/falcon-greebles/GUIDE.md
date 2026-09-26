# Millennium Falcon service-bay details

Small familiar LEGO fittings can suggest machinery when arranged in a coherent recessed service bay.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

Study the domes, control sticks, loudhailer, antenna and wing panel as a small directed composition.

Reserve the protruding antenna and bar envelope; attach the underlying plate to exposed studs, not through finished hull tiles.

10179-1.mpd supplies the surrounding hull recess. This is the right upper service cluster, not an entire Falcon panel.

Keep greebles grouped and lower than the main silhouette. Reuse their mounting logic; avoid covering every hull surface with unrelated decoration.

## Source and evidence

Source: `10179-1.mpd` / `10179 - subModel-43.ldr`. Original SHA-256: `69efb0b373df38363e2095a3d5d7ef11eea0f22d315f36c917977d3230cd19e2`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. No additional position repairs were made.

15 physical placements. The manual preserves source STEP groups, with highlighted additions and per-step parts. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export falcon-greebles --outdir output/my-falcon-greebles`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
