# Generate a new LDraw model

Create an original, coherent LEGO-style model and deliver its editable `.mpd` source. Follow the user's subject, size, features, palette, and constraints. If the user gives no subject, choose a modest recognizable object you can finish and verify, such as a small building, bridge, or brick-built sculpture. Prefer a simple complete construction over features whose connections you cannot verify. Continue through generation, checking, repair, rendering, and delivery.

Your objective is correct LDraw syntax, real part references and colours, sensible geometry, and a physically plausible connected assembly. Use the tools below to obtain evidence. Do not claim that parsing or rendering alone proves physical buildability.

## 1. Prepare and read

Work from this repository's root. Run:

```sh
./ldraw-agent doctor
```

If the environment is missing, run `./setup.sh`. It installs Python tools into `.venv` and prepares local indexes. Python 3.12+, Poppler `pdftotext`, and LeoCAD are required for the complete workflow. `mpd2glb.sh` is optional for detailed Blender inspection. Use **LeoCAD for snapshots** on this macOS system.

Read these short references before constructing the model:

- [docs/agent/ldraw-reference.md](docs/agent/ldraw-reference.md): MPD structure, colours, transforms, headers, steps, and BFC.
- [docs/agent/geometry.md](docs/agent/geometry.md): part origins, stacking, connection evidence, collisions, and Blender review.
- [docs/agent/tooling.md](docs/agent/tooling.md): executable commands and JSON plan fields.
- [docs/agent/validation.md](docs/agent/validation.md): what the checks cover and how to repair failures.

The mandatory source of language rules is [docs/ldraw-specs.pdf](docs/ldraw-specs.pdf). The [source map](docs/agent/specification-map.md) gives exact PDF pages. Retrieve a disputed rule with `./ldraw-agent spec --page 65` or search with `./ldraw-agent spec 'INVERTNEXT'`. Do not confuse official part-submission rules with requirements for a personal model.

Resources default to `../ldraw-lib/ldraw/parts/` and `../ldraw-lib/models-annotated/`. Use `LDRAW_DIR` / `MODELS_DIR` or global `--library` / `--models` options if the resources are elsewhere. Keep source libraries and reference OMR models unchanged; put your work under `output/`.

## 2. Choose real parts and plan the assembly

Briefly identify the model, its intended features, approximate size, palette, and useful subassemblies. Design the structural base and connections before decorative details. Use purposeful section names such as `garden-house-main.ldr` and `garden-house-roof.ldr`.

Search and inspect actual parts:

```sh
./ldraw-agent search parts 'brick 2 x 4' --limit 8
./ldraw-agent part 3001 --limit 30
./ldraw-agent colours 'blue'
./ldraw-agent profiles
```

Never invent a part number, infer an Element ID from a description, or assume a filename exists. For every unfamiliar part, inspect its description, variant/replacement, local origin, axes, bounds, and connectors. Use current physical parts rather than arbitrary primitives or internal subparts. A palette code being valid does not prove that the chosen part was manufactured in that colour; check inventory separately if real-world purchasing/building is required.

For an unfamiliar mechanism or assembly, use the annotated reference models:

```sh
./ldraw-agent search submodels 'wheel OR steering' --limit 5
./ldraw-agent sections '../ldraw-lib/models-annotated/106-1.mpd'
./ldraw-agent sections '../ldraw-lib/models-annotated/106-1.mpd' --section '106 - car.ldr'
```

The search reports the original file path and whether it exists. Read the original section and its dependencies before applying its construction. Treat annotations and legacy placements as clues to verify. Preserve original author/licence information if copying source; do not pass a copied OMR model off as a new design.

## 3. Generate reproducibly

Prefer a JSON plan using [examples/bridge.plan.json](examples/bridge.plan.json) as a **format example**. Build your own model, not merely a renamed copy. Follow [ldraw_tools/data/plan.schema.json](ldraw_tools/data/plan.schema.json):

- Top level: `version: 1`, accurate `author`, and `sections`; optionally an authorized `license`.
- First section is the main model. Each section has a unique flat `.ldr` name, a useful description, and `steps` containing arrays of placements.
- Each placement has a unique local `id`, a real `ref`, a `colour`, and either `at: [x,y,z]` in LDU or `on: "earlier-id"`. Add a short `purpose` describing its role.
- Optional `yaw` rotates around +Y; use `matrix` instead for other rigid orientations. Never provide both. `offset_studs: [x,z]` is only for `on`, in the supporting part's local axes.
- `on` works only for curated upright studded bricks/plates in `profiles`. Use explicit inspected placement for other parts or submodels. Check half-stud parity; an offset of `0.5` is 10 LDU.

Critical placement rules:

- Negative Y is up. Stud pitch is 20 LDU, brick body height 24, and plate body height 8.
- Typical studded-part origins lie on the top body plane. For a standard upright upper part: **`y_upper = y_lower - upper_body_height`**. Stud height does not add a gap.
- Inspect actual axes: `3001.dat` is 80 LDU along local X and 40 along Z. Its 28-LDU full height includes the stud; its stacking height is 24.
- Complete parts must not be stretched, sheared, or mirrored. Compute rotations with `./ldraw-agent matrix y 90` or the Python API.
- Colour `16` inherits from a parent; colour every root placement so all visible leaves resolve. Colour `24` is for edges, never part placements.
- Repeated assemblies belong in submodels. Embed all model subassemblies in the MPD and reference the official part library for `.dat` files. No cycles, duplicate FILE names, library-name shadowing, or coincident duplicate parts.
- Use construction steps in a sensible installation order. Side-by-side touching bricks need a real connecting plate or other verified mating interface.

Generate:

```sh
./ldraw-agent build output/my-model.plan.json --output output/my-model.mpd --report output/my-model.build.json
```

Replace `my-model` with your chosen descriptive basename consistently. Existing MPDs require `--force` for a deliberate rebuild; errors prevent writing. The builder emits UTF-8 without BOM, CRLF, model headers, comments, and step boundaries. Fix the plan and rebuild rather than editing an output that will later be overwritten.

For procedural repetition, see [examples/python_api.py](examples/python_api.py), executed with `.venv/bin/python`. Reuse `build_plan`, `rotation`, and the existing `ldraw` classes instead of writing your own parser or transform serializer. The standard workflow uses real parts; custom polygons, textures, embedded images, local colour definitions, and unofficial part authoring require additional external review and are explicitly outside the generation profile.

## 4. Check, repair, and inspect the result

Run each command and check its exit status and JSON diagnostics:

```sh
./ldraw-agent validate output/my-model.mpd --geometry --report output/my-model.validation.json
./ldraw-agent bom output/my-model.mpd --report output/my-model.bom.json
./check-model.sh output/my-model.mpd
./ldraw-agent render output/my-model.mpd --outdir output/my-model-review
```

Exit 0 means the selected checks completed; 1 means validation/coverage failed; 2 means input, dependency, or execution failure. Read warnings and completeness flags even after exit 0. Use `validate --strict` when the model should have no warnings. `check-model.sh` uses the Python validator and LeoCAD for a temporary snapshot/BOM import test; it does not perform all physical checks.

Repair all errors in the plan and regenerate. Use reported section/source line paths to find the placement, including inside repeated submodels. Resolve each warning or document the specific evidence that explains it. Never suppress a problem merely to obtain a passing status.

Inspect the rendered **home, top, and front PNGs**. Check silhouette, scale, orientation, missing parts, unintended intersections, floating pieces, supported overhangs, and connections hidden from the home view. Add side/bottom views when necessary. Compare the Python BOM with `my-model-review/leocad-bom.csv` by part, colour, and quantity. Do not say you visually reviewed images unless you opened them.

For uncertain connections, use `inspect` for occurrence indices and `snap --moving N --fixed M` for candidate world transforms. Revalidate after applying a candidate. An AABB overlap is only a potential collision; correctly engaged studs and sockets normally overlap in bounding boxes. A connector algorithm's “confirmed” label and a single connected group are evidence, not guarantees of strength, legal stress, stability, or buildability.

For deeper examination:

```sh
./prepare-glb.sh --file output/my-model.mpd output/my-model.glb
```

Import that annotated GLB with Blender MCP into a separate collection and inspect suspect part geometry and custom properties. Establish the LDraw-to-Blender unit/axis conversion before comparing coordinates. Keep source changes in the plan/MPD and regenerate derived files. If a complex construction cannot be verified, simplify it to an inspected construction or report precisely what remains uncertain.

After the last source change, rerun the affected checks and regenerate the final renders/BOM. Deliver artifacts from the exact final MPD, not an earlier revision.

## 5. Deliver

Provide clickable paths to the final `.mpd`, editable plan or Python generator, validation report, BOM, and preview images. Briefly describe the model and its actual features, part count, checks performed, and any unresolved physical/inventory limitations. The tooling reports `physical_validity: not_proven`; describe concrete review evidence instead of declaring guaranteed correctness.

The task is complete when the requested model is generated, errors are fixed, warnings are assessed, final artifacts are consistent, and the visual/physical review is performed to the available tools' stated coverage. Do not stop at a design proposal or merely provide instructions for the user to run.
