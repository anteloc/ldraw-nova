# LDraw records, transforms and specification sources

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

## Dimensions and origins

The PDF's standard dimensions (p.63) are:

| Quantity | LDU |
|---|---:|
| Stud grid pitch / brick unit width | 20 |
| Brick body height | 24 |
| Plate body height | 8 |
| Stud diameter | 12 |
| Stud height | 4 |
| Approximate millimetres per LDU | 0.4 |

The typical studded-part origin is the centre of the top stud group at the **base** of the studs, Y=0; body extends downward toward positive Y (PDF p.143). Hinge origins often lie on the rotation axis. These are generic conventions: inspect the actual file, especially slopes, wheels, hinges, minifigures, brackets and asymmetric parts.

## Specification source map

Authority: [../ldraw-specs.pdf](../../ldraw-specs.pdf), the supplied 171-page compilation. Page numbers below are **1-based PDF pages**, including blank/navigation pages, not printed document numbers. References are grounded in this snapshot; installed `LDConfig.ldr` and `.dat` geometry supply the actual palette and parts available here.

`./ldraw-agent spec --page 65` returns a page. `./ldraw-agent spec 'INVERTNEXT'` searches all pages using case-insensitive AND terms. Reports contain the PDF's SHA-256. The raw Poppler extraction is cached under `.cache/spec-<sha256>.json`, invalidated when the PDF changes. Raw extraction preserves words better than layout mode for this file, but some diagrams and typesetting require opening the PDF itself. The source PDF remains authoritative; extraction is not OCR or diagram interpretation.

| PDF pages | Document / relevant content | Agent use |
|---|---|---|
| 1–11 | Official Library Header Specification; revision 21-Feb-2025 | Header fields, classifications, aliases, licences, BFC and history. Official part submission rules are distinct from personal model conventions. |
| 12–15 | Parts Library Policies and FAQ | Library administration and part review context. |
| 16–18 | Library Sticker Box Standard | Custom sticker part authoring. |
| 19–28 | Official Model Repository Specification | MPD structure and OMR naming/headers; examples pp.22–24. Personal models do not automatically satisfy OMR requirements. |
| 29–30 | OMR rules and procedures | Repository submission and maintenance. |
| 31–47 | Colour Definition Reference | Snapshot palette; query installed `LDConfig.ldr` for executable choices. |
| 48–51 | Common Error Check Messages | Additional official part review diagnostics. |
| 52–56 | Contributor Agreement | Source licensing context; preserve attribution when copying source blocks. |
| 57–60 | Legal information | Distribution context. |
| 61–83 | File Format Specification 1.0.2 | Core syntax. Encoding p.61; whitespace/extensions/CRLF/axes p.62; units and types p.63; transforms pp.64–65; lines/polygons pp.65–67; conditional edges pp.67–68; colours pp.68–70; basic META pp.70–73. |
| 84–90 | `!COLOUR` language extension, revision 01-Apr-2025 | Ordered file/subfile scope p.84; syntax/materials pp.85–87. Custom definitions need external review in this tool's current profile. |
| 91–108 | BFC language extension | Winding/culling states; commands pp.94–96; determinant reversal differs from `INVERTNEXT` pp.97–98. |
| 109–116 | `!TEXMAP` language extension | Texture modes, nested scopes, FALLBACK, NEXT and paths pp.109–112. Requires external review here. |
| 117–124 | `!CATEGORY` and `!KEYWORDS` | Semantic library search metadata and category fallback. |
| 125–129 | MPD and `!DATA` extension, revision 26-May-2020 | Blocks and ignored regions p.125; main block and namespace hazards p.126; data example p.127. |
| 130–137 | Localisation guideline | Translation resources, not part placement rules. |
| 138–139 | `!AVATAR` extension | Viewer avatar metadata; not connection geometry. |
| 140–157 | Official Parts Library Specifications, revision 2.4 | Part naming/case p.140; matrix and numeric rules p.141; angle tolerances p.142; origin rules p.143; duplicates/colour/BFC pp.144–145; shortcuts/flexible/stickers/patterns pp.145–149. |
| 158–171 | Official Library Part Number Specification | Design IDs vs Element IDs p.159; subparts, shortcuts, patterns, stickers pp.159–165. Search actual filenames; never synthesize IDs from appearance. |

Later pages in several ranges contain only navigation, images, or footers. Use the content pages cited above for short retrievals.

The specification describes a geometry language. It does **not** supply a complete connection database, collision solver, inventory of manufacturable part/colour combinations, or structural engineering model. This project's upright rectangular profiles are explicitly curated geometry aids, not statements from the language specification. pyldraw3's inferred connectors retain provenance and confidence.

