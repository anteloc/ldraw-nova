# Sculpture conversion

`design.py` turns ordered JSON shapes into colored voxels. `conversion.py` fills
two layers of enclosed interior space, runs fixed-seed rectangular-brick packing
and writes an MPD with supported instruction steps.

`parts.py` maps the six allowed footprints directly to LDraw filenames.
`structure.py` tracks voxel occupancy, stud connections and build ordering.
`packing.py` packs bricks using color constraints and seed 42, then repacks
disconnected regions using the same fixed-seed ordering.

Input bounds, voxel coverage, overlap and stud connectivity are checked before
export. The agent revises unsuccessful designs through the existing tool workflow.
Connectivity checks do not certify physical stability.
