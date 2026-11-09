# Orchestrator's own roof defect list (written 19:0x, BEFORE reading the auditor's report)
Images: before-iso/panels/01-home-view.png, 02-front-view.png, 04-top-view.png (delivered model sha 9c55ea54…).
Unverified visual suspicions, to be checked against geometry later.

| id | where | suspicion |
|---|---|---|
| O1 | stair-house | projects ~2–4 studs beyond the BACK edge of the 24×16 footprint (top view) — contract violation, overhangs the back façade |
| O2 | chimney | straddles the right parapet; pot/stack appears to extend past X +12 (top view) |
| O3 | corner piers / urns | white piers + round urns at the front corners stick out sideways beyond X ±12 (top/front view) |
| O4 | pediment | white cap plate over the pediment protrudes forward past the cornice line (top view) — beyond Z -9? and reads as a loose slab in front view |
| O5 | planters | "plants" are 2x2 round bricks — read as green/yellow barrels, not plants |
| O6 | bistro set | chairs are dark minifig seats, read as unidentifiable dark shapes under the pergola |
| O7 | pergola | posts unclear at the front-left; slats may rest on beams only at one end (needs check) |
| O8 | urn caps | 6141 round plates floating (known from contacts) |

## Geometry check of my own suspicions (19:06)
`inspect --section roof.ldr` on the delivered model: section bounds X -240..240, Z -180..160, Y 0..-204, and
**0 parts** have bounds outside X ±240 / Z -180..160. So O1, O2, O3 and O4 (envelope protrusions) are
**false positives**: LeoCAD's "top" view is a perspective camera, so tall objects (stair-house, chimney, piers,
pediment) look as if they spill outward. Lesson: never call an envelope violation from a top render alone;
confirm with bounds. O5–O8 remain open (aesthetic / contacts).
