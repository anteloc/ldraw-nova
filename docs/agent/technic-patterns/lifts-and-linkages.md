# Lifts, links and indexed controls

Source case: [Chiron mechanisms](../../../examples/technic-studies/README.md#chiron-lift-and-selector-studies).
These constructions suggest platforms, loaders, service hatches and control
details beyond their original car bodywork.

## Orientation-preserving lift

The Chiron wing study uses a parallelogram: two fixed pivot axes, equal cranks,
and a strut carrying the wing between the crank pins. The four sides are
nominally **40 LDU in the linkage's YZ plane**, with revolute axes along X.
The payload keeps its orientation as the arms rotate.

One source check measures a 72.111-LDU spatial distance because its two
representative points are also 60 LDU apart along X. That is not the crank
radius. Measure from the appropriate axis in the motion plane before selecting
beam lengths or moving a pivot.

The platform follows a shallow arc. At the source's 0.4-radian endpoint it moves
about (0,-15.863,+0.984) LDU; it does not rise in an exact straight line. Two
rear rods of about 120 LDU close onto short links of about 40 LDU. Preserve
those endpoint relationships and the source assembly branch when changing a pose.
Do not stretch rods or switch the linkage to the other side of a toggle to make
a desired picture fit.

The **upper pivot is assumed fixed** in the studied rig. The example does not
establish the complete key-driven wing-tilt mechanism. Nearby bodywork was kept
in a separate clearance study: no new sampled crossings through 0.40 radians,
crossings at 0.45. These are source-specific observations, not a guaranteed
travel range for a broader deck or new casing.

For a cargo platform, preserve the linkage core and add a real frame that fixes
both pivots, lateral support for the wider deck, and an accessible actuation
interface. Design clearance for both rise and sideways drift. This is an
adaptation idea requiring a new build/review, not an exported working recipe.

## Paddles, pawls and indexing

The Chiron stepper contains a rocking paddle assembly, hinged left/right pawls,
a ratchet, knob shafts and rotary catches. It offers useful packaging lessons:
each pawl pivot travels with the rocker, and the pawl then turns relative to
that moving pivot. Preserve the actual pin joints and room for the return stroke.

However, the saved demonstration keys `paddle` and `shift` independently. A
paddle stroke alone leaves the ratchet stationary in that rig. Its driving pawl
sweeps about 69.3°, short of a 90° index; detent completion and rubber-band return
are assumed, with those parts static. An animated sequence is therefore not
evidence that the pawl physically advances the catch.

Use the example to study part roles and access, and keep the missing drive,
return and detent relations explicit. For a simpler new mechanism, a directly
accessible selector may be easier to adapt than an incompletely studied stepper.
See [transmission selectors](transmissions.md#selectors-and-driving-rings) for
the source gearbox's two added reconstruction gears.

## Mechanism surroundings are part of the construction

A cutaway is helpful for reading pins and link lengths but removes obstacles
and sometimes mounts. Compare it with the parent before deciding where a
panel, beam, stop or neighbouring shaft can go. The source car's moving door
mirrors even sit outside its door FILE sections: an MPD section boundary is
not necessarily a physical assembly boundary.

For a new lift or hatch, list payload, links, pivots, fixed holders, actuator and
surrounding frame. Inspect attachments that cross submodel boundaries, then
check the whole dressed model. Keep the chosen pose and intended action readable
without claiming the source's animation coverage applies to the new design.
