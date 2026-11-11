# Place parts on actual interfaces

Start from the documented construction/recipe, then resolve specific part
questions using [informational sources](part-information.md). Never read or parse
library `.dat` contents directly. Identify exact filenames first; use cached
dimensions to narrow choices and existing tools for interface/geometry evidence.

## Inspect before placing

After identifying a candidate, run `./ldraw-agent part 3001 --limit 30`. It returns actual library metadata, origin-relative bounds, dimensions, stud positions, connectors, provenance, and completeness. Bounds include decorative geometry and stud height; **bounding-box height is not stacking height**. Do not infer axes from the part description alone.

Use `catalog parts QUERY --category NAME` for metadata discovery; general categories are fallible hints. Use `dimensions PART...` for cached extents and request `--measure` on a narrowed catalog query when actual geometry comparison is needed. Category `ldu_y`, `plates_y` and rounded `studs_*` fields describe extents, not connection planes. For example, the supplied `3659` arch cache reports Y=37.41191 LDU while the installed file measures 28. The [visual-design guide](design-models.md) explains selection boards, palettes and supported detail recipes. Reserve openings and overhangs before adding them; a new ornament must be checked in its containing module too.

Standard dimensions and origin conventions are in the [LDraw reference](../reference/ldraw.md#dimensions-and-origins).

Verified against this library, `3001.dat` (2×4 brick) has bounds X=-40..40, Y=-4..24, Z=-20..20. Its body is 24 high, its full bounds 28 high, and its longest dimension is local X. Stud centres are X=-30,-10,10,30 and Z=-10,10, at Y=0.

## Stacking ordinary bricks and plates

For upright standard parts, the **upper part's underside** must meet the **lower part's top body plane**:

```text
y_upper = y_lower - height_of_upper_body
```

A plate placed on a brick at Y=0 goes at Y=-8. A brick placed on that plate goes at Y=-32. Do not subtract the lower part's height or add a 4-LDU gap for the stud. Studs enter the upper part's sockets, so their bounding boxes legitimately overlap.

The plan's `on` field implements this rule for the curated parts in `./ldraw-agent profiles`. `offset_studs: [x,z]` is measured in **the supporting part's local axes**, times 20 LDU. `yaw` describes the new part's orientation in the containing section, independently of the support's yaw. `on` requires an earlier placement ID in the same section and at least one aligned stud grid point. It is not available for unknown part profiles, tiles, slopes, rotated sideways parts, or submodel references; use inspection and explicit `at` coordinates instead.

Half-stud offsets are 10 LDU. A centred 1×1 over a 2×2 needs an X/Z offset to an actual stud, e.g. `[0.5,0.5]`, not `[0,0]`. Side-by-side bricks touching walls have no clutch connection; bridge them with a plate or a correctly mated connector. Place long plates across seams for connected assemblies.

For perpendicular stud grids and shaped-part origins, follow the [SNOT guide](snot.md). Its small parrot head demonstrates exact socket-to-stud alignment, sideways jumper offsets and seven visible construction stages using the same plan format.

## Reuse subassemblies and connection evidence

Search `./ldraw-agent search submodels 'steering' --limit 5`, then inspect the original section with `sections`. Learn its real relative transforms and mating components, but verify names, variants, completeness and annotations. OMR examples are evidence, not proof that every legacy transform is rigid or every annotation accurate. Preserve attribution if copying actual source.

For hinges, axles, wheels and clips:

1. Inspect both parts' connector frames, profile dimensions, kind, occupancy, and source/confidence. Matching visual bounds alone is insufficient. The supplied LDCad shadow metadata loads automatically; inspect its coverage and diagnostics.
2. Put them in a small test MPD. Use `inspect` to obtain stable occurrence indices and current contacts.
3. Run `connectors test.mpd --occurrence 1` to find feature IDs, then `snap test.mpd --moving 1 --fixed 0 --limit 5`. Candidates include world and parent-local poses with collision reports. `--moving-depth 0` moves the whole outer submodel. See the [snapping guide](../reference/connections.md) for filters, application to an MPD copy and reproducible plan snaps.
4. Review candidate collisions, apply the selected pose and rerun assembly checks. Snapping checks moving descendants against stationary parts using body and oriented envelopes. General material intersections, stresses, permitted articulation ranges and strength still need review.

Use actual matching wheel/rim/tyre assemblies from inspected official shortcuts or verified references. Do not invent axle diameters, hinge pivots, or minifigure offsets.

## Module interfaces and large scenes

The [complex-model guide](compose-modules.md) defines named anchor frames, relative plan includes, dependency-closed assets and regular repeats. Anchor alignment composes full rigid transforms and accounts for each module's local origin. It is an authored interface, not automatic connector detection. Keep actual mating studs/holes clear and inspect both modules together.

Use `--section NAME --colour CODE` for a floor, roof or furniture detail. Source line paths remain tied to the input, while occurrence indices restart in the selected frame. Use `--detail full --limit 30 --offset 30` to obtain another instance page. Full-scene summary reports still check all resolved bounds and curated overlaps. Contacts are computed automatically through 500 physical leaves; above that, skipped coverage is explicit. `--contacts none` yields null component counts; `--contacts all` requests the full computation. Embedded physical DAT definitions are geometry leaves for BOM/instance purposes, while their internal geometry is expanded through an isolated document library overlay.

