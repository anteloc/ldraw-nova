# Design advanced spaceships

Use this workflow for detailed starfighters, freighters, shuttles and capital ships, including Star Wars subjects. Start with the [spaceship atlas](../../examples/spaceship-atlas/README.md): whole ships teach silhouette and scale; smaller cockpit, engine, wing, armour and service-bay studies teach construction. Keep the source's authorship when copying it, and distinguish a reconstruction from an original design.

```sh
./ldraw-agent spaceship list
./ldraw-agent spaceship details
./ldraw-agent examples --family spaceship
./ldraw-agent examples --family spaceship --details
./ldraw-agent spaceship brief starfighter --output output/my-ship-brief.json
```

`brief` also accepts `freighter` and `capital-ship`. It supplies design roles, module suggestions, part-search prompts and a review checklist. Complete its scale, dimensions, pose and attachment decisions before building; it is a brief, not a generated model.

## Establish identity and scale

Decide whether the model is minifigure scale, a larger display model or microscale. Choose two or three defining masses before adding small details: an X-shaped wing arrangement, a long engine pair, a broad asymmetric cargo hull, or a wedge with a raised bridge. For a named fictional ship, study the specific variant and retain its defining proportions.

For new designs use X for width, -Z for forward and negative Y for up. Choose a hull or display-stand datum explicitly; spacecraft do not inherit a car's wheelbase and road plane. Imported source axes may differ. Measure the source before rotating or positioning it, and use proper rotations rather than mirrored or stretched parts.

| Family | Main construction decisions | Visual priorities |
| --- | --- | --- |
| Starfighter/interceptor | Central spine, wing roots, cockpit, nacelles and landing/display attachments | Nose/cockpit balance, thin wing edges, engine spacing and a distinct front silhouette |
| Freighter/shuttle | Cargo frame, access corridor, hull panels, ramp, cockpit and landing supports | Hull mass, deliberate asymmetry, readable loading access and restrained weathering accents |
| Capital ship | Internal truss, lower hull, paired upper panels, bridge, trenches and engine block | Large clean outline, layered silhouette, recessed detail and consistent miniature scale |

## Study constructions and choose real parts

Use Jev only after its availability check; use explicit FTS when unavailable. Search separately for whole-ship proportions and each construction role. Do not restrict useful source parts to the same theme. Spacecraft often combine System skins with Technic frames; `--construction all` helps discover both.

```sh
./ldraw-agent discover search models 'a detailed Star Wars starfighter with wing and engine submodels' \
  --construction all --min-parts 300 --max-parts 2500 --limit 5
./ldraw-agent discover search submodels 'a spaceship engine nacelle with a cylindrical shell and exhaust' \
  --construction all --max-parts 180 --limit 5
```

Inspect dedicated canopies and windscreens with their mating rims, printed instrument tiles, seats and control sticks, matched wedge plates, curved slopes, brackets, hinge halves, cylinders, dishes, cones, grilles, bars and clips. Preserve embedded custom definitions where the source needs them. Do not invent a part ID or replace all these distinctive forms with rectangular slabs.

Use [build pages](build-manuals.md) when layers or hidden interfaces are hard to read. The atlas includes manuals for an X-wing nacelle, an enclosed canopy cockpit, a UCS Y-wing armour panel and a Millennium Falcon service cluster. Its larger wing study includes source sections that can be expanded into manuals when needed.

## Build from the frame outward

Reserve the cockpit, cargo volume, engine envelopes and attachment space first. Separate the internal spine/truss, cockpit tub, nose, wing roots, wings, engines, hull panels, service details and landing/display supports. Record each module's local origin, bounds, mounting parts and dependencies.

Long wings and cantilevered engines need a bonded plate stack or a braced frame. Do not place a wing or pod in space merely because its bounding box touches the hull. Keep a bare-frame or root close-up to inspect the real attachment. Use the [Technic workflow](technic.md) for fixed supports and the [mechanism workflow](mechanisms.md) for actual folding wings, ramps or retracting gear. Analytical mechanism verification remains deferred; a static hinge pose does not demonstrate motion.

Export a reviewed starting construction:

```sh
./ldraw-agent spaceship export b-wing --outdir output/my-starship
./ldraw-agent build output/my-starship/scene.plan.json --contacts none \
  --output output/my-starship/my-starship.mpd
```

Edit the placement plan to position the whole module; edit its attributed `source.mpd` when changing internal parts. Its origin frame is not a promised connector. Check individual new interfaces and fixed supports separately. Export is blocked for inspiration entries with unresolved source errors. Whole-model source studies can contain minifigures, stands or accessories; inspect the section list before using them as a single ship module.

## Make the design attractive

Keep the primary hull colour dominant and use smaller roles for panel shadows, markings, frame, canopy and exhaust. Differentiate mechanical cores from exterior armour. Put fine pipes, clips and grille patterns in a few recessed service areas; leave broad hull and wing surfaces quiet enough to show the silhouette. Repeated engine parts, coherent panel seams and a few deliberate asymmetries read better than uniformly dense decoration.

Use real depth: inset cockpits, layered leading edges, thin outer wing edges, recessed trenches, overlapping armour and concentric engine nozzles. Avoid thick plate sandwiches at every exposed edge. Design the underside, landing feet and display mount with the same care as the top.

## Inspect and deliver

Run normal source and geometry validation and compare Python/LeoCAD BOMs. The spaceship family does not imply car-wheel checks, flight physics or automatic symmetry checks. Preserve diagnostic coverage, especially on imported angled constructions and curves.

Render home/front/back/right/left/top/bottom for a delivered spacecraft, plus exposed frame, cockpit and wing-root views where the exterior hides important work. Judge front/top silhouette, side thickness, rear engines, canopy fit, negative space, detail density and underside supports. Revise after opening the images.

Deliver the editable MPD, reproducible plan/generator, design brief, checks, BOM comparison, attribution and final visual review. Explain source adaptations and outstanding physical limits. Atlas overviews are study images; a new model still needs its own final inspection.
