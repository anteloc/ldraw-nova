---
name: ldraw-format
description: 'LDraw records, transforms and specification sources: line types 0-5 syntax, transform matrices and coordinates, colours, MPD structure (0 FILE, 0 NOFILE), BFC and other metadata, dimensions and origins, and where each rule is in the bundled specification PDF. Use when reading or checking an .ldr or .mpd file by hand or reasoning about rotations, colours or MPD sections.'
---

# LDraw format

The LDraw facts an agent needs when reading or checking `.ldr`/`.mpd` output by hand: line records, transforms, colours, MPD structure, BFC and headers, standard dimensions, and where each rule lives in the bundled specification PDF. Plans normally generate all of this for you ([write-plans](../../write-plans/SKILL.md)).

## Line records (PDF pp.63–68)

| Type | Syntax | Meaning |
|---|---|---|
| 0 | `0 // explanatory text` | Comment. The first ordinary line of a section is its title; follow with headers. |
| 1 | `1 colour x y z a b c d e f g h i filename` | Place referenced part or submodel. |
| 2 | `2 colour x1 y1 z1 x2 y2 z2` | Straight edge between endpoints. |
| 3 | `3 colour x1 y1 z1 x2 y2 z2 x3 y3 z3` | Filled triangle. |
| 4 | `4 colour x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4` | Filled convex planar quad, vertices ordered around perimeter. |
| 5 | Same field count as type 4 | Conditional edge: first two points are endpoints; last two are visibility control points, not surfaces or collision geometry. |

New model source normally needs only types 0 and 1. Triangles cannot have collinear vertices; quads cannot be concave, twisted, crossed or have collinear corners.

## Transforms (PDF pp.62–65)

Right-handed coordinates, **negative Y is up**, translations in LDU.

```text
M = [[a,b,c], [d,e,f], [g,h,i]]
p_world = M @ p_local + [x,y,z]
M_world = M_parent @ M_child
t_world = M_parent @ t_child + t_parent
```

- Identity is `1 0 0 0 1 0 0 0 1`.
- `./ldraw-agent matrix y 90` returns `[[0,0,1],[0,1,0],[-1,0,0]]`: it sends local +X toward world -Z. It is an active rotation, not a camera angle.
- Composed rotations: multiply matrices; never add Euler angles. Order matters.
- Physical parts need proper rigid rotations (determinant > 0). The assembly profile rejects scaling, shear and reflection on placements (they are allowed inside embedded DAT definitions). A negative determinant is not fixed with `INVERTNEXT`.

## Colours (PDF pp.68–70, 84–87)

`./ldraw-agent colours 'blue'` picks a code from the installed palette. LDraw codes are not BrickLink, LEGO Element ID or RGB values.

| Code | Meaning |
|---|---|
| `16` | Inherit the referring record's current colour. Use inside reusable submodels; colour the parent placements explicitly so every visible leaf resolves. |
| `24` | Edge colour of the current colour, for type 2/5 edges. Never on type 1 placements. |
| `0x2RRGGBB` | Opaque direct RGB (uppercase hex). Valid, but prefer palette codes. |
| `!COLOUR` | Custom definition scoped to its file and descendants; must not redefine 16/24. Flagged for external review by the checker. |

A renderable colour does not prove LEGO made that part in that colour.

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

- The first block is the main model; others appear only through references. Definition order does not set draw order.
- `FILE` names are unique ignoring case and must not collide with official part or primitive names (including `stud.dat`).
- `NOFILE` is optional at block end; content after it is ignored until the next `FILE` or `!DATA`. Text before the first block is discarded, but geometry there is an error. `!DATA` blocks (`0 !:` base64) are outside the supported profile.
- `0 STEP` **ends** a building step. Steps inside submodels are local; the parent's reference installs the whole subassembly.
- Library subparts (`s\3001s01.dat`) and primitives (`48\...`) belong inside part definitions, not as substitute bricks.

## BFC and headers (PDF pp.94–98)

- BFC controls winding and back-face culling, not connectivity. At most one `CERTIFY [CCW|CW]` / `NOCERTIFY` before operational lines. `INVERTNEXT` applies only to the immediately following subfile record (blank lines allowed, no comment between). Do not use it on complete physical parts.
- Keep titles, `Name:`, `Author:` and `!LDRAW_ORG Model` accurate. Preserve licences/authors on copied blocks; never label new work as official or assert someone else's licence.
- The builder omits `!LICENSE` unless the plan supplies one. The example above is **not** a delivery-ready header: AI-generated models need the `[AI-GENERATED] ` title prefix, `0 Author:`, `0 !LICENSE CC-BY-NC` plus its comment line and `0 !KEYWORDS AI, AI-generated` in every generated section, delivered as `ai-NAME.mpd`, named after the model (e.g. `ai-ford-mustang.mpd`) ([review-and-deliver](../../review-and-deliver/SKILL.md)).

## Dimensions and origins (PDF p.63, p.143)

| Quantity | LDU |
|---|---:|
| Stud grid pitch / brick unit width | 20 |
| Brick body height | 24 |
| Plate body height | 8 |
| Stud diameter | 12 |
| Stud height | 4 |
| Approximate millimetres per LDU | 0.4 |

The typical studded-part origin is the centre of the top stud group at the **base** of the studs (Y=0), with the body extending toward +Y. Hinge origins often lie on the rotation axis. These are conventions: check the actual part with `./ldraw-agent part CODE`, especially slopes, wheels, hinges, minifigures, brackets and asymmetric parts.

## Specification lookup

Authority: `docs/ldraw-specs.pdf` (171 pages). Page numbers are **1-based PDF pages**.

```sh
./ldraw-agent spec --page 65
./ldraw-agent spec 'INVERTNEXT' --limit 4
```

`spec` searches all pages with case-insensitive AND terms and reports the PDF's SHA-256; extraction is cached under `.cache/spec-<sha256>.json`. Diagrams need the PDF itself.

| PDF pages | Content |
|---|---|
| 1–11 | Official Library Header Specification (headers, classifications, aliases, licences, BFC, history) |
| 12–18 | Library policies and FAQ; sticker box standard |
| 19–30 | Official Model Repository Specification (MPD structure and OMR naming; examples pp.22–24) and rules |
| 31–47 | Colour Definition Reference (snapshot; query installed `LDConfig.ldr`) |
| 48–60 | Common error check messages; contributor agreement; legal |
| 61–83 | File Format Specification 1.0.2: encoding p.61; whitespace/CRLF/axes p.62; units and types p.63; transforms pp.64–65; lines/polygons pp.65–67; conditional edges pp.67–68; colours pp.68–70; META pp.70–73 |
| 84–90 | `!COLOUR` extension (scope p.84; syntax pp.85–87) |
| 91–108 | BFC extension (commands pp.94–96; determinant reversal vs `INVERTNEXT` pp.97–98) |
| 109–116 | `!TEXMAP` extension |
| 117–124 | `!CATEGORY` and `!KEYWORDS` |
| 125–129 | MPD and `!DATA` extension (blocks p.125; main block and namespaces p.126) |
| 130–139 | Localisation; `!AVATAR` |
| 140–157 | Official Parts Library Specifications 2.4: naming p.140; matrices p.141; angle tolerances p.142; origins p.143; duplicates/colour/BFC pp.144–145; shortcuts/flexible/stickers/patterns pp.145–149 |
| 158–171 | Part Number Specification (design vs element IDs p.159; subparts, shortcuts, patterns pp.159–165) |

The specification is a geometry language. It supplies no connection database, collision solver, part/colour availability or structural model; this project's upright profiles are curated aids. Never synthesize part IDs from appearance: search actual filenames.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/reference/ldraw.md](references/docs-agent-reference-ldraw.md)
