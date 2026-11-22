---
name: engines
description: 'Technic engines and reciprocating constructions: crank-and-connecting-rod engines, cam followers and how to integrate an engine''s appearance, with worked references (single-cylinder piston and crank, 42050 V8 crank train under the cylinder banks). Use when building a piston engine, crankshaft, cam or any reciprocating mechanism.'
---

# Technic engines

Build piston engines, crankshafts and cam followers, for an engine bay or reused as a pump, workshop exhibit or industrial machine. Port placement and checks are in the parent [technic](../SKILL.md) skill. Source cases are the W16 and Defender studies (`examples/technic-studies/README.md`). Choose the actual construction before designing the bay around it.

## Crank-and-connecting-rod engines

The mechanical loop: fixed frame → crank bearing → offset crank pin → rod → piston → fixed cylinder guide. The rod has two moving endpoints and belongs neither to the crank's rigid group nor to the piston. One MPD cylinder-bank section can hold both moving parts and fixed heads.

The Chiron section `42083 - engine.ldr` has **223 physical parts, 16 pistons and three crankshafts arranged 8+4+4** (its annotation wrongly says V8/two crankshafts).

| Feature | Source construction | Preserve during adaptation |
| --- | --- | --- |
| Piston and rod | `2851.dat` and `2852.dat` | Dedicated joints and the rod's pin-to-ball spacing |
| Crank throw | Nominally 10 LDU; central source approximately 9.999701 | Offset from the actual shaft line, not from a part bounding-box centre |
| Rod length | Nominally 40 LDU | Endpoints; never stretch a rod to reach a new cylinder |
| Stroke | Approximately 20 LDU for this centred arrangement | Piston/cylinder envelope and room at both ends |
| Central bank | Four shared pin stations at Z=50,90,130,170 | Two separate rods per station and their individual cylinder directions |
| Lower banks | Repeated sections at occurrences `84` and `85` | Distinct occurrence transforms, crank supports and input gears |

- The lower banks point approximately (-0.8,-0.6,0) and (+0.8,-0.6,0), so equal travel gives different world translations. Reuse proper rotations and the actual opposite-side construction; never reflect or scale physical parts. Give each bank its own identity in a larger model.
- The source pose already encodes crank phase: some pistons start near a dead centre, others between. A universal 0..20 displacement from the imported pose is wrong. Preserve rest rod/piston placements when extracting a bank. The pattern is linkage geometry, not a firing order.
- Sizing intuition for a centred slider crank with throw `r`, rod `L` and angle `a`: the piston ball sits `r*cos(a) + sqrt(L² - r²*sin²(a))` from the crank line along the cylinder axis. Travel is not a sine wave. This is not a solver or a required check; copying the studied pose beats inventing rod angles.

## Single-cylinder piston and crank

From 42048 Race Kart (`42048 - engine.ldr`, 19 placements, 4 steps). Cylinder and mounting cross blocks fix it to the chassis; crankshaft pieces, connecting rod and piston move; an external geared shaft from the kart drivetrain is the input; the piston at the cylinder opening is a display output.

- Keep crank, rod and piston together and preserve their phase.
- The cylinder is an **embedded DAT definition** that must travel with the assembly.
- Inspect the internal steps before mounting the whole engine.

```sh
./ldraw-agent mechanism export piston-crank --outdir output/my-piston-crank
./ldraw-agent build output/my-piston-crank/scene.plan.json --contacts none --output output/my-piston-crank/my-piston-crank.mpd
```

For a compact engine stand, start here or from one W16 bank: keep the crank/piston core, then design a new support frame, accessible input, head clearance and a restrained palette. Removing other banks also removes their supports and drive: replace bearings and mounts deliberately.

## 42050 V8: crank train hidden under the banks

70 parts in 8 steps, one section; source checks pass and BOMs match. Steps 1–2: 5×3 Technic brick frame and first bank of four cylinders. Step 3: the whole crank train (8 pistons, 8 rods, crankshaft ends and centres, 26 placements). Step 4: the second bank closes over it. Steps 5–8: frame brick, cross block, liftarms, a 16-tooth gear, a T-beam. The 8 heads are embedded `42050 - 2850b.dat` parts. The parent `42050 - Drag Racer.ldr` tilts it about 4° about X; how the parent drives the crank was not traced.

- Build the crank train before closing the second bank.
- Keep the embedded cylinder definition (the extracted `source.mpd` carries it).
- The crank was not turned and piston clearance was not checked.

```sh
./ldraw-agent manual export examples/42050-v8-engine --outdir output/my-03-42050-v8-engine
./ldraw-agent build output/my-03-42050-v8-engine/scene.plan.json --output output/my-03-42050-v8-engine/03-42050-v8-engine.mpd
```

Export needs a current visual review. Look it up with `./ldraw-agent discover show submodel-aafc08dae1dd1923fd248597`; replay its board (an x-ray copy shows both banks in a V over one crank) with `./ldraw-xray board run examples/submodel-atlas/recipes/03-42050-v8-engine.json --output output/boards/03-42050-v8-engine`.

## Cam followers

The Defender inline-six uses liftarm cams lifting guided axle followers, with no slider cranks. A drive shaft and idler feed the camshaft; cam eccentricity is 20 LDU and the assumed follower lift 0..10 (values for this example only).

- Phases differ along the bank and one follower starts 10 LDU raised: keep that rest offset and the guides; do not set every follower to the same height.
- The lift law is a surface-contact hypothesis: gravity return, continuous contact and clearance are not established.
- Good for a compact exposed engine or a row of pump heads. Keep guides and stops visible. A different cam shape or follower end is a different construction.

## Appearance and integration

- Expose the parts that explain the mechanism: crank webs, rods and piston heads for a crank engine; cam lobes and guides for a follower engine. Put a quiet frame or removable casing around them.
- Repeated cylinders give visual rhythm without arbitrary extra gears.
- The W16 preview hides fixed heads and frame: it is a cutaway, not a freestanding construction. Add real mounts, keep source attribution, and review the whole engine bay as well as the exposed core.

## Reusing an exported module

`mechanism export` / `manual export` write a `scene.plan.json` that places the module with a proper transform; `source_origin` is a positioning frame, not a connector. Read the manual and parent context first, edit the plan or the bundled `source.mpd`, and inspect the combined model. Operation notes are interpretations: no motion, load or physical operation is certified.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/mechanism-patterns/engines.md](references/docs-agent-guides-mechanism-patterns-engines.md)
- [examples/piston-crank/GUIDE.md](references/examples-piston-crank-GUIDE.md)
- [examples/42050-v8-engine/GUIDE.md](references/examples-42050-v8-engine-GUIDE.md)
