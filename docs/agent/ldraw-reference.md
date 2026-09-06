# LDraw reference for model-generating agents

Read this before writing source. Full authority and page links are in [specification-map.md](specification-map.md).

## Use the assembly workflow

Build new models from existing official `.dat` **physical parts**, referenced by type 1 records. Group reusable assemblies in uniquely named embedded `.ldr` blocks inside a single `.mpd`. Prefer `./ldraw-agent build` with a JSON plan; it writes the transform fields, headers, steps, and MPD boundaries for you. Reuse of classified embedded DAT definitions is supported through dependency-closed assets. Those definitions retain their polygons, internal primitive transforms, BFC and authorship; only complete physical placements must be rigid. Creating new primitives/subparts still needs a separate part-authoring review.

Write UTF-8 without BOM and CRLF newlines. Blank lines are allowed. Fields are separated by spaces/tabs. Type 1's filename is the entire remainder after its 12 numeric transform values; ordinary spaces in names are allowed. For portability use simple ASCII names with single spaces or hyphens. Never quote a type 1 filename. `!TEXMAP` filenames use different quoting rules.

## Line records (PDF pp.63–68)

| Type | Syntax | Meaning |
|---|---|---|
| 0 | `0 // explanatory text` | Comment. The first ordinary line of a section is its title; follow with headers. |
| 1 | `1 colour x y z a b c d e f g h i filename` | Place referenced part or submodel. |
| 2 | `2 colour x1 y1 z1 x2 y2 z2` | Straight edge between endpoints. |
| 3 | `3 colour x1 y1 z1 x2 y2 z2 x3 y3 z3` | Filled triangle. |
| 4 | `4 colour x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4` | Filled convex planar quad, vertices ordered around perimeter. |
| 5 | Same field count as type 4 | Conditional edge: first two points are endpoints; last two are visibility control points, not surfaces or collision geometry. |

New model source normally needs only types 0 and 1. Triangles cannot have collinear vertices. Quads cannot be concave, twisted, crossed (bow-tie), or have collinear corners. Break such shapes into valid triangles. Custom polygons and library primitives need additional part-authoring review.

## Transforms and coordinates (PDF pp.62–65)

Right-handed coordinates, **negative Y is up**. All translations are in LDraw units (LDU).

```text
M = [[a,b,c], [d,e,f], [g,h,i]]
p_world = M @ p_local + [x,y,z]
M_world = M_parent @ M_child
t_world = M_parent @ t_child + t_parent
```

For identity use `1 0 0 0 1 0 0 0 1`. `./ldraw-agent matrix y 90` returns `[[0,0,1],[0,1,0],[-1,0,0]]`: it sends local +X toward world -Z. This is an active rotation, not a camera angle. For composed rotations order matters. Use matrix multiplication, not addition of Euler angles. Complete physical parts need proper rigid rotations; scaling, shear, and reflection may render but do not correspond to the original physical part.

The general language permits scaling/mirroring, especially when constructing parts from primitives. The assembly profile deliberately rejects these on physical model placements while permitting them inside embedded DAT definitions. A negative determinant and BFC inversion have different meanings; do not insert `INVERTNEXT` to compensate for a mirrored complete part.

## Colours (PDF pp.68–70,84–87)

Use `./ldraw-agent colours 'blue'` to choose a code from the installed palette. LDraw codes are not BrickLink, LEGO Element ID, or RGB values.

- `16` means **inherit the referring record's current colour**. It is not Pearl Dark Grey or a fixed visible colour. Use it inside reusable colourable submodels; explicitly colour the parent placements until every visible leaf has a defined colour.
- `24` means the **edge colour associated with the current colour**. It is intended for type 2/5 edges. Never use it for type 1 placements; avoid it on filled faces.
- `0x2RRGGBB` is an opaque direct RGB colour, with uppercase hexadecimal letters. Valid language syntax, but prefer palette codes for model generation. A renderable colour does not establish that LEGO manufactured that part in that colour.
- Custom `!COLOUR` definitions have ordered scope through the defining file and its descendants. They must not redefine reserved codes 16/24. The checker marks local definitions as requiring external review rather than silently applying incorrect global scope.

## MPD structure (PDF pp.125–127)

```text
0 FILE example-main.ldr
0 Example with a red reusable assembly
0 Name: example-main.ldr
0 Author: Generated for this workspace
0 !LDRAW_ORG Model
1 4 0 0 0 1 0 0 0 1 0 0 0 1 example-module.ldr
0 NOFILE
0 FILE example-module.ldr
0 Reusable colourable brick
0 Name: example-module.ldr
0 Author: Generated for this workspace
0 !LDRAW_ORG Model
1 16 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
0 NOFILE
```

The first block is the main model; subsequent blocks appear only through references. Definition order after the main block does not determine draw order. Each `FILE` name must be unique ignoring case. Avoid collisions with any official part or primitive name, including `stud.dat`. Library subparts use paths such as `s\3001s01.dat`, primitives such as `48\...` use `p/48`; these belong inside part definitions, not as arbitrary substitute bricks.

`NOFILE` is optional at the end of a block; it is required to delimit trailing non-LDraw content. Content after `NOFILE` is ignored until the next `FILE` or `!DATA`. Text preceding the first block is discarded, but geometry there is an error. An MPD can contain binary image data in `!DATA` blocks with `0 !:` base64 lines; generation/analysis of these blocks is currently outside this tool's supported profile.

`0 STEP` **ends** a building step. Put it between installation groups. Steps inside submodels are local; the parent's reference installs the whole subassembly. Semantic descriptions should explain what an assembly does, and placement comments should explain what the part contributes.

## BFC and other metadata

BFC controls winding and back-face culling, not mechanical connectivity. At most one explicit `CERTIFY [CCW|CW]` / `NOCERTIFY` declaration belongs before operational lines and other BFC commands. `INVERTNEXT` applies only to the immediately following subfile record, permitting intervening blank lines but no comment. It is for part/subpart construction; do not use it on complete physical parts. Library part geometry already carries its own BFC metadata (PDF pp.94–98).

Keep model titles, `Name:`, `Author:`, and `!LDRAW_ORG Model` accurate. Preserve licences/authors on copied OMR or unofficial part blocks; do not falsely label new work as official, invent release tags, or assert a licence for someone else's source. The builder leaves `!LICENSE` out unless the plan supplies an authorized value. An original model does not need OMR set naming unless OMR publication is explicitly requested.
