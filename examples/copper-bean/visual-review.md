# Visual review — The Copper Bean

Every image named here was rendered with LeoCAD and opened before the note was
written. Geometry results are recorded separately in `copper-bean.validation.json`
and `copper-bean.inspection.json`; a passing render is not a geometry result and
a passing geometry check is not a design verdict.

## Round 1 — first whole-model set

Viewed: `review/home.png`, `review/front.png`, `review/left.png`, `review/top.png`
(821 placements at that revision).

| Problem seen | Change made |
|---|---|
| The flank elevations were near-blank: one 4-stud window per floor in a 12-stud-deep wall, and the plate ring at each storey head sat flush so it cast no line. | `crown()` now projects the cornice one stud on both flanks and the rear as well as two studs at the front; each storey gained a second flank window (bays at z = ±3) and a second rear window. |
| Street trees from the shared atlas `tree()` stood 240 LDU tall — taller than the shopfront — and read as spindly palms. | Wrote `street_tree()`: 168 LDU, three trunk segments and three leaf tiers over a 4-stud plinth. |
| The side and rear lawns were large empty green fields. | Added a tiled service path from the pavement round to the rear door, two garden trees, a garden seat, two beds and eight flower clusters. |
| Window bands sat one course too low, making each storey bottom-heavy. | Moved every window band from courses 1–3 to courses 2–4. |
| The ground floor was an undivided mass of dark green. | Added a Dark_Bluish_Grey plinth course all round (course 0). |

## Round 2 — shopfront close-up

Viewed: `shop-review/front.png` (module rendered on its own, colour 288).

| Problem seen | Change made |
|---|---|
| The 2x2 printed sign straddled the top of the door and left two side studs of the 1x4 mount bare either side of it. | Replaced the single `30414` mount with three `11211` bricks and made a 6x2 sign board: the printed coffee-cup tile in the middle, two plain white panels beside it, covering every side stud. |
| The sign band was only one course tall, so the board could not clear the door head. | Shop went from 7 to 8 courses; courses 6–7 are now the sign band and the board sits entirely inside it. |
| The shop read as an empty glass box. | Added an interior: service counter with a tiled top, espresso machine, two pedestal tables and four stools, all visible through the display bays. |

## Round 3 — terrace close-up

Viewed: `terrace-review/home.png`, `terrace-review/front.png` (module on its own).

| Problem seen | Change made |
|---|---|
| A white table top against a white torso and grey chair frames made the group read as one grey lump. | Bistro chairs went to White with Reddish_Brown seat tiles, the table top to Reddish_Brown on white legs, and the third guest's torso from White to Orange. |
| The chair was two separate stacks — seat block and back frame — standing side by side on the deck with nothing tying them. | Added a single 2x3 base plate under both; the chair is now one connected object and the seat top moved from 32 to 40 LDU. |
| The two centre plates of the table top had no stud under them: they were held only by edge contact and were in fact floating. | Added 1x4 rails at 56 LDU across each leg pair; their centre studs now carry those plates. Confirmed by contacts: the table is a single 19-part group. |

## Round 4 — connectivity read-through

`inspect --section ... --contacts all` on each module, then the whole scene.

The awning slopes came back as eight singletons. `3039`'s underside sockets sit
on a grid offset half a stud in Z from its origin, so at `z = -d/2 - 1` the
slopes rested on the cornice without engaging a single stud — a real floating
course that no render showed. Moving the course to `z = -d/2 - 0.5` seats all
eight on the cornice studs; they are now inside the main group.

The same pass showed `6141` (Plate 1x1 Round) carries only pin/pin-hole frames
in the shadow library and can never register a stud contact. Where it was doing
structural work (shop stools, espresso machine) it was swapped for `3024`.

## Round 5 — final whole-model set

Viewed: `review/home.png`, `review/front.png`, `review/left.png`,
`review/back.png`, `review/top.png` at 1022 placements.

- **Thumbnail read.** The subject is legible small: a tall banded block with a
  green shop at its foot and a green parasol on the pavement beside it.
- **Proportion.** The taller ground floor against two shorter apartment floors
  gives the building its shop-with-flats-above character. The 8x8 parasol is the
  only wide horizontal element and balances the vertical mass.
- **Focal hierarchy.** Shopfront first (awning, sign, glazing), then the café
  group and the top-floor balcony, then small planting accents. No elevation is
  uniformly busy.
- **Depth.** Three projecting cornices wrap all four sides; the awning and
  balcony railing stand two studs proud of the wall.
- **Quiet against detailed.** The tan wall field, the tiled roof terrace and the
  open pavement west of the café are deliberately left plain.
- **Exposed sides and rear.** Both flanks and the rear now carry the full window
  rhythm, the wrapping cornice and ground-level planting; the rear also has the
  service door, path and garden seat.
- **Entrances.** The shop door is clear of planting; the approach across the
  terrace is open. The rear door has its own path.

### What remains imperfect

- From a dead-on front view the parasol canopy covers the left display bay. That
  is inherent to putting an 8x8 canopy on a pavement in front of a shopfront; the
  three-quarter view reads correctly and the shopfront module renders clear on
  its own.
- The flank fascia band of the shop (courses 6–7) is plain dark green, because
  the sign board is only on the street elevation.
- The roof service bay is functional rather than pretty; it is small and mostly
  hidden below the parapet line from normal viewing angles.
