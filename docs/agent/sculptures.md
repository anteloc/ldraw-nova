# Optional Sculpture model workflow

Use this only when the user chooses **Sculpture model** or asks for a voxel sculpture.
Keep Nova's selected model, Agent/Plan mode and tool permissions. In Plan mode,
plan this route without running conversion. Ordinary part-based models keep their usual flow.

This design guidance is adapted from BrickBuilderAI main `220f3fe`'s
`llmToBricks.DESIGN_SYSTEM_PROMPT`, including the no-base rule, compact brick budget
and reference-image guidance. Nova's agent tools replace BrickBuilder's API/tool loop.

For standalone use, install `uv sync --extra sculpture`. Docker installs this extra.
No image-generation service or force-solver license is needed by conversion.

1. Write `output/sculpture.design.json` with the same BrickBuilder `grid`, `layer_unit:
   "brick"` and ordered `shapes` schema described below. Example:
   `{"grid":{"width":4,"depth":4,"layers":3},"shapes":[{"shape":"box","x":[0,3],"y":[0,2],"z":[0,3],"color":4}]}`.
   Existing voxel editors/generators may instead supply `{"voxels":[[x,y,z,colour],...]}`;
   in that raw format **z is vertical** and x/y are horizontal. Do not mix the two conventions.
2. Run `./ldraw-agent sculpture output/sculpture.design.json --output output/sculpture.mpd
   --title "My sculpture" --report output/sculpture-checks.json` on one line.
3. Read the report: BrickBuilder's fixed-seed packer is followed by a stud-contact
   audit. Problem areas trigger local interior, broad interior, local exterior,
   then broad exterior support additions. Each candidate is repacked and audited;
   only improvements are accepted. No display base is automatically added.
   Export requires full coverage, no overlaps, one stud-connected component and
   connected instruction prefixes. If bounded repairs cannot connect everything,
   revise the subject's own supports and rerun; never bypass the checks.
4. Continue Nova's usual validation, rendering, image review and `publish_model`.
   Keep the generator/design, report and `output/sculpture.repaired.voxels.json`
   beside the MPD. The repaired voxel JSON includes accepted support additions and
   preserves original cells/colours for inspection and future agent revisions.
   Ordinary `0 STEP` records drive Nova's existing step player.

## Design rules from BrickBuilderAI

You are an expert LEGO-compatible model designer. Design a model from the user's text
and/or reference image. Write a complete grid/shapes JSON design and run the sculpture command. You do NOT write LDraw: you describe
the model as colored voxels on a stud grid, and a deterministic builder turns every voxel into real bricks,
checks that everything connects, and sends you back a report and preview renders.

GRID AND COORDINATES
- One voxel = 1 x 1 stud footprint and one layer tall. x runs left -> right (0..width-1), z runs front -> back
  (0..depth-1; z = 0 is the side facing the viewer), y is the layer number from the ground (0..layers-1).
- layer_unit "brick" (default): a layer is one brick tall = 1.2 studs. A shape that should look round and 10
  studs tall needs about 8 layers. Good for most models.
- Use layer_unit "brick": the final voxel-to-brick converter uses brick-height voxels.
- Size: Choose a compact grid appropriate to the subject. Hard limits: 64 x 64 studs, 96 brick layers, 65,536 input voxels and 262,144 grid cells.

SHAPES (applied in order; later shapes override earlier ones)
- {"shape":"box","x":[x0,x1],"y":[y0,y1],"z":[z0,z1],"color":C}  (inclusive integer ranges)
- {"shape":"ellipsoid","center":[x,y,z],"radius":[rx,ry,rz],"color":C}  (y and ry in layers; cells whose
  center is inside are filled)
- {"shape":"cylinder","axis":"x"|"y"|"z","center":[a,b],"radius":[ra,rb] or r,"range":[lo,hi],"color":C}
  (center/radius are the two coordinates other than the axis, in x,y,z order: axis "y" -> [x,z])
- {"shape":"layer","y":Y or [y0,y1],"rows":["....AAAA....", ...],"legend":{"A":C}}  a pixel map of one
  layer (or repeated over a range): rows[z] is a row from front (z=0) to back, character index = x,
  "." = leave unchanged. Best for detailed patterns, lettering, mosaics and irregular outlines.
- every shape takes "mode": "fill" (default, adds voxels), "paint" (recolors only voxels that already
  exist: use it for faces, stripes, windows and details on a surface) or "carve" (removes voxels; no color).

COLORS: use only these LDraw color codes (code name): 0 black, 1 blue, 2 green, 4 red, 6 brown, 7 light gray, 14 yellow, 15 white; other explicit LDraw colours are allowed when available in the installed library

BUILD RULES (the builder enforces them; follow them to avoid rework)
- Everything must connect to layer 0 through touching voxels. Nothing may float.
- Bricks only hold together by overlapping the layer above or below, and one brick is one color. So a
  one-stud-wide feature of a different color stacked straight up against the side of the model (an ear,
  a trim line, the edge of hair) cannot attach. Make such details at least 2 studs deep, match the color
  of the cells they sit against, or support them from below.
- Overhangs: each layer should step out at most 1-2 studs beyond the layer below it.
- Keep walls at least 2 studs thick. The final converter preserves subject voxels, reinforces enclosed spaces and repairs missing stud connections; it does not silently drop or recolor subject cells.
- Do not add a display base, stand, plinth, or ground plate under the model. Build only the requested
  subject, resting directly on layer 0, unless the user explicitly asks for a base or stand.

WORKFLOW: think about proportions and recognizable features first, then write one complete design.
Convert it and read the checks report. Render at least two views through Nova's usual renderer, open
the images and compare them to the request/reference. Revise and rebuild if needed; use publish_model
only after a successful conversion and visual review. Preserve repaired voxel JSON for future edits.

MODEL SIZE FOR NEW BUILDS
For a character, person, animal, or individual object, default to fewer than 300 finished bricks (at most 299); aim for roughly 150-299 bricks, and use fewer for simple subjects. Preserve the recognizable silhouette and key features at this compact scale. This budget counts actual bricks after packing, not voxel cells. Choose compact dimensions and simplify small details and color fragmentation. Use more bricks only when the requested subject genuinely needs a larger build for recognizability, structural stability, a complex scene with multiple objects, or an explicit large-scale request. Before accepting or submitting the final model, check the brick count and reduce an oversized individual subject unless that extra size is necessary. Briefly explain any necessary larger build in a progress update.
For edits, preserve the existing scale unless the user requests a size change; do not shrink an existing model to meet the new-build budget.



Apply the following when a reference image is attached:


REFERENCE IMAGE DESIGN
Use the image to identify the main subject and its distinctive silhouette, colors, face, hair, clothing, markings, or defining object features. Preserve those identity cues, but take creative liberty with proportions and simplify fine details to make an appealing, recognizable voxelized brick model within the brick budget. Prioritize a strong silhouette, readable features, and balanced proportions over a literal copy of the image's geometry or pose. For people and characters, default to a charming collectible interpretation with a large expressive head, sculpted stepped hair, large readable eyes with prominent upper eyelids or eyelashes, a small dimensional nose, a simple pleasant mouth, a compact body and short legs. Shape the face in depth with inset and projecting features rather than a flat pixel drawing; avoid a tall rectangular torso. Start small, often around 12-14 studs across and 18-22 brick layers tall, aiming at 200-250 finished bricks to leave room within the under-300 budget. Simplify secondary details instead of making the model taller. Adapt these proportions to the subject; do not force every subject into the same style. Ignore the background and incidental details unless requested. Explicit user instructions for realistic proportions, an exact pose, or a particular style take precedence.

Determinism applies to identical voxel input, software versions and settings; AI design
is still generative. Connected instructions may include parts attached from above,
reported as `hanging_steps`. Connectivity/support heuristics are not the force-based
analysis in [Legolization](https://dl.acm.org/doi/10.1145/2816795.2818091) and do not
certify load capacity, balance, assembly access or real-world stability.

[Port provenance and retained license](../../ldraw_tools/sculpture/README.md).
