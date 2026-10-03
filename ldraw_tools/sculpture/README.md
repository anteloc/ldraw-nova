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
preserved. The resulting `.repaired.voxels.json` includes accepted additions for edits.
The CLI also saves `.sculpture.json` with hashes of the MPD and repaired cells, so
the web app can identify matching editable revisions without trusting a stale design.

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

## Import a colored GLB

`./ldraw-agent glb-sculpture model.glb --resolution 24 --output output/model.mpd`
loads a self-contained glTF 2.0 mesh with Python
[Trimesh](https://trimesh.org/trimesh.voxel.creation.html), using its subdivision
voxelizer instead of BrickBuilder's legacy C++ `obj2voxel`. The color sampling
approach follows BrickBuilder's Python `trimesh_voxelizer.py` in the same saved
worktree snapshot noted above. Mesh instances retain their scene transforms and
individual textures. Closest-surface barycentric UV sampling preserves texture
detail between vertices; material factors and interpolated vertex colors are
mapped by nearest RGB distance to explicit opaque colors in `LDConfig.ldr`.
Materials without colors use light gray. Transparency is converted to opaque
bricks. GLB Y-up becomes sculpture Z-up, with the 24/20 brick-height ratio applied
before voxelization to preserve proportions.

The generated surface cells enter the **same** `conversion.convert` shell-fill,
packing, support repair and connected-step pipeline as sculpture mode. Import
reports include resolution, surface cells, palette colors and dimensions. Matching
repaired voxel and hash sidecars make imports editable in the web app. No LLM,
hosted BrickBuilder API, Open3D, C++ voxelizer or force solver is involved.

Bounds: 16 MB per GLB, 8–48 studs on the longest grid axis, 100,000 triangles
including instances, 200,000 source vertices, 128 scene nodes, 4 megapixels per
embedded PNG/JPEG texture and a 2-million-face subdivision budget. External
resources and required glTF extensions (including compressed meshes) are rejected;
export an uncompressed GLB with embedded textures in the first UV channel. Bake
skinning, morph targets and texture transforms before importing. Imports use the default static
scene pose. Lower resolution or simplify a mesh when limits or connectivity repair
prevent conversion. Fine gradients can produce many tiny bricks because packing
preserves each mapped surface color.
