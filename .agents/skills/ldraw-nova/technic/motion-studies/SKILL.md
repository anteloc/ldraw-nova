---
name: motion-studies
description: 'Mechanism relations and the optional motion study: interface graphs, partitioning by rigidity, choosing inputs, gear and joint relations in the correct frame, technic trace, and the separate ldraw-mecha animation project, with the supported gear drive starter. Use only when a brief asks to show or verify motion; static mechanisms are checked by the build.'
---

# Technic motion studies

Mechanisms are normally built and checked in their delivered pose (see [technic](../SKILL.md)): place parts by ports, declare the section's `mechanism` contract and read `./ldraw-agent technic trace PLAN`. That is enough for a model that must be built correctly; it does not have to move. Use this skill only for the rarer study that must **show or verify motion**: an interface graph, gear and joint relations, and the separate `ldraw-mecha` project that animates them.

## Start

```sh
./ldraw-agent knowledge search 'worm drive support'
./ldraw-agent examples --family mechanism
```

Read the returned lesson and limits: a rack carriage can need a parent pinion, a gearbox cutaway can lack bearings. Pattern skills: [engines](../engines/SKILL.md), [transmissions](../transmissions/SKILL.md), [suspension-steering](../suspension-steering/SKILL.md), [lifts-and-linkages](../lifts-and-linkages/SKILL.md).

**Static vs motion.** For a static construction, review pose, connections, supports, clearance and assembly sequence with the build checks and `technic trace`. Scope fixed-rigidity contracts to stationary supports; joint scope can test named moving-part mounts in one pose; do not require a complete mechanism to be rigid. When motion is requested, build the interface graph below, then use `ldraw-mecha` from that project's directory and current documentation. Rendered poses alone do not verify travel, engagement or strength.

## Starter: supported gear drive

`examples/gear-drive/`: an original 23-part 8:24 drive with a fixed base, bonded bearing rails, two 8L axles, four round bearings, gear stops and outer retaining bushes. The output turns at `-input/3`.

```sh
.venv/bin/python examples/gear-drive/build.py --output output/my-gear-drive
./ldraw-agent review output/my-gear-drive/gear-drive.mpd --contacts none --views home front top
./ldraw-agent technic catalog --model output/my-gear-drive/gear-drive.mpd --connectors --output output/my-gear-drive/parts.json
```

- Pitch spacing 40 LDU; shaft centres at Y = -62; bearing rails at Z = ±40; gear hubs between half bushes at ±15; outer full bushes at ±60. The 24-tooth shaft starts at 7.5° for tooth phase.
- Its three MPD groups deliberately match one fixed frame and two rigid shafts. Do not infer rigidity from the hierarchy of an arbitrary imported model.
- `--contacts none` skips contact discovery explicitly; it does not declare the model collision-free.

In `ldraw-mecha` (set `LDRAW_DIR` and, if needed, `BLENDER_BIN`; use a new directory when rebuilding):

```sh
.venv/bin/python scripts/gear_drive.py --output output/gear-drive
./ldraw-mecha check output/gear-drive --require-reviewed --require-constrained --set drive=0.731
./ldraw-mecha rig output/gear-drive --require-constrained --animate --reopen
```

## Find parts and inspect occupied interfaces

```sh
./ldraw-agent technic catalog --family coupling
./ldraw-agent technic catalog 'crown'
./ldraw-agent technic catalog --model MODEL.mpd --connectors --output output/parts.json
./ldraw-agent part 3749
```

Default catalog browsing is metadata-only; `--connectors` adds installed interface and alias evidence. Search tags are not motion profiles. Preserve suffixes such as `3648a`, `3650c`, `85543-f3`.

For each occupied interface record occurrence ID, part-local point and axis, world frame, engaged interval and evidence:

| Interface | Motion to permit or constrain |
|---|---|
| Cross axle in matching cross hole | Lock relative twist; establish insertion and axial retention separately |
| Axle in round hole | Permit rotation; constrain bearing axis and finite engagement |
| Mixed pin/axle | Inspect the section inside each neighbour; one end can be keyed while the other is a bearing |
| Gear contact | Constrain phase/ratio in the carrier frame; check axes, contact geometry and tooth overlap |
| Link pivot | Close pivot centres and preserve link length; keep intended rotation freedom |
| Cam/follower | Establish occupied cam hole, surface contact, follower direction and travel |
| Sliding CV coupling | Check articulation, shaft phase and finite insertion separately |

Pitfalls:

- LDCad connector axes are local **Y** of the connector frame. Ordinary Technic axles run along part-local X; many gears use local Z. Multiply by the full occurrence matrix: an upright-looking part does not tell you its world shaft axis.
- An alias can change orientation and colour: `6575.dat` wraps `6575a.dat` with a 180° Y rotation. Compose it before using canonical frames.
- Primitive inference can duplicate features or mistake a hole for a male axle. SNAP `rotate`/`slide` flags describe placement metadata, not torque transmission.

## Partition by rigidity, then choose inputs

- Build a graph whose edges are **keyed**, **bearing**, **gear mesh**, **pivot**, **slider**, **surface contact** or **unresolved**. MPD names and nesting are authoring organisation, not rigidity.
- Group shafts, keyed gears, bushes and couplings that really move together. Keep bearing supports, differential carriers, planets and followers separate. Include remote couplings and the parts that hold shafts in place.
- Complete shortcuts may contain internal joints: `61903.dat` holds two yokes and a cross. Split a separate copy into documented components, preserving rest geometry, colours, attribution and occurrence mapping.
- Choose independent inputs after closing the graph. A motor-driven differential needs another boundary condition. An animation variable is not evidence of a degree of freedom; keep unresolved freedoms explicit.

## Write relations in the correct frame

Angles are source-pose offsets, in radians, with consistent right-hand axes. Oppositely facing part matrices do not imply opposite rotation. Parallel external gears `Na`, `Nb` on a rotating carrier:

```text
Na * (a - c) + Nb * (b - c) = 0
b = c - Na/Nb * (a - c)
```

`b = -Na/Nb*a` assumes a fixed carrier. Spacing alone does not establish a mesh: check tooth overlap, face direction and contact. Equal differential side gears about the same directed axis:

```text
c = (left + right) / 2
planet_relative = sign * Ns/Np * (left - right) / 2
```

Parent the planet to its carrier; determine its sign from the selected contact and axis. A Cardan joint at fixed bend: `phi = atan2(cos(beta)*sin(theta), cos(theta))`, with continuous phase unwrapping. A phased equal-bend pair cancels variation at the output; the intermediate shaft direction is `normalize(input_axis + output_axis)`, and the centring mechanism must enforce it.

`ldraw-mecha` provides `linkages.gear_pair`, `differential`, `universal_joint` and `double_cardan`, emitting ordinary plan signals. The double-Cardan helper assumes fixed articulation and correct fork phase.

## Check geometry as well as expressions

- Keep the source pose intact and report fit residuals. Search tolerances are not permission to reshape a model.
- In `ldraw-mecha`, add executable `rigid`, `coaxial`, `rotation` and `distance` checks. A gear signal agreeing with its own driver proves only program execution.

  ```sh
  ./ldraw-mecha check output/study --require-reviewed --require-constrained
  ./ldraw-mecha rig output/study --require-constrained --animate --reopen
  ```

- Test off-grid angles, both signs, multiple revolutions and asymmetric inputs. Deliberately break one coupling and require a failure: a gear animated independently of its axle can pass at rest.
- `--require-constrained` detects bodies without a cross-body check; it does not prove sufficient constraints. Reopen the animation in a fresh Blender process and assess clearance.
- Record supported motion, unresolved contacts and untested effects separately. `technic check` is for fixed supports, not a motion solver.
- Nominal fit and sampled motion are not physical certification. Animations and `.blend`/`.glb` files are not default deliverables ([review-and-deliver](../../review-and-deliver/SKILL.md)).

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/mechanisms.md](references/docs-agent-guides-mechanisms.md)
- [examples/gear-drive/README.md](references/examples-gear-drive-README.md)
