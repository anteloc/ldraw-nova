# Build and review an LDraw model

Deliver the requested model as an editable `.mpd`, its reproducible source, checks, parts list and inspected previews. Match the requested subject, scale, palette, features and complexity. Correct geometry and good visual design both matter.

## 1. Start with a design

Run `./ldraw-agent doctor` from the repository root; run `./setup.sh` if needed. Set `LDRAW_DIR` (or `LDRAWDIR`) to the installed parts library. LeoCAD must be on `PATH` for previews. Keep new work under `output/`; leave the parts library and supplied `data/` resources unchanged.

Write a short brief: silhouette, dimensions, palette, focal feature, supporting details and build order. For a large model, split it into modules with clear origins, envelopes and attachment surfaces. Reserve space for interfaces before adding decoration. Choose a recognizable subject and state the scope if none was supplied.

Start with relevant examples and inspect unfamiliar parts:

```sh
./ldraw-agent examples --family building
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
./ldraw-agent part 3001
./ldraw-agent design palettes
```

**Spaceships use SNOT by default.** Follow the [Halcyon](examples/snot/halcyon/README.md) for construction and visual quality: a supported core, attached sideways hull skins, axial engine modules, smooth contours and thin wing edges. Make SNOT part of the main exterior design. Adapt this approach to each ship's own silhouette and scale; upright internal frames are still appropriate.

When the user provides an allowed-parts CSV, choose only its exact LDraw part/color pairs and honor any `max_quantity` limits. Use `build --parts-palette CSV` for JSON plans, or check a generated MPD with `python -m ldraw_tools.catalog_inventory MODEL LIBRARY --palette CSV`. Repair every violation before delivery. Do not create custom geometry, change part dimensions or override library DAT definitions to imitate an allowed part.

Use the appropriate guide as the design requires it:

| Task | Guide |
|---|---|
| Shape, palette, detail and image review | [Visual design](docs/agent/visual-design.md) |
| Plans, placements and Python generation | [Plan guide](docs/agent/plans.md) |
| Large models and reusable modules | [Module workflow](docs/agent/complex-models.md) |
| Sideways studs, SNOT cores and offsets | [SNOT](docs/agent/snot.md) |
| Vehicles or spaceships | [Vehicles](docs/agent/vehicles.md), [spaceships](docs/agent/spaceships.md) |
| Fixed Technic structures | [Technic](docs/agent/technic.md), [design patterns](docs/agent/technic-design.md) |
| Moving mechanisms | [Mechanisms](docs/agent/mechanisms.md) |
| Finding or adapting source constructions | [Discovery](docs/agent/reference-discovery.md), [build manuals](docs/agent/build-manuals.md) |

For semantic discovery, perform the [Jev availability check](docs/agent/reference-discovery.md#check-jev-availability-before-searching) first. If unavailable, report why and use `discover search parts|models|submodels ... --engine fts`, catalogs and examples. Do not keep retrying a failed service. Rankings suggest candidates; actual dimensions, connectors and parent context determine suitability. Preserve authorship and extraction manifests when reusing source.

## 2. Build the smallest useful module

Use a JSON plan directly. Add a Python generator when loops, calculations or conditional patterns make it clearer; a separate generator is optional. The [bridge plan](examples/bridge.plan.json) is a small complete example. See the [plan guide](docs/agent/plans.md) for the format and advanced placements.

```sh
./ldraw-agent build output/my-model.plan.json
```

This writes `output/my-model.mpd` only after source and geometry checks pass. Use `--force` for a rebuild; a failed build preserves the previous MPD. Keep fixes in the source plan or generator.

Keep these rules visible while placing parts:

- Negative Y is up. Stud pitch is 20 LDU; brick and plate bodies are 24 and 8 LDU high. For upright stacking, `y_upper = y_lower - upper_body_height`; studs add no gap. Check half-stud alignment. Prefer `on` for supported upright bricks/plates.
- Inspect actual origins, bounds, variants and connectors. Never invent part IDs, infer axes from names or treat cached full bounds as stacking heights. Use physical parts, not internal primitives.
- Use proper rotations (`yaw`, `matrix`, or `./ldraw-agent matrix y 90`); never stretch, shear or mirror complete parts. Anchors describe intended interfaces; inspect the mating parts.
- Colour 16 inherits from an explicit ancestor colour; 24 is for edges. A palette code does not establish retail availability.
- Keep section names unique, dependencies acyclic and placements distinct. Bond adjacent seams and keep floor, roof, door and hinge interfaces clear.

Read [geometry](docs/agent/geometry.md) for unfamiliar connections and [snapping](docs/agent/snapping.md) when using connector-based placement. Consult [LDraw rules](docs/agent/ldraw-reference.md) when reading or writing raw source. The language authority is [ldraw-specs.pdf](docs/ldraw-specs.pdf), searchable with `./ldraw-agent spec 'INVERTNEXT'`; the [source map](docs/agent/specification-map.md) identifies relevant pages. Use the existing builder and pyldraw3 rather than adding a parser or serializer.

## 3. Review, repair and repeat

One command builds a plan if needed, validates the assembly and geometry, writes the Python BOM, renders LeoCAD previews and compares both BOMs:

```sh
./ldraw-agent review output/my-model.plan.json
```

For an existing model, use `review output/my-model.mpd`. Results go to `output/my-model-review/`. Read `review.json` and `validation.json`, then **open the images in `previews/`**. Use `--force` to replace a previous generated review after editing the source. Keep your design/visual-review notes beside the source, outside that generated directory. See [review options and artifacts](docs/agent/tooling.md#review-a-model) for scopes, output paths and failure behavior.

Fix every error and investigate warnings. Check the silhouette at thumbnail size, proportions, palette, depth, support, openings, intersections, overhangs and exposed sides/rear. Inspect interiors and obscured interfaces separately. Record the images actually opened, weaknesses found and changes made; improve specific weaknesses and render again. Producing a PNG is not visual review.

For targeted work:

```sh
./ldraw-agent inspect output/my-model.mpd --section my-floor.ldr --colour 19 --contacts all --limit 30
./ldraw-agent review output/my-model.mpd --section my-floor.ldr --colour 19 --outdir output/my-floor-review
./ldraw-agent review output/my-model.plan.json --no-render --outdir output/my-model-checks
```

Replace example section names with actual FILE names. `--no-render` is a fast intermediate check; it explicitly skips rendering and BOM comparison. Use [build-step views](docs/agent/build-manuals.md#inspect-a-model-during-construction) for hidden gaps or uncertain connections. Check details, their modules, then the full assembly: checked neighbors can still collide when combined.

Run family checks where applicable: `vehicle check --profile road|motorcycle|watercraft|aircraft`; `technic check --contract ...` for fixed supports. These remain separate from general `review`. For source-derived mechanisms, use `--contacts none` and follow the mechanism guide: analytical motion verification is deferred; normal source/geometry checks, BOM comparison and visual inspection remain required.

Read exit status and coverage, not just `checks_passed`. Exit 0 means the selected automatic checks passed; 1 means checks or BOM comparison failed; 2 means input/dependency/execution failure. Contacts automatically skip above 500 physical placements; check modules or deliberately use `--contacts all`. `--detail summary` limits displayed rows, not checks. The default expansion budget is 100,000 placements. Skipped contacts give no connectivity conclusion; AABB overlaps and fragmented connector groups need interpretation. The [validation guide](docs/agent/validation.md) explains diagnostic repairs and limitations.

## 4. Deliver the reviewed revision

After the last source change, rerun review and open the final images. Link the review folder's `model.mpd`, source plan/generator, reused-asset manifests, design/visual-review notes, `review.json`, `validation.json`, BOMs and previews. State actual features, physical placement count, checks passed and specific remaining limitations. `physical_validity: not_proven` is intentional: syntax, rendering, matching BOMs and connector graphs do not prove physical buildability, strength, legal connections or inventory availability.

For a semantic GLB export, use `./prepare-glb.sh --file MODEL.mpd MODEL.glb`. Existing individual commands and shell wrappers remain available in the [tool reference](docs/agent/tooling.md). Finish the model and its review artifacts; do not stop at a proposal or commands for the user to run.
