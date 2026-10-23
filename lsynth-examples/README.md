# LSynth construction studies

These 26 examples are useful references for **the rigid construction around
flexible parts**: track carriers, bearing supports, pneumatic controls, cable
terminations, lighting fixtures and shaped frames. They add useful subjects and
part combinations to the Technic repertoire. Their strongest lesson is to design
the mounts, wheel stack or port hardware before shaping the flexible route.

Each `*-Constraints.*` file now starts with a plain-language identity, followed
by scene, rigid-construction, building and reuse notes. Local `Study N` comments
explain selected SYNTH blocks; numbers refer to their order in that file. Existing
part annotations remain in place. The matching `*-Synthesis.*` files show the
supplied generated scenes; they have not been regenerated or edited.

Start with the track carrier, pneumatic controls, Flex-System frame and swept
axle frame below. Then read the [industrial construction lessons](../docs/agent/technic-patterns/industrial-assemblies.md)
for applying them to a new model. Use the [LSynth guide](../docs/agent/flexible-parts.md)
for generation commands and the [small flex examples](../examples/flex/README.md)
for simpler inputs to adapt.

![Opaque study views of the platform, swept frame, track carrier and cable linkage](previews/opaque-2.jpg)

*Study copies make transparent parts opaque grey to expose the construction.
These colours do not establish a real inventory.*

## Choose a reference by construction

| Constraint source | What the scene shows | Most useful lesson |
| --- | --- | --- |
| [TECHNIC_CHAIN_TREAD_38](TECHNIC_CHAIN_TREAD_38-Constraints.ldr) | Long track carrier, four large middle wheels, small end wheels and a spring detail | Wheel plane, beam carrier, bushes and end mounts; four wheel positions are duplicated in the route records |
| [TECHNIC_PNEUMATIC_HOSE](TECHNIC_PNEUMATIC_HOSE-Constraints.ldr) | Hand pump, lever valve and two-port cylinder | Actual nozzles, accessible controls and cylinder mounts before hoses |
| [TECHNIC_FLEX-SYSTEM](TECHNIC_FLEX-SYSTEM-Constraints.ldr) | Tall frame with crossed cables, outer guide and lower clip samples | Distinguish cable ends, fixed sleeve supports and lever pivots |
| [TECHNIC_AXLE_FLEXIBLE](TECHNIC_AXLE_FLEXIBLE-Constraints.ldr) | Swept open frame with angular rails and curved lower edges | Axle joiners and angle connectors establish a light body or canopy outline |
| [TECHNIC_TREAD_CRAWLER](TECHNIC_TREAD_CRAWLER-Constraints.ldr) | Vintage low, stepped and upright crawler layouts | Dedicated bearing bricks and their matching cylindrical-axle wheel family |
| [TECHNIC_TREAD](TECHNIC_TREAD-Constraints.ldr) | Three continuous-rubber-track carriers | Axle support, retention and angled liftarm frames; wheels are hidden in the supplied synthesis |
| [TECHNIC_CHAIN_TREAD](TECHNIC_CHAIN_TREAD-Constraints.ldr) | Two separate track-size comparisons | Carrier bricks, axle pins and end-wheel size define the envelope |
| [TECHNIC_CHAIN_LINK](TECHNIC_CHAIN_LINK-Constraints.ldr) | Gear pairs, a long supported chain route and smaller wrap studies | Gear centres, chain planes and the support rail |
| [TECHNIC_CHAIN_LINK_WITH_TWO_STUDS](TECHNIC_CHAIN_LINK_WITH_TWO_STUDS-Constraints.ldr) | Studded chain around coarse-toothed wheels | A starting point for conveyor flights, using its own link/wheel family |
| [STRING_HOSE](STRING_HOSE-Constraints.ldr) | Reel, sheaves, hooks and wound shafts | Separate drum, hook block, rope route and the still-needed bearing frame |
| [RUBBER_BAND](RUBBER_BAND-Constraints.ldr) | Triangular, crossed and micromotor pulley arrangements | Pulley planes and guides; some displayed routes need correction |
| [RUBBER_BELT](RUBBER_BELT-Constraints.ldr) | Two-wheel and multi-wheel flat-belt layouts | Plan centres and shafts together; a rim is not automatically a suitable pulley |
| [FIBER_OPTICS_CABLE](FIBER_OPTICS_CABLE-Constraints.ldr) | Four-cylinder V engine, optical distributor and loose guide samples | Repeated cylinder details and an orderly cross-block accessory rail |
| [FIBER_OPTICS_CABLE_WIDE](FIBER_OPTICS_CABLE_WIDE-Constraints.ldr) | Paired broad light guides around a compact mirrored frame | Short axles, cross blocks and hanging levers; the parent unit is unresolved |
| [ELECTRIC_POWER_FUNCTION_CABLE](ELECTRIC_POWER_FUNCTION_CABLE-Constraints.ldr) | Battery box, receivers and four motors laid out on a bench | Reserve controls, plug access, motor mounts and output couplings |
| [ELECTRIC_POWER_FUNCTION_CABLE_HALF](ELECTRIC_POWER_FUNCTION_CABLE_HALF-Constraints.ldr) | Plug, middle box and two small lamp heads | Use the actual branch junction and lamp-entry variants |
| [ELECTRIC_NXT_CABLE](ELECTRIC_NXT_CABLE-Constraints.ldr) | Controller, three sensors and two motors | Sensor faces, port access and cable slack; local plug geometry is missing |
| [ELECTRIC_RCX_CABLE](ELECTRIC_RCX_CABLE-Constraints.ldr) | RCX controller, sensors and motors | Separate electrical, mounting and output interfaces in a legacy system |
| [ELECTRIC_CABLE](ELECTRIC_CABLE-Constraints.ldr) | Tall workshop lamp with dish shade and a coiled lead | A signal mast, side arm and lamp make a slim industrial fixture |
| [HOSE_FLEXIBLE_12L](HOSE_FLEXIBLE_12L-Constraints.ldr) | Three-wheeled exploration rover with bubble cockpit | Combine Technic wheel mounts with System bodywork and a clear silhouette |
| [HOSE_FLEXIBLE_19L](HOSE_FLEXIBLE_19L-Constraints.ldr) | Raised equipment turret beside a curved barrier | Large cylinders, turntable, side studs and small fittings establish industrial massing |
| [HOSE_FLEXIBLE_8.5L](HOSE_FLEXIBLE_8.5L-Constraints.ldr) | Pipe mounting board with arches and an upright loop | Side-facing end seats and fitting variants control the route |
| [TECHNIC_RIBBED_HOSE](TECHNIC_RIBBED_HOSE-Constraints.ldr) | Tall arch, low return and straight samples | Pin-bearing supports and ribbed texture; touching spans do not establish a joint |
| [BRICK_ARC](BRICK_ARC-Constraints.dat) | Four curved fingers around a cylindrical wrist | Robotic silhouette and cylindrical housings; the fingers are shape studies |
| [MINIFIG_CHAIN_16L](MINIFIG_CHAIN_16L-Constraints.ldr) | Chains spread across a square display board | Visible end fittings for barriers, retained cargo and hanging detail |
| [STRING_xxL](STRING_xxL-Constraints.ldr) | Measuring-board display of straight and curved strings | End hardware and deliberate sag; length presets do not certify stock lengths |

## View the evidence

The semantic review on 2026-10-23 rendered all 26 supplied synthesis scenes in
home and front views. All 26 home views were opened in the labelled sheets below.
Twelve additional opaque views were opened to read the rigid structures, plus
the individual front views of the [optical engine](previews/optical-engine-front.png)
and [raised platform](previews/platform-front.png).

| Opened sheet | Contents |
| --- | --- |
| [Original 1](previews/original-1.jpg) | Claw, workshop lamp, NXT, Power Functions, twin lights, RCX |
| [Original 2](previews/original-2.jpg) | Both optical studies, three corrugated-hose scenes, minifigure chains |
| [Original 3](previews/original-3.jpg) | Bands, belts, winch, strings, swept frame, small-link chain |
| [Original 4](previews/original-4.jpg) | Studded chain, both hinged-track studies, Flex-System, pneumatics, ribbed hose |
| [Original 5](previews/original-5.jpg) | Continuous tread and vintage crawler |
| [Opaque 1](previews/opaque-1.jpg) | Claw, optical engine, broad-guide frame, exploration rover |
| [Opaque 2](previews/opaque-2.jpg) | Raised platform, swept frame, long track carrier, Flex-System |
| [Opaque 3](previews/opaque-3.jpg) | Pneumatics, continuous tread, vintage crawler, winch |

The [additional tread view](previews/tread-wheels-visible.png) also reveals the
nine hidden wheel placements, with their original positions and orientations.
It is an explanatory copy, not a change to the supplied synthesis.

The [review record](semantic-review.json) binds the source hashes, annotation
preservation checks, previews and known omissions. Full-size renders and local
render scripts are in `output/lsynth-semantic-study/` in the working checkout.
Rendering used an isolated library overlay for bundled LSynth geometry; the
installed parts library was left unchanged. Only the overlay's LS22 author text
needed Latin-1 decoding.

## What can be reused

**Strong construction references:** the track carriers, pneumatic component
layout, shaped axle frame, cable/sleeve terminations, lamp and rover. Select one
coherent assembly and preserve its interface context while adding the mounts
needed by the new model.

**Useful part and layout studies:** the electrical benches, winch hardware,
optical fittings and chain/belt comparisons. These identify parts and relationships;
many omit a chassis, bearing frame, output coupling or fixed anchor.

**Primarily shape demonstrations:** isolated wheel wraps, floating string/chain
poses and the brick-arc fingers. These suggest visual treatments. They do not
establish gravity, legal joints, articulation, tension or manufactured length.

Specific qualifications belong with the useful evidence:

- The local previews omit `x933c01.dat` plugs in NXT, `4173497.dat` in the broad
  optical study, `3020a.dat` in the rover, and `57539a.dat`/`57539b.dat` hose
  geometry in the raised-platform synthesis. The identity of the unresolved
  optical parent is not inferred from its surrounding frame.
- The optical constraints inline one `6637` distributor into 14 placements;
  the synthesis uses the whole part. Keep the nested credits and distinguish
  part geometry from an assembly inventory.
- The string constraints contain six studies; the supplied synthesis contains
  only the first three. Later STRING_BAND routes are described from their source.
- The continuous-tread synthesis hides its nine wheel constraints. The long
  hinged-track source repeats four middle-wheel positions along the return
  route. Neither hidden records nor repeated constraints should silently become
  missing or duplicate wheels in a new model.
- Earlier [adapter checks](../docs/reports/lsynth-integration.md) found tangent
  warnings in rubber-band, rubber-belt, small-link-chain and vintage-crawler
  scenes. Other legacy inputs have missing parts, imperfect transforms, internal
  primitives or unresolved colour 16. The annotations identify relevant cases;
  this semantic review does not repair or approve their geometry.

All 26 constraint titles were clarified and 211 ordinary comment lines added.
Every other original line, including part annotations, author and licence text,
geometry and SYNTH records, was preserved. All 26 synthesis files are byte-for-byte
unchanged. Authors remain credited in their files, including Eric Albrecht,
Steffen, Holly Wood/Holly-Wood, Jetro de Chateau, J.C. Tchang, Willy Tschager and
the inlined part author Remco Braak. The new descriptions are editorial study
notes, not claims made by those authors.

These examples are sufficient to broaden the construction vocabulary now.
Before calling a derived model correct, complete its supports and interfaces
and run the normal source, geometry, BOM and visual review. This study is not
a physical or functional certification.
