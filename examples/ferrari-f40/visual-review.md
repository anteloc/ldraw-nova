# Ferrari source and image assessment

Reviewed the supplied source, its section/STEP structure, declared child transforms, physical inventories and rendered views. No discovery service was needed for this explicitly supplied file. The semantic labels describe construction roles; they do not certify physical assembly or reconstruct missing hierarchy.

## Images inspected

The 73 saved-callout `catalog/01` through `catalog/73` home previews were inspected in five labeled overview sheets, generated from the corresponding manual overview renders. Working sheets are `output/ferrari-f40-assessment/sheet-01.png`, `sheet-17.png`, `sheet-33.png`, `sheet-49.png` and `sheet-65.png`. Also inspected the complete, bounds-fitted `catalog/00/renders/home.png`. Earlier raw home/back/right/top views in the working output helped identify body roles; some orthographic views were cropped, so they are not the retained whole-car preview.

For the five exported studies, inspected every home/back source-step image and final home preview in labeled sheets under `output/ferrari-f40-studies/<study>/contact-sheet.png`. These comprise 9 body-mount images, 5 door-rail images, 9 rear-lamp images, 7 window-louver images and 7 fascia-core images: **37 images total**. Each retained `studies/<study>/visual-review.json` enumerates those exact source image paths and binds the review to the exported evidence. The sheets were a viewing aid; their constituent images are retained with the manuals.

## Observations and decisions

- The full car has a low nose, sloping windscreen, side intakes, a broad rear wing and a louvered rear window. These give useful context for how small SNOT constructions contribute to a continuous vehicle body.
- The body mount exposes bracket and side-stud faces at different heights beside a clip. The door rail repeats three brackets behind a smooth, narrow trim edge. The rear lamp combines a dish and grille on perpendicular faces.
- The louver shows thin translucent panels and two end mounts; its declared clamshell parent supplies three stepped placements. The fascia core shows a separate perpendicular stud field beside Technic holes. A hole, clip or hinge does not by itself establish a functioning mechanism.
- Saved callouts can use different parts, colours and orientations from the main car. The multipart windscreen is especially clear evidence. Declared child transforms are retained; main step pointers remain contextual annotations.

All 73 isolated callouts have passing source/geometry error checks and all 74 overview BOM comparisons match. Existing bounded normalization repairs 14 unique original matrices: four in section 42 and five each in 68 and 69. Extraction manifests on enclosing callouts repeat the appropriate repair records. No part positions or colours were repaired for this reference.

The full-car extraction has 25 body-overlap errors, ranging from roughly 0.000166 to 2.50358 LDU penetration. Its checks and failing catalog status remain visible. No claim is made that these are all harmless, or that the complete car can be exported as a checked construction.

The five focused studies have no source/geometry errors, matching rendered inventories and one optimistic connection group each under all-contact analysis. Their remaining warning concerns incomplete material collision coverage for nonrectangular parts. Their interfaces must be checked again in any new parent assembly. Physical validity remains `not_proven`.
