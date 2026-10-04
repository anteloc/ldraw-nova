# BrickBuilder voxel conversion

The packing heuristics, six-part rectangular-brick catalogue, stud-connection graph,
and earliest-supported instruction ordering are adapted from
[BrickBuilderAI](https://github.com/jjohnson5253/brickbuilderai), commit `220f3fe`.
The original MIT copyright and license are retained in `LICENSE.brickbuilder`.

Shape rasterization and the sculpture design guidance also come from that main
revision's `brick_design.py` and `llmToBricks.py`: ordered box/ellipsoid/cylinder/layer
operations, compact new-build budgets, reference-image guidance, and **no display
base unless requested**. Nova uses its existing selected model and agent tools
for the design/review loop; it does not call BrickBuilder's hosted API or force Opus.

The inside-first support repair is adapted from the user's saved BrickBuilder
worktree snapshot `3fac6df27dc0508b504f1da41275696f9b8dbcfb` (`voxel_support.py` and
`glb2brick.py`). That later repair code is not on main `220f3fe`. It audits actual
vertical stud contacts, tries local/broad interior reinforcement before local/broad
exterior bridges, and repacks/re-audits each candidate. Existing cells/colours are
preserved. The resulting `.repaired.voxels.json` includes accepted additions for
inspection and future agent revisions.

Integration changes: isolate the numerical code from API/storage, Open3D and the
Gurobi force solver; remove inactive debug blocks; retain disconnected geometry
for repair or explicit rejection instead of silently deleting it; sort tie-breakers;
retain hard colour constraints during reconnection; reinforce enclosed interior
cavities; validate bounded input; and gate MPD export on complete
voxel coverage, one stud-connected component, and connected instruction prefixes.
The original reordering supplies priorities; a connected frontier chooses subsequent
steps, preferring support from below before hanging parts. One ordinary LDraw `STEP`
per brick makes the result compatible with Nova's existing player and publications.

This is the current BrickBuilder heuristic pipeline inspired by
[Legolization: optimizing LEGO designs](https://dl.acm.org/doi/10.1145/2816795.2818091),
not the paper's full force-based optimizer or a physical stability certificate.
No alternate assembly engine is used for Nova's existing part-based workflows.
