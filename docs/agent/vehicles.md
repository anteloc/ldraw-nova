# Design stud-built vehicles

Use this workflow for attractive System vehicles. Keep Technic frames, suspension,
steering mechanisms, gears and drivetrains outside the current scope. Ordinary
wheel-pin plates, rims, tyres, brackets, clips and stud-built bodies are suitable.
The executable starting set covers road vehicles; boats and aircraft use the
same design process but need hull/wing/landing-gear interfaces and their own
clearance review. Do not run a road-wheel check as certification of those subjects.

## Start with a silhouette and a wheel package

Record the intended era, purpose, character and viewing scale before placing
parts. Choose a low bonnet/cabin/deck, cab-forward commercial body, separate
cab/load bed, or another subject-specific arrangement. Describe what distinguishes
this vehicle from a generic wheeled box. A larger part count is not a design goal.

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
./ldraw-agent design palettes heritage-racing
./ldraw-agent examples --family vehicle
./ldraw-agent vehicle plan grand-tourer --output output/tourer.plan.json
```

`vehicle plan` exports an ordinary version-1 plan and a sibling
`tourer.plan.brief.json`. It is an editable construction starting point, not a
substitute for designing the requested vehicle. It does not scale parts or promise
colour availability. Change the brief and source together. Use the
[vehicle atlas](../../examples/vehicle-atlas/README.md) to study the three different
body arrangements and their opened-image review.

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

The atlas exposes chassis, axles, body, cab and front/rear fascias as separate
sections. Python helpers use X/Z in studs and height in LDU, emitting ordinary
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

`vehicle check` is explicitly for symmetric, fixed-axle road vehicles in the
documented frame. It checks the two supported separate tyre references, actual
ground contact, transverse axes, left/right axle pairing, matching rim transforms,
below-road geometry, and Technic parts. It reports wheelbase and track. Use
`--section` to select a vehicle from a scene, and `--ground-y` only when the
selected frame has a different declared road height.

Circular wheel-space tests against upright curated rectangular bodies produce
**review warnings**, not rubber/material-collision claims. Unknown wheels and
shortcuts remain explicitly unreviewed; no supported tyres fails the check.
Spare wheels, dual wheels, steering poses, motorcycles, aircraft and boats need
manual or separately authored checks. Do not mislabel an intentional alternative
as a valid four-wheel result, or suppress warnings to obtain a green report.

The pinned pyldraw3 version infers the wrong rim-seat axis for the wide 6014a/b
rim because it chooses the shortest bounding-box dimension. Our query adapter
corrects only those shortcut-backed rim frames to their actual local Z axis.
The source library remains unchanged. Tyre/rim contact evidence then works, but
wheel-pin retention and some hollow round-plate lamp contacts remain outside
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

Record image paths, findings and revisions. Automated checks do not measure
beauty. Regenerate checks, BOM and renders from the exact final plan, and retain
`physical_validity: not_proven`. State untested rolling freedom, stress, strength,
driver fit and part/colour availability specifically where relevant.
