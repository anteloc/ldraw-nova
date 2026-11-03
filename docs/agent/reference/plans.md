# Plan format and builder API

## The format

The [JSON schema](../../../ldraw_tools/data/plan.schema.json) is the complete contract. Unknown keys, malformed vectors, mixed position modes, duplicate IDs, unresolved references, invalid colours and nonfinite numbers fail explicitly.

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

`attach` aligns both named frames; optional `offset` is in the supporting anchor's axes. Frames contain `at` and an optional proper `matrix`. Anchors describe intended interfaces, so verify the actual mating parts. The [module guide](plans.md#3-define-module-contracts) has a complete floor-to-floor example.

`snap` moves the whole selected part/submodel and checks candidate collisions. It supports explicit leaf/feature selectors and a candidate index; see the [snapping guide](connections.md). Missing metadata or eligible candidates fail explicitly rather than inventing a connection.

With `at`, `repeat: {"count": 8, "step": [40,0,0]}` repeats in the containing section's axes. IDs become `id-0`, `id-1`, etc. For conditional patterns, use Python loops instead.

## Grow the model when needed

The [bridge](../../../examples/plan-basics/bridge.plan.json) demonstrates reusable colour-inheriting pillars. The [Copper Lane plans](../../../examples/copper-lane/scene.plan.json) demonstrate includes, module anchors and a larger scene. Keep module origins and connection surfaces clear, and check each module before composing it with neighbors.

Use colour 16 inside reusable submodels only when an explicit ancestor colour resolves every visible leaf. Colour 24 is for edges, not placements. Subassemblies belong in embedded `.ldr` blocks; classified imported `.dat` parts retain geometry, transforms and attribution and count as single physical leaves. Avoid loose external models, library-name shadowing, duplicate placements and dependency cycles.

Use `extract --section NAME --namespace UNIQUE --output output/assets/NAME.mpd` to copy an attributed dependency closure from a reference. Keep its `.manifest.json` and use the returned `root` name in the plan. Extraction may retain invalid source for review: check its diagnostics before reuse. Explicit BFC/rotation repairs are recorded changes, not physical certification.

## Use Python for calculations

The [Python example](../../../examples/plan-basics/python_api.py) produces a four-brick tower and preserves its editable plan:

```sh
.venv/bin/python examples/plan-basics/python_api.py
./ldraw-agent review output/tower.mpd
```

For larger procedural patterns, see the [Copper Lane generator](../../../examples/copper-lane/generate.py). Generate ordinary dictionaries and lists, keeping geometry fixes in the generator so rebuilding preserves them.

| API | Purpose |
|---|---|
| `builder.load_plan(path)` | Resolve relative includes/assets and preserve headers |
| `builder.build_plan(plan, parts)` | Produce serialized text, parsed model and source diagnostics |
| `workflow.build_checked(plan, parts, **geometry_options)` | Run geometry and declared structural checks; return text, model and combined report |
| `builder.rotation(axis, degrees)` | Compute a proper rotation |
| `common.get_parts()` | Load the configured parts library and shadow metadata |
| `geometry.analyze_geometry(model, parts, ...)` | Inspect geometry and connection evidence independently |

`build_plan` prepares declared flexible assets but does not run full assembly geometry or structural contracts. Use `load_plan` followed by `build_checked` for the complete build path, and check its report before writing output. `ldraw.Model`, `Piece`, `Matrix` and `Vector` also remain available from pyldraw3; validate serialized bytes when using them directly. Do not add a second parser/serializer.

The builder emits UTF-8 without BOM, CRLF, headers, comments and steps. It supports rigid placement of real parts, including SNOT orientations; physical verification has narrower coverage. New part geometry, model polygons, textures/data and local colours need the additional review described in [LDraw rules](ldraw.md) and [validation](validation.md).

## 3. Define module contracts

Before populating parts, record each module's purpose, approximate envelope, local origin, attachment frames, inherited palette, construction steps, and review status. For a building, start with the street/base, then separate each floor, façade detail, roof, interior and landscaping. Keep the main section short enough to read in one screen.

In JSON plans, a section can expose named **anchor frames**:

```json
"anchors": {
  "base": {"at": [0, 8, 0]},
  "next": {"at": [0, -160, 0]}
}
```

These match Copper Lane's floor plate: its underside is at +8, while its cornice top is at -160. The resulting storey pitch is 168 LDU. Frames may have an explicit proper `matrix`; omitted matrices are identity. Keep the interface clear of decorative geometry and leave actual attachment studs/sockets accessible.

A containing section can place a floor and attach another:

```json
[
  {"id":"lower", "ref":"lane-ground.ldr", "colour":19, "at":[0,-8,0]},
  {"id":"upper", "ref":"lane-upper.ldr", "colour":19,
   "attach":{"to":"lower", "anchor":"next", "using":"base"}}
]
```

The builder solves `T_moving = T_support × A_support × T_offset × inverse(A_moving)`. All matrices act on column vectors. Optional `attach.offset` is in the supporting anchor's axes. The target ID must already exist in this section, including earlier steps. `attach` sets both position and orientation: do not combine it with `at`, `on`, `yaw`, `matrix`, or `repeat`. Anchors are authored assembly interfaces, **not inferred mechanical connectors**. Check the parts at each interface.

## 4. Compose plans and repeat structure

A main plan can use `"includes": ["buildings.plan.json"]`; that plan can include `details.plan.json`. Paths resolve relative to the file declaring them, each file loads once, cycles fail, and duplicate section names fail. The first section of the root plan remains the MPD main. Each module retains its own author/licence unless it explicitly supplies section-level values.

Use `"assets": ["assets/clock.mpd"]` to embed an extracted MPD's definitions. Assets resolve relative to their declaring plan and retain original headers. Names must not collide with generated sections, other assets, or the official library. Final validation checks the combined source and inherited colours. Imported assets use inspected `at` placements; named anchors are currently declared on generated JSON sections.

For a regular row:

```json
{"id":"roof-slope", "ref":"3039.dat", "colour":320,
 "at":[-140,-24,-130], "repeat":{"count":8,"step":[40,0,0]}}
```

This expands to IDs `roof-slope-0` through `roof-slope-7`. `step` is a translation in the containing section's axes, in LDU; it does not rotate with `yaw`. Repetition is supported with `at` only. Use an included submodel for a repeated multi-part construction. Use a small Python generator for conditional openings, different floor counts, brick bonds and parameterized patterns; serialize through `build_plan`, not a handwritten LDraw parser.

## Reproducible plans

Build the supplied example:

```sh
./ldraw-agent build examples/plan-basics/shadow-snap.plan.json --output output/shadow-snap.mpd
```

Use `snap` as the fourth placement mode alongside `at`, `on`, and `attach`:

```json
{"id":"cap", "ref":"cap.ldr", "colour":1,
 "snap":{"to":"base", "near":[0,-8,0], "moving_leaf":0, "fixed_leaf":0}}
```

`to` names an earlier placement in the same section. `near` is an initial position in that section's coordinates and guides ranking; it defaults to the support's position. Optional `yaw` or `matrix` supplies the initial orientation. The solver determines the final pose. `moving_leaf` and `fixed_leaf` default to zero and select physical leaves within the moving and supporting references. Both can refer to complete submodels; the entire moving reference is repositioned rigidly. Modules are built in dependency order, while the first declared section remains the MPD root.

Optional `moving_feature`, `fixed_feature`, and `candidate` make interface selection explicit. A plan snap checks up to 100 distinct candidates. It fails for absent interfaces, invalid leaf indices or a selected body collision. `snap` cannot coexist with `at`, `on`, `attach`, `offset_studs`, or `repeat`. Ordinary plan validation still applies. Keep edits in the plan when rebuilding generated models.

Python entry points are `connection_report`, `snap_report`, and `apply_snap` in `ldraw_tools.connectivity`. The existing `ldraw_tools.geometry.snap` remains a list-returning convenience wrapper; use `snap_report` to retain coverage and search-limit information.

## Declared checks and flexible placements

Use named inline [structure contracts](technic.md#name-the-intended-connections) for new work; numeric external contracts remain supported. Both build and review execute declared checks. [Flexible placements and generated assets](flex.md) document named endpoints, mounted-wheel ownership, source paths, caching, output measurements and compatibility with existing MPD assets.

