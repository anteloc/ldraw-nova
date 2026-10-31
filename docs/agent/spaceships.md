# Design advanced spaceships

**Every new spaceship uses SNOT by default. Start with the [Halcyon interceptor](../../examples/snot/halcyon/README.md) as the default construction and visual-quality reference.** Its supported core, sideways hull skins, axial intakes and exhausts, smooth contours and thin wings establish the approach. Use SNOT for substantial exterior surfaces and give each surface a real attachment. An upright internal core is appropriate; the exterior should have deliberately shaped panels and a coherent silhouette.

Apply this workflow to starfighters, freighters, shuttles and capital ships, including Star Wars subjects. Adapt Halcyon's construction principles to the requested scale and identity. Use the [spaceship atlas](../../examples/spaceship-atlas/README.md) for supporting silhouette, cockpit, engine, wing and armour studies. Keep source authorship when copying a construction.

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

The [6208 B-Wing SNOT study](../../examples/snot/b-wing-6208/README.md) supplies a complementary introduction with 22 inspected views and two exposed-core selections. It uses the supplied 6208 source, distinct from the atlas's 75050 B-Wing. Geometry and flexible-part verification are deferred for that learning study.

The [submodel atlas](../../examples/submodel-atlas/README.md) adds a shuttle OMS pod with a colour-coded SNOT core under a hinged shell (06), a cockpit pod on a revolute pivot with its axis marked (07), and two micro ships: wings stood on edge on clips (S16) and a hull built sideways along its length (S22). Find them with `./ldraw-agent examples --family submodel --details spaceship`.

Halcyon's generator, exposed-core images, module views and visual review show the complete workflow. Read its [attachment map](../../examples/snot/halcyon/README.md#3-module-topology) before adapting the local frames and panel mounts.

## Build surfaces in their own local grids

The 6208 construction shows four useful ways to attach a spaceship's outer surfaces:

| Surface role | Source example | Design lesson |
|---|---|---|
| Fixed perpendicular details | `Center Front`: opposing `44728` brackets, a `2436a` bracket and `52107` side-stud bricks | Establish the stud faces before adding tiles, fins and slopes |
| Curved skin around a Technic core | `Center Side 2`: axle connectors, `4032a` round plates and opposing plate skins | Separate the internal attachment system from the visible surface grid |
| Angled armour | `Center Front`: `3937`/`6134` hinge pairs | Give oblique panels their own attachment and local plane |
| Large wing module | `Center Side 1` carrier and the three wing sections | Build a thin local wing with a defined root, then orient the whole module in its parent |

Choose the interface that serves the surface's role. A rotated module can contain mostly ordinary upright stacks in its own frame. Keep that frame readable, and distinguish its local up direction from the complete ship's pose. The cockpit and its support arm are a useful example of this separation.

For visual variety, combine a few broad wing or hull shapes with small repeated engine and tip details. The 6208 exhaust uses four round-brick/dish nozzle stacks; its cockpit is shaped around a dedicated transparent canopy. Source prose can misdescribe those parts, so read the actual inventory and images. Its sections each contain one construction state: selected-part cutaways reveal layers, but are not source build steps.

## Build from the frame outward

Reserve the cockpit, cargo volume, engine envelopes and attachment space first. Separate the internal spine/truss, cockpit tub, nose, wing roots, wings, engines, hull panels, service details and landing/display supports. Record each module's local origin, bounds, mounting parts and dependencies.

Long wings and cantilevered engines need a bonded plate stack or a braced frame. Do not place a wing or pod in space merely because its bounding box touches the hull. Keep a bare-frame or root close-up to inspect the real attachment. Use the [Technic workflow](technic.md) for fixed supports and the [mechanism workflow](mechanisms.md) for actual folding wings, ramps or retracting gear. Analytical mechanism verification remains deferred; a static hinge pose does not demonstrate motion.

Copy the default design as an editable starting point:

```sh
./ldraw-agent spaceship export halcyon --outdir output/my-starship
./ldraw-agent build output/my-starship/halcyon.plan.json \
  --output output/my-starship/my-starship.mpd
```

For Halcyon, edit its generator and rebuild the plan. Other atlas exports supply a placement plan and attributed `source.mpd`; edit the placement plan to position the whole module and the source for internal changes. An origin frame is not a promised connector. Check new interfaces and fixed supports separately. Export remains blocked for inspiration entries with unresolved source errors. Whole-model source studies can contain minifigures, stands or accessories; inspect their section lists.

## Make the design attractive

Keep the primary hull colour dominant and use smaller roles for panel shadows, markings, frame, canopy and exhaust. Differentiate mechanical cores from exterior armour. Put fine pipes, clips and grille patterns in a few recessed service areas; leave broad hull and wing surfaces quiet enough to show the silhouette. Repeated engine parts, coherent panel seams and a few deliberate asymmetries read better than uniformly dense decoration.

Use real depth: inset cockpits, layered leading edges, thin outer wing edges, recessed trenches, overlapping armour and concentric engine nozzles. Avoid thick plate sandwiches at every exposed edge. Design the underside, landing feet and display mount with the same care as the top.

Review the exposed attachment course before the skins and then the completed exterior, following Halcyon's core/module/final views. Major hull faces should read as shaped spacecraft surfaces; keep the supports inside and use deliberate seams, curves and recesses to control the visible form.

## Inspect and deliver

Run normal source and geometry validation and compare Python/LeoCAD BOMs. The spaceship family does not imply car-wheel checks, flight physics or automatic symmetry checks. Preserve diagnostic coverage, especially on imported angled constructions and curves.

Render home/front/back/right/left/top/bottom for a delivered spacecraft, plus exposed frame, cockpit and wing-root views where the exterior hides important work. Judge front/top silhouette, side thickness, rear engines, canopy fit, negative space, detail density and underside supports. Revise after opening the images.

Deliver the editable MPD, reproducible plan/generator, design brief, checks, BOM comparison, attribution and final visual review. Explain source adaptations and outstanding physical limits. Atlas overviews are study images; a new model still needs its own final inspection.
