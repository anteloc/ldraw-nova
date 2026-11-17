# Plan card

A plan is a JSON file of named placements; `build` turns it into an MPD. Every field is in the [plan reference](../reference/plans.md).

```json
{
  "version": 1,
  "author": "Your name",
  "sections": [{
    "name": "model.ldr",
    "description": "A red brick with a sideways tile",
    "steps": [
      [{"id": "base", "ref": "3001.dat", "colour": 4, "at": [0, 0, 0]}],
      [{"id": "top", "ref": "3022.dat", "colour": 1, "on": "base"}],
      [{"id": "lamp", "ref": "87087.dat", "colour": 15, "on": {"to": "top"}}],
      [{"id": "lens", "ref": "3070b.dat", "colour": 14, "on": {"to": "lamp", "face": "-Z"}}]
    ]
  }]
}
```

Each step is a list of placements, and a later placement may refer to an earlier one by `id`. The [recipes](../../../examples/recipes/README.md) are small plans that use every placement mode; `knowledge search` returns them first when one fits.

For a user model, replace the sample author with the contributing agent/model names and versions, add `"license": "CC-BY-NC"`, and prefix the root section's `description` with `[AI-GENERATED] ` exactly once. The description becomes the internal model title; keep `name` and submodel references unchanged. The [delivery requirements](review.md#deliver) specify section attribution, the separate comment immediately below the licence, the required AI keywords meta, final filename and evidence. Plans and generators remain internal unless requested.

## Place a part

A placement has an `id`, a `ref` (a part such as `3001.dat`, or a section such as `wing.ldr`), a `colour` and exactly one position:

| Position | Use it for |
|---|---|
| `"at": [x, y, z]` | explicit coordinates in the section, in LDU |
| `"on": "ID"` | an ordinary brick or plate stacked upright on another; `"offset_studs": [x, z]` shifts it by whole or half studs |
| `"on": {"to": "ID"}` | any part seated by a socket on a stud of another part, on top by default or on any face: see the [SNOT card](snot.md) |
| `"under": {"to": "ID"}` | any part hung by one of its studs in a socket of the part above, such as an inverted slope or a chassis plate |
| `"on": {"to": "ID", "hole": "hole-1", "pin": "grip-0"}` | Technic pins, axles and the parts on them, by port: see the [Technic card](technic.md) |
| `"join": {"to": "ID", "holes": {"hole-0": "hole-0"}, "side": "+X"}` | a Technic beam or module laid on another by matching holes; the pins are inserted for you |
| `"attach": {...}` | aligning named module anchors (plan reference) |

Turn a part with `"orient": {"up": "-Z"}`: its studs then point toward -Z. Add `"x": "+Z"` to say where its local +X points. Directions are `+X -X +Y -Y +Z -Z up down`. `"yaw": 90` turns a part about the vertical axis. You never need to write a rotation matrix.

`"repeat": {"count": 4, "step": [40, 0, 0]}` copies an `at` placement in a row (IDs `id-0` to `id-3`). `"count": [4, 2]` with `"step": [[40, 0, 0], [0, 0, 20]]` makes a grid (IDs `id-0-0` to `id-3-1`).

## Organise larger models

- Put each module (wing, floor, cab, panel) in its own section with its own origin, and build it upright. Place it like a part: `{"id": "wing-left", "ref": "wing.ldr", "colour": 15, "at": [...]}`. Parts inside the module that use colour 16 take the placement's colour.
- Place the other side of a symmetric model with `"mirror": "x"` (or `y`, `z`) on the module's placement: each part becomes its own mirror image with a proper rotation, or its Left/Right partner. A part with a real handedness, such as a worm, stops the build; place that one by hand.
- A path such as `wing-left/flap` names a part inside a placed module; `on.to` accepts paths.
- Write a `generate.py` that emits the plan when the model has loops, mirrored halves or many similar parts. Keep repairs in the generator so a rebuild preserves them.
- Keep the first section, the model root, short: it places modules.
