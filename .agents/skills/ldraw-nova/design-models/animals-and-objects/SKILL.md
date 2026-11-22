---
name: animals-and-objects
description: 'Builds animals and small organic subjects with SNOT details: the tropical parrot (SNOT head in seven stages, sideways eyes, jumper offsets, shaped beak) and the cat (diagonal details, compact joints, repeated legs with separately posed paws). Use when the subject is an animal, character or other organic shape.'
---

# Animals and objects

Build animals, characters and other organic shapes: a small SNOT core for the head, details angled around one stud, compact repeatable limbs and posed joints. Two prepared references teach it: the **tropical parrot** (fixed perpendicular SNOT head) and the **cat** (diagonal details and compact joints). Shared principles are in [design-models](../SKILL.md); the parrot head's exact offsets and SNOT seats are worked through in [snot-construction](../../snot-construction/SKILL.md).

For an animal, establish silhouette, pose and expressive features at the chosen scale, and test articulation and support separately. For an object, define its proportions, readable controls and actual seams. Use the references' connections without inheriting their whole appearance.

## Tropical parrot: a SNOT head on a turntable

| Reference | Editable source | Pieces |
|---|---|---:|
| Head: seven stages, one connected group | `examples/parrot/head.plan.json` | 14 |
| Complete bird: body, head, wings, tail and perch | `examples/parrot/parrot.plan.json` | 66 |

```sh
./ldraw-agent review examples/parrot/head.plan.json --outdir output/snot-head
./ldraw-agent review examples/parrot/parrot.plan.json --outdir output/snot-parrot
./ldraw-agent manual prepare output/snot-head/model.mpd \
  --section parrot-head.ldr --outdir output/snot-head-steps --views home back
```

- Two opposing `67329` bricks on a `3679` turntable top form a core with studs up and toward four sides; eyes go on opposite side faces, a curved beak on two jumper studs.
- The full plan `includes` the head plan: place `parrot-head.ldr` as one rigid module and keep its author credit. Its palette is explicit, so a parent colour does not recolour it. The `neck` anchor is an authored positioning frame, not joint validation.
- The body follows printed steps 1–11 with two tail subassemblies; each wing has five stages and an origin at its ball centre; the perch follows steps 21–24. Left and right wings use the correct **handed moulds**, not mirrored transforms.
- The tail rotates on handle/clip axes and the neck on a turntable. Study these joints separately from the fixed SNOT head.
- Source `source.ldr` is credited to **marco9999** (no licence statement; none invented). `preparation.json` records every correction (largest 0.011462 LDU before a common -80 LDU X shift).
- Both reviews pass checks and match BOMs, but **the full bird reports ten automatic connection groups** because of recessed connections the checker misses; `interface-evidence.json` explains them.

## Cat: diagonal details and compact joints

| Study | Editable source | Pieces |
|---|---|---:|
| Face panel, eight stages | `examples/cat/head.plan.json` | 16 |
| Leg with hip socket and ankle clip | `examples/cat/leg.plan.json` | 3 |
| Complete cat, including both studies | `examples/cat/cat.plan.json` | 55 |

```sh
./ldraw-agent review examples/cat/head.plan.json --outdir output/snot-cat-head
./ldraw-agent review examples/cat/leg.plan.json --outdir output/snot-cat-leg
./ldraw-agent review examples/cat/cat.plan.json --outdir output/snot-cat-cat
./ldraw-agent manual prepare examples/cat/head.mpd \
  --section cat-head.ldr --outdir output/snot-cat-head-steps --views home bottom
```

### What transfers to another model

| Construction | Lesson | Possible use |
|---|---|---|
| `35480` round-ended plates, each attached at one end | Rotate around the engaged socket; the free end leaves the stud grid | Diagonal trim, eyebrows, small fins |
| `25269` quarter-round tiles | A single-stud tile can turn within its plane; check surrounding material clearance | Noses, markings, curved corners |
| `15573` jumper over two `60897` clip plates | Centre a detail between stud columns and layer it in front of neighbouring shapes | Muzzles, badges, compact controls |
| `14418` socket plate, `60897` clip and `11477` curve | Keep a repeatable limb rigid between two distinct joint interfaces | Small creatures and articulated figures |
| Two `25214` elbows around a `32062` axle | Form a curved tube from actual keyed parts | Tails and pipe details |

### The face, built flat

The face is authored flat (-Y out of the face, +Z toward the ears, origin at the `3020` plate top) and posed upright by its neck ball joint. The `99781` brow bracket's sideways studs stay exposed and support nothing: this is a companion to SNOT, not a fixed perpendicular stud connection.

| Stage | Construction |
|---|---|
| 1 | Rear inverted curve and neck ball plate |
| 2 | 2 × 4 face plate ties the rear pieces together |
| 3 | Brow bracket |
| 4 | Two corner-cut cheek plates |
| 5 | Round-ended ears and quarter-round tips |
| 6 | Printed eyes cover the ear attachments |
| 7 | Two clip plates suggest whiskers |
| 8 | Centred jumper muzzle and angled nose |

- **Angled ear:** 45° about local Y; engaged socket `[10,8,0]` on support stud `[-30,0,10]` gives origin `[-37.071067812,-8,17.071067812]` from `target - R*socket`. As a seat: `"on": {"to": "face-base", "stud": 1, "socket": 1, "roll": 45}`. Never round the fractional coordinates: that moves the clutch off its stud.
- **Nose:** `yaw: 45`, origin `[0,-32,-30]`, so its socket at local `[0,8,0]` lands on the jumper top `[0,-24,-30]`. A rotated shape still needs clearance from neighbours.
- Build the attachment before decoration covers it: the eyes (stage 6) hide the ear pivots.
- Reuse: include the head plan and place `cat-head.ldr` as one module. Its `neck` anchor is the ball centre `[0,12,-30]`; in the full cat a +90° X rotation faces the panel toward -Z.

### Repeat the leg; pose the paw separately

`cat-leg.ldr` has its origin at the hip socket centre and its ankle clip centre at `[-60,-8,0]`. The full model places four copies with proper rotations, then places each `26047` paw so its bar meets the ankle clip. **Pose a child at its own joint** when its orientation must stay independent: rotating a whole leg-and-paw copy by 180° would turn the paw backward. No part is mirrored. The tail is two elbows on an axle with a towball at each end (one into the body socket).

### Evidence

`source.ldr` names LEGO Digital Designer 4.3 as author (software, not a person; no attribution or licence invented). All three reviews pass checks and match BOMs; head and leg each form one optimistic group, but **the full cat reports four groups** (recessed `14417` sockets and a tail axle crossing the reviewed Technic registry's boundary). Corrections stay under 0.191 LDU; six `3023.dat` aliases became `3023b.dat`.

## Lessons for any organic model

- Start from a small reviewed SNOT core for the head or body, then check the combined model's clearances and support.
- Build the core and its attachments before covering them; use `manual prepare` steps to see them.
- Keep articulation (ball joints, clips, turntables) separate from fixed connections. A plausible pose or coincident joint centre does not establish the movement range.
- Use real handed parts for left/right pairs, and proper rotations for repeated limbs.
- When cleaning a rounded export, recover the module's local grid, re-seat the joint at the pivot, then rotate the whole module; never round angled world coordinates.
- Automatic group counts can be pessimistic around recessed sockets: inspect in the render and record the interface evidence instead of raising tolerances.

## Source docs

Verbatim copies, for details not covered above:

- [examples/parrot/README.md](references/examples-parrot-README.md)
- [examples/cat/README.md](references/examples-cat-README.md)
