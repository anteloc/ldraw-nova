# Boombox visual and physical review

Final review: `output/boombox-review/` (model sha256 `0f7d917a…`), built from `boombox.plan.json`, which `generate.py` produces. 392 physical placements, 44 distinct parts, 68 part/colour rows.

## Revision 1 — first assembly

**Opened:** `previews/home.png`, `front.png` and `top.png`; `output/boombox-scratch-r1/back.png` and `right.png`.

- It reads as a boombox at thumbnail size: two round woofers, a central deck and a bar handle. The flush fascia sits cleanly inside the black frame.
- **Problem:** the 6108 arch handle looked like a stepped ziggurat, not a carry handle.
- **Problem:** a row of base studs was exposed between the rear panel's bottom edge and the base plate (back view).
- **Problem:** the sides were plain; the model had studs facing only up, forward and back.

## Revision 2 — handle, rear sill, strap lugs, sliders

**Changes:**
- New handle: two `3062b` round posts, a `60479` 1 × 12 bridge, and a silver plate+tile grip with `11477` curved ends falling away outward. Candidates came from Jev discovery and a part board (`output/boombox-handles/`).
- Smooth 1 × 8 tiles cover the rear sill.
- Course 8 of each side wall now holds an outward `11211` carrying a `2432` strap lug, so studs also face ±X.
- Added two slider pairs in the top strip; the open slot cells expose base studs.

**Opened:** `home`, `front`, `back` and `right`, plus fascia-only `output/boombox-scratch-fascia/home.png` and `top.png`.

- The handle now has the expected rounded-shoulder silhouette, the rear stud row is hidden, and the lugs read from the front and sides.
- **Problem:** in the fascia close-up the black `3069bp08` counter was a blank black block. Its print is black on the base colour, so the digits vanish on black.
- **Problem:** the top band had no accent near the centre.

## Revision 3 — final

**Changes:** the counter base colour is now Medium Azure, which reads as a fluorescent "10:21". Added a blank chrome 1 × 4 nameplate in the top band.

**Opened:** all seven final previews (`home`, `front`, `back`, `left`, `right`, `top`, `bottom`). Also opened the build steps `output/boombox-steps/manual/00/step-010-home.png` and `step-010-back.png`.

- Step 10 shows the exposed SNOT core before covering: the 22885 wall presents 288 forward studs, and the back wall presents exactly two rows of 30414 studs. Both match the panel grids.
- The bottom view shows four feet and two staggered base plates. The left and right views show symmetric lugs and a plain case side.
- The palette organises the front: black frame and bezels, silver skin, one red/orange/azure cluster in the centre column. Quiet areas remain at the bottom band, the outer top strip and the lid.

## Automatic evidence and its limits

- `checks_passed: true`; validation, BOM, render and BOM comparison all pass. Python and LeoCAD both count 392 placements. Connection coverage is complete for all 392 instances.
- There is **one optimistic connection group** but 185 confirmed groups. Most 1 × N brick/plate links and the 22885 deep-socket links are *potential* adapter evidence (inscribed stud in square socket, deep stud socket), not confirmed fits.
- No `rectangular_body_overlap`. Of 748 overlap candidates, 110 are expected stud-zone overlaps. The rest are `review_oriented_bounds`; I grouped them by part pair. Only three kinds have no matching connection:
  - Round parts (`3941`, `4032a`, `4150p01`) beside skin bricks and tiles. Their bounding boxes exceed 20 LDU by 0.0005 LDU; the round bodies do not.
  - Bottom-course 22885 top studs inside the box of the fascia plate above the row-5/6 seam (4 LDU). The studs are at Z −16…−4; the plate is at Z −32…−20.
  - The woofer dish against its upper spacer (12 LDU box overlap). See the next point.
- **Woofer dish pairing artifact.** `44375b`'s underside sockets are 8 LDU above its rim, inside the dish. The checker's whole-box entry-face test pairs them with the *lower* spacer's studs at the rim plane (penetration 20) and reports none to the upper spacer. The placed coordinates put the upper spacer's studs at the socket plane (dish Y=8 = fascia-local −16). The rim stays 4 LDU above the exposed base studs. This is the recessed-socket limitation described in `docs/agent/snot.md`; global tolerances were not relaxed.
- `physical_validity: not_proven`. Remaining unverified points:
  - The fascia and rear panel each hang on stud clutch alone; the fascia's bottom edge rests on the sill.
  - The handle bridge is held by one stud on each post.
  - The `2432` lugs and `11477` ends rely on single-row clutch.
  - Colour availability (e.g. a Trans Orange 1 × 4, an azure printed counter) is not established.
