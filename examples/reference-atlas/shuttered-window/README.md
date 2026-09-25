# Opening window with shutters

Dedicated window leaves and louvred shutters add depth and a recognizable opening mechanism to a facade.

Source: `6769-1.mpd` / `6769 - North - Window.ldr`. Scale: minifigure.

Use the frame footprint for the wall opening, not the approximately 7.5-stud open-shutter envelope. Reserve front and side sweep and preserve the leaf pivots. Connection analysis leaves 3 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
