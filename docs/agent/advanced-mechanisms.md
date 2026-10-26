# Build a mechanism before animating it

Start with physical interfaces and a small number of independent inputs. Every
gear does not get its own animation control. Start with the reproducible
[gear-drive starter](../../examples/technic-studies/gear-drive/README.md), then
add one checked coupling at a time.

For supported parallel spur drives, Mecha's `transmission.port`, `shaft` and
`mesh` helpers emit the existing motion plan: one rigid group per keyed shaft,
finite bearing checks and one derived follower angle. The starter's motion
recipe demonstrates the whole path. Unknown or crown/bevel/worm contacts need
their own measured relation; catalog membership does not grant solver support.

## Find parts and inspect occupied interfaces

```sh
./ldraw-agent technic catalog --family coupling
./ldraw-agent technic catalog 'crown'
./ldraw-agent technic catalog --model MODEL.mpd --connectors --output output/parts.json
./ldraw-agent part 3749
```

The [catalog](technic-catalog.md) includes every supplied Technic assignment,
newer installed parts, mechanical parts from other categories and an explicit
online watchlist. Search tags are not motion profiles. Preserve suffixes such
as `3648a`, `3650c` and `85543-f3`; a sanitized Python symbol is an index label.

For each occupied interface record occurrence ID, part-local point and axis,
world frame, engaged interval and evidence for its behaviour:

| Interface | Motion to permit or constrain |
|---|---|
| Cross axle in matching cross hole | Lock relative twist; establish insertion and axial retention separately |
| Axle in round hole | Permit rotation; constrain bearing axis and finite engagement |
| Mixed pin/axle | Inspect the section inside each neighbour; one end can be keyed while the other is a bearing |
| Gear contact | Constrain phase/ratio in the carrier frame; check axes, contact geometry and tooth overlap |
| Link pivot | Close pivot centres and preserve link length; keep intended rotation freedom |
| Cam/follower | Establish occupied cam hole, surface contact, follower direction and travel |
| Sliding CV coupling | Check articulation, shaft phase and finite insertion separately |

LDCad connector axes are local **Y** of the connector frame. Part axes vary:
ordinary Technic axles run along part-local X, while many gears use local Z.
Multiply by the complete occurrence matrix; a part appearing upright in an
image does not identify its world shaft axis.

An alias can change orientation and colour. `6575.dat` wraps `6575a.dat` with a
180-degree Y rotation. Compose this transform before using canonical frames.
The catalog retains it rather than silently changing the part number.

Primitive inference can duplicate features or mistake a hole primitive for a
male axle. SNAP `rotate`/`slide` flags describe placement metadata; they do not
establish torque transmission. Keep provenance and inspect ambiguous cases.

## Partition by rigidity, then choose inputs

Build a graph whose edges say **keyed**, **bearing**, **gear mesh**, **pivot**,
**slider**, **surface contact** or **unresolved**. MPD names and nesting describe
authoring/build organisation, not necessarily rigidity. Group shafts, keyed
gears, bushes and couplings that really move together. Keep bearing supports,
differential carriers, planets and followers separate. Include remote couplings
and the parts that hold the shafts in place.

Complete shortcuts may contain internal joints. `61903.dat` contains two yokes
and a centre cross; rotating its one mesh cannot articulate that joint. Split a
separate copy into documented components, preserving rest geometry, colours,
attribution and old-to-new occurrence mapping.

Choose independent inputs after closing the graph. A motor-driven differential
needs another boundary condition to determine both outputs; articulation is
different from shaft spin. An animation variable is not evidence that the
mechanism has that degree of freedom. Keep unresolved freedoms explicit.

## Write relations in the correct frame

Angles are source-pose offsets. Use consistent right-hand axes and radians.
Oppositely facing part matrices do not automatically imply opposite rotation.
For parallel external gears with tooth counts `Na`, `Nb` on a rotating carrier:

```text
Na * (a - c) + Nb * (b - c) = 0
b = c - Na/Nb * (a - c)
```

`b = -Na/Nb*a` assumes a fixed carrier. Spacing alone does not establish a mesh:
check tooth band overlap, face direction and contact. Opposed coaxial gears can
be differential side gears. For equal side gears about the same directed axis:

```text
c = (left + right) / 2
planet_relative = sign * Ns/Np * (left - right) / 2
```

Parent the planet to its carrier. Equal side rates give zero **relative** planet
spin, but the planet still travels with the carrier. Determine the planet sign
from the selected contact and axis. A differential used as an angle bisector
still needs its two side angles and carrier orientation connected to the linkage.

A Cardan joint at fixed bend has nonuniform output. In a compatible fork-phase
convention, `phi = atan2(cos(beta)*sin(theta), cos(theta))`, with continuous phase
unwrapping. A phased equal-bend pair cancels the variation at the final output;
the intermediate shaft still varies. Its direction is the vector bisector
`normalize(input_axis + output_axis)`, not an average of Euler angles. The
centring mechanism must actually enforce it.

The independent `ldraw-mecha` project provides `linkages.gear_pair`,
`differential`, `universal_joint` and `double_cardan`. They emit ordinary plan
signals. The double-Cardan helper assumes a fixed articulation and correct fork
phase; its centring linkage must be modelled and checked separately.

## Check geometry as well as expressions

Keep the supplied source pose intact and report fit residuals. Search tolerances
are not permission to reshape a historical model or manufacturing allowances.
Preserve phase offsets when driving keyed groups.

In `ldraw-mecha`, add executable `rigid`, `coaxial`, `rotation` and `distance`
checks. They measure occurrence transforms and closure, including fixed parts.
A gear signal agreeing with its own driver proves only program execution.

```sh
./ldraw-mecha check output/study --require-reviewed --require-constrained
./ldraw-mecha rig output/study --require-constrained --animate --reopen
```

Check off-grid angles, both signs, multiple revolutions and asymmetric inputs.
Mecha's Blender workflow checks off-grid poses and samples the saved timeline
with animation active; opening the animation remains part of visual review.
Deliberately break one known coupling and require a failure. Default/rest pose
alone is insufficient: a gear animated independently of its keyed axle can pass
at rest and fail immediately when driven.

`--require-constrained` detects bodies without a cross-body check; it does not
prove sufficient constraints. Inspect the complete demonstration, reopen it in
a fresh Blender process and assess clearance. Record supported motion,
unresolved contacts and untested effects separately. Use `technic check` for
fixed supports; it is not a motion solver for the complete machine.
