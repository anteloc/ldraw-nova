# Design expressive Technic models

Use Technic construction to make the subject's function visible: a lifting deck,
articulated wheel, exposed piston bank or accessible winding handle can determine
the whole silhouette. Start with one useful action and build its supports and
body around it.

This guide adapts Technic knowledge from `ldraw-mecha/docs` and
`ldraw-mecha/examples` for **model generation in ldraw-nova**. The
[worked studies](../../examples/technic-studies/README.md) retain the source
identities, measurements, qualifications and attribution. Their animation reports
are historical evidence about those examples, not validation of a new model.
The [structural workflow](technic.md) and [mechanism workflow](mechanisms.md)
remain the implementation paths here; analytical mechanism verification remains
deferred. No Blender rig or sibling checkout is needed to read these lessons.

## Choose a construction by function

| Intended feature | Pattern and construction lesson | Starting example |
| --- | --- | --- |
| Visible drive route | [Parallel gears](technic-patterns/transmissions.md#parallel-gear-trains): preserve shaft lines and tooth planes | W16's three crankshafts |
| Drive around a corner | [Bevel train](technic-patterns/transmissions.md#bevel-trains-and-winches): support each shaft and retain the drum | Defender winch |
| Slow adjustment | [Worm drive](technic-patterns/transmissions.md#worm-driven-adjustment): keep the wheel beside the finite threaded span | Mustang rear adjuster; local worm atlas |
| Split an axle or drivetrain | [Differential](technic-patterns/transmissions.md#differentials): distinguish carrier, side gears and spider | Defender front/rear/centre differentials |
| Route drive past obstacles | [Cardan shafts](technic-patterns/transmissions.md#cardan-shafts): preserve centres, yokes, crosses and phasing | Defender internal propshafts |
| Select a transmission path | [Driving rings](technic-patterns/transmissions.md#selectors-and-driving-rings): loose gears differ from axle-locked gears | Defender four-speed and range/direction boxes |
| Compact visible reciprocation | [Cam followers](technic-patterns/engines.md#cam-followers): guide the followers above phased cams | Defender inline-six |
| Recognizable crank engine | [Slider cranks](technic-patterns/engines.md#crank-and-connecting-rod-engines): keep rods, crank and guides distinct | Chiron W16 |
| Independent wheel corners | [Wishbones and shocks](technic-patterns/suspension-steering.md#suspension-corners): preserve pivot geometry and real mounts | Standalone Defender suspension |
| Steerable front axle | [Rack and links](technic-patterns/suspension-steering.md#rack-steering): connect rack, tie rods and knuckles | Defender steering; local rack atlas |
| Raise a platform without tilting it | [Four-bar lift](technic-patterns/lifts-and-linkages.md#orientation-preserving-lift): match arms and pivot spacing | Chiron rear wing |
| Indexed control detail | [Paddles and pawls](technic-patterns/lifts-and-linkages.md#paddles-pawls-and-indexing): retain hinges, return and detent context | Chiron stepper, with an incomplete drive relation |

These are patterns, not a list of permitted subjects. A car's wing linkage can
teach a cargo lift; its engine can teach a pumping station. The new context still
needs its own mounting structure, dimensions and review.

## Turn function into a design brief

Before placing parts, record:

- **Subject and focal action:** what the model is, what visibly changes, and which
  feature makes it recognizable at thumbnail size.
- **Input and output:** the accessible handle, axle or lever; the resulting drum,
  wheel, slider or platform; the intended delivered pose.
- **Supports and interfaces:** fixed frame, bearing locations, retention, body
  mounts and parts that the source's parent supplies.
- **Spatial budget:** actual shaft lines and joint centres, axial stacks, wheel
  space, moving envelopes and room to insert connectors.
- **Appearance:** dominant structural colour, body colour, a restrained accent,
  exposed mechanism and quiet body surfaces. Colour does not determine pin
  friction or gear engagement.
- **Reuse and variation:** exact source/section, what stays geometrically intact,
  what changes, and which new subject-specific structure makes this an original
  composition.

Sketch the mechanism route as `input -> transmission -> output` and the support
route as `output mounts -> frame -> base/wheels`. Label a missing coupling or
support explicitly. Two visually adjacent assemblies do not supply that link.

Develop two or three silhouettes around the same core before committing. Compare
an exposed central mechanism, a low chassis with offset drive, or a tall frame
with a working deck. Select for the requested subject and a clear focal feature,
then reserve the mechanical interfaces before adding panels.

## Compose a new subject from studied modules

These are design prompts, **not built or verified recipes**:

| Subject | Studied core | New construction and visual opportunity |
| --- | --- | --- |
| Rough-terrain service rover | Suspension corners + rack steering | Open chassis, high wheel clearance, low equipment bed; reconcile the two systems at the same hubs before adding drive |
| Harbour maintenance crane | Local driven turntable + worm support + drum transmission | Braced pedestal, accessible controls and removable machinery cover; supply the winding assembly and appropriate load support |
| Workshop engine stand | One W16 lower bank or the local piston/crank study | Compact stand with visible crank and piston contrast; support the input independently after removing the other banks |
| Cargo loading platform | Wing's parallelogram | Broader deck, paired supports and fixed upper/lower pivots; leave room for the deck's small sideways travel |
| Agricultural pumping station | Crank/rod core or guided cam followers | Repeated exposed pump heads and a service walkway; choose the actual mechanism before styling it |
| Mechanical observatory | Local driven turntable + a studied lift | Separate azimuth and platform controls, a compact tower and a removable dome; design the shared frame and avoid overlapping shafts |

Use repetition for cylinder banks, frame bays and matched corners; use deliberate
asymmetry for a service control or offset power route. Keep the engineering
readable through openings and removable covers. A dense collection of gears
without bearings, retaining parts or an output is not a richer design.

## Build and review with the existing tools

1. Open a relevant [local atlas manual](../../examples/mechanism-atlas/README.md)
   or prepare the exact annotated source section. Read the relevant pattern and
   the [source-reuse lessons](technic-patterns/source-reuse.md) first.
2. Preserve the internal spacing of the selected core. Adapt mounts, frame and
   cladding first. Add source-missing supports as real parts with an insertion
   order, and record substitutions in `operation.json`/adaptation notes.
3. Build one module before repeating it. Use `technic check` on the fixed frame
   and normal mechanism source/geometry checks on moving assemblies. An authored
   anchor is a positioning frame until its actual mating parts are inspected.
4. Inspect the bare assembly and the dressed model, including underside and
   concealed mounts. Check that the delivered pose leaves gears, rods, wheels,
   controls and extraction paths visibly unobstructed. Additional posed copies
   can help review an uncertain interface; simulation is not a completion gate.
5. Finish with the usual final-revision MPD, reproducible source, operation notes,
   attribution, BOM comparison and opened previews. Record what is intended,
   directly observed, adapted or still unresolved.

Use [reference discovery](reference-discovery.md) for new constructions and
[visual design](visual-design.md) for part selection and composition. Do not
replace a promising mechanical idea with a generic block chassis just because
it lies outside the small curated connector registry; study and report the
unreviewed interfaces through the existing mechanism workflow.
