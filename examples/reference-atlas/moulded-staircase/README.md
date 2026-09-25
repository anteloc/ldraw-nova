# Moulded staircase and landing

A dedicated staircase provides thin risers and an open underside with far fewer parts than stacked solid bricks.

Source: `10182-1.mpd` / `10182 - First floor - Staircase.ldr`. Scale: minifigure.

Reserve four studs across the stair and a twelve-stud source depth including the narrow upper landing. Match the actual landing height to the floor; add handrails where the brief needs them.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
