# Engines and reciprocating constructions

Source cases: [W16 and Defender](../../../examples/technic-studies/README.md).
Choose the actual construction before designing an engine bay or reusing it
as a pump, workshop exhibit or industrial machine.

## Crank-and-connecting-rod engines

The Chiron section `42083 - engine.ldr` has **223 physical parts, 16 pistons
and three crankshafts arranged 8+4+4**. Its annotation says V8/two crankshafts;
the recursive inventory and reviewed geometry disagree with that label.

The mechanical loop is fixed frame → crank bearing → offset crank pin → rod
→ piston → fixed cylinder guide. The rod has two moving endpoints and is
neither part of the crank's rigid group nor part of the piston. Likewise,
one MPD cylinder-bank section contains both moving parts and fixed heads.

| Feature | Source construction | Preserve during adaptation |
| --- | --- | --- |
| Piston and rod | `2851.dat` and `2852.dat` | Dedicated joints and the rod's pin-to-ball spacing |
| Crank throw | Nominally 10 LDU; central source approximately 9.999701 | Offset from the actual shaft line, not from a part bounding-box centre |
| Rod length | Nominally 40 LDU | Endpoints; never stretch a rod to reach a new cylinder |
| Stroke | Approximately 20 LDU for this centred arrangement | Piston/cylinder envelope and room at both ends |
| Central bank | Four shared pin stations at Z=50,90,130,170 | Two separate rods per station and their individual cylinder directions |
| Lower banks | Repeated sections at occurrences `84` and `85` | Distinct occurrence transforms, crank supports and input gears |

The two lower banks have cylinder directions approximately (-0.8,-0.6,0) and
(+0.8,-0.6,0). Equal scalar travel therefore gives different world translations.
Reuse proper rotations and the actual opposite-side construction; do not reflect
or scale complete physical parts. Both banks need independent identity when
included in a larger model.

The source pose already encodes crank phase. Some pistons start near one dead
centre and others between centres, so a universal 0..20 displacement from the
imported pose is wrong. Preserve the rest rod/piston placements when extracting
a bank. The source pattern is LEGO linkage geometry, not a combustion firing order.

For sizing intuition, a centred planar slider crank with throw `r`, rod length
`L` and angle `a` relative to its cylinder axis places the piston ball at
`r*cos(a) + sqrt(L² - r²*sin²(a))` along that axis from the crank line. This
explains why piston travel is not a simple sine wave. It is not an offset-bore
solver or a required Nova verification step. Copying the studied source pose is
preferable to inventing unmeasured rod angles.

To build a compact engine stand, start from the
[local piston/crank manual](../../../examples/mechanism-atlas/piston-crank/GUIDE.md)
or one of the W16 banks. Preserve the crank/piston core, then design a new
support frame, accessible input, head clearance and contrasting but restrained
palette. Removing the other banks also removes their supports and drive context;
replace the needed bearings and mounts deliberately.

## Cam followers

The Defender inline-six uses liftarm cams lifting guided axle followers. It has
no connecting-rod slider cranks. A drive shaft and idler feed the camshaft;
the reviewed cam eccentricity is 20 LDU and its assumed follower lift is 0..10.
Those values describe this example's cam and stop geometry.

Phases differ along the bank and one follower starts 10 LDU raised. Preserve
that rest offset and the guides instead of putting every follower at the same
height. The source lift law is a surface-contact hypothesis: gravity return,
continuous cam contact and full clearance were not established.

This construction is useful for a compact exposed engine or a sequence of pump
heads. Keep follower guides and stops visible enough to explain the action.
Changing the cam shape or follower end changes the construction; do not reuse
the source lift range as a universal dimension.

## Appearance and integration

Expose the parts that explain the chosen mechanism: crank webs, connecting rods
and piston heads for a crank engine; cam lobes and guides for a follower engine.
Reserve a quiet frame or removable casing around them. Repeated cylinders give
visual rhythm without needing arbitrary extra gears.

The [W16 preview](../../../examples/technic-studies/images/w16-cranks.png) hides
the fixed heads and frame to reveal its internals. It is a cutaway study, not a
complete freestanding construction. Add real mounts, keep the source attribution,
and review the complete engine bay as well as the exposed core.
