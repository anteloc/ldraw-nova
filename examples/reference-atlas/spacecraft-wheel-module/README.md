# Spacecraft wheel module

Wheel-pin plates, a tall bracket and small exhaust and grille fittings give a compact wheeled module a mechanical identity.

Source: `5980-1.mpd` / `5980 - 5980-4-a.ldr`. Scale: unknown.

The original parent calls this landing gear; its isolated appearance also suggests rover ideas. Preserve the hinge and bracket interfaces and test deployed clearance in the parent before reuse. Connection analysis leaves 7 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
