# Vehicle atlas visual and construction review

Reviewed 2026-09-24. Opened all six views (home, front, back, right, top and
bottom) for seven complete vehicles and six fitting recipes, including six-view
contact sheets of the final images. Each `visual-review.json` identifies the
exact MPD hash. This is image and digital assembly review, not a physical build.

| Model | Physical placements | Visual focus |
|---|---:|---|
| Grand tourer | 97 | Long green bonnet, short rounded tan roof and inset glazing |
| Delivery van | 122 | Pale cargo volume, blue belt, actual seats/controls and compact mirrors |
| Workshop pickup | 129 | Separate cab and capped bed, real handled cargo chest on its pallet |
| Site tipper truck | 113 | Forward cab, warning lamps and a purpose-made open tipper bucket |
| Touring motorcycle | 8 | Vintage fairing, actual frame/handlebars, spoked wheels and luggage rack |
| Harbour launch | 12 | Moulded hull, glazed helm, seat, lights and a visible life ring |
| Courier jet | 46 | Matched streamlined nose, swept wings, closed windowed cabin, engines and T-tail |

## Revisions made after inspection

Replaced the van and pickup's brick-built seats with 4079 seats and provided
real steering controls, a printed dashboard and supported mirrors. Deepened
the cab by one stud for the seat backs, moved the cargo boundaries and replaced
short roof strips with longitudinal plates. The latter change removed a floating
middle roof group found during connection review.

The pickup chest occupies exposed stud space; the corresponding floor tiles
were removed. Its three-wide bottom socket grid required a half-stud centre offset
on the even-width truck bed. The tipper uses 4080 directly on the deck, with a
forward cab and a fixed transport pose. No tipping motion is asserted.

The motorcycle follows the actual fairing/frame and rim/tyre shortcut offsets.
Its symmetric wheel geometry uses proper rotations, avoiding the reflected
matrix in a legacy shortcut. The launch's ring sits clear of the seat back and
hull walls. Its hull floor is the datum, not an inferred waterline.

The first aircraft had undersized wings, no horizontal stabilizers and a boxy
cabin roof. Replaced these with larger matched swept wings, a supported T-tail
and shaped roof parts. Side views exposed openings at the moulded nose/rear
interfaces; filled those pockets at their actual support heights. A long lower
plate and a support brick bond the rear shell into the fuselage. Correcting the
3039 roof slopes' off-centre origins joined their sockets to the window tops.
The final side view has a continuous fuselage profile.

The detail previews expose real fitting geometry: the seat back projection,
steering stand, instrument slope, upright control stick, recessed side-stud mirror,
chest lattice, lamp crossbar and engine shell/core. These are compact building
lessons. Minifigure knee room, hand reach, headroom and access remain untested.

## Evidence and limits

Every example passes assembly checks; complete vehicles pass their selected
family profile. Python and LeoCAD BOMs match by reference, colour and quantity.
Sources, reports and render manifests share hashes. Road/motorcycle checks find
the expected tyres at the declared ground plane and no curated rectangular
body intrusions into the tested wheel space. Boat/aircraft checks explicitly omit
road-wheel tests and do not infer buoyancy or flight.

Road cars/van/pickup retain nine optimistic connection groups: the full studded
structure, four rim/tyre pairs and four lamps. The tipper adds two lamp groups.
The launch has one structural group plus three round lamps. The aircraft is one
evidenced group. All structural parts in those models must share a group in the
regression tests. Motorcycle frame/fairing/wheel metadata does not establish its
snap connections: seven groups remain, with inspected official shortcut offsets
providing placement evidence. Fitting recipes form one group except the two
round navigation lamps, whose socket metadata is incomplete.

No physical assembly, general solid-intersection analysis, rolling/friction,
strength, balance, figure-fit or retail part/colour availability test was performed.
Curved, hollow and sideways interfaces still need that review for a physical
build. `physical_validity: not_proven` is retained throughout.
