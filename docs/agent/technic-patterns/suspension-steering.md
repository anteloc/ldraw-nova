# Suspension and steering construction

Source cases: [Defender and standalone suspension](../../../examples/technic-studies/README.md).
Choose a wheel corner's parts and mounting geometry before fixing track, body
width, arches or chassis height.

## Suspension corners

The studied Defender has equal parallel upper/lower wishbones, an upright
knuckle, guide links, a half-shaft and two shocks per corner. The relevant
dimensions have different jobs:

| Source measurement | Construction implication |
| --- | --- |
| Inner pivot to outer ball: 100 LDU | Wheel corner follows an arc about the frame pivots |
| Inner coupler attachment: 80 LDU from pivot | The coupler follows a smaller displacement than the outer knuckle |
| Upper/lower pivot separation: approximately 80 LDU | Preserve both the frame and knuckle spacing for this parallelogram |
| Half-shaft length: approximately 100 LDU | Match both joint centres; source vectors are close to, but not exactly, the wishbone vectors |
| Shock eye-to-eye free length: 110.028 LDU in rounded source | Size from attachment eyes, not the mesh extent or wheel travel |

Equal parallel arms keep the knuckle orientation in this example, with vertical
and lateral movement. They do not create an exact vertical slide. Zero camber
or toe change is a property of this arrangement, not a rule for all suspensions.
Shorter/unequal arms or relocated guide links need a new geometric study.

The saved source pose is **full droop**, not normal ride height. The sibling's
adopted front/rear rises are 30.5/40.5 LDU; these are particular sampled limits.
Front travel stops early because a lower-arm tile/liftarm crossing appeared at
31 LDU in its shrunk-mesh study. Rear travel is limited by the chosen shock
compression budget. Do not transfer these limits to a new chassis or use them
as manufactured tolerances.

Keep space around the wheel, wishbones, guide links, half-shaft and shocks as a
single corner envelope. A body arch that clears the tyre at droop can obstruct
the intended raised position. Build and inspect one corner before making the
opposite side and before skinning the body.

## Shocks and fixed mounts

Wheel rise and shock compression are different: at the saved front/rear limits,
shock compression is about 11.86/15.90 LDU. Attachment position and angle determine
the relation. Preserve the shock's two real eyes and surrounding pin supports;
do not use a shock as a convenient telescoping decoration with unattached ends.

Complete-shock shortcuts `76537.dat` and `41838.dat` were split in Mecha into
rod `4254.dat`, cylinder `4255.dat`, and spring `22977.dat` or `41837.dat` for
animation. Nova can retain a suitable complete shortcut in its authored pose.
If studying separate components, preserve the official child transforms and
the BOM boundary; never count both the complete shortcut and its children.

Mecha compresses the spring mesh by axial scaling for presentation. **Do not
copy that scale into a Nova physical-part placement.** Keep physical transforms
rigid and use a supported part/assembly pose. A visually shortened coil does
not establish stroke, coil binding or spring strength.

The 259-part standalone selection includes 117 moving parts, 38 mounts and 104
frame parts, yet is not a complete self-supporting build. Front inner tie-rod
pins (extract IDs 74/75) have prescribed positions with their rack/holders
omitted. Input-side Cardan yokes are also absent. Add actual holders and complete
the input interfaces when adapting a corner into a new model.

## Rack steering

Study the complete route: control/column → gear train → pinion → sliding rack
→ two tie rods → knuckle steering arms. The
[local rack carriage](../../../examples/mechanism-atlas/steering-rack/GUIDE.md)
omits its parent's pinion; it cannot teach the whole route alone.

The Defender has nominal 100-LDU tie rods and roughly 40-LDU steering arms.
Each rod closes on its own knuckle, so the two wheel angles need not be equal.
Preserve the rack guides, tooth alignment, ball joints, kingpin axes and stops.
Let rod endpoints determine placement; do not guess identical wheel yaw angles
and then stretch or detach the links to suit them.

The source uses a particular rack-pitch calibration and accepts rounded gear
centre distances. Its approximately ±18-LDU rack travel is not a default for
every rack. Measure the actual rack/pinion and reserve its end travel before
placing a bumper, differential or frame crossmember.

Mirror the intended function using each side's actual axes and parts. Check
left/right control direction and corner clearance separately, including an
asymmetric pose when useful. Repeated submodel filenames do not make two physical
occurrences interchangeable.

## Combining steering, suspension and drive

The sibling's steering/drivetrain and suspension references are separate rigs.
The suspension example holds wheel spin and steering fixed; the steering example
uses a fixed suspension height. Their success does not certify a combined axle.

In a Nova model, give each shared physical hub, knuckle, arm and shaft one
occurrence. Reconcile their joint centres and bearing/steering roles before
adding bodywork. Record whether the delivered corner is intended to steer,
articulate, drive, or combine these features. Study the combined geometry at the
chosen pose and leave the analytical verification status deferred.
