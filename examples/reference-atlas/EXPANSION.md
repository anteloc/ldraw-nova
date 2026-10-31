# Cross-category construction additions

This selection uses the descriptions in `data/ldraw-info.db` to find candidates,
then checks the actual sections and parent placements in `data/models-annotated`.
It complements the existing reference and submodel atlases rather than replacing
them. Source MPDs and the database are not edited.

| Construction | Source | Parts | What it adds |
|---|---|---:|---|
| [Two-axle bogie](rail-bogie/README.md) | 10183 switcher | 22 | Wheelsets, central pivot, buffers and magnetic coupling |
| [Dormer and balcony](dormer-balcony/README.md) | 10270 | 86 | Floor support, door, glazing, railing and sloping roof transition |
| [Aircraft landing strut](aircraft-undercarriage/README.md) | 6745 Harrier alternative | 7 | Compact pin/axle strut and a matched rim/tyre pair |
| [Spacecraft hatch](spacecraft-hatch/README.md) | 924 | 17 | Hull-side hinge dependency and perpendicular engine-cone mounting |
| [Warehouse forklift](warehouse-forklift/README.md) | 6375 | 21 | A complete small vehicle around a dedicated lifting-mast part |
| [Swivel armchair](swivel-armchair/README.md) | 10297 | 7 | Opposing brackets, sideways tiled arms and both turntable halves |

Each guide links an inspection board showing the module highlighted in its
ghosted parent, an isolated home view and an isolated right view. Magenta edges,
ghosting and default inherited colours are inspection aids. The forklift's
ordinary preview inherits the parent's red; its isolated board panels use the
xray renderer's default yellow. Source-local origins are not attachment anchors.

## Discovery and selection

Jev availability was verified with one successful uncached request. Six bounded
semantic searches covered rail bogies, balconies, landing gear, cargo hatches,
cranes and furniture, with four candidates per query, at most 120 physical
placements and one result per parent model. Offline FTS searches for sofas,
armchairs and forklifts filled gaps after the initial candidates proved redundant
or unsuitable. The retained [manifest](expansion.manifest.json) records exact
identities, whole-source hashes, lessons and description corrections.

Two prepared candidates were deliberately excluded:

- `722-1_Factory-and-Truck.mpd` / `722-1 - Crane.ldr`: the opened home render
  shows a detached hook/load assembly without a modeled rope. The building also
  supplies the turntable base. It remains a historical reference, not an addition
  to this reusable selection.
- `42038-1.mpd` / `42038 - canearm.ldr`: contact inspection reports two
  `technic.invalid_transform` errors. No source transform was silently repaired
  or structural check removed to promote it.

Description corrections matter: the bogie has two wheelsets, not a single axle;
the aircraft strut's description asserts retraction that this pose does not
demonstrate; the hatch requires the mating hinge half from its parent. The forklift
uses a complete mast shortcut, not a newly verified lifting mechanism.

## Evidence

All six extracted sources pass the available source and geometry error checks.
All six Python/LeoCAD BOM comparisons match, totalling 160 physical placements.
The six ordinary home previews and all six three-panel context boards were opened.
The other ordinary views are rendered evidence, not claimed as separately inspected.
The cards retain artifact hashes, attribution, extraction changes and diagnostics;
board recipes and provenance are retained beside the images.

The optimistic connection-group counts are respectively **2, 4, 6, 1, 3, 1**.
In particular, the aircraft strut is useful source geometry but has poor automatic
connection coverage. A passing source check does not prove attachment, absence
of material collisions, strength, stability or motion. Read each guide's parent
requirements before composing it into a new model.

## Find, rebuild and inspect

```sh
./ldraw-agent examples --family reference 'bogie'
./ldraw-agent examples --family reference 'hatch'
./ldraw-agent examples --family reference 'furniture'
./ldraw-agent build examples/reference-atlas/swivel-armchair/scene.plan.json --output output/chair.mpd
.venv/bin/python examples/reference-atlas/generate.py --manifest examples/reference-atlas/expansion.manifest.json --outdir output/expansion-refresh --jobs 2
./ldraw-xray board run examples/reference-atlas/swivel-armchair/board/recipe.json --output output/chair-board
```

The exported placement plans rebuild from their local attributed `source.mpd`
files. Refreshing cards or context boards requires the original annotated models.
Fresh cards start with visual review pending: inspect their new images, record
`discover review`, and use `discover example` to export. A saved review note in a
selection manifest is historical evidence, not permission to approve changed images.
