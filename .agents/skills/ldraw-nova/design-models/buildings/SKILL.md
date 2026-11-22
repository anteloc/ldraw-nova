---
name: buildings
description: 'Builds buildings and streetscapes: the Copper Lane parameterized bookshop and house (storeys, roofs, reusable windows, doors, awnings, generate.py with includes) and its visual review, plus how to study a complex real model such as the 10270 Bookshop with the study command before reusing its modules. Use when the subject is a house, shop, modular building, street or interior.'
---

# Buildings

Build houses, shops, modular buildings, streets and interiors: plan massing and storeys, compose floors and roofs as anchored modules, give façades a focal feature, and learn from a complex real model without inheriting its defects. Shared design principles (including the architecture checklist) are in [design-models](../SKILL.md); anchors, includes and generators in [write-plans](../../write-plans/SKILL.md).

## Plan the building

- Record massing, storey heights, entrance hierarchy, roof shapes, recessed glazing, supported projections and the street/landscape relationship. Keep quieter walls beside focal details.
- Start with the street/base, then separate each floor, façade detail, roof, interior and landscaping into modules. Keep the main section short enough to read in one screen.
- Reserve openings (window bays, doors, dormers) before adding fittings, and remove conflicting core geometry first.
- `design details` exports editable architectural fittings.

## Copper Lane: a parameterized streetscape

`examples/copper-lane/`: an original botanical bookshop (three storeys, tan/green) beside a two-storey sand-green townhouse, with green-and-white awnings, a gold BOOKS sign, arched flower windows, embossed masonry, a dormer, a stepped clock pediment, layered leaf trees and fluted lamps. Five furnished storeys lift off for access. 1,655 placements resolve without errors and the BOMs match. It is an original example, not a recreation of set 10270.

```sh
.venv/bin/python examples/copper-lane/generate.py
./ldraw-agent build examples/copper-lane/scene.plan.json --output output/copper-lane.mpd --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

- **Structure:** `scene.plan.json` places the street and buildings; `buildings.plan.json` defines storeys and roofs; `details.plan.json` defines reusable windows, doors, furniture and landscaping. Paths in `includes` are relative to the declaring plan.
- **Generator:** `generate.py --floors 4 --outdir output/four-storeys` makes a four-storey shop and three-storey house. Edit the generator for persistent changes; direct JSON edits are overwritten when regenerating. It uses the shared detail recipes (`ldraw_tools/details.py`), palette roles (`ldraw_tools/data/design-palettes.json`) and `@category.Symbol` / `@colours.Name` values.
- **Storey anchors:** a storey's `base` is its floor-plate underside at Y=8 and `next` the cornice top at Y=-160, so each attachment advances 168 LDU. Each arch replaces reserved wall cells; the dormer replaces conflicting roof slopes; the awning's two-row support beam meets real slope sockets.
- **Limits:** floors lift off, with no stairwell or minifigures; interiors are simple reading rooms (bookcase and table repeated in every floor). The open area above each front frame is an unglazed arch. `detail-flower-planter` is actually a small layered tree on a flowered base. Isolated roof sections render yellow from colour inheritance; the parents are blue and red.

### Decisions made from the renders

| Observed weakness | Revision |
|---|---|
| Front walls read as repeated brick grids with small openings. | Reserve six-stud window bays, use real arch/frame/pane parts, project the sills and cornice, and confine embossed masonry mostly to lower courses. |
| The roofs had little individual character. | Cut a dormer opening into the bookshop's slope layout; give the house a stepped clock pediment and a different roof colour. |
| The shop did not read clearly from the street. | Add tall display glazing, green-and-white awnings and a sign above them. |
| The first sign's two white page tiles looked like a blank plaque. | Search the categories for patterned book tiles, open a LeoCAD shortlist, and use the actual metallic-gold BOOKS tile on the side-stud mounts. |
| One-piece tree candidates looked mechanically ribbed. | Build four foliage layers on round trunks, vary leaf orientation and tree height, and use small flowers at the base. |
| Exposed side walls looked blank in the home view. | Reserve openings for two vertical window pairs per storey on each exposed side. Keep the party walls solid. |
| The first awning beam did not meet the slopes' underside sockets. | Replace it with a two-row beam: its front row mates the sockets at local Z=-20 and its rear row attaches to the cornice. |

Lesson: geometry passing is only the starting condition. Give each building a different identity (palette, roof silhouette, focal fitting) and connect them with shared rhythm (arch proportions, flower accents). Choose your own focal feature and detail vocabulary for a new model, and review its renders afresh.

### Review at three scales

```sh
./ldraw-agent inspect output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --contacts all --detail summary --report output/ground-inspection.json
./ldraw-agent render output/copper-lane.mpd --section lane-ground.ldr --colour 19 \
  --outdir output/ground-review --views home top
./ldraw-agent validate output/copper-lane.mpd --geometry --detail summary
```

Detail (window, hinge, one angled roof joint) → module (a floor or roof with `--section` and `--colour`; renders of extracted floors expose rooms a closed exterior hides) → scene (whole assembly, cross-module overlaps, BOM, several views). Whole-scene contacts are skipped automatically above 500 placements; collision coverage is then incomplete.

## Learn from a complex real model: the 10270 Bookshop

Study structure before geometry:

```sh
./ldraw-agent study data/models-annotated/10270-1.mpd --report output/bookshop-study.json
```

`study --detail full` reports the FILE hierarchy, direct vs expanded counts, reuse, reachability, steps, authors/licences, frequent parts, BOM and validation findings (default summary limit 30 rows; `--limit`). It is informational: read `source_checks_passed`. The Bookshop has 42 definitions (25 assemblies, 17 embedded DATs); the main scene reaches 2,456 physical placements of 245 distinct references.

| FILE name | Physical placements | What to study |
|---|---:|---|
| `10270 - Stair Step.ldr` | 4, instantiated 17 times | Repeat a small local construction with different rigid transforms. |
| `10270 - Window-1.ldr` | 14, instantiated twice | A framed window as a reusable façade detail. |
| `10270 - Bookshelf-1.ldr` | 15 | Small interior module and part palette. |
| `10270 - Pendulum_Clock.ldr` | 27 | A detailed object inspected independently from its room. |
| `10270 - Building-1_Second_Floor.ldr` | 342 | Floor envelope, furnishings, stairs, and their shared coordinate frame. |
| `10270 - Building-1_Roof.ldr` | 242 | Roof modules, decorative subassemblies, and orientation. |
| `10270 - Building-2_First_Floor_Balcony.ldr` | 86 | An interface with a separately placed building storey. |

Read a section with `sections FILE --section NAME`; bounded geometry with `inspect FILE --section NAME --colour 15 --detail full --limit 30`.

**Do not inherit its problems.** The annotated Bookshop has 18 comments between `BFC INVERTNEXT` and its target line, 215 placement matrices rounded to three decimals, and a duplicated `3010.dat` at `(148,-129,0)` in the townhouse ground floor. It is not a physically valid golden fixture.

```sh
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Pendulum_Clock.ldr' --namespace ref-clock \
  --output output/assets/clock.mpd
./ldraw-agent extract data/models-annotated/10270-1.mpd \
  --section '10270 - Complete.ldr' --namespace bookshop \
  --repair-bfc-comments --normalize-rotations \
  --output output/bookshop-reference.mpd
./ldraw-agent inspect output/bookshop-reference.mpd --detail summary --contacts none \
  --report output/bookshop-inspection.json
```

- Use the returned `root` name when importing; keep the `.manifest.json` (source hash, renames, authors/licences, edits) beside the asset. Repeated imports need distinct namespaces.
- `--repair-bfc-comments` only moves comments ahead of INVERTNEXT. `--normalize-rotations` projects matrices with orthogonality error above 1e-4 and at most 0.002 to proper rotations, recording each change: an explicit approximation, not design intent. Larger scale/shear and reflections stay and fail.
- Extraction writes a review artifact even when checks fail, then returns 1.

Real-set building entries in the submodel atlas: 10 hinged corner roof, S03 patterned floor, S06 clipped-vine column, S07 glazed wall built in its own frame, S10 recessed entrance (`./ldraw-agent examples --family submodel`).

## Source docs

Verbatim copies, for details not covered above:

- [examples/copper-lane/README.md](references/examples-copper-lane-README.md)
- [examples/copper-lane/visual-review.md](references/examples-copper-lane-visual-review.md)
- [docs/reports/bookshop-source-audit.md](references/docs-reports-bookshop-source-audit.md)
