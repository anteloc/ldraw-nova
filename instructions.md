# Generate and verify a new LDraw model

Create the model the user requests and deliver its editable `.mpd`, reproducible source plans/generator, checks, BOM and reviewed previews. Match the requested subject, scale, palette, features and complexity. Make visual quality an explicit design objective: recognizable proportions, a controlled palette, depth, coherent details and a readable focal feature. Geometric correctness alone does not complete the task. For a large model, divide it into modules and finish them in stages. Do not silently reduce a requested detailed scene to a few bricks. When no subject is supplied, choose a recognizable subject and state its scope briefly.

Work through design, construction, checks, repair, rendering and delivery. Correct syntax, a plausible picture and a connected-component result are separate kinds of evidence; none alone proves physical buildability.

## 1. Prepare

Run from this repository's root:

```sh
./ldraw-agent doctor
```

Run `./setup.sh` if needed. It installs pinned Python packages in `.venv` and prepares local indexes. Use **LeoCAD for snapshots on this Mac**, including embedded unofficial parts; the render adapter supplies those parts through an isolated temporary library. Use `./prepare-glb.sh --file MODEL.mpd MODEL.glb` when semantic GLB/Blender inspection is needed.

Read:

- [LDraw rules](docs/agent/ldraw-reference.md): records, coordinates, colours, MPD, BFC and headers.
- [Geometry](docs/agent/geometry.md): origins, stacking, connectors and collision evidence.
- [Visual design](docs/agent/visual-design.md): composition, category discovery, role-based palettes, reusable details and visual iteration.
- [Tool reference](docs/agent/tooling.md) and [validation guide](docs/agent/validation.md).
- For complex work, [module workflow and Bookshop case study](docs/agent/complex-models.md), [measured reference inventory](docs/agent/resources/bookshop-study.json), and [Copper Lane example](examples/modular-street/README.md).

The language authority is the mandatory [docs/ldraw-specs.pdf](docs/ldraw-specs.pdf). Use `./ldraw-agent spec --page 65` or `./ldraw-agent spec 'INVERTNEXT'`; the [source map](docs/agent/specification-map.md) identifies relevant pages. Distinguish official part-authoring rules from personal model rules.

The supplied resources are `../ldraw-lib/ldraw/` and `../ldraw-lib/models-annotated/`. Override with `LDRAW_DIR` / `MODELS_DIR` or global `--library` / `--models` before the command. Keep the official library and OMR originals unchanged. Put new work under `output/`.

## 2. Plan the model and study useful constructions

Record a short design brief outside the assembly plan: subject/story, silhouette, dimensions, palette roles, primary focal feature, two supporting features, detail vocabulary, quiet surfaces, physical subassemblies and build order. State what will make this particular design attractive; do not equate part count with quality. For a building scene, separate the street/base, individual storeys, roofs, façade/window modules, interiors and landscaping. Allocate space and attachment surfaces before decoration. Keep a module checklist with local origin, envelope, anchors, dependencies and review status.

Search and inspect real parts:

```sh
./ldraw-agent catalog categories
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
./ldraw-agent catalog parts 'leaves' --category plants --limit 5
./ldraw-agent design palettes
./ldraw-agent design details
./ldraw-agent search parts 'brick 2 x 4' --limit 8
./ldraw-agent part 3001 --limit 20
./ldraw-agent colours 'blue'
./ldraw-agent profiles
```

Use categories to discover appropriate forms, then compare a short list visually with `part-board REF ... --outdir output/part-shortlist` when names are insufficient. Categories supply descriptive symbols and dimension hints; current LDraw geometry and LDConfig remain authoritative. Cached dimensions may differ, include studs, and are not stacking heights. Never invent a part ID or infer axes from a description. Inspect each unfamiliar part's actual bounds, origin, variant/status and connector frames. Use physical parts, not arbitrary primitives or internal subparts. A valid palette code does not prove retail part/colour availability.

Study references in small sections:

```sh
./ldraw-agent search submodels 'window OR balcony' --limit 5
./ldraw-agent study ../ldraw-lib/models-annotated/10270-1.mpd --report output/reference-study.json
./ldraw-agent sections ../ldraw-lib/models-annotated/10270-1.mpd --section '10270 - Pendulum_Clock.ldr'
```

Read `source_checks_passed`, reachability and physical counts. An annotation can describe empty or unreferenced modules. Embedded `.dat` parts count as physical leaves; their studs/primitives are geometry, not separate BOM pieces. OMR examples can contain real source errors and rounded transforms.

To copy a useful module, use `extract --section NAME --namespace UNIQUE --output output/assets/NAME.mpd`. It includes transitive dependencies, renames references and preserves author/licence headers. Keep its `.manifest.json`. Read the returned `root` instead of guessing the new filename. Review source problems before using the asset. `--repair-bfc-comments` and `--normalize-rotations` are explicit, recorded changes to a copy; neither certifies the construction. Do not present copied source as an original design.

## 3. Build reproducibly with module contracts

Use the [JSON schema](ldraw_tools/data/plan.schema.json). The [bridge](examples/bridge.plan.json) teaches basic format; the [modular street plans](examples/modular-street/scene.plan.json) teach complex composition. Use these as examples of technique, then design the requested model.

- Every plan has `version: 1`, accurate `author` and `sections`; an authorized `license` is optional. The root plan's first section is the scene main.
- Use `includes` for other JSON plans and `assets` for extracted MPDs. Paths are relative to the declaring plan. Section names must be unique across all inputs; copied headers retain their authorship.
- Each generated section has a unique flat `.ldr` name, useful `description` and `steps` of placement arrays. Optional `anchors` expose named local frames (`at` and optional proper `matrix`).
- Refs may be descriptive category symbols such as `@arches.Arch1X6X2WithThickTopAndReinforcedUnderside`, and colours may be `@colours.Tan`. The builder resolves these to numeric LDraw source without changing the symbolic plan. Missing symbols/parts fail explicitly.
- Use `design details NAME --palette PALETTE --output output/detail.plan.json` for a starting detail. Build/render it, reserve its envelope, and adapt its interface; do not paste decoration through existing wall/roof parts.
- Each placement has a unique local `id`, real `ref`, `colour`, and exactly one position mode: `at: [x,y,z]`, `on: "earlier-id"`, or `attach: {"to":"earlier-module-id","anchor":"seat","using":"base"}`. Add a short useful `purpose`.
- `on` supports only curated upright bricks/plates. Optional `offset_studs: [x,z]` uses the supporting part's axes. Inspect other connections and use explicit placement or module anchors.
- `attach` aligns the two authored module frames, including orientation. Optional `offset` is in the support anchor's axes. Anchors describe intended interfaces; verify the actual mating parts.
- With `at` or `on`, use `yaw` or a proper `matrix`, never both. `attach` already determines the matrix. `repeat: {"count":N,"step":[dx,dy,dz]}` works with `at`; offsets use the containing section's axes and IDs become `id-0`, `id-1`, etc.

Keep these placement rules visible while constructing:

1. Negative Y is up; stud pitch is 20 LDU; a brick body is 24 high and a plate body is 8.
2. For ordinary upright stacking, **`y_upper = y_lower - upper_body_height`**. Stud height does not add a gap. A brick's full bounding-box height is not its stacking height.
3. Check half-stud parity. For example, a 1×1 above a centred 2×2 needs an actual stud offset such as `[0.5,0.5]`.
4. Do not stretch, shear or mirror complete parts. Compute rotations with `./ldraw-agent matrix y 90` or the Python API. Arbitrary rigid SNOT/hinge orientations require connection and clearance review.
5. Colour 16 inherits; explicit ancestor placements must resolve all visible leaves. Colour 24 is for edges, not part placements.
6. Model subassemblies belong in embedded `.ldr` blocks. Imported classified `.dat` definitions may contain polygons and primitive transforms; keep those internal definitions separate from rigid physical placements.
7. Avoid cycles, unresolved dependencies, library-name shadowing and coincident duplicates. Bridge adjacent brick seams with actual connecting parts. Leave floor, roof, hinge and door interfaces clear.

Use Python for parameterized bonds, openings, stepped roofs or other conditional patterns. See [generate.py](examples/modular-street/generate.py). Use `load_plan(path)`, `build_plan`, `rotation`, and pyldraw3's existing classes; do not implement another LDraw parser/serializer. Keep geometry fixes in the generator/plan so rebuilding retains them.

```sh
./ldraw-agent build output/my-model.plan.json --output output/my-model.mpd \
  --detail summary --report output/my-model.build.json
```

Use one descriptive basename consistently. `build` writes only after selected assembly/geometry checks have no errors; warnings remain visible. It emits UTF-8 without BOM, CRLF, headers, comments and steps. Use `--force` for an intentional rebuild. Texture/data/custom colour semantics and newly authored unofficial part geometry need the additional review described in the references.

## 4. Check details, modules and the assembled scene

Work locally first: test one window/hinge/roof detail, then its containing module, then the full scene. A checked module can still collide with its neighbour after assembly.

```sh
./ldraw-agent inspect output/my-model.mpd --section my-floor.ldr --colour 19 \
  --contacts all --detail full --limit 30 --report output/my-floor.inspection.json
./ldraw-agent render output/my-model.mpd --section my-floor.ldr --colour 19 \
  --outdir output/my-floor-review --views home top
./ldraw-agent validate output/my-model.mpd --geometry --detail summary \
  --report output/my-model.validation.json
./ldraw-agent bom output/my-model.mpd --report output/my-model.bom.json
./check-model.sh output/my-model.mpd
./ldraw-agent render output/my-model.mpd --outdir output/my-model-review
./ldraw-agent compare-bom output/my-model.mpd --csv output/my-model-review/leocad-bom.csv \
  --report output/my-model.bom-comparison.json
```

Replace example section names with your actual FILE names. `--section` includes dependencies, resolves inherited colour when supplied, and preserves original source-line attribution. Its occurrence indices are local to that selection. Use `--offset 30 --limit 30` to retrieve another page; `snap --moving N --fixed M` uses these indices with the same selection. Snap candidates are world transforms: convert through the parent inverse before changing a nested placement.

Automatic contacts run for at most 500 physical placements. Larger scenes explicitly report `coverage.contacts_skipped`; check contacts on modules or deliberately request `--contacts all`. `--contacts none` still checks resolved geometry and curated body overlaps. No contacts means no connectivity conclusion. `--detail summary` suppresses long lists, not checks. The default expansion budget is 100,000 placements; use `--max-instances` when justified.

Read exit status, errors, warnings, `complete`, truncation flags and `contacts_checked`. Exit 0 means the selected operation completed; 1 means checks/BOM comparison failed; 2 means input/dependency/execution failure. `study` is informational; `extract` may write a failing review copy. `validate --strict` also fails warnings, without increasing coverage.

Repair every error, rebuild and rerun affected checks. Explain each remaining warning using specific evidence. AABB candidates are not material-collision proofs; engaged studs/sockets normally overlap in bounds. Fragmented connector groups can indicate missing metadata, floating parts or intentionally separate objects. Investigate the implicated parts instead of deleting warnings.

Open the first whole-model PNGs and perform a visual design pass before final delivery. Check thumbnail silhouette, proportions, focal hierarchy, palette balance, depth/shadows, useful variation, quiet versus detailed areas, exposed side/rear walls, and readable entrances. Improve specific weaknesses and render again. Do not add random ornament everywhere or stop because geometry passes. Record the viewed images, problems found and revisions in a short visual-review document.

Open the final PNGs. Inspect silhouette, palette, orientation, support, openings, missing parts, intersections and overhangs. Review individual floors/interiors and obscured rear/side interfaces. Compare Python and LeoCAD BOMs by reference, colour and quantity using `compare-bom`; do not reconcile a mismatch by discarding parts. The macOS adapter handles embedded DAT definitions without modifying the source library.

For uncertain material intersections or unusual mechanisms, convert the selected model to semantic GLB and inspect it through available Blender tools. Confirm the LDraw/Blender axis and unit conversion using a known 20-LDU distance. Record any physical checks that remain unperformed. Do not claim visual review unless the images were opened, or buildability merely because a renderer succeeded.

## 5. Deliver the exact final revision

After the last source change, regenerate affected checks, BOMs and renders. Provide clickable paths to the final `.mpd`, plans/generator, reused-asset manifests, design brief/visual review, validation report, BOM comparison and preview images. Briefly state actual features and physical placement count, which checks passed, and specific unresolved physical/inventory limitations. The toolkit's `physical_validity: not_proven` is intentional.

Finish the requested model and its review artifacts. Do not stop at a design proposal or instructions for the user to run.
