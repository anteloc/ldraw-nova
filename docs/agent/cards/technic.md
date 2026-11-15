# Technic card

Technic parts join through pins and axles in holes. Seat them by naming the ports; the tool turns and positions the part and checks the fit as it builds.

## Find the ports

`./ldraw-agent part CODE` lists a reviewed part's ports under `technic_ports`: an ID, its kind (`pin`, `axle`, `pin_hole`, `axle_hole`), its centre and its axis. A beam's holes are `hole-0`, `hole-1` and so on along its length. A pin's two halves are `grip-0` and `grip-1`, and an axle is `shaft`. Thirty-nine common beams, Technic bricks, pins, axles, bushes, a gear and a cross block are reviewed; `./ldraw-agent technic parts` lists them.

## Seat pins, beams and axles

```json
{"id": "upper", "ref": "32523.dat", "colour": 71, "at": [0, 0, 0]},
{"id": "pin", "ref": "2780.dat", "colour": 0, "on": {"to": "upper", "hole": "hole-1", "pin": "grip-0"}},
{"id": "lower", "ref": "32523.dat", "colour": 72, "on": {"to": "pin", "hole": "hole-1", "pin": "grip-1"}}
```

- `hole` and `pin` are port IDs; each belongs to whichever part has it. So the second seat puts the lower beam's hole on the pin's free half.
- A pin half sits centred in its hole. An axle can slide: `"slide": 20` moves it 20 LDU along the hole axis.
- `roll` turns the placed part about the shared axis. For an axle in a cross hole the tool tries the 45° alternative itself.
- A seat that breaks a fit rule fails with the rule's name: `family` (a pin needs a pin hole), `alignment`, `keyed roll`, `engagement` (the hole runs past the end of the pin) or `pin grip`.

```json
{"id": "axle", "ref": "3705.dat", "colour": 0, "on": {"to": "brick", "hole": "hole-0", "pin": "shaft", "slide": 20}}
```

## Build frames that hold

- Every beam needs pins or axles into another layer; beams that only touch fall apart. `assembly.floating_group` names such parts.
- Use friction pins (`2780`) for rigid joints and frictionless pins (`3673`) for pivots.
- Declare the joints a mechanism needs as a structure contract, so `build` checks them: see the [Technic reference](../reference/technic.md#name-the-intended-connections).
- System studs and Technic mix: a Technic brick (`3700`, `32064a`) has studs on top and a hole through its side.
