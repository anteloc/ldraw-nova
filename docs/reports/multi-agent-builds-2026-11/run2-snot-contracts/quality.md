# Quality report — Linden Row House, run 2 (SNOT + submodel contracts)

Model: `linden-row.mpd` = `review/model.mpd`, sha256 `d8501b413c610d4440f152bcd432bfc942f431471cc59bb8faea88fe25b98d4a`.

| Check | Result |
|---|---|
| Build / validation | checks_passed; 0 errors; warnings disconnected_evidence (glass) + collision_review |
| Physical placements | 1427 |
| BOM Python vs LeoCAD | match 1427 = 1427 |
| Contacts (--contacts all) | 37 groups; **main group 1391 / 1427 (97.5 %)**; all 36 outside = clipped window glass |
| **contract_check (scene)** | **49 / 49 submodels PASS** (existence, count, envelope by owning part, connected, SNOT interface contacts, colours, duplicates, symmetry, forbidden zones) |
| SNOT | 205 parts (14.4 %) mounted sideways; every ✦ interface meets its contact minimum (e.g. floor3 cornice 16, roof cornice 20, kerb 32, floor2 facade 16) |
| Failed builds | 5 of ≈51, all overlap refusals fixed next build |
| Cross-module collisions | none at any round |

Images inspected (final revision): `review/previews/home.png`, `integration/r2/whole/panels/0{1,2,3}-*.png`,
`integration/final-studs-{ground,floor2,floor3,roof}/mosaic.png` (floor3 opened), `integration/final-cutaway/mosaic.png`.

Remaining limits: sign has no lettering (one stud row); awning is scalloped (1x1 double slopes), not one smooth
slope; trees have heavy trunks; lamps stand in front of the inner glazing; side walls are plain; roof corner urns
are tall white stacks; French doors are a single leaf; physical strength not proven.
