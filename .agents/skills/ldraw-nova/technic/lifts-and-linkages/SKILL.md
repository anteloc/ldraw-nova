---
name: lifts-and-linkages
description: 'Technic lifts, links and indexed controls: orientation-preserving (parallelogram) lifts, paddles, pawls and indexing, and the surroundings a mechanism needs. Use when building a lifting arm, linkage, lever, ratchet or indexed control.'
---

# Technic lifts and linkages

Build orientation-preserving lifts, linkages, levers and indexed controls (paddles, pawls, ratchets) for platforms, loaders, service hatches and control details. Port placement and checks are in the parent [technic](../SKILL.md) skill. The source case is the Chiron lift and selector studies in `examples/technic-studies/README.md`.

A checked starting plan: `technic-cylinder-lever` in `examples/recipes/` (a pneumatic cylinder raising a lever on a frictionless pin; [write-plans](../../write-plans/SKILL.md)).

## Orientation-preserving lift (four-bar)

The Chiron wing study is a parallelogram: two fixed pivot axes, equal cranks, and a strut carrying the wing between the crank pins. The four sides are nominally **40 LDU in the linkage's YZ plane**, with revolute axes along X. The payload keeps its orientation as the arms rotate.

- **Measure in the motion plane.** One source check reports 72.111 LDU between two points that are also 60 LDU apart along X: that is not the crank radius. Measure from the axis in the motion plane before choosing beam lengths or moving a pivot.
- **The platform follows a shallow arc**, not a straight line: at the 0.4 rad endpoint it moves about (0,-15.863,+0.984) LDU. Design clearance for rise *and* sideways drift.
- Two rear rods of about 120 LDU close onto short links of about 40 LDU. Keep those endpoint relationships and the assembly branch when changing a pose. Never stretch rods or flip the linkage across a toggle to fit a picture.
- The **upper pivot is assumed fixed** in the studied rig; the complete key-driven wing-tilt mechanism is not established. The clearance study (no crossings through 0.40 rad, crossings at 0.45) is source-specific, not a guaranteed range.

For a cargo platform: keep the linkage core, add a real frame that fixes both pivots, lateral support for the wider deck and an accessible actuation interface. This is an adaptation idea that needs its own build and review, not an exported working recipe.

Declare the intended movement with a `mechanism` contract (`pivots`, `dof`) so `build` checks it in the built pose ([technic](../SKILL.md)).

## Paddles, pawls and indexing

The Chiron stepper has a rocking paddle assembly, hinged left/right pawls, a ratchet, knob shafts and rotary catches. Packaging lessons:

- Each pawl pivot travels with the rocker, and the pawl then turns relative to that moving pivot. Keep the real pin joints and room for the return stroke.
- The saved demonstration keys `paddle` and `shift` independently: a paddle stroke alone leaves the ratchet stationary. The driving pawl sweeps about 69.3°, short of a 90° index; detent completion and rubber-band return are assumed with those parts static. An animated sequence is **not** evidence that the pawl advances the catch.
- Keep missing drive, return and detent relations explicit in your report. A directly accessible selector may be easier to adapt than this incompletely studied stepper. Gearbox selectors: [transmissions](../transmissions/SKILL.md).

## The surroundings are part of the construction

- A cutaway helps read pins and link lengths but removes obstacles and sometimes mounts. Compare it with the parent before deciding where a panel, beam, stop or neighbouring shaft can go.
- An MPD section boundary is not necessarily a physical assembly boundary: the Chiron's moving door mirrors sit outside its door FILE sections.
- For a new lift or hatch, list payload, links, pivots, fixed holders, actuator and surrounding frame. Inspect attachments that cross submodel boundaries, then check the whole dressed model.
- Keep the chosen pose and intended action readable without claiming the source's animation coverage applies to the new design. Motion studies proper: [motion-studies](../motion-studies/SKILL.md).

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/mechanism-patterns/lifts-and-linkages.md](references/docs-agent-guides-mechanism-patterns-lifts-and-linkages.md)
