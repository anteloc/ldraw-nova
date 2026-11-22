---
name: design-models
description: 'Designs recognizable, varied models from a brief: silhouette and defining parts first, dedicated parts over substitutes, build from the inside out, then revise from the renders. Covers architecture, vehicles, spacecraft, animals, objects and interiors, with subject-specific subskills. Use when planning what a model should look like and how its masses, palette and modules are laid out, before writing the plan.'
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

- [aircraft](aircraft/SKILL.md): Builds aircraft in any style: brief and datums, choosing a style, airframe topology (fuselage, wings, tail), moving features such as hinged surfaces, doors and gear, build order and review, using the aircraft family of reviewed real-set studies (examples --family aircraft). Use when the subject is a plane, jet, airliner, glider or other aircraft.
- [spacecraft](spacecraft/SKILL.md): Builds spaceships with a SNOT core and hull skins: identity and scale, comparing at least three construction sources (spaceship list, knowledge search --family spaceship --diversify source, discover search), surfaces in their own local grids, frame-outward build order, attractive detailing and the seven-view review, with two studies that are not templates: the original Halcyon core-and-skin interceptor (spaceship export halcyon) and the 6208 B-Wing basics (Technic fittings carrying System skins, wings on their own grid, cockpit and engines as modules). Use when the subject is a spaceship, starfighter, freighter, capital ship or other spacecraft.
- [vehicles](vehicles/SKILL.md): Builds System vehicles (cars, trucks, vans, buses, boats, motorcycles) with SNOT bodywork: master layout (X across, -Z forward, Y=0 at the road), wheels first, scale and stance decisions, dedicated fittings (vehicle list, vehicle wheels, vehicle details, vehicle plan), inside-out build order and render-driven revision, plus the Ferrari F40 reference with five small body studies. Use when the subject is a car, truck, boat, motorcycle or other System vehicle (for a Technic chassis see the technic skill).
- [buildings](buildings/SKILL.md): Builds buildings and streetscapes: the Copper Lane parameterized bookshop and house (storeys, roofs, reusable windows, doors, awnings, generate.py with includes) and its visual review, plus how to study a complex real model such as the 10270 Bookshop with the study command before reusing its modules. Use when the subject is a house, shop, modular building, street or interior.
- [animals-and-objects](animals-and-objects/SKILL.md): Builds animals and small organic subjects with SNOT details: the tropical parrot (SNOT head in seven stages, sideways eyes, jumper offsets, shaped beak) and the cat (diagonal details, compact joints, repeated legs with separately posed paws). Use when the subject is an animal, character or other organic shape.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/design-models.md](references/docs-agent-guides-design-models.md)
