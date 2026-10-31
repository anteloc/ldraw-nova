# Compact aircraft landing strut with matched wheel and tyre

Use a short axle and two angle connectors to separate the fuselage mounting pin from a freely mounted wheel.

Source: `6745-1_Harrier-Jet.mpd` / `6745 - Landing Gear.ldr`. Scale: minifigure.

The fuselage Technic receiving bricks and the placement angle. The parent contains two differently rotated occurrences at X = -50 and +50; the extracted strut is not already in its installed orientation. Keep the wheel/tyre pair and pin roles. Measure the host receiving hole before placement and review the complete fuselage clearance. Six optimistic connection groups remain for seven placements: this is a geometry study, not a verified mechanical core.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/aircraft-undercarriage/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

Two 32013 angle connectors are joined by a 32062 axle. A 2780 friction pin supplies the host attachment, while a 3673 pin carries the 42610 rim and 51011 tyre.

**The parent supplies:** The fuselage Technic receiving bricks and the placement angle. The parent contains two differently rotated occurrences at X = -50 and +50; the extracted strut is not already in its installed orientation.

**Description check:** The description calls it retractable. The source shows one pose only; retraction travel, locking and wheel clearance have not been demonstrated.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. Home and the context/right-view board show the wheel, two-connector strut and separate mounting pin, with both installed occurrences visible through the ghosted aircraft.

## Evidence and limits

The extracted source has 7 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 6 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Keep the wheel/tyre pair and pin roles. Measure the host receiving hole before placement and review the complete fuselage clearance. Six optimistic connection groups remain for seven placements: this is a geometry study, not a verified mechanical core.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/aircraft-undercarriage/board/recipe.json --output output/boards/aircraft-undercarriage`. Changed renders require a new inspection; do not reuse this review automatically.
