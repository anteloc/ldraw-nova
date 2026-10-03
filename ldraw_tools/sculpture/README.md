# BrickBuilder voxel conversion

The packing heuristics, six-part rectangular-brick catalogue, stud-connection graph,
and earliest-supported instruction ordering are adapted from
[BrickBuilderAI](https://github.com/jjohnson5253/brickbuilderai), commit `220f3fe`.
The original MIT copyright and license are retained in `LICENSE.brickbuilder`.

Integration changes: isolate the numerical code from API/storage, Open3D and the
Gurobi force solver; remove inactive debug blocks; retain disconnected geometry
for explicit rejection instead of silently deleting it; sort tie-breakers; retain hard colour constraints during reconnection; fill
enclosed interior cavities; validate bounded input; and gate MPD export on complete
voxel coverage, one stud-connected component, and connected instruction prefixes.
The original reordering supplies priorities; a connected frontier chooses subsequent
steps, preferring support from below before hanging parts. One ordinary LDraw `STEP`
per brick makes the result compatible with Nova's existing player and publications.

This is the current BrickBuilder heuristic pipeline inspired by
[Legolization: optimizing LEGO designs](https://dl.acm.org/doi/10.1145/2816795.2818091),
not the paper's full force-based optimizer or a physical stability certificate.
No alternate assembly engine is used for Nova's existing part-based workflows.
