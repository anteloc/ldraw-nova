# BrickBuilder sculpture conversion

The shape rasterizer, six-part rectangular-brick catalogue, fixed-seed packing,
stud-connection graph and supported instruction ordering are adapted from
[BrickBuilderAI](https://github.com/jjohnson5253/brickbuilderai), main `220f3fe`.
The original MIT copyright and license are retained in `LICENSE.brickbuilder`.

This adapter follows the design route in `llmToBricks._convert_design_voxels`:
existing design voxels skip mesh voxelization, receive two layers of enclosed
interior fill, and use color-constrained `Voxel2Brick` packing with seed 42,
`max_failures=100`, `wc=1000`, hard surface-color constraints and force stability
passes disabled. Its reconnection pass uses soft color constraints, as BrickBuilder
does.
Nova writes an MPD with ordinary build steps and rejects incomplete or disconnected
results so the agent can revise its design. There is no editor or GLB import.

Integration changes remove API/storage and unused force-solver dependencies,
resolve local imports, bound inputs and sort packing tie-breakers. AI design and
review continue through Nova's existing selected model and tools.
Connectivity checks do not certify physical stability.
