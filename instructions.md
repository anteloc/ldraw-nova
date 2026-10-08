# Generate and verify a new LDraw model

Create the model the user requests and deliver its editable `.mpd`, reproducible source plans/generator, checks, BOM and reviewed previews. Match the requested subject, scale, palette, features and complexity. Make visual quality an explicit design objective: recognizable proportions, a controlled palette, depth, coherent details and a readable focal feature. Geometric correctness alone does not complete the task. For a large model, divide it into modules and finish them in stages. Do not silently reduce a requested detailed scene to a few bricks. When no subject is supplied, choose a recognizable subject and state its scope briefly.

Work through design, construction, checks, repair, rendering and delivery. Correct syntax, a plausible picture and a connected-component result are separate kinds of evidence; none alone proves physical buildability.

## 1. Prepare

Run from this repository's root:

```sh
./ldraw-agent doctor
```

Run `./setup.sh` if needed. It installs pinned Python packages in `.venv` and prepares local indexes. Use the globally available **`leocad` CLI** for snapshots, including embedded unofficial parts; the render adapter supplies those parts through an isolated temporary library. Use `./prepare-glb.sh --file MODEL.mpd MODEL.glb` for semantic GLB export through the global `mpd2glb.sh` executable.

Read:

- [LDraw rules](docs/agent/ldraw-reference.md): records, coordinates, colours, MPD, BFC and headers.
- [Geometry](docs/agent/geometry.md): origins, stacking, connectors and collision evidence.
- [Visual design](docs/agent/visual-design.md): composition, category discovery, role-based palettes, reusable details and visual iteration.
- For vehicles, [System vehicle workflow](docs/agent/vehicles.md) and [vehicle atlas](examples/vehicle-atlas/README.md): measured running gear, stance, body shaping, cab/cargo layouts and review.
- For spaceships, [spacecraft workflow](docs/agent/spaceships.md) and [spaceship atlas](examples/spaceship-atlas/README.md): advanced silhouettes, frames, dedicated cockpits/engines, layered hulls and concentrated service details. Use `spaceship brief starfighter|freighter|capital-ship` to begin the design brief; inspect the selected source before adapting it.
- For Technic structures or a Technic skeleton supporting a System body, [Technic structural workflow](docs/agent/technic.md) and [structural atlas](examples/technic-atlas/README.md). Stage 1 covers fixed assemblies, seating, bracing and mounts.
- For models with mechanisms, follow the [mechanism workflow](docs/agent/mechanisms.md) and [mechanism atlas](examples/mechanism-atlas/README.md). Stage 2 is authorized for construction from studied examples; analytical mechanism verification is deferred by the user. Read the build pages, preserve parent context, describe intended operation and adapt the source.
- For Technic design vocabulary, read [creative Technic design](docs/agent/technic-design.md) and the [Mecha construction studies](examples/technic-studies/README.md). Choose patterns by function, preserve their measured interfaces and source qualifications, and adapt the supporting frame and appearance to the new subject.
- For reusable Mecha-derived mechanisms, the [Technic atlas](examples/technic-atlas/README.md#mechanisms-from-ldraw-mecha) includes engines, paired Cardan shafts, a four-speed gearbox, a lift and suspension with editable source and build pages. Find them with `examples --family technic --limit 20` and use `mechanism export` on the prepared directory; read its omitted-parent interfaces before composing it with a frame.
- [Tool reference](docs/agent/tooling.md) and [validation guide](docs/agent/validation.md).
- For complex work, [module workflow and Bookshop case study](docs/agent/complex-models.md), [measured reference inventory](docs/agent/resources/bookshop-study.json), and [Copper Lane example](examples/modular-street/README.md).

The language authority is the mandatory [docs/ldraw-specs.pdf](docs/ldraw-specs.pdf). Use `./ldraw-agent spec --page 65` or `./ldraw-agent spec 'INVERTNEXT'`; the [source map](docs/agent/specification-map.md) identifies relevant pages. Distinguish official part-authoring rules from personal model rules.

Resolve the parts library through `LDRAW_DIR`, falling back to `LDRAWDIR` if unset or empty, or pass global `--library` before the command. Reference models and their database are always `data/models-annotated/` and `data/ldraw-info.db`. Part catalogs and connector metadata are under `data/categories/` and `data/offLibShadow/`. Keep these resources unchanged. Put new work under `output/`.

## 2. Plan the model and study useful constructions

Before using Jev, follow the [availability check](docs/agent/reference-discovery.md#check-jev-availability-before-searching): verify the CLI, credentials and a bounded live request. If Jev is unavailable or fails later (including missing/invalid credentials or a service outage), report the reason briefly and continue with `discover search models|submodels|parts ... --engine fts`, existing catalogs and examples. Identify the fallback as offline keyword ranking, and avoid repeatedly retrying the unavailable service.

Use [reference discovery](docs/agent/reference-discovery.md) to expand the design vocabulary: inspect whole-model precedents for proportions and styling, submodels for useful constructions, and their actual parts for fittings. Start with `examples --family reference`, then `discover search models|submodels|parts` as needed. Render a small shortlist with `discover catalog`, open the relevant views, compare dimensions and parent context, and record which references you will copy, adapt or study. Preserve attribution and source checks; curated examples and high relevance scores do not establish fit in the new model.

When a useful submodel is difficult to read from its completed picture, follow the [build-manual workflow](docs/agent/build-manuals.md). `manual prepare` renders its source steps with per-step parts and child-assembly callouts; study parent interfaces, record the inspected pages and export a useful construction for the appropriate atlas. Use `--overview` for completed-model studies of large references. Keep inspiration sources with unresolved errors separate from reusable examples.

Record a short design brief outside the assembly plan: subject/story, silhouette, dimensions, palette roles, primary focal feature, two supporting features, detail vocabulary, quiet surfaces, physical subassemblies and build order. State what will make this particular design attractive; do not equate part count with quality. For a building scene, separate the street/base, individual storeys, roofs, façade/window modules, interiors and landscaping. Allocate space and attachment surfaces before decoration. Keep a module checklist with local origin, envelope, anchors, dependencies and review status.

For a spaceship, choose scale and silhouette before selecting the canopy, wing system and engine size. Allocate the internal spine/truss, cockpit, hull panels, engines and landing/display supports; use a few dense service areas beside quiet armour surfaces. Inspect wing roots, internal mounts and underside views. Use general model checks and the relevant Technic/mechanism workflow for those modules; road-wheel and aircraft-profile checks do not establish spacecraft quality.

For a Technic model, make one intended action the focal feature and trace both its input/output route and its physical supports. Use the [pattern index](docs/agent/technic-design.md#choose-a-construction-by-function) for gears, engines, suspension, steering and lifts. Record the delivered pose, shaft/pivot frames, retained stacks, missing parent parts and moving envelopes before cladding. Explore different silhouettes around the studied core; preserve internal spacing while adapting the frame and body. Source animation assumptions, omitted mounts and reconstruction parts must remain explicit in the adaptation notes.

For a vehicle, choose its family and inspect the defining parts **before** fixing the body dimensions: wheel package for road vehicles, frame/fairing for a motorcycle, hull for a boat, or nose/wing/engine interfaces for an aircraft. Record wheel centres, track, wheelbase, front/rear overhangs, ground clearance, body width, cabin height and the bonnet/cab/deck or cab/load-bed silhouette. Use X for width, -Z for forward and Y=0 for the road. Separate running gear, bonded chassis, wheel wells, body, glazing/interior, roof and front/rear fascias. Reserve wheel space and actual attachments before skinning the body. For System vehicles, use ordinary wheel-pin plates and System construction. For a Technic skeleton, follow the [structural workflow](docs/agent/technic.md) and declare the body mounts. For mechanisms, use the [Stage 2 workflow](docs/agent/mechanisms.md); keep fixed structural checks scoped to the supports. Boats/aircraft require their own hull/wing/landing-gear interfaces rather than the fixed road-wheel assumptions.

```sh
./ldraw-agent vehicle list
./ldraw-agent vehicle wheels
./ldraw-agent vehicle details
./ldraw-agent examples --family vehicle --details
./ldraw-agent examples --family vehicle
./ldraw-agent vehicle plan grand-tourer --output output/vehicle-start.plan.json
```

Adapt a relevant starting point to the requested subject and scale. Do not treat the supplied examples as the limits of vehicle design, or call a colour swap a new body design. Establish the silhouette with wheels and main masses, then refine curves, glazing and functional details. Choose actual seats, steering wheels, instruments, glazing, cargo fittings and other dedicated vehicle parts before building substitutes from blocks. Reserve their measured envelopes and attachment surfaces; use `vehicle details NAME` for reusable fittings and inspect all replacements. A display cabin does not establish minifigure fit.

For a part's intended role or visual character, use Jev's ranked candidates when the availability check passes; otherwise use `discover search parts ... --engine fts`:

```sh
jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field parts_descriptions.description --top 10 \
  --query 'a wall decoration for a castle' --show --json
```

Write each query as a description of **one suitable part**, including its role and model context. Use a separate query for each role; `--top 10` requests ten alternatives to that one part. Read each result's `source.key.part`, `text`, and `score`, then inspect promising references in the installed library. Discard internal subparts and primitives; inspect aliases/replacements and sticker shortcuts before choosing. Ranking measures semantic relevance, not fit or attachment. See [Jev part discovery](docs/agent/tooling.md#jev-part-discovery) for setup, result fields, and search coverage.

Use exact part/category searches to refine the shortlist and inspect real geometry:

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
./ldraw-agent study data/models-annotated/10270-1.mpd --report output/reference-study.json
./ldraw-agent sections data/models-annotated/10270-1.mpd --section '10270 - Pendulum_Clock.ldr'
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
- Each placement has a unique local `id`, real `ref`, `colour`, and exactly one position mode: `at: [x,y,z]`, `on: "earlier-id"`, `attach: {"to":"earlier-module-id","anchor":"seat","using":"base"}`, or `snap: {"to":"earlier-id","near":[0,-8,0]}`. Add a short useful `purpose`.
- `snap` uses connector evidence, checks candidate collisions, and moves a complete part/submodel. Use the [snapping guide](docs/agent/snapping.md) for leaf/feature selectors, shadow coverage, and plan examples.
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

Select `vehicle check --profile road|motorcycle|watercraft|aircraft` for the family. Non-road profiles check their documented dedicated assemblies and never imply successful car-wheel checks, buoyancy or flight. For a road vehicle, test a wheel pair and chassis first, then the fenders, cab and fascias. Run `vehicle check MODEL.mpd --report output/vehicle-check.json` alongside normal validation. This checks supported separate tyre/rim pairs, ground contact, transverse axes, axle symmetry and conservative wheel-space candidates; read its explicit coverage. Curved arches and wheel-pin retention still need inspection. Render `--views home front back right top bottom` and a roof-off cabin when interiors matter. Revise stance, bonnet/cabin/tail proportions, roof thickness, shoulder lines, surface seams and front/rear identity after opening the images. Do not apply building-specific façade or entrance review criteria to vehicles.

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

Replace example section names with your actual FILE names. `--section` includes dependencies, resolves inherited colour when supplied, and preserves original source-line attribution. Its occurrence indices are local to that selection. Use `--offset 30 --limit 30` to retrieve another page; `snap --moving N --fixed M` uses these indices with the same selection. Snap candidates include world transforms and ready-to-use `local_placement` values. `--moving-depth 0` moves the outer submodel; `--output` applies to a validated copy while isolating repeated submodel occurrences. Read [shadow and snapping coverage](docs/agent/snapping.md).

Automatic contacts run for at most 500 physical placements. Larger scenes explicitly report `coverage.contacts_skipped`; check contacts on modules or deliberately request `--contacts all`. `--contacts none` still checks resolved geometry and curated body overlaps. No contacts means no connectivity conclusion. `--detail summary` suppresses long lists, not checks. The default expansion budget is 100,000 placements; use `--max-instances` when justified.

Read exit status, errors, warnings, `complete`, truncation flags and `contacts_checked`. Exit 0 means the selected operation completed; 1 means checks/BOM comparison failed; 2 means input/dependency/execution failure. `study` is informational; `extract` may write a failing review copy. `validate --strict` also fails warnings, without increasing coverage.

Repair every error, rebuild and rerun affected checks. Explain each remaining warning using specific evidence. AABB candidates are not material-collision proofs; engaged studs/sockets normally overlap in bounds. Fragmented connector groups can indicate missing metadata, floating parts or intentionally separate objects. Investigate the implicated parts instead of deleting warnings.

Open the first whole-model PNGs and perform a visual design pass before final delivery. Check thumbnail silhouette, proportions, focal hierarchy, palette balance, depth/shadows, useful variation, quiet versus detailed areas, exposed side/rear walls, and readable entrances. Improve specific weaknesses and render again. Do not add random ornament everywhere or stop because geometry passes. Record the viewed images, problems found and revisions in a short visual-review document.

Open the final PNGs. Inspect silhouette, palette, orientation, support, openings, missing parts, intersections and overhangs. Review individual floors/interiors and obscured rear/side interfaces. Compare Python and LeoCAD BOMs by reference, colour and quantity using `compare-bom`; do not reconcile a mismatch by discarding parts. The LeoCAD adapter handles embedded DAT definitions without modifying the source library.

Inspect uncertain interfaces with close LeoCAD views and the global `ldraw-render-steps.sh` tool. Render the unfinished submodel step by step from multiple views to locate a misplaced part, hidden gap or weak support; see [construction review](docs/agent/build-manuals.md#inspect-a-model-during-construction). Fix the generator or plan and regenerate. Record any physical checks that remain unperformed. Do not claim visual review unless the images were opened, or buildability merely because a renderer succeeded.

## 5. Deliver the exact final revision

After the last source change, regenerate affected checks, BOMs and renders. Provide clickable paths to the final `.mpd`, plans/generator, reused-asset manifests, design brief/visual review, validation report, BOM comparison and preview images. Briefly state actual features and physical placement count, which checks passed, and specific unresolved physical/inventory limitations. The toolkit's `physical_validity: not_proven` is intentional.

Finish the requested model and its review artifacts. Do not stop at a design proposal or instructions for the user to run.
