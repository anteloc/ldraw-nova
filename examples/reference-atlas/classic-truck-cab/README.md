# Classic compact truck tractor

A moulded windscreen, doors, grille, lights and antenna make a compact truck read as a vehicle rather than a box.

Source: `6594-1.mpd` / `6594 - Truck Head.ldr`. Scale: minifigure.

This source includes wheels and rear chassis as well as the cab. Inspect its coupling and wheel envelope before attaching a trailer; retain or replace the branded panel deliberately. Connection analysis leaves 8 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
