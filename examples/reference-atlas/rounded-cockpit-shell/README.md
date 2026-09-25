# Rounded cockpit shell

Repeated curved roof pieces form a smooth shell while narrow side ledges leave space for a cockpit or nose insert.

Source: `10212-1.mpd` / `10212 - subModel-19.ldr`. Scale: display.

The source shell is six studs wide and open at one end and underneath. Preserve the ledges and rear opening, then build the glazing, floor and host attachments for the new model.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.
