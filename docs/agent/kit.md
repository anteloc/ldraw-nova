# Optional construction helpers

Use the kit for positioning real parts after choosing a composition. Explicit coordinates, matrices, custom Python helpers and the existing JSON-plan workflow remain first-class options. References teach techniques; no whole-model recipe is mandatory.

The runnable [canopy study](../../examples/python_kit.py) sketches an unsupported canopy, saves a draft, then adds supports while preserving its footprint and height. It also exports a normal JSON plan.

```python
from ldraw_tools.kit import Model

m = Model("study", "Study the form, then engineer its attachments")
base = m.place("3001", "Tan", cell=(0, 0), level=0, id="base")
m.place("3020", "Reddish_Brown", cell=(0, 0), level=base.top, id="deck")
m.save("output/study/draft.mpd", draft=True)
# Open: ./ldraw-agent look output/study/draft.mpd
# Revise composition, engineer missing interfaces, then review final views.
m.save("output/study/study.mpd")
```

By default placement allows incomplete geometry so exploration can continue. `Model(..., strict=True)` enables immediate collision/seating errors while engineering a detail. It is optional. Regardless of this setting, final `save(path)` checks the full assembly and raises `KitValidationError` on FAIL or REVIEW, preserving any existing output. The exception's `.report` contains the findings. `save(path, draft=True)` writes a visibly tagged draft and returns the findings without requiring a pass. Invalid part references and non-rigid transforms remain errors in drafts.

| Operation | Meaning |
|---|---|
| `place(ref, colour, cell=(x,z), level=n, turn=0)` | Stud-grid footprint corner; one cell is 20 LDU. Bottom level is measured in plates of 8 LDU. |
| `place(..., on=part.port("stud[k]"))` | Build on a real stud face, including a side or tilted face. |
| `add(ref, colour, at=(x,y,z), matrix=...)` | Explicit rigid LDraw placement. Alternatively use `turn=` or `axes={"y":"X", "z":"-Z"}`. |
| `mate(ref, colour, port, to=other.port(name))` | Align compatible interfaces and seat studs through the socket mouth. Does not invent a connection. |
| `hinge(ref, colour, port, to=..., angle=30)` | Position a matching hinge half; positive angles raise it toward the root's top. |
| `pin(colour, between=(a.port(...), b.port(...)))` | Close coaxial holes with a suitable pin. |
| `wall(..., openings=[...])`, `fill(...)` | Optional layout helpers. Adjacent pieces still need real connections across seams. |
| `mirror(parts, about=part)` | Place counterpart parts with proper rotations, swapping left/right parts when available. |
| `section(name, description)` | Build a subassembly; instance it with `add(section, None, at=..., turn=...)`. |
| `section.expose_port(name, part.port(...))` | Export an actual connector; `instance.port(name)` follows the instance transform. Finish the section before placing its instances. |
| `section.anchor(name, at=..., matrix=...)` | Author a module frame for the existing plan `attach` operation. Frames still need actual physical mating evidence. |
| `m.plan()` | Export a version-1 plan for `build_plan`, `includes`, assets and module anchors. |
| `next_step()` | Begin a new construction step. |

Use `./ldraw-agent ports 3001 32524 2780` to inspect named ports, bounds, profiles and metadata coverage. Symbols such as `@bricks.Brick2X4` and LDConfig colour names are accepted. Never guess a port name: the 1x1 brick's underside, for example, may be described as a `pin_hole` rather than a `stud_receptacle`.

For `mate`, `along="UP"` (or X, -Z, etc.) selects a reference direction across the port axis; `roll` turns around it. `slide` moves along the axis in LDU, optionally toward `toward="UP"`. `flip` reverses the part, but cannot enter a socket from its solid side. Invalid profile matches and slides with no engagement are rejected even during exploration. Use explicit `add` to sketch a provisional placement when the interface is not yet known.

`part.top` and `part.bottom` are **body extrema**, not attachment guarantees. On ordinary upright bricks, `level=base.top` is a useful stacking height. A double-slope ridge has no top studs: its highest point cannot support a chimney by stud attachment. Inspect a real face/port, preserve the feature's intended shape, and engineer an opening and support where needed.

Placement options include `id`, `purpose`, `free="reason"` for an intentionally separate object, and `overlap="reason"` for an overlap requiring review. `free` does not exempt collisions. `overlap` does not prove an interface or permit a final pass. A checker limitation should be recorded and investigated, never hidden by a declaration.

For example, the tested `4275b`/`4276b` finger hinge at 30 degrees still produces an unresolved overlap review. Preserve the intended design as a draft and investigate the interface with the detailed geometry tools and reference evidence. Do not remove a useful hinge or distort the design solely to obtain PASS. See the [implementation record](../reports/hybrid-approach-implementation.md) for current coverage and remaining work.

Render drafts and unfinished modules with `look` at any stage. Final static checks do not judge beauty, physical strength, retail availability or movement. Keep the composition and [feature brief](design-brief.md) visible while repairing the model.
