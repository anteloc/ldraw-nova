# Spaceship atlas visual review

Reviewed on 2026-09-26. **All 50 retained images were opened**: four overview views for each of the three complete ships and the X-wing wing, plus 30 source-step views and four final previews for the remaining constructions. Each `visual-review.json` binds the current source, notes, checks and images through `manual.json` hashes.

| Study | Images | Observations |
| --- | ---: | --- |
| [B-wing](b-wing/visual-review.json) | 4 | Long blade, opposed short wings, offset canopy and four orange engine faces remain readable. Orthographic views reveal thin wing layers. The source points along a different axis from the new-design convention. Three tiny recorded copy corrections have no visible silhouette effect. |
| [UCS Y-wing](ucs-y-wing-study/visual-review.json) | 4 | Paired long nacelles, narrow spine, yellow cockpit markings and tilted stand establish the silhouette. Top clarifies spacing. Dense edges limit fine inspection in the full view. Source overlap errors remain; this is inspiration only. |
| [Star Destroyer](star-destroyer-study/visual-review.json) | 4 | Home/top reveal the wedge, surface steps and bridge; back reveals the blue engine cluster. Front is strongly foreshortened. Source transform and overlap errors remain; export as a checked construction is blocked. |
| [X-wing wing](x-wing-wing/visual-review.json) | 4 | Plate thickness, shaped panel, nacelle and long tip cannon are distinct. Top reveals the projection lengths; source axes and root mounting stack must be retained or deliberately adapted. These are overview images. |
| [X-wing nacelle](x-wing-nacelle/visual-review.json) | 3 | Cylinders, red inner round parts, concentric core and transverse axle mounts are visible. It stands vertically in source-local axes. Its sole STEP group cannot teach intermediate insertion order. |
| [Canopy cockpit](canopy-cockpit/visual-review.json) | 9 | Real transparent canopy halves show the pilot. Child pages expose the rear glazing/hinges and pilot/helmet assemblies. Every section has one STEP group. Legacy minifigure parts remain; replacement parts require a new fit review. |
| [Y-wing armour](y-wing-armour/visual-review.json) | 15 | Successive steps distinguish the support strip, end plates, vents, hinges, slopes, rod and upper details. The quieter sloped border stays visually separate from the dense centre. |
| [Falcon service cluster](falcon-greebles/visual-review.json) | 7 | Wedge base, domes and brackets precede bars/antenna and smaller fittings. The concentrated mechanical detail reads clearly; its parent hull recess and clearances are still required. |

Visual inspection also rejected an initially selected `75075` fitting as a cockpit teaching example. Its appearance and parent context did not support the initial interpretation of its annotated description. It was replaced with the actual canopy enclosure from `6887-1.mpd`. Semantic relevance did not substitute for looking at the source and images.

The B-wing copy records three sub-0.00033-LDU translations in its rounded wing plate/tile stack. Strict collision tolerances were retained, and all original library source hashes remain unchanged. Geometry checks also now distinguish optional connector-metadata warnings from missing solid geometry; the original warnings remain in reports.

These images support construction study and agreement with source poses. They do not certify articulation, physical strength, insertion access or flight performance. New compositions need their own interface checks and final images.
