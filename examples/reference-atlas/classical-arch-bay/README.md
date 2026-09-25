# Classical arch and cornice

A moulded arch, grooved masonry and round plates under the cornice create shadow lines in a shallow facade bay.

Source: `10276-1.mpd` / `10276 - bk3-step185.ldr`. Scale: display.

The source is only one stud deep and has two separate pier feet. Tie both piers into the host base and continue the cornice rhythm; use the parameterized arcade recipe for another height.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
