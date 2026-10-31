# Hinged spacecraft side hatch with bracket-mounted engine cone

Carry an engine cone, fin and layered side shell on a hinged module while leaving the mating hinge half in the hull.

Source: `924-1.mpd` / `924 - Space Ship - Hatch Left.ldr`. Scale: minifigure.

The mating 3830 hinge top: the hull places it at [-60, -128, 240], beside the hatch occurrence at [-60, -72, 240]. The opposite hatch is a separately authored section, not permission to reflect rigid parts. Copy or rebuild the hull-side hinge support before claiming an attached hatch. Preserve hinge alignment and reserve the swept space; opening travel is not checked by this static source.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/spacecraft-hatch/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

A 3831 hinge base is bonded into plates and inverted slopes. A 3956 bracket presents a perpendicular attachment for the 3943b cone. The fin and cap complete the side silhouette.

**The parent supplies:** The mating 3830 hinge top: the hull places it at [-60, -128, 240], beside the hatch occurrence at [-60, -72, 240]. The opposite hatch is a separately authored section, not permission to reflect rigid parts.

**Description check:** The description identifies the visible elements correctly but omits the critical mating hinge half in the parent.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. Home and the context/right-view board show the exposed hinge fingers, sideways cone, fin and layered hatch positioned at the rear of the spacecraft.

## Evidence and limits

The extracted source has 17 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 1 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Copy or rebuild the hull-side hinge support before claiming an attached hatch. Preserve hinge alignment and reserve the swept space; opening travel is not checked by this static source.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/spacecraft-hatch/board/recipe.json --output output/boards/spacecraft-hatch`. Changed renders require a new inspection; do not reuse this review automatically.
