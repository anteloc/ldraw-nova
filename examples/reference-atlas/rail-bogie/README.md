# Two-axle train bogie with buffers and magnetic coupling

Combine two wheelsets, a bogie pivot and a coupling on one supported undercarriage; minifigure heads become buffer faces.

Source: `10183-1_Switcher.mpd` / `10183 - 17 - wheels back.ldr`. Scale: minifigure.

The locomotive chassis and receiving mount for the bogie pin. The parent turns this assembly 90 degrees about Y and places it at [-170, 56, 0]. It does not provide a motor or powered transmission for this bogie. Keep the wheelsets, pin and coupling stack together. Reserve turning space around the bogie and buffer faces; do not assume clearance on a different chassis or track curve.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build examples/reference-atlas/rail-bogie/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Construction and source context

Two 2878c02 wheelsets sit at local Z = -60 and +60. The 4092b short-pin bogie plate supplies the upward pivot. The buffer beam, coupling and magnet are included.

**The parent supplies:** The locomotive chassis and receiving mount for the bogie pin. The parent turns this assembly 90 degrees about Y and places it at [-170, 56, 0]. It does not provide a motor or powered transmission for this bogie.

**Description check:** The database says single-axle; the section actually contains two single-axle wheelset assemblies, making a two-axle bogie.

[Inspection board](board/mosaic.png) shows the highlighted module in its ghosted parent, then isolated home and right views. Panels use independent framing. Home and the context/right-view board show both wheelsets, the central mounting pin, magnetic coupling and paired round buffer faces.

## Evidence and limits

The extracted source has 22 physical placements, passing available source/geometry checks and a matching Python/LeoCAD BOM. Four views were rendered; the home preview and the three-panel inspection board were opened. Contact analysis reports 2 optimistic groups. Missing contact evidence is not proof of disconnection; these checks also do not prove absence of material collisions, rigidity, strength or motion.

Keep the wheelsets, pin and coupling stack together. Reserve turning space around the bogie and buffer faces; do not assume clearance on a different chassis or track curve.

These are source construction studies for adaptation, not certified mechanical cores. Original authorship and licences remain in the MPD and extraction manifest.

Recreate the board with `./ldraw-xray board run examples/reference-atlas/rail-bogie/board/recipe.json --output output/boards/rail-bogie`. Changed renders require a new inspection; do not reuse this review automatically.
