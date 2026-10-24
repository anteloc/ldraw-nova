# Write a model plan

A plan is an ordinary JSON object describing parts, submodels and building steps. Edit it directly for small models; use Python to produce the same format for procedural designs. Both paths use the same builder and checks. There is no required intermediate generator.

## A complete small example

Save this as `output/stack.plan.json`:

```json
{
  "version": 1,
  "author": "Your name",
  "sections": [{
    "name": "stack.ldr",
    "description": "A blue plate on a red brick",
    "steps": [
      [{"id": "base", "ref": "3003.dat", "colour": 4, "at": [0, 0, 0]}],
      [{"id": "top", "ref": "3022.dat", "colour": 1, "on": "base"}]
    ]
  }]
}
```

```sh
./ldraw-agent review output/stack.plan.json
```

`build` writes `output/stack.mpd`. `review` puts checks, a frozen model copy, BOMs and previews in `output/stack-review/`. You can also run `review output/stack.plan.json` directly. Open the previews before accepting the construction. For a rebuild, add `--force`; explicit `--output` on `build` and `--outdir` on `review` override the defaults.

The upper plate's body is 8 LDU high, so `on` puts its origin at Y=-8. It does not add stud height. A different upper part requires its own body height; bounding-box height is not a stacking height.

## The format

The [JSON schema](../../ldraw_tools/data/plan.schema.json) is the complete contract. Unknown keys, malformed vectors, mixed position modes, duplicate IDs, unresolved references, invalid colours and nonfinite numbers fail explicitly.

- A plan has `version: 1`, an accurate `author` and ordered `sections`. Its first section is the scene main. An authorized `license` is optional.
- Each section has a unique flat `.ldr` name, a description and `steps`: arrays of placements. It may declare `anchors` and its own author/license.
- A placement has a section-local unique `id`, a real `ref`, a `colour` and exactly one position mode. Add `purpose` when it explains something useful.
- `includes` imports other JSON plans; `assets` imports MPDs or declares flexible sources (below). A section may link a `structure` contract. Paths are relative to the declaring plan, including inside includes. Names must remain unique across all inputs. Includes are loaded once and preserve their authorship; cycles fail.

Refs can be numeric filenames (`3003.dat`), module names (`pillar.ldr`) or category symbols (`@arches.Arch1X6X2WithThickTopAndReinforcedUnderside`). Colours can be palette codes or symbols such as `@colours.Tan`. The builder resolves symbols against the installed library without changing the editable plan.

## Choose a placement

| Position mode | Use it for | Example |
|---|---|---|
| `at` | Explicit coordinates in the containing section | `"at": [0, -24, 40]` |
| `on` | Stacking supported upright bricks/plates on an earlier placement | `"on": "base"` |
| `attach` | Aligning authored module anchors | `"attach": {"to": "lower", "anchor": "seat", "using": "base"}` |
| `snap` | Aligning actual connector evidence on a part/submodel | `"snap": {"to": "base", "near": [0, -8, 0]}` |

`at`, `on` and `snap` allow `yaw` (degrees about +Y) or a proper 3×3 `matrix`, never both. `attach` sets the orientation itself. Use `./ldraw-agent matrix y 90` or `rotation("y", 90)` to compute rotations. Coordinates use LDU: negative Y is up, stud pitch is 20, brick body height is 24, plate body height is 8.

`on` only supports the curated upright studded bricks/plates listed by `profiles`. Its optional `offset_studs: [x,z]` uses the support's axes. For example, a 1×1 above a centered 2×2 needs an actual stud offset such as `[0.5,0.5]`. For other parts, inspect their origin and connectors, then use `at`, anchors or snapping.

`attach` aligns both named frames; optional `offset` is in the supporting anchor's axes. Frames contain `at` and an optional proper `matrix`. Anchors describe intended interfaces, so verify the actual mating parts. The [module guide](complex-models.md#3-define-module-contracts) has a complete floor-to-floor example.

`snap` moves the whole selected part/submodel and checks candidate collisions. It supports explicit leaf/feature selectors and a candidate index; see the [snapping guide](snapping.md). Missing metadata or eligible candidates fail explicitly rather than inventing a connection.

With `at`, `repeat: {"count": 8, "step": [40,0,0]}` repeats in the containing section's axes. IDs become `id-0`, `id-1`, etc. For conditional patterns, use Python loops instead.

## Grow the model when needed

The [bridge](../../examples/bridge.plan.json) demonstrates reusable colour-inheriting pillars. The [Copper Lane plans](../../examples/modular-street/scene.plan.json) demonstrate includes, module anchors and a larger scene. Keep module origins and connection surfaces clear, and check each module before composing it with neighbors.

Use colour 16 inside reusable submodels only when an explicit ancestor colour resolves every visible leaf. Colour 24 is for edges, not placements. Subassemblies belong in embedded `.ldr` blocks; classified imported `.dat` parts retain geometry, transforms and attribution and count as single physical leaves. Avoid loose external models, library-name shadowing, duplicate placements and dependency cycles.

Use `extract --section NAME --namespace UNIQUE --output output/assets/NAME.mpd` to copy an attributed dependency closure from a reference. Keep its `.manifest.json` and use the returned `root` name in the plan. Extraction may retain invalid source for review: check its diagnostics before reuse. Explicit BFC/rotation repairs are recorded changes, not physical certification.

## Generated flexible assets

Declare original LSynth constraints in `assets`; `build` and `review` prepare them automatically:

```json
{
  "version": 1,
  "author": "Your name",
  "assets": [{"source": "hoses.ldr", "namespace": "my-hoses", "checks": {"min_radius": 15}}],
  "sections": [{
    "name": "machine.ldr",
    "description": "Hose route study",
    "steps": [[{"id": "hoses", "ref": "my-hoses.ldr", "colour": 4, "at": [0, 0, 0]}]]
  }]
}
```

For a single-section LDR source, the root is `NAMESPACE.ldr`. MPD sources retain their declared FILE names; use the actual root name. Choose distinct namespaces and FILE names for different assets. The generated parts are embedded in the final MPD; consumers do not need LSynth or the cache.

`timeout` optionally sets the synthesis deadline in seconds (default 90). `checks` is optional. It accepts `min_radius`, `max_turn`, `tube_radius`, `min_separation`, `length`, `length_tolerance`, `block`, `obstacles` and `obstacle_section`, with the same meanings as `flex check --asset`. Distances are LDU. These are chosen geometric limits, not certified material properties. Obstacle models must use the constraints' frame. Band/chain closure still requires visual inspection.

Constraints are checked before synthesis. The actual generated asset is validated and measured afterward; failed checks prevent the model build. Results live under `.cache/flex-assets/`. Synthesis reuse depends on source, configuration, engine code/version and Python version; the current library and geometric limits are checked every time. A damaged synthesis cache is rebuilt. Delete `.cache/flex-synthesis/` to discard cached synthesis, or use standalone `flex build --no-cache` for a diagnostic run.

Review records these results in `validation.json` under `flex`, and copies constraints, MPDs and manifests into `flex/` in its output bundle. Keep your editable sources beside the plan. See the [complete pneumatic press](../../examples/flex/pneumatic-press/README.md) and [constraint authoring](flex-constraints.md).

Existing `"assets": ["hoses.mpd"]` entries remain portable and do not require LSynth. For manual generation, `flex build hoses.ldr` writes `hoses.mpd` and its manifest after the same checks.

## Automatic Technic checks

Put `"structure": "frame.structure.json"` on the section whose occurrence indices the contract describes. `technic plan` writes this link for you. `build` and `review` run that section's required-joint, seating, restraint and assembly-order checks, even with `--contacts none`. Included plans retain their own section contracts and relative paths.

Review saves the results under `structure` in `validation.json` and copies the contracts into `structure/`. A stale model hash or invalid occurrence index fails explicitly. Regenerate and review contracts after changing structural geometry or ordering; do not discard the mismatch. [Technic contracts](technic.md#check-intended-joints-and-restraint) describe the coverage and limitations.

## Use Python for calculations

The [Python example](../../examples/python_api.py) produces a four-brick tower and preserves its editable plan:

```sh
.venv/bin/python examples/python_api.py
./ldraw-agent review output/tower.mpd
```

For larger procedural patterns, see the [Copper Lane generator](../../examples/modular-street/generate.py). Generate ordinary dictionaries and lists, keeping geometry fixes in the generator so rebuilding preserves them.

| API | Purpose |
|---|---|
| `builder.load_plan(path)` | Resolve relative includes/assets and preserve headers |
| `builder.build_plan(plan, parts)` | Produce serialized text, parsed model and source diagnostics |
| `workflow.build_checked(plan, parts, **geometry_options)` | Run geometry and declared structural checks; return text, model and combined report |
| `builder.rotation(axis, degrees)` | Compute a proper rotation |
| `common.get_parts()` | Load the configured parts library and shadow metadata |
| `geometry.analyze_geometry(model, parts, ...)` | Inspect geometry and connection evidence independently |

`build_plan` prepares declared flexible assets but does not run full assembly geometry or structural contracts. Use `load_plan` followed by `build_checked` for the complete build path, and check its report before writing output. `ldraw.Model`, `Piece`, `Matrix` and `Vector` also remain available from pyldraw3; validate serialized bytes when using them directly. Do not add a second parser/serializer.

The builder emits UTF-8 without BOM, CRLF, headers, comments and steps. It supports rigid placement of real parts, including SNOT orientations; physical verification has narrower coverage. New part geometry, model polygons, textures/data and local colours need the additional review described in [LDraw rules](ldraw-reference.md) and [validation](validation.md).
