# Seven-part swivel armchair with sideways tiled armrests

Turn a moulded seat into a compact armchair using opposing brackets, sideways tiles and a complete turntable pair.

Source: `10297-1.mpd` / `10297 - armchair.ldr`. Scale: minifigure.

Only the room/floor context; both turntable halves are included. The source places the chair at an angle through a proper Y rotation, rather than changing its internal construction. Keep the bracket offsets and turntable pair. Recolour or place the whole chair, leaving room around its armrests; verify floor attachment separately when mounting it.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/swivel-armchair/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

A 3680 base and 3679 turntable top support two opposing 99207 brackets, a 4079 seat and two vertical 3068b armrest tiles.

**The parent supplies:** Only the room/floor context; both turntable halves are included. The source places the chair at an angle through a proper Y rotation, rather than changing its internal construction.

**Description check:** The short description is accurate but undersells the construction: the two brackets and vertical tiles form the armrests, and the turntable includes both halves.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. Home and the context/right-view board show a complete seat with two smooth vertical armrests in a furnished room. The single optimistic connection group supports selection, not physical certification.

## Evidence and limits

The extracted source has 7 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 1 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Keep the bracket offsets and turntable pair. Recolour or place the whole chair, leaving room around its armrests; verify floor attachment separately when mounting it.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/swivel-armchair/board/recipe.json --output output/boards/swivel-armchair`. Changed renders require a new inspection; do not reuse this review automatically.
