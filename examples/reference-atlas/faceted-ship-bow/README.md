# Faceted research-ship bow

Side-stud bricks and small slopes shape a compact ship bow in multiple directions without scaling any physical part.

Source: `31045-1.mpd` / `31045 - Ship front.ldr`. Scale: microscale.

The source axes do not present the bow as a complete horizontal hull. Consult the parent placement matrix before orienting it, and continue its red, dark blue and grey bands into the adjoining hull. Connection analysis leaves 3 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
