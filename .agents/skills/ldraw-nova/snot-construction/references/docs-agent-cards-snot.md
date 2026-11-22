# SNOT card

SNOT (studs not on top) builds surfaces sideways: a part with studs on its side carries plates, tiles or whole panels that face outward. You choose the support, the stud and the part; the tool computes the rotation and position.

## 1. Choose a support with side studs

| Part | Side studs (in the part's own frame) |
|---|---|
| `87087` brick 1 x 1 with stud on 1 side | 1 facing -Z |
| `30414` brick 1 x 4 with studs on side | 4 facing -Z |
| `52107` brick 1 x 2 with studs on sides | 2 facing -Z, 2 facing +Z |
| `67329` brick 1 x 2 x 1.667, 8 studs on 3 sides | 2 +X, 2 -X, 4 -Z |
| `99780` bracket 1 x 2 - 1 x 2 up | 2 facing -Z |
| `4070` headlight brick | 1 facing -Z, recessed 4 LDU |

The [SNOT interface table](../reference/snot-interfaces.md) covers 43 parts with stud positions. `./ldraw-agent part CODE` lists any part's studs and sockets by face, in the order `on` counts them.

## 2. Seat parts on its studs

```json
{"id": "core", "ref": "30414.dat", "colour": 71, "at": [0, -24, 0], "yaw": 90},
{"id": "panel", "ref": "3710.dat", "colour": 15, "on": {"to": "core", "face": "-Z", "stud": 0}}
```

- `face` and `stud` pick the support's stud. Faces are the support part's own faces as `part` lists them, so they stay correct however the support is turned. Without `face`, the part goes on top.
- `socket` picks the new part's socket (default 0). The tool turns the new part so that socket faces the stud.
- By default it uses the quarter turn that covers the most studs; `"roll": 90` overrides that. The full report (`--report`) lists each seat with `mated`, the number of studs it covers.

## 3. Build surfaces as modules

Build a panel flat, studs up, in its own section. Then seat the whole section by the point that touches the stud:

```json
{"id": "flank", "ref": "flank.ldr", "colour": 15, "on": {"to": "core", "face": "-Z", "stud": 0, "socket_at": [-30, 8, 0], "roll": 90}}
```

`socket_at` is in the section's frame, and its underside faces +Y as with any part built upright. A module has no socket list, so give `roll` or `orient` explicitly.

## 4. Hang parts underneath

Studs that point down, or parts built downward from a surface, use `under`: the placed part's stud goes into a socket of the part above.

```json
{"id": "chin", "ref": "3665a.dat", "colour": 15, "under": {"to": "deck", "socket": 0}}
```

`socket` and `socket_face` pick the support's socket (default its underside); `stud` and `face` pick the placed part's stud (default its top). The default turn again covers the most studs.

## Finish

- Cover studs that face outward with tiles unless they are a deliberate texture; review warns with `appearance.exposed_side_studs`.
- A sideways part needs studs behind it. Turning a part next to a wall does not attach it.
- Five plates (40 LDU) equal two studs: use this to line up sideways and upright grids.
- Round off blocky edges with curves on side studs; vehicles must ([silhouette pass](../guides/design-models.md#soften-blocky-vehicle-silhouettes)). A curved slope's sockets sit only under its flat end, so name one and check `mated`: `{"id": "edge", "ref": "61678.dat", "colour": 15, "on": {"to": "core", "face": "-Z", "stud": 0, "socket": 2}}` on a `30414`.
- Real-set examples: `./ldraw-agent examples --family submodel --details snot` and the [SNOT guide](../guides/snot.md).
