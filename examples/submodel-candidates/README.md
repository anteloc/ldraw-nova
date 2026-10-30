# Submodel candidates

These are reference submodels for a future submodels catalog. Each is shown on
an [ldraw-xray](../../docs/agent/submodel-inspection.md) board:

- parent context, with only the selected submodel highlighted in magenta;
- isolated views;
- highlighted source steps;
- an x-ray or stud-direction map, where it helps.

Every entry was rendered, inspected and reviewed by the user. Sources are in
`data/models-annotated/`. The hashes are SHA-256 of the whole MPD.

| Path | Contents |
|---|---|
| [`candidates.json`](candidates.json) | One row per kept candidate: source, section, hash, parent, family, lesson and recipes |
| `recipes/` | One xray board recipe per candidate. The panels are the reviewed views, and the labels are the reviewed captions. |

Render a board into `output/`:

```sh
./ldraw-xray board run examples/submodel-candidates/recipes/01-8081-front-axle.json \
  --output output/candidates/01-8081-front-axle
```

The board's `manifest.json` records the source hash, the camera and the layers of
each panel.

**Limits for every entry.** Renders and the source teach a construction. They do
not establish physical fit, clearance, travel or stability. None of these
entries has been through `manual prepare`/`review`/`export` or atlas promotion.

## Summary

| # | Family | Submodel | Main lesson | Recipe |
|---|---|---|---|---|
| 1 | Technic chassis | `8081 - Front Axle.ldr` | The steering rack's pinion lives in the parent | [01](recipes/01-8081-front-axle.json) |
| 2 | Technic chassis | `42075 - rearaxle.ldr` | Differential axle; the parent sets its tilt | [02](recipes/02-42075-rear-axle.json) |
| 3 | Technic mechanism | `42050 - engine.ldr` | The crank train is hidden; steps and a see-through copy reveal it | [03](recipes/03-42050-v8-engine.json) |
| 4 | Technic-to-System SNOT | `42078 - light1.ldr` | A sideways lamp on a Technic mount; the parent explains the orientation | [04](recipes/04-42078-headlight.json) |
| 5 | Vehicle SNOT | `10269 - step199-212.ldr` | A sideways round disc; the parent corrects a wrong DB description | [05](recipes/05-10269-headlight-nacelle.json) |
| 6 | Spaceship SNOT | `10283 - shuttle-421-451.ldr` | A colour-coded SNOT core under a hinged shell; steps beat transparency | [06](recipes/06-10283-shuttle-framework.json) |
| 7 | Spaceship mechanism | `75060 - step84.ldr` | A cockpit pod on a revolute pivot; shows how a pivot is marked | [07](recipes/07-75060-cockpit-base.json), [poses](recipes/07-75060-cockpit-base-poses.json) |
| 8 | Vehicle shaping | `7784 - Bat.ldr` | Built flat, stood upright about 98° on a pin mount | [08](recipes/08-7784-bat-hull.json) |
| 9 | Building | `10182 - Second floor - Roof tower.ldr` | Corner tower: parrot gargoyles, hinged pyramid roof | [10](recipes/10-10182-roof-tower.json) |

`10262-1.mpd` :: `10262 - step150-164.ldr` (number 09) is excluded for now. It is
the DB5's front module, not a rear one. The DB and the model header both call
the model a "Lunar Lander", and its purpose is still open.

**Duplicate panels.** The last source step looks almost the same as the finished
isolated view, so boards avoid pairing them. xray reports `duplicate_panels`
when two panels' 96×72 greyscale thumbnails differ by a mean below 7 (0–255
scale). A real duplicate measures 0–4.5.

---

## 1. Steerable Technic front axle; the pinion is in the parent

- **Source:** `8081-1.mpd` :: `8081 - Front Axle.ldr`
- **SHA-256:** `3fef02705debc0930762955a5dd92465cb09a2fe4d1f1eccdf7e9d6b20b2699e`
- **Parent:** `8081 - Frame.ldr`, placed at `0 -10 -120` with an identity matrix.
- **DB description (accurate):** "Steerable front axle assembly with suspension
  arms, shock absorber, steering rack, and steering links."
- **Size:** 29 parts, 11 source steps, 2× `8081 - Front Axle S10` hub children.

**Construction:**

- Step 6: suspension arms pivot on a 1×6 Technic brick, with towball ends.
- Step 10: the hub children.
- Step 11: the rack housing `6574` and both steering links.

**What the parent supplies:** the **8T pinion `3647`**, placed in `8081 -
Frame.ldr` on the line after the axle. In axle coordinates it sits at y = −30.
The rack's toothed face is at y = −22, which matches the 10 LDU pitch radius of
an 8T gear. The isolated submodel has a rack and no pinion, which is the gap
seen in the Technic car trial.

**Board:** [`recipes/01-8081-front-axle.json`](recipes/01-8081-front-axle.json).

The isolated home view duplicates step 11, the last step, so the board leaves it
out.

**Review:** kept. A close-up of the mesh was judged unnecessary; the numbers
above settle it.

## 2. Differential rear axle with U-joints, mounted tilted

- **Source:** `42075-1.mpd` :: `42075 - rearaxle.ldr`
- **SHA-256:** `1b44ac7315a873ff5658ccfd75080273fa95d3ce3d541623a2d8feec2ed7bb2c`
- **Parent:** `42075 - vehicle.ldr`, matrix `-1 0 0 / 0 0.932 -0.363 / 0 -0.363
  -0.932`. That is about 21° about X plus a half turn.
- **DB description (accurate):** "Rear axle assembly featuring a differential
  with bevel gears, universal joints, and a multi-link suspension structure."
- **Size:** 63 parts, 8 evenly sized steps (6–12 placements each).

**Construction:**

- Step 3 (back view): the input bevel and U-joint enter the differential in its
  open black frame.
- Step 5: hub frames and outgoing half-shafts on both sides.

**What the parent supplies:** the tilted mount and the body anchor for the shock.
The ghosted parent shows both clearly.

**Board:** [`recipes/02-42075-rear-axle.json`](recipes/02-42075-rear-axle.json).

**Review:** kept; the shock anchoring is clear.

## 3. V8 engine; the crank train is hidden under the cylinder banks

- **Source:** `42050-1.mpd` :: `42050 - engine.ldr`
- **SHA-256:** `35f18ae53fcac3fa08109c468245d7fad4351435437708f7f69048f8586173e6`
- **Parent:** `42050 - Drag Racer.ldr`, tilted about 4° about X.
- **DB description (accurate):** "A Technic V-engine assembly with eight cylinder
  heads, pistons, connecting rods, and dual crankshafts mounted on a 5x3 brick
  base."
- **Size:** 70 parts, 8 steps. The 8 cylinder heads are embedded
  `42050 - 2850b.dat`; they render correctly.

**Construction:**

- Steps 1–2: the frame and the first cylinder bank.
- Step 3: the whole crank train (8 pistons, 8 rods, crankshaft parts; 26
  placements).
- Step 4: the second bank closes over it.

**What inspection adds:**

- The isolated view hides the crank completely.
- The x-ray panel (`xray` layer on `!step:3`) makes every placement outside
  step 3 see-through. It shows the two banks in a V over one crank, which no source view
  shows. This is the case where a see-through copy pays off: a thin shell over
  a few distinctively coloured parts.

**Board:** [`recipes/03-42050-v8-engine.json`](recipes/03-42050-v8-engine.json).

**Review:** kept.

## 4. Technic-to-System SNOT headlight cluster

- **Source:** `42078-1.mpd` :: `42078 - light1.ldr`
- **SHA-256:** `3dc932db5957805ac0aa592c1bdfe16c0da7f17471d54c68335af07539965be1`
- **Parent:** `42078 - tractor.ldr`, with an axis-permutation matrix
  `0 0 1 / 1 0 0 / 0 1 0`.
- **DB description (accurate):** "Brackets and translucent elements forming a
  left headlight assembly."
- **Size:** 20 parts, 4 steps.

**Construction:**

- Step 1, the Technic mount: 2× plate 1×2 with an offset peghole underneath, a
  long axle pin, and a 1×2–1×2 bracket.
- Step 2: trans-clear and trans-orange lens plates on a second bracket.
- Steps 3–4: an inverted curved-slope housing and an axle connector.

**What the parent supplies:** the orientation, and the identity of the part. In
isolation it is an unreadable sideways block. The parent front view shows it as
the left headlight in the bumper.

**Board:** [`recipes/04-42078-headlight.json`](recipes/04-42078-headlight.json).

**Review:** kept.

## 5. Motorcycle primary-drive cover: a sideways round disc on headlight bricks

- **Source:** `10269-1.mpd` :: `10269 - step199-212.ldr`
- **SHA-256:** `c2c1a05aaea52e217d020c6f10452bee081ac65f7815ea16c00d275289eadb6c`
- **Parent:** `10269 - main.ldr`, rotated 90° about Y.
- **DB description (misleading):** "Dashboard and headlight nacelle subassembly…"
  - The parent shows the **left primary-drive/belt cover** beside the footboard.
  - "Headlight" refers to the 1×1 headlight bricks inside it.
- **Size:** 41 parts, 13 steps.

**Construction:**

- Step 8: four headlight bricks give sideways studs.
- Step 11: a 4×4 round plate ringed by four 2×2 corner-round tiles makes the
  disc.
- Step 13: a 45° hinge-arm/angle-connector shift linkage.

**Lesson:** check the parent before trusting a description.

**Board:** [`recipes/05-10269-headlight-nacelle.json`](recipes/05-10269-headlight-nacelle.json).

The isolated home view nearly duplicates step 11, so the board leaves it out.

**Review:** kept.

## 6. Space Shuttle OMS pod: a colour-coded SNOT core under a hinged white shell

- **Source:** `10283-1.mpd` :: `10283 - shuttle-421-451.ldr`
- **SHA-256:** `19bbbc644ca8c24548ffbfd8b483096318864ca0b09d4b4ccceda3352288613f`
- **Parent:** `10283 - shuttle.ldr`, matrix `0 -0.707 0.707 / 0 0.707 0.707 /
  -1 0 0`. That is 45° and on its side.
- **DB description (misleading):** "Shuttle main body structure … complex
  internal framework". It is **one rear OMS engine pod** beside the tail.
- **Size:** 46 placements in 24 steps, plus 5 children (`432`, `433`, `437`,
  `440`, `444`).

**Construction:**

- Steps 1–9 are a core in yellow, black, blue and olive:
  - plates 2×2×⅔ with two side studs;
  - bricks 1×4 with side studs;
  - brackets;
  - a hinge base.
- Steps 10–24 add the white shell:
  - curved panels; child `433` is hinged on the blue hinge base;
  - wedges;
  - wheel rims as engine bells (child `444`).

**Inspection lesson:** a see-through copy did not help. All 38 white parts were
recoloured, including those inside the children, and the layered shell was
still unreadable. Steps 9 and 15 explain the construction. Recolouring a child's
placement line doesn't change parts with explicit colours inside it.

**Board:** [`recipes/06-10283-shuttle-framework.json`](recipes/06-10283-shuttle-framework.json).

**Review:** kept.

## 7. Slave I cockpit pod on a revolute pivot (marked)

- **Source:** `75060-1.mpd` :: `75060 - step84.ldr`
- **SHA-256:** `0bf76c215fe21b44e614fa22d28c655a624b5899c15e6d2996c2b669fd74ddd3`
- **Parent:** `75060 - main.ldr`, rotated 90° about Y.
- **DB description (vague):** "Hinged structural platform … cockpit or canopy
  base". It is the **pilot pod inside the canopy dome**, with Boba Fett tilted
  15°.
- **Size:** 50 parts, 13 steps.

**Construction:**

- Step 1: a 4×4 round plate.
- Step 3: a bracket and a 9-position hinge.
- Step 9: four curved arches loop over the seat.
- Step 11: liftarms and blue axle pins.
- Step 13: 1×6 Technic bricks on both sides.

**The pivot** (the user confirmed that the cockpit rotates):

- The axle half of each `43093` sits in a `74695` liftarm, which is pinned to the
  pod.
- The pin half turns in the centre hole of a `3894` brick.
- The axis runs through (0, −18, 0) along +Z in section coordinates. In the ship
  it runs through (0, −182, −300) along −X, a lateral axis.
- The fixed group is the two bearing bricks; everything else moves.

**How the axis is found** (from connector data, not from the picture):

1. Take each joint part's connector from `./ldraw-agent part`. The `43093` axle
   runs along local X through its origin. The `3894` centre pin hole is at local
   (0, 10, 0), along local Z.
2. Map each connector into section coordinates with its placement line:
   point = position + R · local point; direction = R · local axis.
3. Check that all four lines coincide. The two pins (z = ±80) and the two holes
   (z = ±90) all lie on x = 0, y = −18, along ±Z, with 0.0 LDU offset. The axis
   has no direction, so ±Z is the same axis.
4. The marker centre is their midpoint, (0, −18, 0).
5. For the parent view, map the same line through the section placement:
   (0, −164, −300) + `0 0 −1 / 0 1 0 / 1 0 0` gives (0, −182, −300) along −X.
6. Each pose applies p′ = R(θ)·(p − centre) + centre and M′ = R(θ)·M to every
   part except the bearings.

The recipes hold the centre and direction as constants, derived this way;
recomputing from the connectors gives the same numbers. `./ldraw-xray axes`
proposes such axes, but the recipe states the chosen one explicitly. Coaxial
parts prove the geometry only, not that the joint turns freely.

**How the pivot is marked** (xray layers on synthetic copies):

- **Magenta outline:** the pivot hardware only (pins and bearings), by a
  `highlight` layer on `part:43093|part:3894`.
- **Neon-green rod:** an `axis` layer, a synthetic marker in custom code 9008
  (`#39FF14`), not a LEGO part and not a LEGO colour. In the parent it is a
  thicker rod in ship coordinates.
- **Pose sweep:** a `pose` layer rotates the moving group 0°/45°/90° about the
  axis, bearings fixed. The poses recipe renders all three with one explicit
  camera in `analysis` mode.

**Board:** [`recipes/07-75060-cockpit-base.json`](recipes/07-75060-cockpit-base.json) and [`recipes/07-75060-cockpit-base-poses.json`](recipes/07-75060-cockpit-base-poses.json).

**Limits:** the poses are rigid re-placements. No clearance against the dome was
checked. The marker makes the copies invalid as assemblies; they are for
rendering only.

**Review:** kept. The marking reads clearly, and the three-pose sweep is the
default for moving parts: it plays like a short movie.

## 8. Batmobile bat grille: built flat, stood upright on a pin mount

- **Source:** `7784-1.mpd` :: `7784 - Bat.ldr`
- **SHA-256:** `495724c03f1645d73619cc5c82117027ef0581972b3f84ead27ea3f268a0decf`
- **Parent:** `7784 - Batmobile.ldr`, matrix `1 0 0 / 0 -0.139 -0.99 / 0 0.99
  -0.139`. That is about 98° about X.
- **DB description (misleading):** "angular black vehicle body … bat-shaped
  hull". It is the **front grille/nose**.
- **Size:** 37 parts, 8 steps.

**Construction:**

- Step 1: a 10×9 boat-bow plate, face-down.
- Steps 3–6: wedges and slopes.
- Steps 7–8: a Technic 1×1 brick and a pin/connector mount on the back.

**Lesson:** build a silhouette flat on its studs, then tilt it into place on a
pin mount.

**Board:** [`recipes/08-7784-bat-hull.json`](recipes/08-7784-bat-hull.json).

**Review:** kept.

## 9. Café Corner roof tower: parrot gargoyles and a hinged pyramid roof

- **Source:** `10182-1.mpd` :: `10182 - Second floor - Roof tower.ldr`
- **SHA-256:** `42164d93e442d125195d722cc2e3fa6cc116b2d5c410a2a3bfdeab0b36f54c11`
- **Parent:** `10182 - Second floor.ldr`, rotated 45° about Y onto the corner.
- **DB description:** accurate.
- **Size:** 81 parts, 12 steps.

**Construction:**

- Step 5: four parrots stand in the arch openings as gargoyles.
- Step 9: four hinge 1×2 bases on the cap plate.
- Step 10: a central `Roof tower pillar` child.
- Step 11: four identical `Roof tower roof element` children, each rotated
  about 69° onto a hinge.
- Step 12: a turntable top cap.

**Lesson:** a pitched roof from four identical hinged panels around a pillar.

**Board:** [`recipes/10-10182-roof-tower.json`](recipes/10-10182-roof-tower.json).

**Review:** kept.

---

# SNOT examples

These are found by measuring stud directions over the whole corpus, not by
description. The scan was a one-off script:

- 1,821 annotated MPDs, every section with children flattened;
- for each part, the direction its studs point: `R · (0,−1,0)`.

| Filter | Sections left |
|---|---|
| 15–220 parts and at least 25% of studs not pointing up | 1,918 |
| Also: ≥3 SNOT enablers (brackets, studs-on-side and headlight bricks), ≤35% parts at odd angles, ≤20% Technic, has a parent, ≥4 steps, 20–130 parts, a real description | 273 |

Sections already used by an atlas or example were excluded, and so were the
existing SNOT references (parrot, cat, F40, 6208 B-Wing and Halcyon). The
candidates below were picked from the 273 by hand.

**Extra panels:**

- the **stud-direction map** (`stud_map` layer). Each part is recoloured by where
  its studs point, in section coordinates, with children flattened;
- where a parent is huge, a close-up with an explicit camera on the placement.

**Map palette.** The colours are xray's custom codes 9001–9007. They are
deliberately not LEGO colours: each is ΔE ≥ 16 from every `LDConfig.ldr` colour.

| Studs point | Colour |
|---|---|
| Up | lilac |
| +X | rose |
| −X | vermilion |
| +Z | electric blue |
| −Z | aqua |
| Down | lime |
| Odd angle | violet |

`./ldraw-xray palette` lists the codes and values.

| # | Family | Submodel | Stud directions | Lesson | Recipe |
|---|---|---|---|---|---|
| S1 | Vehicle body | `10298-1.mpd` :: `10298 - front.ldr` | 0 of 63 up | Studs-forward Technic-brick column, tile skin, tilted 23° | [s01](recipes/s01-10298-vespa-front.json) |
| S2 | Vehicle mechanical detail | `21307-1.mpd` :: `21307 - 21307 Step 71-82 Submodel.ldr` | 18 of 37 sideways | Engine with a sideways exhaust manifold made of revolvers (DB says "nose") | [s02](recipes/s02-21307-caterham-nose.json) |
| S3 | Building pattern | `21319-1.mpd` :: `21319 - Steps 110 to 118.ldr` | 0 of 46 up | Floor pattern from plate edges (DB says "wall") | [s03](recipes/s03-21319-central-perk-wall.json) |
| S4 | Round body | `21309-1.mpd` :: `21309 - 16-22.ldr` | 5 per side | Radial clip hub carrying eight spoke panels by their handles | [s04](recipes/s04-21309-saturn-module.json) |
| S5 | Character | `41627-1.mpd` :: `41627 - Yoda.ldr` | 39 of 80 sideways | BrickHeadz face on a side-stud core; head side is a flat panel built separately and turned | [s05](recipes/s05-41627-yoda.json) |
| S6 | Building ornament | `10278-1.mpd` :: `10278 - doorcolumn2f.ldr` | 52 of 53 not up | Sideways stone column; vines on clip bars from handle plates | [s06](recipes/s06-10278-door-column.json) |
| S7 | Building glazing | `10272-1.mpd` :: `10272 - stretford-end-step186-198.ldr` | 48 down in own frame | Glazed wall built in a convenient frame, rotated to +X and tilted 13° (DB says "rooftop box") | [s07](recipes/s07-10272-rooftop-box.json) |
| S8 | Round/conical | `10267-1.mpd` :: `10267 - christmas-tree.ldr` | 11–12 on each of four sides | Four identical faces on a four-sided stud core | [s08](recipes/s08-10267-christmas-tree.json) |
| S9 | Vehicle body | `10258-1.mpd` :: `10258 - roof.ldr` | 20 each ±X | Rounded roof edges from curved bricks on their sides, on 16 brackets | [s09](recipes/s09-10258-bus-roof.json) |
| S10 | Building facade | `21046-1.mpd` :: `21046 - step49-55.ldr` | 21 of 24 sideways | Recessed entrance in a sideways fin facade (DB says "corner") | [s10](recipes/s10-21046-empire-corner.json) |
| S11 | Aircraft control surface | `10226-1.mpd` :: `10226 - step66.ldr` | 15 of 36 +X | Striped tail rudder built sideways on side-stud bricks, handle as hinge point (DB says "radial engine") | [s11](recipes/s11-10226-radial-engine.json) |
| S13 | Animal head | `40412-1.mpd` :: `40412 - Buckbeak - Steps 15 to 35.ldr` | 20 of 59 −Z (face) | Studs-forward face on a hidden colour-coded core (DB says "body and wings") | [s13](recipes/s13-40412-buckbeak-body.json) |
| S14 | Robot character | `21303-1.mpd` :: `21303 - Oeil gauche.ldr` | every direction; 21 angled | Densest mixed-direction SNOT; ribbed hoses as cables; parent turns it 180° and tilts 10° | [s14](recipes/s14-21303-walle-eye.json) |
| S15 | Train underbody | `10183-1.mpd` :: `10183 - 1 - underside details.ldr` | 14 of 28 down | A real upside-down build: inverted curved bricks give a rounded belly | [s15](recipes/s15-10183-underbody.json) |
| S16 | Micro spaceship | `30050-1.mpd` :: `30050 - m-1.ldr` | 28 of 56 not up | Micro-scale SNOT; a wing child turned 90° about Z on a clip | [s16](recipes/s16-30050-shuttle-fuselage.json) |
| S17 | Ship hull | `10294-1.mpd` :: `10294 - Titanic - 2.11.1.ldr` | 93 of 93 up in own frame | Lower hull wall built flat, stood studs +X and angled 9.4°; curved-top bricks make the bilge | [s17](recipes/s17-10294-titanic-hull.json) |
| S17b | Ship hull | `10294-1.mpd` :: `10294 - Titanic - 3.15.1.ldr` | 147 up, 24 +X | Black hull wall built flat; portholes from open-stud plates; 17 counter-rotated child units end up upright | [s17b](recipes/s17b-10294-titanic-hull-cabins.json) |
| S18 | Helmet detail | `75276-1.mpd` :: `75276 - 211-222.ldr` | 17 of 27 −Z | Stormtrooper mouth vent: offset plates centre a grille; a car mudguard is the arch (DB says "mounting module") | [s18](recipes/s18-75276-tie-mount.json) |
| S19 | Animal | `31031-1_Chameleon.mpd` :: `31031 - Cameleon.ldr` | 30 sideways, 14 angled | Flank stripes on side studs; turret eyes from sideways convex slopes; limbs on hinges | [s19](recipes/s19-31031-chameleon.json) |
| S20 | Tree | `21325-1.mpd` :: `21325 - Steps 70 to 90.ldr` | all six directions | Trunk built lying down and stood up 90°; animal tails as roots (DB description empty) | [s20](recipes/s20-21325-blacksmith.json) |
| S22 | Micro spaceship | `10030-1.mpd` :: `10030 - subModel-127.ldr` | 44 of 79 −Z | Micro Tantive IV built sideways along its length on four-sided-stud bricks (DB says "command tower") | [s22](recipes/s22-10030-isd-tower.json) |

S12 (`10241 - step77.ldr`, Maersk) was dropped: it is hidden under the
container stacks. The numbers follow the original candidate numbering.
S21 (`40413 - charlie.ldr`) was dropped: a whole body built studs-forward
overlaps S5 and S13.

**Source hashes (SHA-256):**

| # | Hash |
|---|---|
| S1 | `4e93be56fd86770a2ae7e16ede8110eec5c85aa23297691738fdfe4beba7c185` |
| S2 | `cb81c162429e7c06f2a53f830ba2176aa08c220bc058d05eb3949eb9d8783ac7` |
| S3 | `ce8497bcfd0135029f8d8ebe6dfd0beaa4fdc89fe83652379f815d161c6e7b5e` |
| S4 | `fca920c256ac2ccdfecc6c168f656cdcf3568a1c40c164292ab7f68d8bcbb3e2` |
| S5 | `dcfc71b1af5915d498fdbe595eadd1ee4d1c4db49981e70288e0687bdee6203d` |
| S6 | `708b1d2c15e25bc3a8a44986a2d2a00598ee8de4acd8c60465e8efad7ff33f84` |
| S7 | `aa866e738cc2403e316d8f3bcca85c722e779be0ecd4c3baabba872da26fe082` |
| S8 | `5b02847de56fb081daf87fb98c027055588a4d3da118f41a565082fd8a5fd773` |
| S9 | `160ecddf6c38a4e0b0b8ff97c473c5c7f50f44adc1b787d02cc76d207ff47de0` |
| S10 | `cd8131b740b424668ae6fd447d4069bfb3c58e0db8f4968b265acc83d55f68c5` |
| S11 | `2903c00bd3f1e0af46d47af2e09bd8ccb423eced0588947cc0fb9bd14ac20511` |
| S13 | `6c82cd637cf6def17916abbfb3425836c4cf62549e51668ad9212203d50a56ad` |
| S14 | `c33e5baf1157dd1b68229942103de5c4ee70c46053b66033bb029b007073107b` |
| S15 | `6e8be34eece2b74cfec73957749f3301a217203366ee586a49b86d7588f55177` |
| S16 | `76661f19abe3250f0e0c5f2ff443590926f1a76df3da2e00f227db7426682d01` |
| S17, S17b | `4c016c7c4d24144b38059c39ab8728bafc205a4579fa506290f8eac9d9a0d6b8` |
| S18 | `87bb2655044e2816d87c60214b6497b6fb91d4767cae94adc4ada60be0191059` |
| S19 | `7967458da7624289a6b4728b1ec16b3ebcf1997053515dd21bc748dc49c61a34` |
| S20 | `afc7ccfde6ba9fc47916e11c4e6746416a3c2f0ad87a3f0a448632619504c706` |
| S22 | `b101947efa8e265689470e048d3382728d49336f232f42237758157bb8156358` |

**S4 evidence.** All 8 hub clip centres fall inside `48336` handle plates of the
eight `21309 - 103-107.ldr` panels. This is bounding-box coincidence; the
clip–bar fit is not verified. The user could not tell from the images either;
this measurement is the evidence. The board's last two panels show the hub with
the eight panels from above, inside the ghosted parent: xray has no layer that
removes the rest of the parent.

**Review:** S1–S11, S13–S20 and S22 kept, including both Titanic walls; S12
and S21 dropped. The stud-direction map, in
the non-LEGO palette, is a standing feature.
