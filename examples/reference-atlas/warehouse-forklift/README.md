# Small warehouse forklift with dedicated lifting mast

Build a complete small service vehicle around a dedicated mast rather than inventing a lifting linkage from loose parts.

Source: `6375-1.mpd` / `6375 - forklift.ldr`. Scale: minifigure.

Cargo, a cart, the aircraft and minifigures are separate scene objects. No structural part of this forklift is supplied by the parent. Its inherited body colour is red (4); the isolated xray board uses its default yellow for inherited colour. Preserve the mast and matched wheel/tyre pairs. Change surrounding bodywork and palette, then check ground contact and fork clearance. Cargo fit, load stability and lift travel remain unverified.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/warehouse-forklift/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

Wheel-pin plates support four wheels, with larger tyres beside the mast. The 3430c01 shortcut includes the mast and raised black forks; two controls and a handle complete the operator area.

**The parent supplies:** Cargo, a cart, the aircraft and minifigures are separate scene objects. No structural part of this forklift is supplied by the parent. Its inherited body colour is red (4); the isolated xray board uses its default yellow for inherited colour.

**Description check:** The database description is broadly accurate. The lifting function belongs to a dedicated complete-part shortcut; the MPD represents its raised pose, not an actuated mechanism.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. The red home preview and context/right-view board show four wheels, tall mast, raised forks and operator controls. The ghosted parent confirms this is a separate vehicle, not a disconnected component of the airplane.

## Evidence and limits

The extracted source has 21 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 3 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Preserve the mast and matched wheel/tyre pairs. Change surrounding bodywork and palette, then check ground contact and fork clearance. Cargo fit, load stability and lift travel remain unverified.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/warehouse-forklift/board/recipe.json --output output/boards/warehouse-forklift`. Changed renders require a new inspection; do not reuse this review automatically.
