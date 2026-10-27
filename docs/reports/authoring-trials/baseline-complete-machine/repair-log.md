# Repair log

1. Initial no-render review failed: supply bend radius 6.328 LDU, cylinder-route clearance 8.005 LDU. Added a wide supply return waypoint and moved the upper cylinder route into a separate outer lane. Limits remain min_radius=15, tube_radius=5, min_separation=10.

2. Review after repair 1 passed bend checks but the cylinder lines crossed near the valve (2.736 LDU separation). Restored the proven lane ordering and translated the cylinder-side waypoints upward by the full 48 LDU gantry change.

3. The second route correction still failed clearance (6.298 LDU) and created a 14.257 LDU bend. Changed the hardware layout: pump and valve now sit on actual 48-LDU plinths, restoring the reference valve-to-cylinder relative geometry. The supply return moves upward with its fittings.

4. Opened all seven complete-machine views. Found the front orange tile row overhanging the bench by one stud; aligned it with the bench. Side-view/source inspection found the original stop plate intersected the upper chain run by 4 LDU. Raised the gantry and both control plinths by 16 LDU, translating the accepted hoses unchanged, and widened the stop plate to 4x4 so its underside is 8 LDU above the straight-run studs. Added a stud-seated tan workpiece 11 LDU before the stop. Replaced moved 3023 aliases with 3023b and equivalent 10-LDU half-bushes with the inspected, structurally reviewed 32123a variant. Added a scoped shaft-support companion and required-joint contract. The exploratory whole-machine Technic check was inapplicable because it deliberately rejects gears/pneumatic parts; its bearing and retention evidence was read, then the final check was scoped to the actual shafts, bearings and retainers as directed by the workflow.

5. Final connector-frame review found that the legacy 569 sprockets' real cross-axle holes are rolled 45 degrees in the XY plane. Rotated each shaft, its keyed bushes and the crank together by 45 degrees about Z, leaving both shaft axes, bearing positions and sprocket/chain geometry unchanged. This preserves the supported dimensional stack and aligns the axle keys with the inspected sprocket holes.
