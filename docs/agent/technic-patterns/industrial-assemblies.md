# Industrial assemblies from the LSynth studies

The [annotated LSynth collection](../../../lsynth-examples/README.md) teaches
more than flexible paths. Its rigid parts show how to mount equipment, retain
wheels, terminate cables and build light frames. Use these lessons alongside
[Technic design](../technic-design.md) and the existing [structural](../technic.md)
and [mechanism](../mechanisms.md) workflows. Analytical motion verification
remains deferred; a posed scene still needs real supports and a readable function.

## Build a carrier before its track

Study [the long hinged-track carrier](../../../lsynth-examples/TECHNIC_CHAIN_TREAD_38-Constraints.ldr),
[the continuous-tread frames](../../../lsynth-examples/TECHNIC_TREAD-Constraints.ldr)
and [the vintage crawler](../../../lsynth-examples/TECHNIC_TREAD_CRAWLER-Constraints.ldr).
They demonstrate different construction families, not interchangeable wheels.

For one wheel station, establish the wheel's actual axis and track plane, its
axle or axle pin, bearing support and axial stops. Read the stack along the shaft:
wheel hub, bush or spacer where required, carrier thickness and remaining
retention. Measure each part's origin and connection depth rather than assigning
a standard spacing from the picture. Decide which member turns, which supports
it and whether the wheel is driven or an idler. A round bearing and a keyed axle
hole have different roles.

Finish one supported station before repeating it along the rail. Tie the rails
into the chassis, leave room for the inner track surface and review the return
run as well as the ground run. A spring drawn beside an end wheel becomes a
tensioner only when its mounts and permitted wheel travel are accounted for.

In the long carrier, four middle sprocket positions occur twice in the route
records. Keep a single physical wheel at each position. If a route needs repeated
constraints, keep the real wheels in the rigid assembly and use hidden route
constraints through the [flex workflow](../flexible-parts.md). Inspect the final
BOM for duplicates. The vintage crawler instead uses `7049` bearing bricks with
older cylindrical-axle wheels: replacing these with cross-axle wheels requires
redesigning the interface.

## Let the controls and ports explain the machine

The [pneumatic study](../../../lsynth-examples/TECHNIC_PNEUMATIC_HOSE-Constraints.ldr)
contains a hand pump, a valve and a two-port cylinder. Three routes make the
system understandable: pump to valve, valve to one cylinder port, and valve to
the other. Loose straight hoses and a closed ring are separate samples.

Mount the pump where its handle can be reached, leave the valve lever accessible,
and give the cylinder body and rod end actual attachments to the fixed and moving
structure. Reserve the intended stroke envelope and the output's guide or pivot
before dressing the frame. Determine the nozzle position and outward axis from
the actual part, then transform that frame with the part placement. The hose
needs a seated end and a straight departure before its first bend.

The existing [pneumatic press](../../../examples/flex/pneumatic-press/README.md)
shows an applied example with nozzle-based placement and explicit hose seating,
bend and clearance checks. Its documented limits still apply; its checks are
evidence about that revision, not automatic approval of a new routing.

The [Flex-System frame](../../../lsynth-examples/TECHNIC_FLEX-SYSTEM-Constraints.ldr)
adds another useful distinction: the inner cable ends, outer guide supports and
lever pivots are separate interfaces. Fix the guide where the intended operation
requires it, retain the ends and allow relative travel. The X-shaped cables and
side sleeve in the display suggest arrangements to study; their appearance alone
does not establish a rigid brace or a working remote-control linkage.

## Finish the rigid hardware at both ends

The [Power Functions bench](../../../lsynth-examples/ELECTRIC_POWER_FUNCTION_CABLE-Constraints.ldr),
[NXT bench](../../../lsynth-examples/ELECTRIC_NXT_CABLE-Constraints.ldr) and
[RCX bench](../../../lsynth-examples/ELECTRIC_RCX_CABLE-Constraints.ldr) show useful
modules with different interfaces. Select the actual controller, motor, sensor
and connector family. Reserve battery access, sensor sight lines, controls and
connector insertion space. Add mounts and a supported coupling at the motor
output; a cable-connected motor lying beside a frame is still an unmounted motor.

Route cables after those choices. Show a purposeful departure from each plug,
slack where relative movement requires it, and clips where the design needs
support. Display colours do not establish an electrical pinout. Missing legacy
plugs require a documented, geometry-checked replacement before reuse.

The [twin-light lead](../../../lsynth-examples/ELECTRIC_POWER_FUNCTION_CABLE_HALF-Constraints.ldr)
has an actual middle box and differently oriented lamp-head entries. Give those
heads holders and leave room for the two branches. This is a better starting
point for vehicle work lights than inventing a cable junction in empty space.

The [winch study](../../../lsynth-examples/STRING_HOSE-Constraints.ldr) separates
reel, sheave and hook hardware. Trace the rope from its attachment through every
guide to its other end. Add the drum bearings, shaft retention, fixed anchor and
drive or holding arrangement required by the intended model. A path marker is
an authoring aid, not a rope anchor; a hanging hook does not establish mechanical
advantage or load capacity.

## Use exotic parts to shape a coherent subject

| Source | Rigid detail worth learning | Design opportunity |
| --- | --- | --- |
| [Swept frame](../../../lsynth-examples/TECHNIC_AXLE_FLEXIBLE-Constraints.ldr) | Bent liftarms, axle joiners and numbered angle connectors establish paired upper rails | Light canopy, guard or body contour with flexible lower edges |
| [Workshop lamp](../../../lsynth-examples/ELECTRIC_CABLE-Constraints.ldr) | Signal mast and stand, retained side arm, dish shade and lightbrick | Slim work light, inspection station or service gantry detail |
| [Optical engine](../../../lsynth-examples/FIBER_OPTICS_CABLE-Constraints.ldr) | Four-cylinder V core with repeated cross-block fittings above it | Exposed engine bench or orderly equipment bay; the guides remain optical |
| [Broad-guide frame](../../../lsynth-examples/FIBER_OPTICS_CABLE_WIDE-Constraints.ldr) | Mirrored short-axle and cross-block offsets with small levers | Instrument bracket or service head; the source's missing parent remains unknown |
| [Exploration rover](../../../lsynth-examples/HOSE_FLEXIBLE_12L-Constraints.ldr) | Technic wheel mounts under a System chassis and bubble canopy | A compact industrial vehicle whose cockpit and stance lead the design |
| [Raised platform](../../../lsynth-examples/HOSE_FLEXIBLE_19L-Constraints.ldr) | Large cylinders, turntable, side studs, dish and clips | Column-mounted equipment or a science-fiction service station |

Inspect the particular connector variant before adapting these ideas. A short
axle, cross block or side-facing brick can turn a bulky stack into a small offset
bracket. Conversely, rotating a series of ordinary bricks does not make the
[brick-arc claw](../../../lsynth-examples/BRICK_ARC-Constraints.dat) a jointed
gripper. Keep the shape idea and design real joints for the desired motion.

## Make the engineering visually readable

Choose one focal assembly: a track carrier, cylinder, winding drum or instrument
head. Let its function determine the silhouette. Develop the frame and service
spaces around it, then add bodywork where it strengthens that outline.

Use repeated rollers, frame bays, cylinder heads or clips to establish an orderly
rhythm. Keep major supports in a consistent palette and use a limited accent for
controls or the chosen mechanism. Leave quiet panels and open space around the
focal feature. Hoses can connect the main masses visually without covering every
surface. Remove extra sample loops and isolated parts when adapting a display.

Review the bare frame and dressed model separately. At thumbnail size the subject
should read clearly; close up, mounts, output connections and cable terminations
should explain how it is assembled. Openings or removable covers should reveal
useful construction. A decorative gear, floating valve or unsupported axle adds
detail without making the machine more convincing.

These are promising **new model briefs**, not completed or verified recipes:

| Subject | Starting construction | What the new design must supply |
| --- | --- | --- |
| Tracked inspection crawler | One studied track family + swept frame + twin lamps | Matched carriers, chassis, drive mounts and a compact equipment deck |
| Small sorting conveyor | Studded chain and its coarse-toothed wheels | Bearing frame, drive, attached flights and clearance at both end wheels |
| Pneumatic service press | Pump/valve/cylinder layout; existing press as a worked reference | Appropriate guided output, both cylinder mounts, control access and reviewed routes |
| Engine service bench | Optical V engine + mast lamp | Corrected engine geometry, stand, input support and orderly accessory wiring |
| Science-fiction maintenance pod | Rover or column platform + instrument brackets | One clear working head, real bracket interfaces and restrained body detail |

Choose one core, keep source attribution and adaptation notes, and complete the
new supports before adding another subsystem. Use normal review and BOM
comparison on the resulting model; source previews are evidence for learning,
not a substitute for reviewing the final assembly.
