# Balcony facade with door, dormer and planted railing

Integrate a balcony floor, door threshold, decorative railing and sloped roof window into a layered facade module.

Source: `10270-1.mpd` / `10270 - Building-2_First_Floor_Balcony.ldr`. Scale: minifigure.

The building below, side/rear enclosure and surrounding roof. The complete-model parent places this section at [78, -185, 120], rotated 180 degrees about Y. Its plate underside needs support across the host building. Preserve the door opening and plate support grid. Rebuild wall courses when changing width; do not stretch the roof window, fencing or glazing.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/dormer-balcony/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

A tan plate floor carries a turquoise wall with door and glazing. Dark-blue slopes frame a dedicated 60806 roof window; fences and brown trim form the balcony edge.

**The parent supplies:** The building below, side/rear enclosure and surrounding roof. The complete-model parent places this section at [78, -185, 120], rotated 180 degrees about Y. Its plate underside needs support across the host building.

**Description check:** The description is broadly accurate, but this is a facade/floor fragment, not a complete room or self-supporting building.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. Home and the context/right-view board show the projecting balcony, sloping dormer glazing, wall and door. The side view exposes the thin wall and floor that need the parent building.

## Evidence and limits

The extracted source has 86 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 4 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Preserve the door opening and plate support grid. Rebuild wall courses when changing width; do not stretch the roof window, fencing or glazing.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/dormer-balcony/board/recipe.json --output output/boards/dormer-balcony`. Changed renders require a new inspection; do not reuse this review automatically.
