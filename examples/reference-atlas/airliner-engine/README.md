# Airliner engine and pylon

A dedicated cylindrical engine casing, turbine face and exhaust create a convincing nacelle with a thin brick-built pylon.

Source: `7893-1.mpd` / `7893 - engine.ldr`. Scale: minifigure.

Reserve the four-stud engine diameter and eleven-stud source length. Match the pylon top studs to the wing and check fan and exhaust clearances before repeating the module. Connection analysis leaves 7 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
