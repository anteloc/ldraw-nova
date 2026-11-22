# Technic card

Technic parts join through pins and axles in holes. Name the ports; the tool turns and positions each part, inserts pins for you and checks the result the way a Technic builder would.

## Work in this order

1. **Frame**: beams joined at two holes per joint, or with an L-liftarm or a triangle. One pin per joint is a hinge.
2. **Shafts**: each axle in round holes of the frame, with a bush or keyed part on each side so it cannot slide out.
3. **Gears and links** at exact mesh distances; pivots on frictionless pins.
4. **Wheels**, then panels and System cladding; hoses last.

Put a repeated or left/right assembly in its own section and place it twice; the other side takes `"mirror": "x"` ([plan card](plan.md#organise-larger-models)).

## Find parts and ports

```sh
./ldraw-agent technic parts --role member --top 25   # most used beams and connectors; also gear, connector, shaft, wheel
./ldraw-agent technic parts --query "liftarm bent"
./ldraw-agent part 32140 3648b 2780                   # ports of several parts in one call
./ldraw-agent technic gears 8 24                      # pitch radii and mesh distances
```

`part` lists `technic_ports`: holes `hole-N` (`pin_hole` or `axle_hole`), pin halves `grip-N` and axles `shaft`, each with centre, axis and length. About 1,600 Technic parts have ports.

## Place parts by their ports

A pin or axle into a hole; `side` is where the rest of it sticks out:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "pin", "ref": "2780.dat", "colour": 0, "on": {"to": "rail", "hole": "hole-0", "pin": "grip-0", "side": "+X"}}
```

A beam laid on another by matching holes. The tool inserts one pin per pair (`IDENT-pin-0`, …): friction `2780` by default, `"pins": "3673.dat"` for a pivot, `"pins": false` for none:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "arm", "ref": "32316.dat", "colour": 72, "join": {"to": "rail", "holes": {"hole-0": "hole-0", "hole-1": "hole-1"}, "side": "+X"}}
```

An axle and the parts on it, each flush against the last:

```json
{"id": "rail", "ref": "32524.dat", "colour": 71, "at": [0, 0, 0], "orient": {"up": "+X", "x": "+Z"}},
{"id": "axle", "ref": "3706.dat", "colour": 0, "on": {"to": "rail", "hole": "hole-3", "pin": "shaft", "end": "-X", "past": 20}},
{"id": "bush", "ref": "3713.dat", "colour": 71, "on": {"to": "axle", "hole": "hole-0", "pin": "shaft", "next_to": "rail", "side": "-X"}},
{"id": "gear", "ref": "3648b.dat", "colour": 7, "on": {"to": "axle", "hole": "hole-2", "pin": "shaft", "next_to": "rail", "side": "+X"}}
```

- `end` + `past`: that end of the axle stands `past` LDU beyond the face of the holed part (0 is flush).
- `next_to` + `side`: the part sits flush against that neighbour, on that side, along the axle.
- `slide` moves along the axis; `roll` turns about it (a cross hole tries 45° itself); `flip` turns a holed part end for end.
- `join` also places a whole section: name the hole of a part inside it, `"holes": {"hole-2": "mount/hole-0"}`.

A failed seat names the fit rule that failed and lists both parts' ports.

## Dimensions

- Hole pitch is 20 LDU (one stud). A beam is 20 thick, a thin liftarm 10. An axle N long is 20 × N LDU.
- Technic bricks have their holes 10 below the top; two plates between bricks put their holes 40 apart.
- Parallel gears mesh with axes 1.25 × (teeth A + teeth B) LDU apart. On whole studs: 8+8 (1 stud); 8+24, 12+20 and 16+16 (2); 8+40, 12+36 and 24+24 (3); 24+40 (4); 40+40 (5). Two 12-tooth bevels mesh with each centre 15 LDU from where the axes cross. A worm meshes a gear whose axis passes 10 LDU + its pitch radius from the worm's axis.

## What the build checks

| Code | Meaning and fix |
|---|---|
| `technic.through_solid` (error) | A pin or axle crosses plastic where there is no hole: move it onto the hole. |
| `technic.cell_overlap` (error) | Two members fill the same space: lay one beside the other. |
| `technic.invalid_seating` | A pin or axle is at a hole but not seated; the rule named says why. Fix it even when it is only a warning. |
| `technic.occupied_hole`, `technic.occupied_span` | Two parts claim one hole or one stretch of a shaft: move one along the axle. |
| `technic.incomplete_grip`, `technic.misaligned` | Half a pin grip is in the air (add a layer or use a 3/4 pin `32002`); a pin or axle is 1.5–5 LDU off a hole's axis (seat it with `on`). |
| `technic.loose_axle` | The axle can slide out: a bush or keyed part against the bearing, or an axle with a stop. |
| `technic.open_pin` | A pin sticks out into the air: seat a part on it or remove it. |
| `technic.gear_gap`, `technic.gear_clash` | Gears are off their mesh distance by the LDU stated. |
| `technic.locked_shaft` | A meshing gear is fixed to the frame: run its axle in round holes. |
| `technic.unsupported_shaft`, `technic.overhung_gear` | A geared shaft runs in no bearing, or its gear is more than two studs from one. |
| `technic.unbraced_mesh` | The two shafts of a mesh sit in different frames: carry both in one beam. |
| `technic.thrust_unbacked` | Nothing backs a worm along its axle: put a bush or beam flush against it. |

## Declare what should move

Add a `mechanism` to the section, beside `steps`. For the axle above:

```json
{"ground": "rail", "input": "axle", "outputs": ["gear"]}
```

`build` then checks that the input can turn and that each output moves with it (`technic.mechanism_locked`, `technic.mechanism_uncoupled`); an output that moves on its own is `technic.mechanism_loose`, and `"dof": N` states the expected degrees of freedom (`technic.mechanism_dof`). `"pivots": [["arm", "rail"]]` lists pairs that must be able to turn about each other (`technic.pivot_locked`). `./ldraw-agent technic trace PLAN` prints the rigid groups, joints and gear meshes. The check reads the built pose; nothing is animated.

## Good practice

- Friction pins (`2780`, `6558`) for structure; frictionless pins (`3673`) or axles in round holes for anything that turns.
- Make a joint rigid with two spaced pins, an L-liftarm or a triangle.
- Carry each shaft in two bearings when you can, with each gear within two studs of one; carry both shafts of a mesh in the same beam.
- Start from a recipe: `./ldraw-agent knowledge search 'technic gear pair'`.
- Do not write your own checker or geometry script. If a check looks wrong, say so in your report.
