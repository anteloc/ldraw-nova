## Prompt

You are an LDraw builder. Using **only** the parts in the bill of materials
below, build the subassembly described here and write it as a single standalone
`.ldr` file to `<OUTPUT_LDR>`.

You have no source file to copy from. Everything you need is in this message.
Build the assembly from the BOM and the spec, then verify it against the
acceptance checks at the end.

### Coordinate conventions

LDraw units (LDU). 1 stud = 20 LDU, one Technic beam hole pitch = 20 LDU, plate
thickness = 8 LDU.

The three axes in this spec are local to the subassembly:

- **X** — the left/right axis. The assembly is symmetric about the plane `x = 0`.
- **Y** — the vertical axis. **In LDraw, +Y points downward**, so a part at
  `y = -50` sits *above* one at `y = +10`.
- **Z** — the depth axis, running through the three build planes.

The local origin `(0, 0, 0)` is the point where the mirror plane meets the
central spine row, on the near build plane. Every coordinate below is relative
to that origin, so the finished file is origin-local and can be placed into a
larger model with a single transform.

### Bill of materials — 29 parts, 13 distinct

Use every one of these, and nothing else. Quantities are exact: do not add a
part "for strength" and do not leave one out because it looks redundant.

| Qty | Part | Colour | Description |
| ---: | --- | ---: | --- |
| 4 | `2780.dat` | 0 (black) | Technic Pin with Friction and Slots |
| 4 | `32062.dat` | 4 (red) | Technic Axle  2 Notched |
| 4 | `6558.dat` | 1 (blue) | Technic Pin Long with Friction and Slot |
| 2 | `32013.dat` | 4 (red) | Technic Angle Connector #1 |
| 2 | `32140.dat` | 0 (black) | Technic Beam  2 x  4 Liftarm Bent 90 |
| 2 | `32291.dat` | 71 (light bluish grey) | Technic Cross Block 2 x 2 (Axle/Twin Pin) |
| 2 | `3705.dat` | 0 (black) | Technic Axle  4 |
| 2 | `41678.dat` | 4 (red) | Technic Cross Block 2 x 2 Split (Axle/Twin Pin) |
| 2 | `43857.dat` | 0 (black) | Technic Beam  2 |
| 2 | `6536.dat` | 4 (red) | Technic Cross Block 1 x 2 (Axle/Pin) |
| 1 | `32034.dat` | 4 (red) | Technic Angle Connector #2 (180 degree) |
| 1 | `32293.dat` | 0 (black) | Technic Steering Link 9L |
| 1 | `6628.dat` | 0 (black) | Technic Pin Towball with Friction |

### What you are building

A symmetric pair of wing-tip endplate structures, joined across the centre by a
single axle spine, plus a one-sided steering-link stub.

Read it as three parallel build planes, stepping outward along +Z:

1. **The spine (`dz = 0`)** — a cross-car axle run centred on `x = 0`. A 180°
   angle connector sits exactly on the mirror plane; a #1 angle connector at
   each `x = ±40` turns the run through a right angle; a 4L axle at each
   `x = ±50` threads outward from those connectors; a 1x2 cross block caps each
   end at `x = ±80`. Above the run, a bent 90° liftarm at each `x = ±40` forms
   the inner face of each endplate, pinned through by friction pins at `x = ±70`
   and located by 2L notched axles at `x = ±40`.
2. **The joint plane (`dz = +20`)** — at each `x = ±80`, three parts stack
   **coaxially at the same point**: a 2x2 split cross block, a 2L notched axle
   running through it, and a 2x2 cross block. This triple is the hinge that
   carries the endplate out to the tip. Both sides are identical apart from
   mirroring.
3. **The tip plane (`dz = +40`)** — at each `x = ±100`, a 2L beam held by two
   long friction pins, one above and one below it. These are the outer faces of
   the endplates.

**The one asymmetry is deliberate.** The 9L steering link and its towball pin
exist only on the `-x` side, at the outermost, lowest position of the tip plane.
They are the stub of a linkage that continues outside this subassembly. Build
them on the `-x` side only — do not "fix" the symmetry by adding a mirrored
copy, and do not drop them for being unpaired.

Everything else comes in mirrored pairs: 13 distinct part types arranged as
13 mirror-symmetric pairs about `x = 0`, plus the 3 unpaired parts above (the
central 180° connector, the towball pin, the steering link).

### Layout

Orientation is written as the image of each local axis, so `X→+Z Y→+Y Z→-X`
means the part's own X axis points along world +Z, its Y along +Y, its Z along
-X. To turn that into an LDraw line, the 3x3 matrix `a b c / d e f / g h i` has
the image of local X as its **first column**, local Y as its second, local Z as
its third. `X→+X Y→+Y Z→+Z` is therefore the identity `1 0 0 0 1 0 0 0 1`.

**Plane dz = +0** — 15 parts

| dx | dy | part | colour | orientation |
| ---: | ---: | --- | ---: | --- |
| -80 | -30 | `6536.dat` | 4 | X→-X Y→-Y Z→+Z |
| -50 | -30 | `3705.dat` | 0 | X→-X Y→+Y Z→-Z |
| -40 | -30 | `32013.dat` | 4 | X→-X Y→-Z Z→-Y |
| +0 | -30 | `32034.dat` | 4 | X→+Z Y→+Y Z→-X |
| +40 | -30 | `32013.dat` | 4 | X→-X Y→-Z Z→-Y |
| +50 | -30 | `3705.dat` | 0 | X→-X Y→+Y Z→-Z |
| +80 | -30 | `6536.dat` | 4 | X→-X Y→-Y Z→+Z |
| -70 | -10 | `2780.dat` | 0 | X→+X Y→-Y Z→-Z |
| +70 | -10 | `2780.dat` | 0 | X→-X Y→+Y Z→-Z |
| -40 | +0 | `32062.dat` | 4 | X→+Y Y→+X Z→-Z |
| +40 | +0 | `32062.dat` | 4 | X→+Y Y→+X Z→-Z |
| -70 | +10 | `2780.dat` | 0 | X→+X Y→-Y Z→-Z |
| -40 | +10 | `32140.dat` | 0 | X→-X Y→+Y Z→-Z |
| +40 | +10 | `32140.dat` | 0 | X→+X Y→-Y Z→-Z |
| +70 | +10 | `2780.dat` | 0 | X→-X Y→+Y Z→-Z |

**Plane dz = +20** — 6 parts

| dx | dy | part | colour | orientation |
| ---: | ---: | --- | ---: | --- |
| -80 | +0 | `41678.dat` | 4 | X→+Y Y→-X Z→+Z |
| -80 | +0 | `32062.dat` | 4 | X→+Y Y→-X Z→+Z |
| -80 | +0 | `32291.dat` | 71 | X→+Y Y→-X Z→+Z |
| +80 | +0 | `41678.dat` | 4 | X→-Y Y→+X Z→+Z |
| +80 | +0 | `32062.dat` | 4 | X→-Y Y→+X Z→+Z |
| +80 | +0 | `32291.dat` | 71 | X→-Y Y→+X Z→+Z |

**Plane dz = +40** — 8 parts

| dx | dy | part | colour | orientation |
| ---: | ---: | --- | ---: | --- |
| -120 | -50 | `32293.dat` | 0 | X→+Z Y→+X Z→+Y |
| -110 | -50 | `6628.dat` | 0 | X→+X Y→+Z Z→-Y |
| -100 | -10 | `6558.dat` | 1 | X→+Z Y→-Y Z→+X |
| +100 | -10 | `6558.dat` | 1 | X→+Z Y→+Y Z→-X |
| -100 | +0 | `43857.dat` | 0 | X→-X Y→-Z Z→-Y |
| +100 | +0 | `43857.dat` | 0 | X→+X Y→-Z Z→+Y |
| -100 | +10 | `6558.dat` | 1 | X→+Z Y→-Y Z→+X |
| +100 | +10 | `6558.dat` | 1 | X→+Z Y→+Y Z→-X |

### Output format

Write one LDraw type-1 line per part, in the order given above:

    1 <colour> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part>.dat

Put a `0 // <part description>` comment line directly above each part line —
use the Description column of the BOM verbatim, adding the colour name in
parentheses.

Begin the file with a one-line description of the assembly, then
`0 Name: <the file name you wrote>`. Do **not** emit any `0 FILE` or `0 NOFILE`
line: this is a standalone model, not an `.mpd` section.

### Acceptance checks

Run these against the file you wrote and report the numbers. Fix and re-check
rather than reporting a failing file.

- exactly **29** lines beginning `1 `, and **13** distinct `.dat` part names
- the per-part quantities match the BOM exactly, colour for colour
- exactly **13** mirror-symmetric pairs about `x = 0`: for each, the two lines
  are identical apart from mirroring, and exactly **3** parts are unpaired —
  the 180° angle connector at `x = 0`, the towball pin and the steering link
- bounding box of the part positions is **dx -120..+100, dy -50..+10, dz +0..+40**
- every matrix is a signed permutation matrix: each row and each column holds
  exactly one non-zero entry, and that entry is +1 or -1
- zero lines beginning `0 FILE` or `0 NOFILE`

### Report back

Give the part count, the distinct-part count, the mirror-pair and unpaired
counts, the bounding box, and the output path. If any instruction here was
ambiguous or looked inconsistent with the BOM, say so explicitly rather than
guessing silently.
