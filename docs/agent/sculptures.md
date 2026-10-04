# Optional Sculpture model workflow

Use this workflow when the user asks for a sculpture model or selects Sculpture Mode.
Design the requested subject as coloured voxels, then use the deterministic converter
instead of writing a custom brick packer or choosing specialist parts. Use Nova's
existing file, CLI and publication tools; there is no separate submission or acceptance loop.

GRID AND COORDINATES
- One voxel = 1 x 1 stud footprint and one layer tall. x runs left -> right (0..width-1), z runs front -> back
  (0..depth-1; z = 0 is the side facing the viewer), y is the layer number from the ground (0..layers-1).
- layer_unit "brick" (default): a layer is one brick tall = 1.2 studs. A shape that should look round and 10
  studs tall needs about 8 layers. Good for most models.
- Use layer_unit "brick": the final voxel-to-brick converter uses brick-height voxels.
- Size: aim for about 28 studs across unless the user requests another size. Hard limits: 64 x 64 studs, 96 brick layers, 65,536 voxels, 262,144 grid cells.

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

COLORS: use only these LDraw color codes (code name): 72 Dark Bluish Gray, 71 Light Bluish Gray, 84 Medium Nougat, 308 Dark Brown, 70 Reddish Brown, 28 Dark Tan, 19 Tan, 85 Dark Purple, 272 Dark Blue, 212 Bright Light Blue, 322 Medium Azure, 321 Dark Azure, 73 Medium Blue, 1 Blue, 330 Olive Green, 323 Light Aqua, 27 Lime, 10 Bright Green, 2 Green, 288 Dark Green, 378 Sand Green, 226 Bright Light Yellow, 14 Yellow, 78 Light Nougat, 191 Bright Light Orange, 25 Orange, 484 Dark Orange, 30 Medium Lavender, 29 Bright Pink, 5 Dark Pink, 26 Magenta, 320 Dark Red, 4 Red, 15 White, 0 Black

BUILD RULES
- Everything must connect to layer 0 through touching voxels. Nothing may float.
- Bricks only hold together by overlapping the layer above or below, and one brick is one color. So a
  one-stud-wide feature of a different color stacked straight up against the side of the model (an ear,
  a trim line, the edge of hair) cannot attach. Make such details at least 2 studs deep, match the color
  of the cells they sit against, or support them from below.
- Overhangs: each layer should step out at most 1-2 studs beyond the layer below it.
- Do not add a display base, stand, plinth, or ground plate under the model. Build only the requested
  subject, resting directly on layer 0, unless the user explicitly asks for a base or stand.

WORKFLOW
1. Explain the intended shape briefly, then use write_file to save a complete grid/shapes
   JSON design under output/. Aim for the user's proportions, colours and brick budget.
2. Run the converter with run_toolkit:
   ./ldraw-agent sculpture output/design.json --output output/sculpture.mpd --title "My sculpture" --report output/checks.json
3. Read the conversion report and call publish_model on output/sculpture.mpd. Nova's normal
   publication flow validates, renders, exports the parts list and creates the chat model card.
4. Reply with the published card_url, final brick count and any unresolved geometry or unmet
   constraint. Do not perform a voxel-preview or visual-revision cycle unless the user asks
   for one. A converter error can be corrected using the normal tools.

The six supported parts are 3001 (2x4), 2456 (2x6), 3010 (1x4), 3004 (1x2), 3005 (1x1)
and 3003 (2x2). These are known rectangular bricks, so part discovery is unnecessary.
Conversion uses two-layer interior fill, fixed-seed color-constrained rectangular-brick packing,
greedy reconnection, supported instruction ordering, and interior-first support repair before
exterior supports. Disconnected and floating bricks are removed. Ordinary 0 STEP records drive
the existing player. Honour requested sizes and brick budgets in your design, but do not claim
a budget was met until the final count is available. Software connectivity checks do not prove
physical strength; the report includes added supports and unresolved voxel counts.

For standalone use, install the optional converter dependencies with `uv sync --extra sculpture`
(or `pip install '.[sculpture]'`) and run the same command. Input can also be
{"voxels": [[x, y, z, LDraw_colour], ...]}, where raw voxel rows use z-up brick-height layers.
