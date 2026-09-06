# Mandatory specification: source map

Authority: [../ldraw-specs.pdf](../ldraw-specs.pdf), the supplied 171-page compilation. Page numbers below are **1-based PDF pages**, including blank/navigation pages, not printed document numbers. References are grounded in this snapshot; installed `LDConfig.ldr` and `.dat` geometry supply the actual palette and parts available here.

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
