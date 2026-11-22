---
name: suspension-steering
description: 'Technic suspension and steering: suspension corners, shock absorbers and fixed mounts, rack-and-pinion steering, and combining steering, suspension and drive, with worked references (steering rack carriage, 8081 steerable front axle whose pinion lives in the parent). Use when building a vehicle chassis with steering, wishbones, swing arms or shocks.'
---

# Technic suspension and steering

Build wheel corners (wishbones, knuckles, shocks) and rack-and-pinion steering, and combine them with drive. Port placement and checks are in the parent [technic](../SKILL.md) skill. Choose a corner's parts and mounting geometry **before** fixing track, body width, arches or chassis height. Source cases: the Defender and standalone suspension studies (`examples/technic-studies/README.md`).

Checked starting plans in `examples/recipes/`: `technic-rack-steering` (kingpin hubs, L-liftarm arms, 1×7 rack, 1 degree of freedom) and `technic-suspension-arm` (swing arm on a frictionless pin with a 6.5L shock) — see [write-plans](../../write-plans/SKILL.md).

## Suspension corners

The Defender corner: equal parallel upper/lower wishbones, an upright knuckle, guide links, a half-shaft and two shocks.

| Source measurement | Construction implication |
| --- | --- |
| Inner pivot to outer ball: 100 LDU | Wheel corner follows an arc about the frame pivots |
| Inner coupler attachment: 80 LDU from pivot | The coupler follows a smaller displacement than the outer knuckle |
| Upper/lower pivot separation: approximately 80 LDU | Preserve both the frame and knuckle spacing for this parallelogram |
| Half-shaft length: approximately 100 LDU | Match both joint centres; source vectors are close to, but not exactly, the wishbone vectors |
| Shock eye-to-eye free length: 110.028 LDU in rounded source | Size from attachment eyes, not the mesh extent or wheel travel |

- Equal parallel arms keep the knuckle orientation, with vertical and lateral movement; they do not make an exact vertical slide. Shorter/unequal arms or relocated guide links need a new geometric study.
- The saved source pose is **full droop**, not ride height. Its front/rear rises of 30.5/40.5 LDU are particular sampled limits: do not transfer them to a new chassis.
- Treat wheel, wishbones, guide links, half-shaft and shocks as one corner envelope. An arch that clears the tyre at droop can block the raised position. Build and inspect one corner before the opposite side and before skinning the body.

## Shocks and fixed mounts

- Wheel rise and shock compression differ (about 11.86/15.90 LDU compression at the saved front/rear limits). Attachment position and angle set the relation.
- Keep the shock's two real eyes on pin supports; never use a shock as a telescoping decoration with loose ends.
- Complete-shock shortcuts `76537.dat` and `41838.dat` can be kept in their authored pose. If you study the split components (rod `4254.dat`, cylinder `4255.dat`, spring `22977.dat` or `41837.dat`), keep the official child transforms and never count both the shortcut and its children.
- **Never scale a spring mesh** to shorten it in a Nova placement. Physical transforms stay rigid.
- The 259-part standalone suspension selection is not self-supporting: front inner tie-rod pins have no rack/holders and input-side Cardan yokes are missing. Add real holders and complete the inputs when adapting it.

## Rack steering

Study the complete route: control/column → gear train → pinion → sliding rack → two tie rods → knuckle steering arms.

- The Defender has nominal 100 LDU tie rods and roughly 40 LDU steering arms. Each rod closes on its own knuckle, so the two wheel angles need not be equal.
- Keep rack guides, tooth alignment, ball joints, kingpin axes and stops. Let rod endpoints set placement; never guess identical wheel yaws and then stretch or detach links.
- The Defender's ±18 LDU rack travel is not a default: measure the actual rack/pinion and reserve end travel before placing a bumper, differential or crossmember.
- Mirror the function with each side's real axes and parts. Check left/right control direction and clearance separately. Repeated submodel filenames do not make two occurrences interchangeable.

### Steering rack carriage (9393)

`9393 - steering.ldr`: carrier beam and cross blocks hold a toothed rack and its steering connections. **The pinion is in the parent** `9393 - vehicle.ldr`, so this is a rack carriage, not a steering system. Add the matching pinion and parent supports; keep the toothed side, axle stops and sliding space.

```sh
./ldraw-agent mechanism export steering-rack --outdir output/my-steering-rack
```

### 8081 steerable front axle

29 parts, 2 sections; source checks pass and BOMs match. Step 6: suspension arms pivot on a 1×6 Technic brick, with towball ends. Step 9: the shock. Step 10: two `8081 - Front Axle S10` hub children (steering arm, axle, bush). Step 11: the gear rack with towball and both 6L steering links. The parent `8081 - Frame.ldr` places it at `0 -10 -120` with identity matrix and supplies the **8T pinion `3647`**: the rack face sits at y = −22 and the pinion at y = −30, matching the 8T gear's 10 LDU pitch radius.

- Reuse it with its drive: copy the pinion and steering axle from the parent, or add an equivalent input.
- Keep the two hub children and the links together; they set the steering geometry.
- No view shows the teeth meshing (a coordinate match only); steering and suspension travel were not checked.

```sh
./ldraw-agent manual export examples/8081-front-axle --outdir output/my-01-8081-front-axle
./ldraw-agent build output/my-01-8081-front-axle/scene.plan.json --output output/my-01-8081-front-axle/01-8081-front-axle.mpd
```

Export needs a current visual review. Look it up with `./ldraw-agent discover show submodel-791f781795f6b497d640ae2e`; replay its board with `./ldraw-xray board run examples/submodel-atlas/recipes/01-8081-front-axle.json --output output/boards/01-8081-front-axle`.

## Combining steering, suspension and drive

The source steering/drivetrain and suspension references are separate rigs: one holds wheel spin and steering fixed, the other a fixed suspension height. Their success does not certify a combined axle.

- Give each shared hub, knuckle, arm and shaft **one** occurrence. Reconcile joint centres and bearing/steering roles before bodywork.
- Record whether the delivered corner steers, articulates, drives or combines these.
- Check the combined geometry at the chosen pose; declare what should move with a `mechanism` contract ([technic](../SKILL.md)). Drive through U-joints: [transmissions](../transmissions/SKILL.md).

Exported modules place the whole source section with a proper transform; `source_origin` is a positioning frame, not a connector. Operation notes certify no motion, load or physical operation.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/mechanism-patterns/suspension-steering.md](references/docs-agent-guides-mechanism-patterns-suspension-steering.md)
- [examples/steering-rack/GUIDE.md](references/examples-steering-rack-GUIDE.md)
- [examples/8081-front-axle/GUIDE.md](references/examples-8081-front-axle-GUIDE.md)
