# Design recognizable, varied models

Start from the requested subject and intended viewing scale. State its distinguishing silhouette, major masses, required functions, palette roles and primary detail. Resolve those choices before adding repeated surface decoration. Part count is not quality. Choose System, SNOT, Technic and flexible techniques by the required form and interface; no subject has a mandatory template.

Search roles, compare different constructions and inspect actual part dimensions. Use one example for a specific lesson; do not inherit its complete proportions or part palette. Dedicated parts are useful when they fit the brief, and brick-built alternatives are useful when they do not. Review shape, support and interfaces together.

## Architecture

Use architecture-specific motifs only for buildings. Record massing, storey heights, entrance hierarchy, roof shapes, recessed glazing, supported projections and a legible street/landscape relationship. Keep quieter walls beside focal details. The [Copper Lane brief](../../../examples/modular-street/design-brief.json) and [review](../../../examples/modular-street/visual-review.md) are one worked example, not a universal design.

`design details` exports editable architectural fittings. The legacy key `flower-planter` describes a tree on a plinth with flower accents, not a low planter. Reserve openings and remove conflicting core geometry before adding fittings. Exact symbol syntax belongs in the [plan reference](../reference/plans.md).

## Vehicles

### Start with a silhouette and the defining parts

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
colour availability. Change the brief and source together. Use current knowledge results for admitted vehicle lessons. The older road recipes remain available as historical fixtures; they are retired from default retrieval.

### Choose dedicated parts before building substitutes

Search [model and submodel references](find-references.md) as well as individual parts. Compare whole vehicles for silhouette, then query one cab, bogie, wing, engine or hull role at a time. `discover parts SAVED_SEARCH.json` exposes the actual fittings used in matched constructions. Inspect parent subject, dimensions, preview images and Technic content before reusing them; a spacecraft module may teach a technique without fitting a passenger aircraft directly.

The [Ferrari F40 section gallery and studies](../../../examples/snot/ferrari-f40/README.md) provide a large sports-car precedent and five checked SNOT details. Study the complete silhouette, then inspect a small body mount, door rail, lamp corner, louver or fascia core. The full source retains overlap errors, and its saved callouts are separate constructions rather than declared children of the flattened car.

The [submodel atlas](../../../examples/submodel-atlas/README.md) adds reviewed vehicle details from real sets, each with a guide and an inspection board: a studs-forward tiled leg shield (S01), rounded roof edges on brackets (S09), a sideways round drive cover (05), a grille built flat and stood on a pin mount (08), a sideways exhaust manifold (S02), an upside-down train belly (S15) and a Technic-mounted lamp cluster (04). Find them with `./ldraw-agent examples --family submodel --details vehicle`.

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

### Build from the inside out

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

### Open renders and make a design revision

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

## Spacecraft

### Establish identity and scale

Decide whether the model is minifigure scale, a larger display model or microscale. Choose two or three defining masses before adding small details: an X-shaped wing arrangement, a long engine pair, a broad asymmetric cargo hull, or a wedge with a raised bridge. For a named fictional ship, study the specific variant and retain its defining proportions.

For new designs use X for width, -Z for forward and negative Y for up. Choose a hull or display-stand datum explicitly; spacecraft do not inherit a car's wheelbase and road plane. Imported source axes may differ. Measure the source before rotating or positioning it, and use proper rotations rather than mirrored or stretched parts.

| Family | Main construction decisions | Visual priorities |
| --- | --- | --- |
| Starfighter/interceptor | Central spine, wing roots, cockpit, nacelles and landing/display attachments | Nose/cockpit balance, thin wing edges, engine spacing and a distinct front silhouette |
| Freighter/shuttle | Cargo frame, access corridor, hull panels, ramp, cockpit and landing supports | Hull mass, deliberate asymmetry, readable loading access and restrained weathering accents |
| Capital ship | Internal truss, lower hull, paired upper panels, bridge, trenches and engine block | Large clean outline, layered silhouette, recessed detail and consistent miniature scale |

### Study constructions and choose real parts

Use Jev only after its availability check; use explicit FTS when unavailable. Search separately for whole-ship proportions and each construction role. Do not restrict useful source parts to the same theme. Spacecraft often combine System skins with Technic frames; `--construction all` helps discover both.

```sh
./ldraw-agent discover search models 'a detailed Star Wars starfighter with wing and engine submodels' \
  --construction all --min-parts 300 --max-parts 2500 --limit 5
./ldraw-agent discover search submodels 'a spaceship engine nacelle with a cylindrical shell and exhaust' \
  --construction all --max-parts 180 --limit 5
```

Inspect dedicated canopies and windscreens with their mating rims, printed instrument tiles, seats and control sticks, matched wedge plates, curved slopes, brackets, hinge halves, cylinders, dishes, cones, grilles, bars and clips. Preserve embedded custom definitions where the source needs them. Do not invent a part ID or replace all these distinctive forms with rectangular slabs.

Use [build pages](review-models.md) when layers or hidden interfaces are hard to read. The atlas includes manuals for an X-wing nacelle, an enclosed canopy cockpit, a UCS Y-wing armour panel and a Millennium Falcon service cluster. Its larger wing study includes source sections that can be expanded into manuals when needed.

The [6208 B-Wing SNOT study](../../../examples/snot/b-wing-6208/README.md) supplies a complementary introduction with 22 inspected views and two exposed-core selections. It uses the supplied 6208 source, distinct from the atlas's 75050 B-Wing. Geometry and flexible-part verification are deferred for that learning study.

The [submodel atlas](../../../examples/submodel-atlas/README.md) adds a shuttle OMS pod with a colour-coded SNOT core under a hinged shell (06), a cockpit pod on a revolute pivot with its axis marked (07), and two micro ships: wings stood on edge on clips (S16) and a hull built sideways along its length (S22). Find them with `./ldraw-agent examples --family submodel --details spaceship`.

Halcyon's generator, exposed-core images, module views and visual review show the complete workflow. Read its [attachment map](../../../examples/snot/halcyon/README.md#3-module-topology) before adapting the local frames and panel mounts.

### Build surfaces in their own local grids

The 6208 construction shows four useful ways to attach a spaceship's outer surfaces:

| Surface role | Source example | Design lesson |
|---|---|---|
| Fixed perpendicular details | `Center Front`: opposing `44728` brackets, a `2436a` bracket and `52107` side-stud bricks | Establish the stud faces before adding tiles, fins and slopes |
| Curved skin around a Technic core | `Center Side 2`: axle connectors, `4032a` round plates and opposing plate skins | Separate the internal attachment system from the visible surface grid |
| Angled armour | `Center Front`: `3937`/`6134` hinge pairs | Give oblique panels their own attachment and local plane |
| Large wing module | `Center Side 1` carrier and the three wing sections | Build a thin local wing with a defined root, then orient the whole module in its parent |

Choose the interface that serves the surface's role. A rotated module can contain mostly ordinary upright stacks in its own frame. Keep that frame readable, and distinguish its local up direction from the complete ship's pose. The cockpit and its support arm are a useful example of this separation.

For visual variety, combine a few broad wing or hull shapes with small repeated engine and tip details. The 6208 exhaust uses four round-brick/dish nozzle stacks; its cockpit is shaped around a dedicated transparent canopy. Source prose can misdescribe those parts, so read the actual inventory and images. Its sections each contain one construction state: selected-part cutaways reveal layers, but are not source build steps.

### Build from the frame outward

Reserve the cockpit, cargo volume, engine envelopes and attachment space first. Separate the internal spine/truss, cockpit tub, nose, wing roots, wings, engines, hull panels, service details and landing/display supports. Record each module's local origin, bounds, mounting parts and dependencies.

Long wings and cantilevered engines need a bonded plate stack or a braced frame. Do not place a wing or pod in space merely because its bounding box touches the hull. Keep a bare-frame or root close-up to inspect the real attachment. Use the [Technic workflow](technic.md) for fixed supports and the [mechanism workflow](mechanisms.md) for actual folding wings, ramps or retracting gear. A static hinge pose does not demonstrate motion; use explicit motion checks when requested.

When the brief calls for Halcyon’s particular core-and-skin construction, export it explicitly:

```sh
./ldraw-agent spaceship export halcyon --outdir output/my-starship
./ldraw-agent build output/my-starship/halcyon.plan.json \
  --output output/my-starship/my-starship.mpd
```

For Halcyon, edit its generator and rebuild the plan. Other atlas exports supply a placement plan and attributed `source.mpd`; edit the placement plan to position the whole module and the source for internal changes. An origin frame is not a promised connector. Check new interfaces and fixed supports separately. Export remains blocked for inspiration entries with unresolved source errors. Whole-model source studies can contain minifigures, stands or accessories; inspect their section lists.

### Make the design attractive

Keep the primary hull colour dominant and use smaller roles for panel shadows, markings, frame, canopy and exhaust. Differentiate mechanical cores from exterior armour. Put fine pipes, clips and grille patterns in a few recessed service areas; leave broad hull and wing surfaces quiet enough to show the silhouette. Repeated engine parts, coherent panel seams and a few deliberate asymmetries read better than uniformly dense decoration.

Use real depth: inset cockpits, layered leading edges, thin outer wing edges, recessed trenches, overlapping armour and concentric engine nozzles. Avoid thick plate sandwiches at every exposed edge. Design the underside, landing feet and display mount with the same care as the top.

Review the actual attachment structure before closing the skins, then inspect the completed exterior. Major hull faces should read as shaped spacecraft surfaces; keep the supports inside and use deliberate seams, curves and recesses to control the visible form.

### Inspect and deliver

Run normal source and geometry validation and compare Python/LeoCAD BOMs. The spaceship family does not imply car-wheel checks, flight physics or automatic symmetry checks. Preserve diagnostic coverage, especially on imported angled constructions and curves.

Render home/front/back/right/left/top/bottom for a delivered spacecraft, plus exposed frame, cockpit and wing-root views where the exterior hides important work. Judge front/top silhouette, side thickness, rear engines, canopy fit, negative space, detail density and underside supports. Revise after opening the images.

Deliver the editable MPD, reproducible plan/generator, design brief, checks, BOM comparison, attribution and final visual review. Explain source adaptations and outstanding physical limits. Atlas overviews are study images; a new model still needs its own final inspection.

## Animals, objects and interiors

For an animal, establish silhouette, pose and expressive features at the chosen scale; test articulation and support separately. For an object, define its characteristic proportions, readable controls and actual seams. For an interior, choose a clear activity and furniture scale with access and headroom where required. Avoid borrowing façade motifs or spacecraft machinery simply because a familiar recipe exists.

## Visual revision

Open whole-model and detail views. Is the subject recognizable at thumbnail size? Do proportions, quiet surfaces, focal detail and palette support it? Check hidden faces, floating details, collisions and parent mounts separately. Record a concrete revision and regenerate final evidence from the same source. Numeric checks do not measure beauty; attractive images do not clear invalid connections.

