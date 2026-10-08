# Technic transmission patterns

Source cases: [W16, Defender, Chiron and Mustang](../../../examples/technic-studies/README.md).
Measurements below describe those arrangements in LDU. They are starting evidence
for construction, not universal placement constants or new Nova checks.

## Parallel gear trains

The W16 has three meshes: input 20T to central-crank 12T, then central 24T to
each of two lower-crank 24T gears. The first pair uses double-bevel parts on
**parallel shafts**; the part name alone does not determine the arrangement.

| Pair in `42083 - engine.ldr` | Centres in section coordinates | Plane | Spacing |
| --- | --- | --- | ---: |
| Input `83` to central `82` | (0,90,-40) to (0,50,-40) | Z=-40 | 40 |
| Central `68` to lower `84/16` | (0,50,200) to (-36,98,200) | Z=200 | 60 |
| Central `68` to lower `85/16` | (0,50,200) to (36,98,200) | Z=200 | 60 |

The lower gears are 72 LDU apart, so they are not another 24T/24T mesh. This is
a useful nonrectangular shaft arrangement: offsets of 36 and 48 LDU give the
60-LDU centre distance. Preserve those real support locations when adapting it.

The reviewed profiles use pitch radius `1.25 * tooth_count` LDU, giving 40 and
60 LDU for these pairs. Use that as a shortlist calculation for these profiles,
then inspect the actual gear type, tooth plane, thickness, bushes and support
stack. Do not apply it to every bevel, worm, rack or turntable interface.

About common +Z axes, output/input increments are -5/3 for input-to-central and
-1 for each central-to-lower pair. Raw discovery reports reverse some local axes
and list the 12T before the 20T, changing signs/order. Copy the physical
arrangement and state axis conventions before quoting a ratio.

## Bevel trains and winches

The Defender routes a vertical knob shaft through a longitudinal intermediate
shaft to a transverse drum. There are **two 12T/12T bevel meshes and three
rotating shaft groups**. Preserve the mating tooth/apex geometry at each turn,
with bearings and retention for every shaft. A change of direction is a packaging
tool: it lets an accessible control drive an output on another face of the model.

Separate the drum, ratchet, pawl, rope and hook roles in the brief. The source
demonstrates drum rotation while the rope/hook and pawl remain static. It does
not establish winding, holding a load or one-way engagement. For a new crane or
winch, supply those parts and describe any unreviewed action honestly. The
[local worm study](../../../examples/mechanism-atlas/worm-drive/GUIDE.md) likewise
needs its parent's winding assembly.

## Worm-driven adjustment

The Mustang audit finds `4716.dat` beside an 8T wheel, connecting a knob/axle to
an output shaft and liftarm cranks. It is a useful compact adjustment pattern.
The connection from those cranks to the rear frame remains unresolved in the
source evidence; do not present the whole ride-height adjuster as a solved recipe.

For that single-start worm, the wheel turns with ratio magnitude `1 / teeth`.
Its thread is finite: the source detector accepts contact stations within
±16 LDU along its local Z axis, inside thread geometry extending to about ±20.
Those are detection bounds for this part, not generic mounting tolerances.
Check perpendicular shaft axes, distance, wheel midplane and thread overlap.
A correct distance between infinite axis lines can still place the gear beyond
the thread. Recheck direction, tooth engagement and the exact worm variant;
friction, backdriving and self-locking are not established by this example.

## Differentials

Treat the carrier, two side gears and carrier-mounted spider as separate roles.
The carrier supports the spider axis; the side shafts leave through bearings
and need retention. For the ideal symmetric arrangements in the Defender, the
carrier angle is the mean of the side angles when expressed about common axes.
That explains the layout; it does not establish traction or torque distribution.

Do not glue all three shafts together because they are coaxial, or replace the
internal mechanism with two independent wheel axles. Study the
[local differential](../../../examples/mechanism-atlas/differential/GUIDE.md) for
parts and build order. For a new chassis, adapt the housing/frame mounts while
preserving the internal bevel arrangement, shaft spacing and escaping-axle stops.

The Defender's differential examples and suspension example were studied
separately. The original drivetrain's hub-spin projection is approximate; it
does not supply an exact constant-velocity joint recipe.

## Cardan shafts

A joint has two yokes and a cross with different axes. Measure the joint centre,
shaft lines and fork orientations instead of inferring them from an axle's bounds.
Preserve enough space around both forks and adjacent axle tips.

The Defender's internal propshafts pair joints with parallel end shafts, equal
bends and matched intermediate fork phasing. That particular arrangement cancels
the single joint's speed variation at the far end. The middle shaft still varies.
It is a useful way to route a drive around a frame, not a rule that arbitrary
two-joint shafts are constant velocity. Small source phase corrections (about
0.0117° and 0.0191°) belong to the reviewed example.

Changing suspension geometry also changes joint centres and bend angles. Do not
combine a fixed-geometry propshaft and a moving suspension by merely placing
their end parts close together. Inspect reach, fork phase and the actual hub
interface at the delivered pose and retain the intended travel envelope.

## Selectors and driving rings

Constant-mesh gears can spin freely on a shaft until a driving ring engages
their clutch faces. Identify free gears, axle-locked gears, shaft joiners,
sliding rings, extensions, forks and stops before reusing a gearbox.

The Defender four-speed alternates two rings across four states. The source
already has ring A at +10 LDU toward first gear; its neutral and opposite
positions are offsets of -10 and -20 from that source pose. Setting every
slider to a guessed neutral position changes the assembly.

Keep ring travel and fork space clear when designing a gearbox enclosure.
An extension that rests on one side is not necessarily rigidly attached to the
ring. The fork follows an arc while the ring follows a line; a plausible final
picture does not establish engagement throughout the lever's travel.

The Chiron extends the idea with a four-position first stage and a second-stage
carry once per first-catch revolution. Its saved gearbox contains **395 retained
source parts plus two added `32270.dat` gears**, mapped as `R/S6_12T` and
`R/S5_12T` (extract IDs 395 and 396). These are a qualified reconstruction,
not verified missing parts from the official set. Retain that distinction if
studying it; use the unmodified annotated source when claiming direct source reuse.

Gear/catch travel, detent windows and paddle timing in those rigs include
authored approximations. Learn the packaging, separate roles and selector
topology without importing their animation controls as construction facts.
