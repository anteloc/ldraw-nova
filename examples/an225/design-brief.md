# An-225 Mriya — design brief and module checklist

**Subject.** Antonov An-225 Mriya, the largest aircraft ever flown. It is shown parked on
all 32 wheels while loading: the nose visor is swung up, the forward ramp is down, and
two microscale containers wait in the hold.

**Scale and family.** About 1:100 System-brick aircraft; 1 stud ≈ 0.8 m. Neither
minifigure scale nor Technic is used.

| Measure | Model | Full size at 1:100 | Real An-225 |
|---|---:|---:|---:|
| Length (closed nose to tail cone) | 104 studs | 83 m | 84 m |
| Wingspan | 106 studs | 85 m | 88.4 m |
| Wing area | 1,332 stud² | 852 m² | 905 m² |
| Fuselage width | 10 studs | 8 m | ≈7.3 m |
| Height to fin-cap top | 455 LDU | 18.2 m | 18.1 m |
| Tyre diameter | 36 LDU | 1.44 m | 1.27 m |

**Axes and datum.** X runs across the aircraft (port is −X), −Z is forward, and −Y is up.
The ground is Y=0. Station *s* counts studs aft of the closed nose tip, with z = s − 52.

## Composition

- **Silhouette.** A long, straight, tall 10-wide fuselage with a stepped aft upsweep. A
  high swept wing is flush with the roof and carries six hanging engines. The H-tail
  has two swept endplate fins. Main-gear sponsons along the lower sides carry
  7 wheel pairs each.
- **Primary focal feature.** The raised nose visor, the open hold with orange and
  sand-green containers, and the lowered ramp with yellow edges.
- **Supporting features.**
  - The six D-18T nacelles (dedicated 43121 engines) under a 1:2 swept leading edge.
  - The twin-fin H-tail with blue/yellow flag caps.
- **Accents.**
  - Buran carrier mounting posts on the roof.
  - Six upper-deck windows.
  - Trans-red and trans-green wingtip lights.
  - The 32-wheel stance.
- **What makes it attractive.** It reads instantly as the Mriya:
  - six engines and the twin fins at thumbnail size;
  - a single loading story at the nose;
  - a restrained Ukrainian blue/yellow cheatline on a quiet white fuselage;
  - large tiled wing and stabiliser surfaces that keep the flying surfaces calm, while
    the studded wedge bands mark the leading and trailing edges.

## Palette roles

| Role | Colour | Where |
|---|---|---|
| Body | White 15 | Fuselage, visor, nacelles, fins |
| Cheatline | Blue 1 / Yellow 14 | Blue ceiling plate course; yellow pinstripe course; fin flag caps |
| Flying surfaces / belly | Light Bluish Grey 71 | Wing, stabiliser, pylons, keel underside, visor chin, rims, hold floor |
| Structure / gear | Dark Bluish Grey 72 | Bogie beams, struts, hinges, ramp deck |
| Glass | Trans-Black 10375 | Windscreen band, windows |
| Tyres | Rubber Black 256 | 32 tyres |
| Cargo accents | Orange 25, Sand Green 378 | Containers |
| Lamps | Trans-Red 36 (port), Trans-Green 34 (starboard) | Wingtips |

**Quiet surfaces.** The fuselage roof (curved 15068 edges and tiles), the upper sides and
the tiled tops of the wing and stabiliser. **Detail vocabulary.** Cheatline plate courses,
1×1 glazing, studded wedge edge bands, pylon fairings and the yellow edges on the hold
threshold and ramp.

## Defining parts and measured interfaces

- **Running gear.** The toolkit's measured `classic` axle recipe
  (`ldraw_tools.vehicles.axle`): a 4600 holder whose origin is at Y=−23, and 4624 rims
  with 3641 tyres on the ground. Staggered 2-wide beams at −23..−39 meet the keel
  underside at −39.
- **Keel.** Three bonded plate layers (−39..−63). In the middle layer, tie plates carry
  the 2-wide sponson extensions into the main keel.
- **Wall courses.**
  - Bricks at 71/95/119/143/167; a blue ceiling plate field at 191; a yellow pinstripe
    at 199; the upper deck at 207; the roof plate at 231; roof/wing top at 255.
  - Course *j* continues aft over belly steps 0..*j*.
  - Each 4-stud belly step is a 3030 deck over ten yaw-180 13547 inverted curves.
- **Wing and stabiliser.**
  - Measured wedge cut ratios: 48205/48208 are 1:2 (26.6°) and 3544/3545 are 1:4 (14°).
  - Leading edges are chained 4×6 wedges; trailing edges are chained 3×8 wedges.
  - The second layer's wedges are offset along the same line: 2 span/1 chord on the
    leading edge, 4 span/1 chord on the trailing edge.
  - The generator chooses the real left/right part and yaw from the measured edge
    geometry. No part is mirrored.
  - Plates are packed below and tiles above, with a bond-aware packer that makes each
    upper piece bridge two lower pieces where possible.
- **Engines.** A 2×6 pylon plate under the wing; the 43121 top studs (2×4) sit in the
  pylon sockets. The inlet faces −Z. A 2×2 tile covers the pylon studs ahead of the
  leading edge.
- **Fins.** 54094 tail planes on the stabiliser tips. Each base underside is 192 LDU below
  its stud origin, and the fin extends 5 studs ahead of the stabiliser leading edge.
- **Visor hinge.**
  - Four 3937/3938 hinge bricks on the ceiling front row (s=7..8), axis at Y=−213.
  - Both parts are yawed 180° so the base's relieved edge faces the swing. Mesh checks
    showed that the opposite orientation cuts the base.
  - The visor module is authored closed and placed with a rigid −70° rotation about
    that axis.
- **Ramp hinge.**
  - 44302a (fixed, in the floor) and 44301a (ramp) click hinges, axis at Y=−69, s=6.5.
  - The ramp sits at the 22.5° click detent; the teeth mesh every 22.5°.
  - Its 7-stud deck leaves the toe 6 LDU above the ground.

## Module checklist

| Section | Local origin / envelope | Interfaces and anchors | Depends on | Status |
|---|---|---|---|---|
| `an225-keel.ldr` | World; s 7..72, X ±5 (±7 at s 37..57), Y −39..−63 | Gear beams below; walls, sponsons and floor above | — | Built, contacts reviewed |
| `an225-main-gear.ldr` (×2) | Local ground Y=0, 14 studs long | Beam top Y=−39 → keel; placed at X ±4, s 39 | `axle-classic` | Road profile passes |
| `an225-nose-leg.ldr` (×2) | Local ground Y=0 | Strut top Y=−39 → keel; X ±2, s 11..13 | `axle-classic` | Road profile passes |
| `an225-fuselage.ldr` | World; s 7..104 | Walls on keel and belly decks; ceiling, roof, windows, roof edges | keel, aft | Built, reviewed |
| `an225-sponsons.ldr` | World; X ±5..7, s 37..57 | Stand on the widened keel | keel | Built, reviewed |
| `an225-aft.ldr` | World; s 72..104 | Six belly steps under the long wall courses, skirt, tail cone | fuselage | Built; stepped profile accepted |
| `an225-cockpit.ldr` | World; s 7..12 | 3937 hinge bases; windscreen; forehead | fuselage | Built, hinge clearance checked |
| `an225-hold.ldr` + 2 containers | World; s 7..31 inside the walls | 44302a lip hinges; containers on keel studs | keel | Built, reviewed |
| `an225-visor.ldr` | Authored closed, s 0..8; rotated −70° about Y=−213, s=7.5 | 3938 hinge tops | cockpit | Built, mesh-checked |
| `an225-ramp.ldr` | Authored flat, s −1..6; rotated 22.5° about Y=−69, s=6.5 | 44301a hinge plates | hold | Built, mesh-checked |
| `an225-wing.ldr` | World; underside Y=−239, span ±53 | Rests on roof plates; pylons below | fuselage | Built, contacts reviewed |
| `an225-engine.ldr` (×6) | Mount = pylon top (wing underside) | X ±12/20/28 at the leading-edge station | wing | Built, contacts reviewed |
| `an225-tail.ldr` | World; stabiliser underside Y=−239, s 88..104, span ±21 | Rests on roof plates; fins on tip studs | fuselage | Built, contacts reviewed |
| `an225-details.ldr` | Roof centre plates | Buran mounting posts | fuselage | Built |

**Build order.**

1. Gear and keel.
2. Hold floor and containers.
3. Walls, sponsons and belly steps.
4. Ceiling, upper deck and roof.
5. Cockpit and hinge bases.
6. Wing and engines.
7. Tail.
8. Visor and ramp on their hinges.

**Stated simplifications.**

- **Wing:** flat, without the real anhedral; hinged anhedral would add joints that can't
  be verified.
- **Aft belly:** a stepped curve profile.
- **Tail cone:** blunt.
- **Nose gear:** the aircraft is shown on its normal stance, not kneeling.
- **Cockpit:** no interior.
