# Validation coverage and repairs

For the authorized [mechanism workflow](mechanisms.md), analytical mechanism verification is deferred. Use `build --contacts none` and `validate --geometry --contacts none` for source-derived mechanism assemblies: normal syntax, references, transforms, duplicate and supported geometry checks remain active; connector analysis is explicitly skipped. Continue BOM comparison and visual inspection. Apply `technic check` only to selected fixed supports, and do not require a whole moving mechanism to satisfy `require_rigid`.

Successful parsing is necessary but insufficient. The tools distinguish file-format checks, constraints for new assemblies, and physical review evidence. `checks_passed` means no reported errors in that selected profile; **it never means a model is proven buildable**.

For [Technic structures](technic.md), normal geometry checks also reject invalid seating, incomplete pin grips and conflicting occupation on reviewed interfaces when contacts are computed. Run `technic check --contract ...` as well to check required mounts, axial retention, connector-before-closure STEP constraints and the conservative multiple-pin restraint rule. Review unknown parts and unsupported bracing patterns. These checks do not simulate mechanisms or prove swept insertion access, strength, stiffness or manufacturing fit.

| Check | Automated behaviour / boundary |
|---|---|
| Types 0–5 and field counts | pyldraw3 parser plus exact field/numeric checks. Invalid type records are errors, even though a viewer may ignore them. |
| UTF-8, BOM, newlines | Reject non-UTF-8/BOM. Warn on non-CRLF input; builder emits CRLF. |
| MPD structure | First main block, duplicate names ignoring case, cycles, preamble geometry, references, ignored NOFILE regions, unused sections. Generated assembly sections use `.ldr`; embedded part/subpart/primitive definitions use `.dat` with an accurate `!LDRAW_ORG` classification. |
| Numbers / matrices | Reject NaN/Infinity and singular matrices. Physical assembly placements require determinant >0 and `M.T @ M` within 1e-4 of identity. Embedded DAT internals permit general nonsingular primitive transforms. No global grid restriction: legitimate SNOT and off-grid rigid placements are possible. |
| Colours | Installed palette lookup, colour inheritance, type-1 edge colour rejection, direct RGB syntax. Custom colour scope, historical dither blending and real inventory availability are not certified. |
| Polygon geometry | Degenerate edges/triangles, concave/crossed/warped quads. Model polygons use a local scale-relative 1e-5 planarity tolerance. Embedded DAT quads use both diagonal normal angles: under 1 degree accepted, 1–3 degrees requires justification (warning), above 3 degrees rejected (PDF p.142). No complete coplanar polygon-overlap or manifoldness checker. |
| BFC | Command combinations, certification placement, INVERTNEXT adjacency. No complete winding/culling certification; render custom geometry with an appropriate authoring tool. |
| Physical part selection | Real library references; reject primitive/subpart placements in assembly profile, warn on aliases/internal descriptions. Library shortcuts and embedded physical DAT parts count as named leaves; internal primitive references do not inflate the scene BOM. Per-document overlays resolve embedded geometry without changing the library. |
| Duplicate placement | Same reference and world transform at 1e-6 precision, across submodels, regardless of colour. An error in assembly mode, a review warning in syntax mode. Different aliases for the same shape require overlap review. |
| Resolved geometry | Expand library parts with source diagnostics; skipped dependencies cannot silently count as complete. Custom model polygons are not included in assembly bounds. |
| Collision | Curated rectangular body envelopes in rigid orientations; AABB candidates refined by oriented-box separation. No general material intersection/containment proof. |
| Connections | pyldraw3's typed connectors, automatically loaded shadows, residuals, provenance/confidence and confirmed/optimistic graphs; see the [frame adapters and coverage](snapping.md). Auto mode computes contacts through 500 placements; larger models explicitly report skipped coverage and null component counts. Scope to modules or use `--contacts all`. Missing metadata, occupied sockets, flexible geometry and mechanical limits require review. |
| `!TEXMAP`, `!DATA`, `0 !:`, local `!COLOUR`, `CLEAR` | Explicit `coverage.*` errors; **unsupported is not synonymous with invalid LDraw**. Use palette colours and real parts for the standard generation workflow. Texture/data in recursively reached library geometry is also flagged. |
| Editor/application metas | Known metadata is retained by the underlying parser, unknown bang commands warn. No promise to execute every application's visibility, camera, animation or instruction extension. Prefer plain STEP/comment metadata. |
| OMR/official library certification | Not performed. New personal models are not automatically OMR-ready or official parts. |

Ordinary filenames containing single spaces and mixed case work. This pinned parser normalizes whitespace inside type-1 filenames; repeated spaces/tabs in filenames are explicitly flagged as unsupported to prevent incorrect resolution. Rename local model sections/references consistently to simple names; do not rename the official library. Portable MPDs should embed their `.ldr` submodels rather than rely on absolute or loose external model paths.

## Repair by diagnostic

| Diagnostic family | Action |
|---|---|
| `syntax.*`, `parse.*`, `number.*` | Use the indicated physical source line. Rebuild the record with all fields; replace nonfinite coordinates; remove prose from operational records. |
| `model.unknown_part`, `mpd.unresolved_submodel` | Search the real library; inspect the variant. Match the exact FILE name for a submodel and include its transitive submodels. Never replace a missing part with an invented ID. |
| `mpd.cycle`, `mpd.duplicate_section`, `mpd.library_shadow` | Give assemblies unique names and an acyclic reference graph. Keep the main block first and avoid library filenames. |
| `matrix.singular`, `assembly.nonrigid` | Recompute a proper rotation using `matrix` or NumPy. Do not “repair” a mirrored asymmetric part by changing its colour or BFC flag. |
| `colour.*`, `model.unknown_colour` | Select a real palette code. Replace unresolved root inheritance with an explicit colour. Colour 24 belongs to edges. |
| `geometry.*` | Fix indicated primitive geometry or unresolved library dependency. Incomplete bounds/contacts cannot justify a pass. |
| `assembly.body_overlap`, `assembly.duplicate` | Inspect the reported instance IDs and source paths. Remove duplicates; recalculate position/origin/stacking height. |
| `assembly.disconnected_evidence` | Check stud parity, upper-body height, mating axes and missing metadata. Explain intentionally separate objects in the delivery notes. Never delete the diagnostic to hide a floating part. |
| `coverage.contacts_skipped` | Select a module and compute contacts, or deliberately request full-scene contacts. Skipped analysis provides no connectivity conclusion. |
| `coverage.*` | Simplify to the supported construction or perform and document the missing external checks. A failed coverage check is not a validation pass. |
| `header.*`, `mpd.unreachable`, `part.alias_or_internal` | Add accurate headers, remove unused assemblies, or inspect the alias/replacement. Preserve original attribution where source is reused. |

If a complex connection remains uncertain, replace it with a simpler inspected assembly and rerun checks. Deliver a specific remaining limitation if it cannot be resolved; do not claim that “the validator guarantees correctness.”

## Large-reference regressions

The [Bookshop audit](complex-models.md) exercises thousands of physical placements, embedded DATs, rounded rotations, reference reuse and a real duplicate. The revised Copper Lane example exercises composition at 1,655 placements. Summary/pagination only reduce report detail. The default expansion budget is 100,000 physical leaves; section selection includes transitive definitions and keeps diagnostic source lines tied to the original file. Neither renderer success nor a matching BOM clears a geometry error. Visual quality has its own [review](visual-design.md), with a design brief and inspected images; it is not inferred from these numeric checks.
