# Sculpture conversion

`design.py` turns ordered JSON shapes into colored voxels. `conversion.py` fills
two layers of enclosed interior space, runs fixed-seed rectangular-brick packing
and writes an MPD with supported instruction steps.

`brick_library.py` maps the six allowed footprints directly to LDraw filenames.
`brick_structure.py` tracks voxel occupancy, stud connections and build ordering.
`voxel2brick.py` packs and reconnects bricks using color constraints, seed 42,
`max_failures=100` and `wc=1000`; force stability passes are disabled.

Input bounds, voxel coverage, overlap and stud connectivity are checked before
export. The agent revises unsuccessful designs through the existing tool workflow.
Connectivity checks do not certify physical stability.
