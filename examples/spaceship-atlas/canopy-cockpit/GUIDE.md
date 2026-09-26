# Enclosed octagonal canopy cockpit

Design the cockpit envelope around real canopy halves and hinges before closing the hull.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

The cockpit combines two octagonal transparent canopy halves, hinge fingers, a glazed rear panel, side mounts and a pilot subassembly. Read the child pages for its layers and occupant.

Retain mating canopy hinges and the panel rim; inspect source mounting bricks and their exact orientation before attaching to a new fuselage.

6887-1.mpd (Allied Avenger) supplies the surrounding spacecraft and mating rear structure. The extraction includes its pilot and several legacy part aliases.

Use the enclosure and hinge vocabulary in a new cockpit. Preserve the clear opening and actual pilot envelope; any new seat, controls or canopy substitution needs its own fit review.

## Source and evidence

Source: `6887-1.mpd` / `6887 - Spaceship - Cockpit.ldr`. Original SHA-256: `4cf7513c2f3eec5a425550c5633fe21240cc08c956435729b5395783e0a9a7f9`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. No additional position repairs were made.

49 physical placements. The manual preserves source STEP groups, with highlighted additions and per-step parts. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export canopy-cockpit --outdir output/my-canopy-cockpit`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
