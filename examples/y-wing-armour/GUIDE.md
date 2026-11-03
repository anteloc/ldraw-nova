# UCS Y-wing contoured armour panel

Combine sloped armour with a small raised vent cluster and a deliberate hinge edge.

Reusable source construction after visual review; inspect new interfaces after adaptation.

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

Read the layered wedge plates, curved/sloped surface and concentrated grille details in successive steps.

Preserve the underlying plate bond and hinge mating face; measure the panel envelope before installing it over machinery.

75181-1.mpd supplies the rest of the Y-wing hull and the mating panel supports.

Adapt a matched set of panels, retaining clean outer surfaces beside a few dense service areas. Use actual left/right pieces for handed variants.

## Source and evidence

Source: `75181-1.mpd` / `75181 - Y-Wing Starfighter - step254-261.ldr`. Original SHA-256: `a780334a32c3082736055bd609730a7dd6817afc850420c83ccfec59a385f7bb`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. No additional position repairs were made.

31 physical placements. The manual preserves source STEP groups, with highlighted additions and per-step parts. Python and LeoCAD BOMs match. Visual review is recorded separately after opening the actual images.

## Adapt it

Run `./ldraw-agent spaceship export y-wing-armour --outdir output/my-y-wing-armour`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
