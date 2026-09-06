# Verification record

Verified on 2026-09-06 in the supplied macOS workspace with Python 3.14.6, pyldraw3 1.7.0, NumPy 2.5.2, JSON Schema 4.26.0, Poppler, and the installed LeoCAD/semantic GLB converter.

- Mandatory PDF: 171 pages, SHA-256 `7f24cb1a331c56248ee3d8b9b24bc422a77d4b3b5723ba0d82a3d1e9ea4cb08c`. Raw page extraction and search succeeded.
- Official library index: 23,732 top-level part records. Local index creation and the locked `setup.sh` workflow succeeded without modifying the source library.
- Automated suite: **44 passed**, including official-library integration cases. Tests use a miniature independent library for syntax tests and the supplied real library for connectors/example geometry.
- [Bridge plan](../../examples/bridge.plan.json) generated [bridge.mpd](../../examples/bridge.mpd), SHA-256 `e6332f49887916bfb7467d880c902b234b65ce7eec84e0b2adbe924c24364916`. Five leaf placements, 16 reported connector contacts, one optimistic connected component. `validate --geometry --strict` passed with no diagnostics; all five leaf geometries resolved.
- Python and LeoCAD BOMs matched exactly: two 3003 bricks (one blue, one red), two 3022 plates (one blue, one red), and one yellow 3032 plate. LeoCAD home/top/front renders were opened and visually inspected. Cameras are framed from resolved bounds for supported assemblies to keep review images inside the canvas.
- `check-model.sh` succeeded using Python plus LeoCAD snapshot/BOM exports. The workflow makes no LDView snapshot calls.
- `prepare-glb.sh --file` converted the new MPD to a GLB. Its JSON chunk contained eight annotated nodes, including assembly/part descriptions, reference names, colours, and build-step information. No Blender material-intersection analysis was needed or claimed for this small rectangular example.
- Annotated OMR files `106-1.mpd` (65 leaves) and `6712-1.mpd` (38 leaves) parsed in syntax mode without errors. The UNICEF car also completed recursive geometry inspection; its reports retain warnings/review requirements. These checks do not assert that historical OMR transforms meet the stricter new-assembly profile.
- Executed part lookup, palette lookup, PDF lookup, database-backed submodel search, source-section retrieval, BOM, inspection, snap candidates, generation, validation, LeoCAD review, and local-file GLB conversion. Shell syntax, documentation links and `git diff --check` passed.

Reproduce with the commands in [tooling.md](tooling.md) and [README.md](../../README.md). Reports/renders produced during this run are in ignored `output/`; the example plan/source and verification record are retained as repository resources. This record documents the tested scope and does not certify all language extensions, material collisions, connection legality, strength, stability, or real part/colour availability.
