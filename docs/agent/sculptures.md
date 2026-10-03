# Optional 3D sculpture workflow

Use this only when the user chooses **3D sculpture** or asks for a voxel sculpture.
It suits statues, characters and organic silhouettes made from ordinary rectangular
bricks. Existing vehicles, buildings, mechanisms and part/submodel designs keep their
usual workflow. Attached images can guide proportions and palette as usual.
Respect the selected Agent/Plan mode and tool permissions; in Plan mode, plan
this route without executing the conversion.

For standalone use, install once with `uv sync --extra sculpture` or
`.venv/bin/python -m pip install '.[sculpture]'`. The companion Docker build installs
this extra. No image-generation service or force-solver license is needed by conversion.

1. Write the usual design brief. Choose a manageable stud resolution, recognizable
   silhouette, palette and connected display base. Coordinates `[x,y,z]` are studs
   in the horizontal plane and **full brick-height layers** vertically, not cubic
   millimetres. Account for the 20:24 aspect ratio when designing round shapes.
2. Generate `output/sculpture.voxels.json` using a reproducible Python generator.
   Format: `{"voxels": [[0,0,0,4], [0,0,1,4]]}`. Colours are explicit LDraw codes
   (4 = red); do not use inherited colour 16 or edge colour 24. Bounds are normalized
   to the ground and input order is irrelevant. At most 65,536 input voxels, 96 cells
   along any axis and 262,144 cells in the bounding grid are accepted.
3. Run `./ldraw-agent sculpture output/sculpture.voxels.json --output output/sculpture.mpd
   --title "My sculpture" --report output/sculpture-checks.json` on one line.
   The fixed-seed BrickBuilder packer uses colour and support heuristics, bridges
   seams and refines connection components. Enclosed cavities can be filled for
   interior reinforcement. It never silently removes disconnected subject voxels.
4. Export succeeds only after checking voxel coverage, non-overlap and a single
   **vertical stud-connected** component. Side-by-side touching bodies alone do not
   connect. The original earliest-supported ordering supplies instruction priorities;
   the connected frontier attaches every next brick to the built assembly, choosing
   below-supported parts before hanging parts. Failure means revise the base/supports
   and rerun; do not bypass the check or substitute an unchecked MPD.
5. Continue the existing checks, rendering, image review and `publish_model` flow.
   Inspect multiple views against the brief. Keep the voxel JSON, generator and
   report alongside the MPD. Ordinary `0 STEP` records drive the existing player.

Determinism applies to identical voxel input, software versions and conversion
settings; AI design is still generative. Connected instructions may include hanging
parts attached from above, reported as `hanging_steps`. Connectivity/support heuristics
are not the force-based analysis in the [Legolization paper](https://dl.acm.org/doi/10.1145/2816795.2818091)
and do not certify load capacity, balance, assembly access or real-world stability.

[Port provenance and retained license](../../ldraw_tools/sculpture/README.md).
