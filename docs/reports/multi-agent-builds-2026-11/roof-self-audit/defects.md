# Roof self-audit: defects

Evidence paths are relative to `output/urban-house/modules/roof-audit/`.
Before-fix baseline: `stage1/after/test.mpd` (refactored, geometry identical to original); `scene-audit.mpd` (pre-fix scene, from Stage 2).
After-fix build: `stage4/build1/` (test harness + scene). Canonical final files in this folder: `test.mpd`, `scene-audit.mpd`, `roof.plan.json`.
Analytics: `analysis/` (before) and `stage4/analysis-b1/` (after). Images: `xray/` (before) and `stage4/xray-b1/` (after).

## Defect table

| id | submodel | kind | description | evidence (metric or image path) | severity | proposed fix | status |
|---|---|---|---|---|---|---|---|
| D1 | front-corner-piers | structural | Both urn caps (6141, h 120..128) had no clutch to the urn stud below. The cap's underside is a pin-hole connector and the urn's top is a stud, so there was no mating pair. Each cap was its own disconnected group. | Before: `stage1/after/inspect.json` components [378,1,1]; `analysis/inspect-roof-front-corner-piers.json` 2 no-contact parts; `check_floating` roof: 2 parts outside main group at world Y -608; `xray/close-urn-caps/panels/01-front-view.png` (cap on a visible neck). After: `stage4/build1/inspect.json` components [1 group]; `stage4/analysis-b1/inspect-roof-front-corner-piers.json` comps [4,4] with 4 confirmed contacts; `check_floating` roof: none; `stage4/xray-b1/s-front-corner-piers/mosaic.png` | high | Replaced the cap with 98138 (round 1x1 tile, stud receptacle underneath, same origin and height). | fixed |
| D2 | bistro-set | geometric | The two side chairs faced away from the table: their backrests (local +Z, 1.25 studs) pointed at it. Each backrest reached about 5 LDU into the pedestal footprint. | Before: chair matrices give back_dir (+1,0,0) for chair@(-140,-40) and (-1,0,0) for chair@(-60,-40), both toward the table; overlap candidates depth X 5 LDU; `xray/close-chairs-top/panels/01-top-view.png`. After: chairs set to yaw -90 and 90; all four back_dir values point away from the table; penetration depth 0.0005 (touching) in `stage4/analysis-b1/inspect-roof-bistro-set.json`; `stage4/xray-b1/s-bistro-set/mosaic.png` | med | Set chair (-7,-2) to yaw -90 and chair (-3,-2) to yaw 90. | fixed |
| D3 | front-parapet, pediment | contract | Front coping (h 64..72) and pediment cap (h 120..128) were 2 deep at Z -9..-7, so they projected to Z -9. CONTRACTS.md allows only the front cornice to project to Z -9. | Before: `slab(...,-9,2,...)` for coping and cap; `xray/roof-xray/mosaic.png` top view. After: min Z of all roof parts is -180 (-9 studs) and it belongs only to `roof-front-cornice.ldr` (3 parts); `stage4/xray-b1/s-front-parapet/mosaic.png`, `stage4/xray-b1/s-pediment/mosaic.png` | med | Coping and pediment cap made 1 stud deep at Z -8..-7. | fixed |
| D4 | front-parapet | visual | Dentil alternation started white at X -10.5 and ended brick at X 10.5, so it was not mirror-symmetric and a white/brick seam sat on the pediment centre. | Before: `xray/s-front-parapet/mosaic.png`. After: dentil colours [15,320,15,...,320,15] mirror-symmetric (checked on `stage4/build1/inspect.json`); `stage4/xray-b1/s-front-parapet/mosaic.png` | low | Dentil colour mirrored about X=0. | fixed |
| D5 | skylight | contract | Skylight frame plates and glass had studs, so the top was at 204 LDU. The body top is 200 (contract h200). | Before: envelope check max top 204 at skylight parts 311..315 in `stage1/after/inspect.json`. After: max top 200 in `stage4/build1/inspect.json`; `stage4/xray-b1/s-skylight/mosaic.png` | low | Smooth tiles (3068b x2 glass, 2431 x2 and 3069b x2 frame) so the top is 200. | fixed |
| D6 | pergola | geometric | Slats sat at X -8.5, -6.5, -4.5, -2.5 (mean -5.5), offset 0.5 stud from the post and beam centre (X -5). The rightmost stud was open. | Before: slat centres mean -5.5 (arithmetic from `build_pergola`). After: slat centres -170,-130,-70,-30 LDU (-8.5,-6.5,-3.5,-1.5 studs), mean -100 = pergola centre; `stage4/xray-b1/s-pergola/mosaic.png` | low | Slats set mirror-symmetric about X -5. | fixed |
| D7 | planter-front-east, planter-west, planter-east | visual | Plants are 2x2 round bricks, so they read as solid drums rather than plants. | `xray/s-planter-*/mosaic.png` | low | Judgement call (design). Optional change to smaller plant parts. Not done in this pass. | not fixed (design choice) |

## Subsystems checked and found clean

- **deck**: no unsupported parts or parts standing only on smooth tiles; no duplicate placements; colours within palette; grid consistent. `xray/s-deck/mosaic.png`.
- **side-parapets**: continuous brick and coping, symmetric about X=0. `xray/s-side-parapets/mosaic.png`.
- **back-parapets**: gap exactly over the stair-house footprint X -1..5. `xray/s-back-parapets/mosaic.png`.
- **stair-house** and **door4**: door frame and leaf fit the opening. The leaf sits 0.4 stud off-grid by design (hinge offset). `xray/s-stair-house/mosaic.png`, `xray/s-door4/mosaic.png`.
- **chimney**: 24 confirmed contacts; cutaway shows no clipping. `xray/s-chimney/mosaic.png`, `xray/roof-cutaway/mosaic.png`.
- **front-cornice**: continuous band, correct support, the only Z -9 projection. `xray/s-front-cornice/mosaic.png`.
- **planters (3)**: rotation correct, footprints covered by pads. `xray/s-planter-*/mosaic.png`.
- **whole roof (after fixes)**: `validate --geometry` passes with only `coverage.collision_review`; stud map uniform (`xray/roof-stud-map/mosaic.png`); build order rests every step on earlier steps (`xray/roof-steps/mosaic.png`).

## Regression evidence (after fixes)

- Whole-house scene (`stage4/build1/scene-audit.mpd`): all non-roof submodel placements identical to the pre-fix scene (street, ground, floor2, floor3). Roof placements 380 -> 381 (skylight glass is now two tiles). `check_floating` main group 1338 -> 1341; roof has no parts outside the main group.

## Out-of-scope observations (not in roof-audit, not changed)

- `check_floating` still reports unsupported or blind-spot parts in street (fluted lamp 6141/3062b/4740/4589), ground (window 60608s, 6141s) and floor2 (window 60608s). floor3 has one part outside the main group. These are other modules' files and were not edited.
- The street lamp uses the same 6141-on-3062b pattern that caused D1. Worth checking in that module.

## Limits of this audit

- `ldraw-agent connections` skips submodel placements (it treats child names as library parts), so roof-level connection data came from `inspect --contacts all`.
- About 190 parts have only `potential` contacts (heuristic matches), which is not proof of clutch. Groups were judged on the optimistic graph; the confirmed-only graph is sparse for the whole house, so this is a tool limit, not a roof defect.
- 82-84 oriented-bounds overlap candidates remain (mostly stud-zone and touching contacts). Only D2 was a real penetration, and it is resolved to touching.
