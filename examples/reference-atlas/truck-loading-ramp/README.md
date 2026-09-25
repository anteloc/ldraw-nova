# Two-track loading ramp

Two wheel tracks, hinge fingers and a small grille communicate a functional loading surface while keeping the centre open.

Source: `5893-1_Truck.mpd` / `5893 - Truck ramp.ldr`. Scale: minifigure.

Measure the mating hinge in the host truck and match its finger spacing. Check both deployed and folded clearance; the source image shows only its stored local pose.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
