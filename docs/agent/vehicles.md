# Design System vehicles

Use this workflow for attractive System vehicles. For a Technic frame or a hybrid
body, also follow the [Technic structural workflow](technic.md). For steering,
gearing, drivetrains or other mechanisms, follow the authorized [Stage 2 workflow](mechanisms.md); analytical mechanism verification is deferred. Ordinary
wheel-pin plates, rims, tyres, brackets, clips and stud-built bodies are suitable.
The executable starting set includes a coupe, van, pickup, tipper truck, motorcycle,
harbour launch and courier aircraft. These use different construction systems:
wheel-pin chassis, a motorcycle frame, a moulded hull, or aircraft nose/wing/engine
assemblies. Select the family before choosing dimensions or checks.

For fictional spacecraft, use the [spaceship workflow](spaceships.md) and its atlas. It has its own silhouettes, module roles and review criteria; the road and aircraft checks here do not establish spacecraft fit or flight performance.

## Start with a silhouette and the defining parts

Record the intended era, purpose, character and viewing scale before placing
parts. Choose a low bonnet/cabin/deck, cab-forward commercial body, separate
cab/load bed, or another subject-specific arrangement. Describe what distinguishes
this vehicle from a generic wheeled box. A larger part count is not a design goal.

For every family, keep **X across, -Z forward and negative Y up**. Boats use
the interior hull floor as Y=0; aircraft use the nose floor and an in-flight display
pose. Neither datum implies water level or landing-gear height. Motorcycles use
the measured frame axle spacing and tyre envelope.

For a road vehicle, use **X across the vehicle, -Z forward, negative Y up, and
Y=0 at the road**. Keep a single master layout of tyre centres, axle stations,
track, wheelbase, front/rear overhangs, body width, sill height, glazing base,
roof height and cabin/bed boundaries. Choose wheels before the chassis and
bodywork. The tyre envelope constrains everything around it.

| Decision | What to establish |
|---|---|
| Scale | Four-wide compact, six-wide town/display, eight-wide detailed, or a deliberate alternative; whether a real figure must fit |
| Stance | Track relative to body width, tyre diameter, ground clearance, wheelbase and overhang balance |
| Major masses | Bonnet length, windscreen rake, cabin position and height, rear deck or cargo volume |
| Surface language | A few related curves/slopes; deliberate transitions through nose, shoulders and tail |
| Identity | One strong front light/grille treatment and two supporting features |
| Palette | Body, roof, trim, chassis, metal, glass, head/tail lamps; keep broad surfaces quiet |

Use length/width, wheelbase/length and roof-height/length as comparisons to your
chosen subject, not universal pass/fail ratios. A bus, sports car and delivery van
should not share proportions. Decide early whether a cabin is display glazing
or must accommodate seats, controls, a driver, headroom and an access route.

```sh
./ldraw-agent vehicle list
./ldraw-agent vehicle wheels
./ldraw-agent vehicle details
./ldraw-agent examples --family vehicle --details
./ldraw-agent design palettes heritage-racing
./ldraw-agent examples --family vehicle
./ldraw-agent vehicle plan grand-tourer --output output/tourer.plan.json
```

`vehicle plan` exports an ordinary version-1 plan and a sibling
`tourer.plan.brief.json`. It is an editable construction starting point, not a
substitute for designing the requested vehicle. It does not scale parts or promise
colour availability. Change the brief and source together. Use the
[vehicle atlas](../../examples/vehicle-atlas/README.md) to study the seven different
vehicle arrangements and their opened-image review.

## Choose dedicated parts before building substitutes

Search [model and submodel references](reference-discovery.md) as well as individual parts. Compare whole vehicles for silhouette, then query one cab, bogie, wing, engine or hull role at a time. `discover parts SAVED_SEARCH.json` exposes the actual fittings used in matched constructions. Inspect parent subject, dimensions, preview images and Technic content before reusing them; a spacecraft module may teach a technique without fitting a passenger aircraft directly.

Use actual seats, steering wheels, windscreens, mudguards, motorcycle frames,
boat hulls, aircraft shells, wings, engine housings, printed instruments and cargo
containers where they suit the design. Do not fill every functional area with
bricks and slabs first and then decorate around it. Choose the fittings, reserve
their envelopes, and build the surrounding structure to their interfaces.
Brick-built alternatives are useful when the dedicated part does not fit the
subject or scale; state the reason in the brief.

```sh
./ldraw-agent vehicle details driver-cockpit --output output/cockpit.plan.json
./ldraw-agent vehicle details cargo-chest --palette desert-utility --output output/load.plan.json
./ldraw-agent examples cockpit --family vehicle --details
./ldraw-agent part-board 4079 3829c01 3039p34 30150 --outdir output/vehicle-fittings
./ldraw-agent search parts 'boat hull' --limit 8
./ldraw-agent search parts 'plane' --limit 8
```

| Recipe | Real fittings | Assembly contract |
|---|---|---|
| `driver-cockpit` | 4079 seat, 3829c01 steering stand/wheel, 3069bp25 printed dashboard | 2×6 floor; base underside Y=0; seat back extends past its floor |
| `pilot-cockpit` | 4079 seat, 4592/4593 control stick, 3039p34 instruments | 2×8 floor; upright static stick, front -Z |
| `wing-mirror` | 4070 side-stud mount and 3070b mirror tile | Recessed stud at Z=-6; tile face Z=-14, whole fitting yawed outward |
| `cargo-chest` | 30150 moulded open chest with handles | 3×4 pallet; half-stud centre offset on an even-width deck; replace tiles under it |
| `navigation-lights` | Paired transparent red/green round lamps | Four-stud crossbar, port -X/red, starboard +X/green |
| `jet-engine-pod` | 4868b engine shell and 4869 core | Common native origin; mount stud body plane Y=0, body hangs to Y=46 |

These export ordinary plans with explicit anchors, just like architectural details.
`ldraw_tools.vehicle_details.detail_module()` composes them directly into other
Python modules. The cockpit palettes use the `wood` role for seat upholstery.
Read `recipe.json` and the opened detail previews in the atlas. A displayed seat
and controls do not establish minifigure fit: check cushion, back, knees, hand
reach, headroom and roof access together. Remove conflicting tiles/core parts
before inserting fittings. Render a roof-off view when the complete shell hides them.

## Find compatible shapes, then inspect actual interfaces

Use [Jev discovery](tooling.md#jev-part-discovery) for one role at a time, for example
`a shallow curved slope for the bonnet of a six-stud vintage car`,
`a low raked windscreen for a small brick-built coupe`, or
`a mudguard for a small delivery van using wheel-pin plates`.
These are part queries, not requests for a complete vehicle. Keep ranks and
rejected candidates in the design notes when they informed a decision.

```sh
./ldraw-agent catalog parts 'mudguard' --category car --limit 8 --measure
./ldraw-agent catalog parts 'windscreen' --category windscreens --limit 8 --measure
./ldraw-agent catalog parts 'curved' --category slopes --limit 8 --measure
./ldraw-agent part 6157 --limit 50
./ldraw-agent part 6014b --limit 50
./ldraw-agent part 6015 --limit 50
./ldraw-agent part-board 98282 2437 4176 50950 --outdir output/vehicle-shortlist
./ldraw-agent search submodels 'wheel OR chassis OR windscreen' --limit 6
```

Open selection boards. Names and cached dimensions are insufficient for tyre
diameter, wheel-pin depth, recessed headlight studs or curved slope undersides.
Use current part geometry, connector frames and official wheel/tyre shortcuts.
Inspect replacements: a legacy `6014.dat` reference is not interchangeable
metadata with current `6014b.dat` without reviewing the variant.

The two measured recipes in `ldraw_tools.vehicles.axle()` place tyres and rims
as separate physical leaves. Their official shortcut relationships are:

| Package | Holder / rim / tyre | Actual tyre envelope | Interface |
|---|---|---|---|
| `classic` | 4600 / 4624 / 3641 | Diameter 36, width 16 LDU; track 60 | Co-located rim/tyre from `4624c01`; holder pins at local Y=5, stud body plane Y=0 |
| `touring` | 6157 / 6014b / 6015 | Diameter approximately 50, width 28 LDU; track 92 | Tyre at rim-local Z=-6 from `6014bc01`; holder pins at local Y=5, stud body plane Y=8 |

For the touring package on the road, holder origin Y=-30, wheel axis Y=-25,
holder stud plane Y=-22, and the first plate top Y=-30. A second plate reaches
Y=-38. The fenders used here sit at Y=-62, X=±20 and face outwards. These are
local construction contracts, not guesses from full bounding-box heights.
`vehicle wheels` reports current installed bounds alongside the authored recipe.
Changing the wheel package requires rechecking the complete chassis and body.

## Build from the inside out

1. Test one axle with both wheels; inspect rim orientation, retention and tyre
   seating. Rotate the opposite side using a proper matrix, never a reflection.
2. Join the axle stations with a bonded narrow spine. Cross plates bridge seams
   outside the tyre space; avoid a full-width floor passing through the wheels.
3. Reserve both side wheel wells. Add actual fenders or supported brick-built
   arches around them. A hollow fender's AABB is not its internal clearance.
4. Establish a continuous shoulder/sill line and coherent bonnet-to-cabin
   transitions. Use slopes for shape, with measured sockets and real support.
5. Fit glazing and any required interior before closing the roof. Avoid a tall
   stack of plates masquerading as a sports-car cabin. Treat windscreen rake,
   roof width and overhang as a single composition.
6. Add supported front/rear fascias and restrained functional details: paired
   headlights, red tail lamps, grille, bumpers, mirrors, handles, exhaust or cargo
   fittings as appropriate. Every sideways tile needs a real side-stud interface.
7. Cap selected broad surfaces with long tiles or curved pieces. Leave studs only
   where they support something or contribute deliberately to the LEGO character.

The road examples expose chassis, axles, body, cab and front/rear fascias as
separate sections. The other families author their own frame, hull or fuselage.
The tipper bucket is fixed in its transport pose; no tipping mechanism is claimed. Python helpers use X/Z in studs and height in LDU, emitting ordinary
plans through the existing `Module`/builder API. New body families should author
their own modules around measured wheel interfaces; do not stretch the existing
plans or simply lengthen every dimension.

## Check structure and vehicle layout separately

```sh
./ldraw-agent build output/tourer.plan.json --output output/tourer.mpd --detail summary
./ldraw-agent validate output/tourer.mpd --geometry --detail summary --report output/tourer.validation.json
./ldraw-agent vehicle check output/tourer.mpd --report output/tourer.vehicle.json
./ldraw-agent render output/tourer.mpd --outdir output/tourer-review \
  --views home front back right top bottom
./ldraw-agent compare-bom output/tourer.mpd --csv output/tourer-review/leocad-bom.csv
```

Choose the review profile explicitly for a non-car family:

```sh
./ldraw-agent vehicle check output/motorcycle.mpd --profile motorcycle
./ldraw-agent vehicle check output/launch.mpd --profile watercraft
./ldraw-agent vehicle check output/jet.mpd --profile aircraft
```

| Profile | Bounded evidence |
|---|---|
| `road` (default) | Supported separate tyres/rims, transverse axes, actual ground plane, symmetric wheel pairs at two or more stations, wheelbase/track, below-road geometry |
| `motorcycle` | Two centreline 50861/50862 wheels, ground contact, measured 50859b axle stations and the 85983 fairing/frame offset from official shortcuts |
| `watercraft` | Presence of the taught 2551 hull, 4079 seat and 3829c01 helm; no road-plane test |
| `aircraft` | Matched 87613/87612/87611 nose and glass transforms, 4868b/4869 engine cores, paired swept wings and engine positions; no road-plane test |

These profiles deliberately recognize the taught part families. A missing
supported part produces an explicit diagnostic; a different hull, aircraft or
motorcycle requires its own measured interface review. All profiles reject
Technic parts. Watercraft and aircraft reports mark wheel checks
`not_applicable`; passing their part/alignment checks does not establish attachment,
buoyancy, flight or landing-gear clearance. Always run assembly validation too.
Use `--section` to select a vehicle from a scene. `--ground-y` only changes the
road/motorcycle datum. Reports keep `physical_validity: not_proven`.

Circular wheel-space tests against upright curated rectangular bodies produce
**review warnings**, not rubber/material-collision claims. Unknown wheels and
shortcuts remain explicitly unreviewed. Spare wheels, dual wheels, articulated
steering, balance and motion need separate review. Do not suppress warnings to
obtain a green report.

The pinned pyldraw3 version infers the wrong rim-seat axis for the wide 6014a/b
rim because it chooses the shortest bounding-box dimension. Our query adapter
corrects only those shortcut-backed rim frames to their actual local Z axis.
The source library remains unchanged. Tyre/rim contact evidence then works, but
wheel-pin retention, motorcycle frame/fairing snaps and some hollow round-plate
lamp contacts remain outside
the connection evidence observed in these examples. Inspect their real geometry
and report that limitation; disconnected evidence is not an automatic construction
failure or a reason to invent connectors.

## Open renders and make a design revision

Review a front three-quarter, true side, front, rear, top and underside. View the
cab/bed separately if the roof hides it. Use these questions to drive a concrete
revision before delivery:

- Does the silhouette read as this vehicle at thumbnail size? Does its stance
  suit its purpose, with wheels neither lost in the body nor comically exposed?
- Is the side profile coherent from bonnet through glazing and roof to the tail?
  Are overhangs, wheel arches and ground clearance convincing together?
- Are the front and rear designed, with readable lamps, grille and bumper depth?
- Do roof thickness, glazing, interior and body width agree at this scale?
- Do long surfaces have clean intentional seams and an organized palette?
  Remove random stripes, excessive studs, oversized roof lips and unrelated trim.
- Are tyres visibly clear of arches, sills and underbody? Are paired wheels
  aligned? Inspect both sides, not just the flattering three-quarter view.

For boats, inspect hull/helm proportions, deck access, hull-side clearance and
the distinction between floor and waterline. For aircraft, inspect wing span and
sweep, engine spacing, nose-to-cabin transitions, closed fuselage interfaces and
tail proportions. For motorcycles, inspect the frame/fairing fit, wheel alignment,
handlebars, saddle and luggage clearance.

Record image paths, findings and revisions. Automated checks do not measure
beauty. Regenerate checks, BOM and renders from the exact final plan, and retain
`physical_validity: not_proven`. State untested rolling freedom, stress, strength,
driver fit and part/colour availability specifically where relevant.
