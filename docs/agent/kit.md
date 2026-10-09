# Construction kit

Write a Python generator with `ldraw_tools.kit`. You choose parts and connections, and the kit computes positions and rotations. Every placement is checked against the parts already placed. A collision or a badly seated part raises `KitError` at the line that caused it, naming the ids and suggesting a fix. `save()` writes the MPD and an equivalent JSON plan, then prints the `check` verdict.

```python
from ldraw_tools.kit import Model

m = Model("pier", "A small pier with a Technic crane arm")            # main FILE block
post = m.place("3005", "Dark_Bluish_Grey", cell=(0, 0), level=0)     # 1x1 brick on the ground
deck = m.place("3034", "Reddish_Brown", cell=(0, 0), level=post.top, turn=90)       # 2x8 plate along Z on it
mount = m.place("32000", "Light_Bluish_Grey", cell=(0, 6), level=deck.top, turn=90)  # Technic brick 1x2
pin = m.mate("2780", "Black", "pin[0]", to=mount.port("pin_hole[0]"))                # pin into its hole
arm = m.mate("32524", "Red", "pin_hole[0]", to=pin.port("pin[2]"), roll=135)         # Beam 7, raised 45°
m.save("output/pier/pier.mpd")                                       # MPD + .plan.json + check verdict
```

## Choose the verb

```mermaid
flowchart TD
  Q{How does the part attach?} -->|"on studs, upright"| P["place(ref, colour, cell=(x, z), level=n, turn=deg)"]
  Q -->|"on studs facing sideways, down or tilted"| O["place(ref, colour, on=part.port('stud[k]'), cell=..., turn=...)"]
  Q -->|"pin, axle, stud, hinge, clip or wheel interface"| M["mate(ref, colour, port, to=part.port(name))"]
  Q -->|"a pin joining two parts' aligned holes"| T["pin(colour, between=(a.port(name), b.port(name)))"]
  Q -->|"the other half of a hinge, at an angle"| H["hinge(ref, colour, 'hinge[0]', to=root.port('hinge[0]'), angle=deg)"]
  Q -->|"nothing fits; I know the LDU position"| A["add(ref, colour, at=(x, y, z), axes={...})"]
  Q -->|"a whole module"| S["s = m.section(name, description); build it; m.add(s, None, at=..., turn=...)"]
  Q -->|"the other side of a symmetric model"| R["m.mirror(parts, about=hull)"]
  M --> N["names: ./ldraw-agent ports PART"]
```

| Verb or property | What it does |
|---|---|
| `place(ref, colour, cell=(x, z), level=n, turn=0)` | `cell` is the stud cell of the footprint's minimum corner (one stud = 20 LDU). `level` is the part's bottom in plates above the ground (one plate = 8 LDU; a brick = 3 plates). `turn` is 0, 90, 180 or 270 about the vertical. |
| `place(ref, colour, on=part.port("stud[k]"), cell=(x, z), level=0, turn=0)` | The same grid on any stud face: a bracket's side, a headlight brick's side stud, a hinged plate, an upside-down part. Cell (0, 0) is that stud; on a top face (even tilted) cells run like the ground, on a side face cell z points up; `turn` rotates about the stud. |
| `part.top`, `part.bottom` | The level of a placed part's top and bottom. Stack the next part with `level=below.top`. |
| `part.port(name)`, `part.ports(kind)` | One port of a placed part, to pass as `to=`; or the names of its ports, optionally of one kind (`"pin_hole"`). |
| `mate(ref, colour, port, to=other.port(name), roll=0, along=None, slide=0, toward=None, flip=None)` | Puts the new part's `port` on the target port: studs seat at the socket mouth, other ports centre on each other. `along="UP"` (or `"X"`, `"-Z"`, ...) points the new part's length that way; otherwise `roll` turns it about the shared axis. `slide` moves it along the axis in LDU, toward `toward="UP"` when given. `flip=True` turns it end for end. |
| `hinge(ref, colour, port, to=root.port("hinge[0]"), angle=0)` | The other half of a hinge: 0 extends it flat, straight out from the root part; positive tilts it toward the root's top (a raised wing), negative toward its underside. Studs stay up. Build on it with `place(on=...)`. |
| `pin(colour, between=(a.port(name), b.port(name)), ref="2780")` | A pin through two coaxial holes of different parts, which closes a Technic frame. 2780 joins holes 20 LDU apart; long pins 6558/32556 join holes 40 apart. |
| `add(ref, colour, at=(x, y, z), turn=0, axes={"y": "X", "z": "-Z"})` | Explicit LDU position. `axes` says where two local axes point (`X`, `-X`, `Y`/`DOWN`, `-Y`/`UP`, `Z`, `-Z`). |
| `wall(colour, start=(x, z), length=n, courses=k, level=l, along="X", openings=[...])` | A straight running-bond wall of 1xN bricks; joints are staggered so the courses lock together. Its top is at `l + 3k`. Each opening `(offset, width, first_course, last_course)` leaves a gap for a door or window. |
| `m.part(ref)` | A part's data without placing it: `.lo` and `.hi` are its body box, so `m.part("3641").hi[1]` is a tyre's radius. |
| `mirror(parts, about=hull, plane="X")` | Places the mirror image of parts across `hull`'s centre line (`plane="Z"` for front/back). Left and right parts swap (41769 Wing Right becomes 41770 Wing Left); ids swap `left`/`right`. Build one side, then mirror it. |
| `fill(colour, cell=(x, z), size=(w, d), level=l, part="plate")` | Covers a rectangle with the largest 2xN (then 1xN) plates or tiles. Plates side by side are not joined: bridge each seam or use one large plate. |
| `section(name, description)` | A submodel with the same verbs; place it with `add(section, None, at=..., turn=...)`. Collision and seating checks run within each section as you build; `save` checks the whole model. |
| Options on any verb | `id="roof-left"` (unique; used in every report), `purpose="..."`, `free="reason"` (an intentionally separate object), `overlap="reason"` (a deliberate overlap, reviewed instead of failing). |
| `next_step()` | Later placements go into a new building step. |

Colours are LDConfig names (`"Light_Bluish_Grey"`, `"Tan"`) or codes. `./ldraw-agent colours NAME` lists them.

## Conventions

| Quantity | Value |
|---|---|
| Axes | X right, Y **down** (negative Y is up), Z toward the viewer |
| Stud pitch | 20 LDU; `cell=(x, z)` puts a stud centre at (20x, 20z) |
| Plate, brick body height | 8 and 24 LDU, so a brick is 3 levels |
| Ports | Port names come from `ports PART`, ordered by kind and then by position; they don't depend on the part's colour |

## When the kit says no

| `KitError` says | Usual fix |
|---|---|
| `sunk N LDU on the stud of 'x' ... level=L` | Use the suggested level (often `x.top`). |
| `collides with 'x' ... spans levels a..b` | Move to another cell, or stack above `b`. |
| `has no port 'name'; it has: ...` | Pick a listed port; `ports PART` shows their positions and axes. |
| Both directions fail in `mate` | The target is blocked; try `roll`, `slide` or another port. |

After `save`, fix anything `check` reports. Typical misses are floating groups (two plates side by side need a part across the seam) and modules that are placed but not attached. Use `check --graph` to see which modules connect.
