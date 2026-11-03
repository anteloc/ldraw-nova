# Review of the prepared parrot

Reviewed 2026-10-21 with the configured official library, pyldraw3 1.7.0, supplied LDCad shadows and LeoCAD. The authoritative editable sources are the two JSON plans. The original supplied LDR is retained without edits.

## Checks

| Evidence | Head | Full parrot |
|---|---:|---:|
| Physical placements | 14 | 66 |
| Source/geometry errors | 0 | 0 |
| Geometry resolved | All | All |
| Python/LeoCAD BOM | Match | Match |
| Automatic optimistic groups | 1 | 10 |

Full review artifacts are in `output/snot-parrot-head/` and `output/snot-parrot/`. The byte-identical reviewed MPDs and selected previews are retained beside this note. `physical_validity` remains `not_proven`; irregular-part material collisions, strength, legal articulation and colour availability are not certified.

The original export's 0.0001 LDU rectangular overlap between `3004` and `3021` is absent after seating the body on its intended planes. Collision tolerances were not changed. Regression coverage retains the original failing case and checks the repaired geometry and inventory.

## Images inspected

- `output/snot-parrot-head/previews/home.png` and `back.png`: opposite eyes, staggered beak supports, rear slopes, crown and exposed turntable stem.
- `output/snot-parrot/previews/home.png` and `top.png`: source silhouette, correctly handed wings, tail connections, perch and preserved wing/foliage poses.
- All seven `output/snot-parrot-head-steps/manual/00/step-NNN-home.png` images: core exposed before covering, jumper offsets before the beak, eye placement and crown sequence.
- Both pages of the official instruction PDF from the assessment: compared the core, body, wing, tail and perch construction.

The finished views preserve the supplied model's appearance. The head's staged views expose the useful SNOT construction. Some rear details are obscured in the home sequence; the final back view and explicit source placements supply the other side. No claim is made that every insertion or material clearance was visually visible.

## Why the full bird still has ten groups

The remaining omitted interfaces have correctly coincident stud bases and authored socket entries. pyldraw3's strict stud check additionally requires entry at an extreme face of the part's overall bounding box. That assumption misses a recessed socket when another part of the same mould extends farther in that direction.

| Interface omitted by that check | Number of mating pairs inspected |
|---|---:|
| `3021` body plate to the two `14704` socket-joint plates | 4 stud/socket pairs across 2 part interfaces |
| Tail wedge plates to `29119`/`29120` curved tips | 2 |
| `2423` leaves to the six `11477` tips | 6 |

[interface-evidence.json](interface-evidence.json) records the ten part interfaces and twelve mating frames, tied to original and prepared occurrence indices. Their entry positions coincide within 0.0000001 LDU and their query axes oppose. Adding these explicitly inspected relationships to the reported graph joins all 66 parts. This is supplementary evidence for this reference, not an override of the automatic graph or a new general collision/connection rule. The tests recompute these relationships from the prepared model and installed metadata.

The head exposed a separate dependency classification issue: deep, closed R 6 underside cavities were labelled pin holes. The adapter now projects only the inspected 36 LDU sockets of `22885`/`67329` and 12 LDU sockets of `47457` to **potential** stud receptacles for queries. Source frames, IDs and library files remain untouched. Tests check upright, sideways and oblique seating, reject other hole profiles/parts, and detect an eye moved off its connection.
