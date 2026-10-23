# Review of the Halcyon

Reviewed 2026-10-22 with pyldraw3 1.7.0, the configured official library, the supplied LDCad shadows and LeoCAD. [generate.py](generate.py) is the editable source; [halcyon.plan.json](halcyon.plan.json) and [halcyon.mpd](halcyon.mpd) are its reviewed outputs.

## Checks

| Evidence | Result |
|---|---|
| Physical placements | 195 (ship 189, stand 6) |
| Source/geometry errors | 0 |
| Geometry resolved | Complete |
| Python/LeoCAD BOM | Match, 195 = 195 |
| Automatic optimistic groups | 1, from 1,265 contacts |
| Module sections checked alone | 16 of 16 form one group each |
| Warnings | `coverage.collision_review` only |

Review artifacts are in `output/snot-halcyon-review/`. The MPD here is byte-identical to its `model.mpd`. Step pages are in `output/snot-halcyon-steps/halcyon/` (7 root steps) and `output/snot-halcyon-steps/halcyon-hull/` (9 hull steps).

The overlap candidates that lack a connection were each inspected:

| Pair | Interpretation |
|---|---|
| `60474` intake/exhaust rings and pod plates | Flush on the pod faces; the round plate's bounds exceed the face by 0.0003 LDU |
| `30384` canopy and the bricks under the cockpit floor | The canopy rests on the floor plate; its bounds include the hull studs below |
| Port `30414` flank mount and the `41769` K4 wedge | The wedge's outer back corner has a receptacle but no stud; the brick is held by the K4 hull plate |
| Intake `3941` hub and strake tiles | Tangent at Y=-16 only |
| `44661` tip fin and the `3068b` tip tile | The fin rises from its 1 × 2 base above the tile; the wing close-up shows no intersection |

## Images actually inspected

- Final previews: `output/snot-halcyon-review/previews/{home,front,back,left,right,top,bottom}.png`.
- Root steps 1–7 and hull steps 1–9 (`manual/00/step-NNN-home.png`), plus hull step 5 `back`.
- Modules in their own frames: `output/snot-halcyon/modules/*/home.png` for flank, pod stripe, nose, intake, exhaust and cannon.
- Close-ups of the starboard wing (`home`, `back`) and the bare hull (`back`, `right`).
- Every iteration's `home/front/back/right/top/bottom` sheet: `output/snot-halcyon/v0-r` to `v5-r`.
- Part boards for canopies, nose shapes and wing planforms, and a side render of curved slopes, used to choose parts and learn their orientation.

## Iterations

| Version | What the images showed | Change |
|---|---|---|
| v0 | Boxy: a flat white tile table behind a narrow fuselage; bare studded wings. The checker reported the nose and the intake hubs as separate groups (the nose did not overlap the hull; the hub was 8 LDU above its ring) | Rebuilt the rear and the nose |
| v1 | One group. Rounded pods (`15068` pairs), dark spine and tiled wings worked. The nose's lower wedges showed studs ahead of the cap | Staggered every nose layer; added K5 so the `47753` meets the deck |
| v2 | Stepped chin, twin tails, grilles, aft cap. Top view still T-shaped; studs on the tail tops and through the canopy; plain pod sides | Strakes, tail caps, cabin tiles, pod stripes, wingtip fins |
| v3 | Arrowhead plan from above. The flank stripe (low) and pod stripe (high) sat at different heights; dark nose steps looked busy | Moved the stripe to the upper flank row; white nose |
| v4 | One continuous stripe from nose to pods; stand added | Wing-root cannons, grey pod band |
| v5 | Final silhouette. The cannons' `4589` cone tip formed its own group: its base is modelled as axle and pin holes, not a stud receptacle | Replaced the tip with a `98138` round tile; checks were not relaxed |

The tests' mutation case found one more weakness after v5: each flank was two separate plate-and-tile stacks, held together only through the hull. Moving the stripe's 1 × 8 tile across the base-plate seam made each flank one group by itself.

## Design assessment

The ship reads at thumbnail size: an arrowhead from above and a slim wedge from the side. The canopy and glowing exhausts are its two focal points, and the dark spine and grey nozzles separate frame from armour. All 62 sideways, forward and aft studs carry a skin or module: 60 on the fifteen `30414` bricks and one on each cannon's `87087`. The only exposed studs are the eight outer studs on each intake ring, kept as intake detail, and the stand base. The cannons, intake rings and tails add detail without crowding the broad surfaces.

Remaining weaknesses:

- From the side and front, the stepped chin shows the wedge plates' underside tubes. A smooth chin would need inverted curved slopes and another bonding layer.
- The forward hull is longer than the pods; a shorter nose would make the ship more compact, at some cost to the needle-nose silhouette.
- The stand base shows its studs, and the single column has not been checked for balance.
- At 195 pieces the model is below the 250–400 estimate in the plan. The size matches the brief; detail was not added just to reach the estimate.

## Verification limits

`physical_validity` remains `not_proven`. The contact graph is computational evidence, not a clutch, strength or balance test. The strakes, wing splices and nose wedges are interleaved with the keel plates: the root's steps add whole modules in reading order, so a physical build has to insert those parts between the K layers. Colour codes are design roles, not a check of retail availability.
