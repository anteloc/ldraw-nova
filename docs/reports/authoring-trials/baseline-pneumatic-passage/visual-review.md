# Visual and fitting review — final revision

All seven final contextual previews were genuinely opened with the image-viewing tool after the hazard-cap revision: `press-review/previews/home.png`, `front.png`, `top.png`, `back.png`, `left.png`, `right.png`, and `bottom.png`. These are observations, not an automated visual score. The seven earlier previews were also opened before the cap revision; only the final images are delivered.

## What was seen

- Home: recognizable workshop press, supported C-frame, extended ram, accessible pump and valve, three distinct hoses, mounted yellow/black guard. The striped cap separates the guard from the black supply hose.
- Top: supply curves around the guard with a visible gap; the red/blue routes run in distinct lanes outside the guard. Pump sleeve is visible on the +Z-facing nozzle. No route passes through the guard.
- Right: all three valve sleeves leave their nozzles in straight, separate runs. Both cylinder sleeves sit against their ports and turn only after the straight departure. The supply loop sits above the bench and clear of the anvil.
- Front: extended rod reaches the pinned press head; red and blue cylinder ends are seated, and the head/die remains above the anvil. The guard and both controls meet the bench without hovering.
- Back: crossbeam and column caps are bonded by the top plate; cylinder mount and head pins are aligned with their rings/Technic holes. Exposed rear has no loose trim.
- Left: pump base rests on the stud grid; its sleeve is straight on the nozzle. Guard base is supported; supply clears its side.
- Bottom: two lower bench plates form a continuous base; the source and upper views show the second layer bridging their seam.

## Actual fittings and mounting

The existing `connectors` CLI was run against final occurrences 36 (pump), 37 (valve), and 31 (cylinder); its world-coordinate reports are delivered. Those reports, the source placements, and the opened images were compared manually. No replacement diagnostic validator was written.

Pump translation is (0,0,-60) LDU, from (-120,-14,-20) to (-120,-14,-80); yaw changes from -90° to -180°, a 90° rotation about the upright axis. Its four bottom sockets are at X=-130/-110, Y=0, Z=-90/-70, on actual bench studs. The generic connector graph labels them pin holes and does not match them to studs; this is a documented metadata gap, not a claim of automated proof.

Valve translation is (+20,0,0) LDU, from (40,-56,-110) to (60,-56,-110); yaw stays -90°. Its two sockets at (50,0,-110) and (70,0,-110) meet the bench studs and both have contact evidence.

Cylinder pose is the starter's extended 74981-f2. Its mount ring is centered at (0,-206,30), rod-end ring at (0,-90,30), with axes along Z. The 40-LDU 3673 pins at (0,-206,40) and (0,-90,40) span Z=20..60: one half in each 20-LDU ring, one half in the beam/head. The matching connholes are not joined by the generic graph, so ring seating remains manual geometric/visual evidence.

The guard remains in the delivered model: two 3001 bricks, envelope X=-80..0, Z=-80..-40, Y=-48..0; four 3069b cap tiles extend it to Y=-56. Eight guard-base stud contacts, eight between its brick courses, and two per cap tile are present in the full inspection report. Guard relocation during repair preserved mounting.

## All six conservative hose obstacle candidates

The full rigid station, including the final guard, was checked at round tube radius 5 LDU with no endpoint exemptions. These are the complete final flex obstacle candidates; all are intended nozzle engagements. Each actual 16-LDU LS22 sleeve was inspected in context and the existing sleeve-to-marker check passed.

| Block / fitting | Actual nozzle base; outward axis | Candidate sleeve end | Review |
|---|---|---|---|
| Supply / pump | (-120,-14,-60); +Z; nozzle length 16 | (-120,-14,-44) | Top, left, back: sleeve covers the nozzle, straight departure; no pump-body crossing. |
| Supply / valve-in | (54,-30,-100); +Z; length 14 | (54,-30,-84) | Right, top: 16-LDU sleeve covers nozzle and extends 2 LDU beyond it; no valve-body crossing. |
| Red / valve-up | (60,-41,-100); +Z; length 14 | (60,-41,-84) | Right, home: upper sleeve seated; red line departs separately. |
| Red / cylinder-top | (10,-196,30); +X; length 16 | (26,-196,30) | Front, right, home: sleeve covers nozzle and clears beam. |
| Blue / valve-down | (60,-19,-100); +Z; length 14 | (60,-19,-84) | Right, home: lower sleeve seated; route clears bench. |
| Blue / cylinder-bottom | (10,-146,30); +X; length 16 | (26,-146,30) | Front, right, back: sleeve covers nozzle; route clears frame. |

There are no final guard candidates in the sampled round-envelope obstacle check. This is finite sampled evidence, not a certified continuous material-clearance proof. At the valve the nearest sleeve-center offset is about 12.53 LDU, greater than the two 6-LDU sleeve radii combined; the actual round tube criterion remains radius 5.

## Assembly warnings and coverage

The full assembly conservative overlap list was read. Stud-stack candidates are the bonded bench layers, columns/caps/top plate, anvil, guard, cap tiles, head and die; their body planes seat at the normal 24/8-LDU pitches. Pump/bench candidates are the four intended sockets spanning two upper plates. Valve/bench candidates are the two intended sockets. Beam/cylinder and head/cylinder boxes only touch at the ring interfaces; their pin candidates are the intended coaxial insertions. Whole-hose bounding boxes also overlap the guard, anvil, head, fittings and each other: opened top/right/home views and the separate sampled route check resolve these overly broad whole-route boxes. No rigid-body penetration error was reported.

The seven optimistic groups are the main rigid structure, cylinder, head/die/pin group, pump, and three posed hoses. Three hose groups have no connector metadata. The pump socket and cylinder ring gaps above explain the remaining disconnected evidence. No strict structural contract was added for unsupported pneumatic interfaces; the supplemental fixed-frame Technic scan passes but covers only one reviewed Technic occurrence and declares zero required joints or insertion constraints. It is not proof of rigidity or mounting completeness.

Physical validity remains `not_proven`: finite sampling, insertion access, clutch/strength, pressure, material elasticity, motion, stock hose lengths, and retail colour availability are not established. The pose is static; the 4-LDU die gap is not a verified loaded operating stroke.

The final full report contains 69 broad-phase overlap candidates; its rows are untruncated. Final physical placements: 47 (44 rigid + 3 posed hoses).
