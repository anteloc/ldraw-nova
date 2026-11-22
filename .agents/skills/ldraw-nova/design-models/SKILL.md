---
name: design-models
description: 'Designs recognizable, varied models from a brief: silhouette and defining parts first, dedicated parts over substitutes, build from the inside out, then revise from the renders. Covers architecture, vehicles, spacecraft, animals, objects and interiors, with subject-specific subskills, plus the mandatory silhouette pass for every vehicle: inspect the outline (ldraw-xray render and mosaic, stud map) and round blocky straight-edged bricks with SNOT curves (curved-top bricks on brackets, triple-curved wedges, curved slopes on side studs, inverted curves) where the subject is rounded. Use when planning what a model should look like and how its masses, palette and modules are laid out, before writing the plan.'
---

# Design models

Decide what a model should look like before writing the plan: its silhouette, masses, functions, palette and focal detail, and which construction lessons to adapt. This skill holds the design principles shared by every subject; the subskills add subject-specific layout, parts and references. How to research lessons and parts: [find-constructions-and-parts](../find-constructions-and-parts/SKILL.md).

## Start from the brief

State, for the requested subject and viewing scale:

- the distinguishing **silhouette** and **major masses**;
- the **required functions** (opening doors, steering, folding wings…);
- the **palette roles** (body, trim, frame, glass, lamps…);
- the **primary detail** that makes it recognizable.

Resolve those choices before adding repeated surface decoration. **Part count is not quality.**

## Construction defaults

- Default to SNOT construction for new models: plan the core and visible surfaces around inspected sideways connections ([snot-construction](../snot-construction/SKILL.md)).
- Combine conventional studs-up System, Technic ([technic](../technic/SKILL.md)) and flexible techniques ([flexible-parts](../flexible-parts/SKILL.md)) where form, structure or function needs them.
- Follow an explicit user construction preference when supplied. The SNOT default chooses an attachment approach; it does not prescribe a silhouette or a template.
- Retrieve construction lessons and examples **before** choosing individual pieces. Use part lookup only for specific details, variants, substitutes or dimensions; do not design by piece-by-piece search, and never inspect raw `.dat` files.
- Search by role, compare different constructions and inspect actual part dimensions. Use one example for a specific lesson; do not inherit its complete proportions or palette.
- Dedicated parts are useful when they fit the brief; brick-built alternatives when they do not. Review shape, support and interfaces together.

## Axes and datums

Keep **X across, -Z forward, negative Y up** for every family. Choose the datum explicitly:

| Family | Y=0 datum |
|---|---|
| Road vehicle | the road |
| Boat | the interior hull floor (not the waterline) |
| Aircraft | the nose floor, in an in-flight display pose (not gear height) |
| Spacecraft | a hull or display-stand datum you choose |
| Motorcycle | measured frame axle spacing and tyre envelope |

Imported source axes may differ: measure the source before rotating or positioning it, and use proper rotations, never mirrored or stretched parts.

## Soften blocky vehicle silhouettes (mandatory)

**Every vehicle** (car, truck, bus, motorcycle, boat, ship, aircraft, spacecraft, including System bodywork on a Technic chassis) gets this pass. Parts with only straight edges and planar faces (bricks, plates, tiles, straight slopes and wedges) give a stepped, boxy outline. Once the construction builds and its first review is open, inspect the silhouette and round off blocky edges with SNOT where the subject is rounded.

### 1. Inspect the silhouette

Judge the outline, not the detail: open the review's front, back, side and top views at thumbnail size. ldraw-xray traces an outline that makes stepped edges easy to see; `mosaic` turns the render into a board:

```sh
bin/ldraw-xray render output/TASK/review/model.mpd --view front --view right --view top \
  -o output/TASK/xray/silhouette-before
bin/ldraw-xray mosaic output/TASK/xray/silhouette-before/manifest.json \
  --output output/TASK/xray/silhouette-before/mosaic.png
bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --stud-map --view home \
  -o output/TASK/xray/NAME-studs
```

The stud map shows which side-stud faces already exist to carry curves. More xray options: [review-and-deliver](../review-and-deliver/SKILL.md). List where the outline reads as stairs or hard corners: nose and tail, roof and shoulder edges, bonnet-to-windscreen and cabin-to-tail transitions, wheel arches and fenders, wing leading edges and tips, nacelles, pods and engine housings, bow, stern and bilge, canopy surrounds, fuel tanks and fairings.

### 2. Decide where rounding makes sense

Round what the real subject rounds; keep square what is meant to be square: box bodies and cargo containers, deliberately faceted or wedge designs, flat functional faces such as doors, decks and ramps, and details too small for the model's scale. Do not trade function for shape: keep wheel and steering clearance, the swept space of moving parts, figure access and every real attachment. Prefer a few large curves on the primary edges to many small ones.

### 3. Round with SNOT

Each curve needs a real stud behind it: a side-stud brick, a bracket, an `under` seat or a jumper offset ([snot-construction](../snot-construction/SKILL.md)). Study the lesson first with `./ldraw-agent knowledge show ID`.

| Blocky feature | SNOT technique | Parts | Lesson |
|---|---|---|---|
| Long body or roof edge | Brackets along the edge, studs out, carry curved-top bricks laid on their sides; tile their flat tops | `6081`, `6091` on `44728`, `2436b`, `99780` | `10258-rounded-roof` |
| Pointed or tapered nose | Studs-up core one stud narrower than the body; triple-curved wedges hung sideways on side-stud bricks; curved and cheese slopes on top; cone tip on an axle | `43712`, `61678`, `54200`, `30414` | `5892-snot-nose` |
| Rounded pod, nacelle or hull top | Two curved slopes back to back along the centreline | `15068` | `halcyon` |
| Curved hull skin over a frame | Technic connectors and axle-hole round plates carry plate skins shaped by curved bricks | `4032a`, `30165`, `30602` | `b-wing-6208#side-shell` |
| Smooth panel or shield | Studs-forward column under a tiled skin, capped by a triple-curved wedge | `99206`, `47753` | `10298-vespa-leg-shield` |
| Ship hull side and bilge | Hull wall built flat in its own section and stood on its side; curved bilge edge | — | `10294-hull-panels#s17-10294-titanic-hull` |
| Chin, belly or overhang | Inverted slope hung under a plate with `under`; inverted curved slopes for a softer edge | `3660b`, `32803` | `recipe-inverted-nose` |
| Engine exhaust or nozzle | Round bricks and dishes on axle-pin supports | `3941`, `4740`, `43093` | `b-wing-6208#exhaust` |
| Small corners and tips | Corner-round and round tiles; round-ended plates turned about one stud | `25269`, `27925`, `98138`, `14769`, `35480` | `cat` |
| Side faces and vertical edges | Curved slopes seated on side studs | `11477`, `50950`, `61678`, `93273`, `24309` on `30414`, `87087`, `52107` | [snot-construction](../snot-construction/SKILL.md) |

- Curved slopes have sockets only under their flat end; the curve overhangs. Read `./ldraw-agent part CODE`, name the `socket`, and check `mated` in the `--report` seats. Choose `roll` so the curve faces outward, and confirm it in a render.
- Build a curved skin as its own module, upright, then seat it with `socket_at` and `roll`. Five plates (40 LDU) equal two studs when sideways and upright grids meet.
- Keep one curve family and palette per surface; tile the flat studs of curved-top bricks and cover bare side studs.

### 4. Check and record

Rebuild and review. Fix new `appearance.exposed_side_studs`, `appearance.deep_overlap` and `assembly.floating_group` warnings, and recheck wheel arches and moving parts. Render the same views again as `xray/silhouette-after` and compare with the before board at thumbnail size; repeat until the primary edges read as intended. Both boards are visual evidence: label the first as an intermediate revision. In the final response, state which edges were rounded and which were deliberately left square, and why.

## Architecture

Use architecture motifs only for buildings. Record massing, storey heights, entrance hierarchy, roof shapes, recessed glazing, supported projections and a legible street/landscape relationship. Keep quieter walls beside focal details. `design details` exports editable architectural fittings (the legacy key `flower-planter` is a tree on a plinth with flower accents, not a low planter). Reserve openings and remove conflicting core geometry before adding fittings. Worked example: [buildings](buildings/SKILL.md).

## Animals, objects and interiors

- **Animal:** establish silhouette, pose and expressive features at the chosen scale; test articulation and support separately ([animals-and-objects](animals-and-objects/SKILL.md)).
- **Object:** define its characteristic proportions, readable controls and actual seams.
- **Interior:** choose a clear activity and furniture scale, with access and headroom where required.

Do not borrow façade motifs or spacecraft machinery simply because a familiar recipe exists.

## Palette and surfaces

- Keep broad surfaces quiet and the primary colour dominant; use smaller roles for shadows, markings, frame, glass, lamps and exhaust.
- Put fine detail (pipes, clips, grilles) in a few recessed areas; leave broad surfaces clean enough to show the silhouette.
- Use real depth (insets, layered edges, recesses, overlaps) rather than thick plate sandwiches at every edge.
- Leave studs only where they support something or contribute deliberately to the LEGO character; cap broad surfaces with tiles or curves.
- `./ldraw-agent design palettes NAME` (e.g. `heritage-racing`) lists palette roles.

## Visual revision

Open whole-model and detail views ([review-and-deliver](../review-and-deliver/SKILL.md)) and ask:

- Is the subject recognizable at thumbnail size?
- Do proportions, quiet surfaces, focal detail and palette support it?
- Are hidden faces, floating details, collisions and parent mounts sound? Check them separately.
- For a vehicle: has the [silhouette pass](#soften-blocky-vehicle-silhouettes-mandatory) been done, with before/after boards?

Record a concrete revision and regenerate final evidence from the same source. Numeric checks do not measure beauty; attractive images do not clear invalid connections. Keep `physical_validity: not_proven` and state untested properties (rolling freedom, strength, figure fit, part/colour availability) where relevant.

## Which subskill

| Subject | Subskill |
|---|---|
| Plane, jet, airliner, glider | [aircraft](aircraft/SKILL.md) |
| Starfighter, freighter, capital ship | [spacecraft](spacecraft/SKILL.md) |
| Car, truck, boat, motorcycle (System) | [vehicles](vehicles/SKILL.md) |
| House, shop, street, interior | [buildings](buildings/SKILL.md) |
| Animal, character, organic shape | [animals-and-objects](animals-and-objects/SKILL.md) |

A Technic vehicle chassis belongs to [technic](../technic/SKILL.md) and its [suspension-steering](../technic/suspension-steering/SKILL.md) subskill. Large models split into modules: [write-plans](../write-plans/SKILL.md).

## Subskills

Read the one that matches your task:

- [aircraft](aircraft/SKILL.md): Builds aircraft in any style: brief and datums, choosing a style, airframe topology (fuselage, wings, tail), moving features such as hinged surfaces, doors and gear, build order with the mandatory silhouette pass (round blocky fuselage, nose, nacelle and wing edges with SNOT curves) and review, using the aircraft family of reviewed real-set studies (examples --family aircraft). Use when the subject is a plane, jet, airliner, glider or other aircraft.
- [spacecraft](spacecraft/SKILL.md): Builds spaceships with a SNOT core and hull skins: identity and scale, comparing at least three construction sources (spaceship list, knowledge search --family spaceship --diversify source, discover search), surfaces in their own local grids, frame-outward build order, attractive detailing, the mandatory silhouette pass that rounds blocky hulls, pods and noses with SNOT curves, and the seven-view review, with two studies that are not templates: the original Halcyon core-and-skin interceptor (spaceship export halcyon) and the 6208 B-Wing basics (Technic fittings carrying System skins, wings on their own grid, cockpit and engines as modules). Use when the subject is a spaceship, starfighter, freighter, capital ship or other spacecraft.
- [vehicles](vehicles/SKILL.md): Builds System vehicles (cars, trucks, vans, buses, boats, motorcycles) with SNOT bodywork: master layout (X across, -Z forward, Y=0 at the road), wheels first, scale and stance decisions, dedicated fittings (vehicle list, vehicle wheels, vehicle details, vehicle plan), inside-out build order, the mandatory silhouette pass that rounds blocky edges with SNOT curves, render-driven revision, plus the Ferrari F40 reference with five small body studies. Use when the subject is a car, truck, boat, motorcycle or other System vehicle (for a Technic chassis see the technic skill).
- [buildings](buildings/SKILL.md): Builds buildings and streetscapes: the Copper Lane parameterized bookshop and house (storeys, roofs, reusable windows, doors, awnings, generate.py with includes) and its visual review, plus how to study a complex real model such as the 10270 Bookshop with the study command before reusing its modules. Use when the subject is a house, shop, modular building, street or interior.
- [animals-and-objects](animals-and-objects/SKILL.md): Builds animals and small organic subjects with SNOT details: the tropical parrot (SNOT head in seven stages, sideways eyes, jumper offsets, shaped beak) and the cat (diagonal details, compact joints, repeated legs with separately posed paws). Use when the subject is an animal, character or other organic shape.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/design-models.md](references/docs-agent-guides-design-models.md)
