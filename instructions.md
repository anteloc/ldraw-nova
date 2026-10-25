# Build and review an LDraw model

Deliver an editable MPD, reproducible source, checks, parts list and inspected previews. Match the requested subject, scale, palette, features and complexity. Keep new work under `output/`; leave the parts library and supplied `data/` unchanged.

## 1. Choose the construction

Run `./ldraw-agent doctor`; use `./setup.sh` if needed. Set `LDRAW_DIR` (or `LDRAWDIR`) to the installed parts library. LeoCAD must be on `PATH` for previews. Add `./setup.sh --with-lsynth` only when generating flexible parts.

Write a short brief: silhouette, dimensions, palette, focal feature and build order. For large models, divide the design into modules with clear origins, envelopes and attachment surfaces. Reserve space for joints before adding decoration. If the subject is unspecified, choose one and state the scope.

Start with examples and inspect unfamiliar parts:

```sh
./ldraw-agent examples --family building
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
./ldraw-agent part 3001
```

**Spaceships use SNOT by default.** Follow the [Halcyon](examples/snot/halcyon/README.md): a supported core, attached sideways hull skins, axial engines, smooth contours and thin wing edges. Adapt these techniques to the requested silhouette and scale.

Read the relevant guide when its construction is needed:

| Need | Guide |
|---|---|
| Shape, palette and image review | [Visual design](docs/agent/visual-design.md) |
| Plan format, Python and placements | [Plans](docs/agent/plans.md), [modules](docs/agent/complex-models.md) |
| Sideways studs and offsets | [SNOT](docs/agent/snot.md) |
| Vehicles or spaceships | [Vehicles](docs/agent/vehicles.md), [spaceships](docs/agent/spaceships.md) |
| Fixed Technic frames and mounts | [Technic](docs/agent/technic.md), [design patterns](docs/agent/technic-design.md) |
| Moving mechanisms | [Mechanisms](docs/agent/mechanisms.md) |
| Advanced mechanisms and animation constraints | [Mechanism construction](docs/agent/advanced-mechanisms.md), [parts catalog](docs/agent/technic-catalog.md) |
| Hoses, cables, bands, chains or treads | [Flex constraints](docs/agent/flex-constraints.md), `flex guide TYPE` |
| Source constructions or build manuals | [Discovery](docs/agent/reference-discovery.md), [manuals](docs/agent/build-manuals.md) |

For semantic discovery, check [Jev availability](docs/agent/reference-discovery.md#check-jev-availability-before-searching) first. If unavailable, report why and use `discover search ... --engine fts`, catalogs or examples. Do not repeatedly retry a failed service. Verify dimensions, connectors and parent context; preserve attribution and extraction manifests when reusing source.

## 2. Write the source

Use an ordinary [JSON plan](docs/agent/plans.md). Use Python to generate the same dictionaries when loops or calculations help. Build the smallest useful module first; keep fixes in its source. The [bridge](examples/bridge.plan.json) is a complete small example.

For Technic, start with `technic plan NAME --output output/NAME.plan.json` or inspect ports with `technic parts PART`. Generated plans link their structural contracts, so normal build/review checks required joints and insertion order. Keep contracts scoped to fixed structures; regenerate and review them after geometry or ordering changes.

For flexible parts, place the real fittings or supported wheels first. Use `Endpoint`, `Waypoint`, `hose` and `band` from `ldraw_tools.flex_authoring`; do not write another curve solver or routing optimizer. Declare the editable constraint source in [plan assets](docs/agent/plans.md#generated-flexible-assets):

```json
"assets": [{"source": "hoses.ldr", "namespace": "machine-hoses", "checks": {"min_radius": 15}}]
```

Build/review checks constraints, synthesizes and measures the result automatically. Choose limits for the actual route; 15 is an example, not a certified material limit. Reuse measured part placements for endpoints and wheel constraints. The [pneumatic press](examples/flex/pneumatic-press/README.md) demonstrates the complete workflow.

Placement rules:

- Negative Y is up. Stud pitch is 20 LDU; brick/plate bodies are 24/8 LDU high. For upright stacking, `y_upper = y_lower - upper_body_height`; studs add no gap. Prefer `on` for supported upright bricks/plates.
- Inspect real part IDs, origins, bounds and connectors. Full bounding-box height is not stacking height. Use physical parts, not internal primitives.
- Use `yaw`, a proper `matrix`, or `rotation(axis, degrees)`. Never stretch, shear or reflect complete parts. Verify actual mates behind anchors and snapping.
- Colour 16 inherits from an explicit ancestor; 24 is for edges. Palette codes do not prove retail availability.
- Keep section names and placement IDs unique, dependencies acyclic and placements distinct. Bond seams and keep attachment, door and hinge interfaces clear.

Consult [geometry](docs/agent/geometry.md), [snapping](docs/agent/snapping.md) or [LDraw rules](docs/agent/ldraw-reference.md) for unfamiliar cases. Use the existing builder and pyldraw3 parser/writer. The language authority is `docs/ldraw-specs.pdf`, searchable with `./ldraw-agent spec QUERY`.

## 3. Review and repair

```sh
./ldraw-agent review output/my-model.plan.json
```

This prepares declared assets, builds the model, runs geometry and declared structural checks, writes the BOM, renders previews and compares Python/LeoCAD BOMs. Results go to `output/my-model-review/`. Read `review.json` and `validation.json`, then **open the images in `previews/`**.

After editing, repeat with `--force`. For intermediate checks, add `--no-render`; finish with rendered review. `build PLAN` writes only an MPD after checks pass. Existing MPDs use `review MODEL.mpd`; separately run `technic check --contract` because an MPD does not carry plan contracts. Run `vehicle check --profile road|motorcycle|watercraft|aircraft` when applicable.

Fix errors and investigate warnings. Inspect silhouette, proportions, palette, support, openings, intersections and exposed sides/rear. Inspect obscured joints with section or [build-step views](docs/agent/build-manuals.md#inspect-a-model-during-construction). Review modules and the combined assembly. Record which images were opened, defects found and changes made beside the source, outside the generated review directory. Producing an image is not visual review.

Read exit status and coverage: 0 means selected automatic checks passed, 1 means failed checks/BOM comparison, and 2 means input/dependency/execution failure. Auto contacts skip above 500 placements; check modules or deliberately use `--contacts all`. `--detail summary` limits displayed rows, not checks. The expansion budget defaults to 100,000 placements. For source-derived mechanisms, follow their guide and use `--contacts none`; syntax, geometry, BOM and visual review remain required. See [validation](docs/agent/validation.md) and [tool options](docs/agent/tooling.md).

## 4. Deliver the reviewed revision

After the final edit, rerun review and inspect its images. Link the MPD, source, reused-asset manifests, review/validation reports, BOMs, previews and visual notes. State actual features, physical placement count, checks passed and specific remaining limitations. `physical_validity: not_proven` is intentional: these checks do not establish strength, motion, complete collision freedom, legal connections or inventory availability.

For semantic GLB export, use `./prepare-glb.sh --file MODEL.mpd MODEL.glb`. Complete the artifacts and review; do not stop at a proposal or commands for the user to run.
