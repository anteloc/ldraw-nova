---
name: spacecraft
description: 'Builds spaceships with a SNOT core and hull skins: identity and scale, comparing at least three construction sources (spaceship list, knowledge search --family spaceship --diversify source, discover search), surfaces in their own local grids, frame-outward build order, attractive detailing, the mandatory silhouette pass that rounds blocky hulls, pods and noses with SNOT curves, and the seven-view review, with two studies that are not templates: the original Halcyon core-and-skin interceptor (spaceship export halcyon) and the 6208 B-Wing basics (Technic fittings carrying System skins, wings on their own grid, cockpit and engines as modules). Use when the subject is a spaceship, starfighter, freighter, capital ship or other spacecraft.'
---

# Spacecraft

Build spaceships: starfighters, freighters, shuttles and capital ships, usually as a SNOT core carrying skins built in their own frames. This skill covers identity and scale, choosing construction sources, surface attachment, build order, detailing and review, with two worked studies: the original **Halcyon** interceptor and the **6208 B-Wing**. Neither is a default design. Shared principles are in [design-models](../SKILL.md); seating on side studs in [snot-construction](../../snot-construction/SKILL.md).

## Establish identity and scale

Decide minifigure scale, a larger display model or microscale. Choose two or three defining masses before small details: an X-shaped wing arrangement, a long engine pair, a broad asymmetric cargo hull, a wedge with a raised bridge. For a named fictional ship, study the specific variant and keep its defining proportions.

Axes: X width (starboard +X), -Z forward, -Y up. Choose a hull or display-stand datum explicitly; a spacecraft has no wheelbase or road plane.

| Family | Main construction decisions | Visual priorities |
| --- | --- | --- |
| Starfighter/interceptor | Central spine, wing roots, cockpit, nacelles and landing/display attachments | Nose/cockpit balance, thin wing edges, engine spacing and a distinct front silhouette |
| Freighter/shuttle | Cargo frame, access corridor, hull panels, ramp, cockpit and landing supports | Hull mass, deliberate asymmetry, readable loading access and restrained weathering accents |
| Capital ship | Internal truss, lower hull, paired upper panels, bridge, trenches and engine block | Large clean outline, layered silhouette, recessed detail and consistent miniature scale |

## Compare construction sources before selecting one

No spacecraft is a default template. Write down scale, silhouette, proportions and defining masses, then **compare at least three different source models** when suitable lessons exist (several sections of one model count as one source; record a smaller pool honestly rather than padding it). For each candidate record the principle it teaches, the role it could serve, scale compatibility and evidence limits.

```sh
./ldraw-agent spaceship list --limit 8
./ldraw-agent knowledge search 'hull attachment' --family spaceship --diversify source --limit 6
./ldraw-agent knowledge search 'wing root' --family spaceship --diversify source --limit 6
./ldraw-agent examples 'cockpit engine' --family spaceship --details --limit 6
./ldraw-agent examples --family submodel --details spaceship
```

Spaceship results interleave sources by default; `--diversify none` restores relevance order for focused study of one source.

| Construction question | Different sources worth comparing |
|---|---|
| Curved or perpendicular hull faces | 6208 B-wing bracket/Technic skins; 10283 OMS pod hinged shell; Halcyon fixed side-stud panels |
| Thin wings and roots | 7191 X-wing root and nacelle; 6208 unequal wings and hinge carrier; 30050 micro shuttle wings on clips |
| Cockpit shape and support | 6887 octagonal enclosure; 6208 canopy pod and offset support arm |
| Small hulls with multiple stud directions | 10030 micro Tantive lengthwise core; 30050 micro shuttle; compare the scale before transferring details |
| Engine and surface detail | 7191 nacelle; 6208 four-nozzle cluster; 75181 armour panel; 10179 service bay |

Submodel atlas entries: 06 shuttle OMS pod (colour-coded SNOT core under a hinged shell), 07 cockpit pod on a revolute pivot, S16 micro wings stood on edge on clips, S22 hull built sideways along its length.

Raw discovery (Jev optional: check availability first, else `--engine fts`). Spacecraft often mix System skins with Technic frames, so `--construction all`:

```sh
./ldraw-agent discover search models 'a detailed Star Wars starfighter with wing and engine submodels' \
  --construction all --min-parts 300 --max-parts 2500 --limit 5
./ldraw-agent discover search submodels 'a spaceship engine nacelle with a cylindrical shell and exhaust' \
  --construction all --max-parts 180 --limit 5
```

Inspect dedicated canopies with their mating rims, printed instrument tiles, seats, control sticks, matched wedge plates, curved slopes, brackets, hinge halves, cylinders, dishes, cones, grilles, bars and clips. Do not invent part IDs or replace distinctive forms with rectangular slabs. After comparing, export only the construction you chose:

```sh
./ldraw-agent spaceship export SELECTED_KEY --outdir output/my-starship/reference
```

An origin frame is not a promised connector. Export stays blocked for inspiration entries with unresolved source errors.

## The Halcyon: a core-and-skin study

The Halcyon is one original core-and-skin study, not a template. Compare it with the other sources above and adapt only the principles that serve the requested ship's silhouette and scale. 195 pieces, 16 modules, 584 × 480 × 140 LDU (about 29 × 24 × 7 studs) without the stand; Y=0 is the keel underside.

```sh
./ldraw-agent spaceship export halcyon --outdir output/my-ship
.venv/bin/python examples/halcyon/generate.py
./ldraw-agent review examples/halcyon/halcyon.plan.json --outdir output/snot-halcyon-review \
  --contacts all --views home front back left right top bottom
./ldraw-agent manual prepare output/snot-halcyon-review/model.mpd --section halcyon-hull.ldr \
  --outdir output/snot-halcyon-steps/halcyon-hull --views home back
```

**1. Core first, exposing its stud faces.** The hull is a plain studs-up stack. One brick course uses fifteen `30414` bricks, each yawed so its studs face the module it carries (unrotated studs face -Z: yaw 0° forward, 180° aft, -90° +X, 90° -X).

| Layer | Top Y | Contents |
|---|---:|---|
| K1–K4 | -8, -16, -24, -32 | Keel plates. K1/K3 and K2/K4 use different seams; K2/K4 bridge the core/pod joint at x=±40 |
| K5 | -40 | Only under the nose cap |
| Side-stud course | -56 | `30414` side studs at Y=-46; plain bricks elsewhere |
| Deck | -64 | Tiles, cockpit floor plate, curved pod tops |

All side studs sit at Y=-46, so flank and pod stripes line up.

**2. Build each skin upright, then turn it onto a face.**

| Module | Local up becomes | Seated on | Contacts |
|---|---|---|---:|
| `halcyon-flank-s/p` | ±X | three `30414` per side, x=±40 | 12 each |
| `halcyon-pod-panel-s/p` | ±X | two `30414` per pod, x=±120 | 8 each |
| `halcyon-intake` (×2) | -Z | one `30414` per pod front, Z=40 | 4 each |
| `halcyon-exhaust` (×2) | +Z | one `30414` per pod rear, Z=240 | 4 each |
| `halcyon-aft-cap` | +Z | centre `30414`, Z=240 | 4 |
| `halcyon-cannon` (×2) | -Z | one `87087` on each wing root | 1 each |

Origins are `stud - R * socket`. Starboard exhaust: `R = [[1,0,0],[0,0,1],[0,-1,0]]` sends local up to +Z; socket `[10,8,-10]` becomes `[10,-10,-8]`; on the stud at `[90,-46,240]` the origin is `[80,-36,248]`. Rotationally symmetric modules (intake, exhaust, cannon) are one section placed twice. The port flank uses the same parts with a different proper rotation and its accent row at local Z=-10: nothing is mirrored. As a plan seat, the starboard flank is `"on": {"to": "hull/flank-mount-0-s", "face": "-Z", "stud": 0, "socket_at": [-110, 0, 10], "roll": -90}`.

**3. Topology.** Stand → 4 studs into K1 underside. Hull → flanks (12 side studs each), pod stripes (8), intakes (4 forward), exhausts (4 aft), aft cap (4 aft), `30384` canopy (4 floor studs). Nose wedges, strakes and wing splices (40 contacts each) are interleaved between keel layers.

**4. Shape without exposed studs.**

| Feature | Construction | Lesson |
|---|---|---|
| Nose | Handed `41769`/`41770` pairs on K1–K5, each 80 LDU long and one stud further forward than the layer below, under a `47753` wedge | Overlap each wedge pair with the next layer's hull plates; the stagger gives a rising chin |
| Strakes | Handed `3933`/`3934` 4 × 8 wing plates at K1 | Fill the gap between nose and wings: a T-shaped plan becomes an arrowhead |
| Pods | `15068` curved slopes back to back along each pod, grey band at the rear | Two curved slopes back to back make a rounded nacelle top |
| Wings | Handed `30355`/`30356` 6 × 12 plates, fully tiled, `44661` tip fins | Choose tiles that reach every stud row; keep the diagonal edge a clean plate edge |
| Tails | Two `2340` on the spine edges, tiled | A symmetric pair avoids a one-stud offset on a 4-wide spine |

A real canopy sets the cockpit width: `30384` is four studs wide on four floor studs.

**Evidence:** checks pass, BOMs match (195), one optimistic contact group from 1,265 contacts; the only warning is `coverage.collision_review` for curved parts. `physical_validity` stays `not_proven`.

**Reuse:** (1) one side-stud height for the whole hull; (2) build and render the core before skins, with a planned module for every stud face; (3) author each skin upright, seat it with `stud - R * socket`; (4) use real handed parts, letting a port section differ in arrangement rather than mirroring; (5) stagger seams inside a module so it holds by itself.

## The 6208 B-Wing: local grids around a hub

A construction-learning study of `6208-1.mpd` (credit Merlijn Wissink [Legolijntje], CCAL 2.0; geometry, rubber-band and mechanism verification deferred; no reviewed manual export). Use `6208 - B-Wing.ldr` for the airframe. **A spaceship does not need one global direction for every stud.**

| Surface role | Source example | Design lesson |
|---|---|---|
| Fixed perpendicular details | `Center Front`: four `44728` brackets in opposing pairs, a `2436a` bracket, `52107` side-stud bricks | Establish the stud faces before adding tiles, fins and slopes |
| Curved skin around a Technic core | `Center Side 2`: `32034` angle connectors, `32062` axles, `6558` pins, eight `4032a` round plates, `3034` plates, `30165`/`30602` curves | Technic attachment → axlehole round plates → broad plate skin → curved surface |
| Angled armour | `Center Front`: `3937`/`6134` hinge pairs | Brackets establish side attachments; hinges establish sloped outer panels |
| Large wing module | `Center Side 1`: four `30540` locking hinge bricks, three `3700`, three `6558`; wings carry `30389b` | Build a thin local wing with a defined root, then orient the whole module in its parent |

- The two smaller wings use real opposite-hand parts (`30355`/`30356`, `47398`/`47397`, `41747`/`41748`); "mirrored" in the annotation describes appearance, not a reflected transform.
- The cockpit pod has its own tub, axle core, controls and `30384` windscreen; its `44728` bracket turns the rear `30367b` dome sideways. In the airframe its local up becomes `-X`: an upright submodel becomes SNOT relative to its parent.
- The exhaust has **four** nozzle stacks (`43093` axle-pin, `3941` round brick, `4740` dish) — the source prose says "twin". Read inventories and images, not descriptions.
- Names like "side" and "top" are local: inspect the parent placement before deciding where a surface faces.

```sh
.venv/bin/python examples/b-wing-6208/generate.py --only front-core
```

## Build from the frame outward

1. Reserve the cockpit, cargo volume, engine envelopes and attachment space.
2. Separate spine/truss, cockpit tub, nose, wing roots, wings, engines, hull panels, service details and landing/display supports; record each module's origin, bounds, mounting parts and dependencies.
3. Choose how each surface changes direction: bracket, side-stud brick, Technic interface or hinge. Build the support before its skin; keep a cutaway view while designing.
4. Long wings and cantilevered engines need a bonded plate stack or braced frame. A bounding box touching the hull is not an attachment: keep a bare-frame or root close-up.
5. Folding wings, ramps or retracting gear need the [technic](../../technic/SKILL.md) workflow and explicit motion checks; a static hinge pose does not show motion.

## Make it attractive

- Keep the primary hull colour dominant; smaller roles for panel shadows, markings, frame, canopy and exhaust. Differentiate mechanical cores from exterior armour.
- Put fine pipes, clips and grilles in a few recessed service areas; leave broad hull and wing surfaces quiet.
- Use real depth: inset cockpits, layered leading edges, thin outer wing edges, recessed trenches, overlapping armour, concentric nozzles. Avoid thick plate sandwiches at exposed edges.
- Repeated engine parts, coherent seams and a few deliberate asymmetries beat uniformly dense decoration. Design the underside, landing feet and display mount with equal care.

## Inspect

Run normal validation and BOM comparison (no car-wheel checks, flight physics or automatic symmetry checks). Render home/front/back/right/left/top/bottom plus exposed frame, cockpit and wing-root views. Judge front/top silhouette, side thickness, rear engines, canopy fit, negative space, detail density and underside supports, and revise after opening the images.

**Mandatory silhouette pass:** where the hull, nose, pods or wing edges still read as stacked boxes, round them with SNOT curves (curved slopes back to back on pods as on the Halcyon, triple-curved wedges hung on side studs for a nose, curved skins on round plates as on the B-Wing), unless the design is deliberately faceted. Procedure, parts table and before/after boards: [design-models](../SKILL.md). Delivery: [review-and-deliver](../../review-and-deliver/SKILL.md).

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/design-models.md](references/docs-agent-guides-design-models.md)
- [examples/halcyon/README.md](references/examples-halcyon-README.md)
- [examples/b-wing-6208/README.md](references/examples-b-wing-6208-README.md)
- [examples/spaceship-atlas/README.md](references/examples-spaceship-atlas-README.md)
