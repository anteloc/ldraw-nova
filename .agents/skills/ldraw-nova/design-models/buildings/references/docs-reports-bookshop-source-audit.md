# Bookshop source audit

Preserved from the former complex-model guide during the 2026-11-03 knowledge-base migration. Counts and diagnoses below refer to that recorded source revision.

## 1. Study structure before geometry

```sh
./ldraw-agent study data/models-annotated/10270-1.mpd --report output/bookshop-study.json
```

`study --detail full` reports the FILE hierarchy, direct versus expanded physical counts, reuse counts, reachability, local steps, authors/licences, frequently used parts, BOM, source hash, and validation findings. The default `study` summary limits section/diagnostic rows to 30 (`--limit`); use full detail when saving a complete inventory. It is an **informational** command: exit 0 does not mean `source_checks_passed` is true. A `.dat` definition is a physical-part boundary for scene traversal; its primitives contribute geometry, not separate BOM pieces. A library shortcut can still represent several manufactured elements.

The measured [Bookshop inventory](resources/bookshop-study.json) is tied to the supplied source's SHA-256. It contains 42 definitions: 25 assemblies and 17 embedded DAT definitions. The main scene reaches 39 definitions and 2,456 physical placements of 245 distinct reference names. Two minifigure blocks are empty and unreachable; the aeroplane is also unreachable. The descriptive annotation mentioning two minifigures is therefore not evidence that the main scene contains them.

Useful starting modules, with their exact FILE names:

| FILE name | Physical placements | What to study |
|---|---:|---|
| `10270 - Stair Step.ldr` | 4, instantiated 17 times | Repeat a small local construction with different rigid transforms. |
| `10270 - Window-1.ldr` | 14, instantiated twice | A framed window as a reusable façade detail. |
| `10270 - Bookshelf-1.ldr` | 15 | Small interior module and part palette. |
| `10270 - Pendulum_Clock.ldr` | 27 | A detailed object inspected independently from its room. |
| `10270 - Building-1_Second_Floor.ldr` | 342 | Floor envelope, furnishings, stairs, and their shared coordinate frame. |
| `10270 - Building-1_Roof.ldr` | 242 | Roof modules, decorative subassemblies, and orientation. |
| `10270 - Building-2_First_Floor_Balcony.ldr` | 86 | An interface with a separately placed building storey. |

Read a section with `sections FILE --section NAME`. Retrieve a bounded geometry report with `inspect FILE --section NAME --colour 15 --detail full --limit 30`. Some source sections have validation errors; extract an explicitly repaired review copy when needed.

## 2. Learn from references without inheriting their problems

This annotated Bookshop has 18 comments between `BFC INVERTNEXT` and its target line, violating PDF p.96. It also has 215 nearly rigid placement matrices rounded to three decimals, exceeding the new-assembly tolerance. Its embedded part quads are within the ordinary **less than 1 degree** tolerance; both diagonals must be measured (PDF p.142). These are different issues and require different handling.

Create a dependency-closed copy of a useful module:

```sh
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Pendulum_Clock.ldr' --namespace ref-clock \
  --output output/assets/clock.mpd
```

Read the returned `root`; use that exact reference when importing the asset. The adjacent `.manifest.json` records the original source/hash, FILE renames, authors/licences, edits, and output hash. Original bytes remain unchanged. Repeated imports need distinct namespaces. Keep the manifest beside the asset, and preserve copied authorship/licences.

For a review copy of the entire Bookshop:

```sh
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Complete.ldr' --namespace bookshop \
  --repair-bfc-comments --normalize-rotations \
  --output output/bookshop-reference.mpd
./ldraw-agent inspect output/bookshop-reference.mpd --detail summary --contacts none \
  --report output/bookshop-inspection.json
```

`--repair-bfc-comments` only moves annotation comments ahead of INVERTNEXT. `--normalize-rotations` uses an SVD projection to a proper rotation only for assembly matrices whose maximum orthogonality error is above 1e-4 and at most 0.002, with positive determinant. Every before/after matrix is recorded. This is an explicit approximation for reviewing rounded legacy rotations, not proof of original design intent; inspect the result. Larger scale/shear and reflections remain unchanged and fail the assembly check.

Extraction writes a review artifact even when syntax checks fail and then returns 1. It does not silently delete bad placements. In this Bookshop, the repaired copy exposes a duplicated `3010.dat` at world `(148,-129,0)` in the townhouse ground floor. Its geometry check correctly fails. Do not treat this reference as a golden physically valid fixture.

The [submodel atlas](../../examples/submodel-atlas/README.md) records, for 30 real sections, what the parent supplies and where the database description is wrong. Its building entries include a hinged corner roof (10), a patterned floor (S03), a clipped-vine column (S06), a glazed wall built in its own frame (S07) and a recessed entrance (S10).

