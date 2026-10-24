# Flexible parts with LSynth

Use **lsynth-nova** to shape hoses, cables, strings, flexible axles, rubber bands and treads, or to lay out separate chain links. Keep the constraints as editable source, generate an MPD asset, then use the normal plan and review commands. The adapter uses the Python port's CLI; it does not implement another curve or belt solver.

**When designing or repairing a flexible part, read the [constraint authoring guide](flex-constraints.md)
and run `flex guide TYPE`.** It provides the family-specific process, endpoint and
wheel helpers, actual-output checks, repair decisions and executable experiments.
Author good constraints, synthesize early, inspect locally, then repair the
reported defect. Agents should use these shared tools instead of writing another
curve approximation or routing optimizer during a model build.

For the rigid construction around those paths, start with the [26 annotated construction studies](../../lsynth-examples/README.md) and [industrial assembly lessons](technic-patterns/industrial-assemblies.md): track carriers, pneumatic controls, cable terminations and shaped frames. Their supplied synthesis scenes are visual references; the smaller examples below are easier starting inputs for generation.

## Install and try

Keep the `lsynth-nova` checkout beside this repository:

```sh
./setup.sh --with-lsynth
./ldraw-agent flex types
./ldraw-agent flex guide TECHNIC_PNEUMATIC_HOSE_BEVELED
./ldraw-agent flex build examples/flex/hose.ldr --output output/flex/hose.mpd
./ldraw-agent review output/flex/hose.mpd --contacts none
```

Open the review's previews. [Small examples](../../examples/flex/README.md) cover a hose, a rubber band and a chain. Copy a constraint file into your own `output/` directory before editing it. `doctor` reports whether the optional package is installed. `LSYNTH_SOURCE=/path/to/lsynth-nova ./setup.sh --with-lsynth` accepts another checkout location. Ordinary setup and builds do not require LSynth; `uv sync` may remove this optional installation, so use the setup flag again afterward.

Authoring, constraint checks and synthesis need LSynth installed. Generated assets embed the required LSynth geometry and work with the ordinary LDraw library, including in LeoCAD, without that installation. Do not run `lsynth --install-parts` for this workflow: the adapter leaves the parts library unchanged.

## Describe a path

A hose uses at least two visible constraints, in path order, inside an ordinary LDR or MPD:

```text
0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4
1 4 -60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 0 -40 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
0 SYNTH END
```

Coordinates are LDU. Each marker's local **−Y axis points along the path**: away from the start, into the end. These matrices point along +X. Move markers to route the hose, and rotate them to control its direction. Use enough clearance for the actual cross section, and inspect bends and endpoints after every change. `flex types` lists supported methods, product aliases and marker parts. Product aliases are hints, not proof that the resulting pose has the correct manufactured length.

A band uses actual pulley, wheel or gear placements as constraints, in loop order. Choose only parts listed under `band_constraints`; their configured radii determine the wrap. `0 SYNTH INSIDE`, `OUTSIDE` and `CROSS` control the route. Start with two separated, coplanar pulleys and inspect a simple loop before adding crossings. Put each wheel in the source once. Visible wheel constraints remain real placements in the generated asset; `SYNTH HIDE` suppresses them when the wheels already belong to another assembly.

Use explicit colours in each SYNTH BEGIN. Keep the original visible constraints even if using `SYNTH HIDE`: LSynth comments markers out in its output, which cannot reliably reconstruct the source on a later run. The adapter rejects already synthesized inputs. Multiple SYNTH blocks and ordinary MPD submodels are supported; blocks must stay within one FILE section. Keep source section names unique when importing several assets, or use the existing `extract --namespace` command to rename a dependency closure.

## Generate and reuse

For a model plan, [declare the constraints directly in `assets`](plans.md#generated-flexible-assets). Then `review PLAN` handles constraint checks, synthesis, measurements, model validation and previews. The [pneumatic press](../../examples/flex/pneumatic-press/README.md) demonstrates this complete loop. Keep editable constraints beside the plan and use the same measured fitting/wheel placements for both rigid geometry and routes.

For a standalone asset:

```sh
./ldraw-agent flex build output/my-hose.ldr
# After changing the original constraints:
./ldraw-agent flex build output/my-hose.ldr --force
```

`flex build` runs source checks before synthesis and measures the generated result before publishing the MPD and manifest. It accepts the same geometric options as `flex check --asset`, such as `--min-radius 15` or `--min-separation 10`; select limits for the actual material and layout. Reports include coverage, measurements and warnings. Standalone `flex check` remains useful for diagnosis without generation or to inspect an existing asset.

Unchanged inputs reuse cached LSynth output. The key covers source, configuration, engine code/version and Python version. Packaging, library validation and measurements still run. `--no-cache` reruns the engine; `--force` permits replacing output after successful checks. Neither bypasses checks. `--timeout` bounds the synthesis subprocess.

The `.manifest.json` retains source/configuration hashes, engine version, source credits, embedded geometry provenance, each synthesized block and recorded compatibility repairs, and adds the geometry report. Unknown types, source errors, LSynth warnings, empty synthesis, assembly errors and failed geometric limits leave the previous MPD and manifest intact. `--namespace` sets the generated prefix; it defaults to the output filename stem. Original constraints are never overwritten.

Import it through the existing plan format. Place the `root` returned by `flex build`:

```json
{
  "version": 1,
  "author": "Your name",
  "assets": ["my-hose.mpd"],
  "sections": [{
    "name": "main.ldr",
    "description": "Assembly containing a posed hose",
    "steps": [[{"id": "hose", "ref": "my-hose.ldr", "colour": 4, "at": [0, 0, 0]}]]
  }]
}
```

Asset paths are relative to the plan. Regenerate after moving endpoints relative to one another; a rigid placement only moves the completed pose. The generated colour remains explicit. Use the normal `build` and `review` commands for the complete assembly, and deliver the constraint source and manifest with it.

## What the checks mean

Continuous hoses, cables, bands and one-piece rubber treads become **one posed embedded part per block**. LSynth's stretched cross sections belong inside that part's geometry, and are not independent BOM items. Separate Technic chain/tread links and BRICK_ARC bricks stay ordinary rigid physical placements. Minifigure chains are supplied as a complete item and stay one posed part. Posed part IDs describe geometry; they are not an inventory or retail part-number claim.

The normal prohibition on stretching, shearing or mirroring complete parts remains in force. For generated rigid links only, the adapter can recover rounding from LSynth's four-decimal output when each corrected matrix coefficient differs by at most 0.00005. Every such repair is recorded. It never applies this repair to input placements or to stretched hose/band geometry. Larger defects fail validation.

Check every route's bend radius as well as its endpoints. Fixed-segment types such as `TECHNIC_RIBBED_HOSE` place separate rigid rings about 5.5 LDU apart, and those rings open visible gaps once neighbours turn more than about 7°. LSynth's stiff curves can also form near-hairpins when waypoints sit close together. Stretched types such as pneumatic hose stay continuous, but can still bend too tightly or cross another hose.

The [pneumatic press](../../examples/flex/pneumatic-press/README.md) places hose ends on the nozzle frames from each part's shadow data. Its test measures sleeve seating, minimum bend radius, tube-to-tube distance and part clearance; reuse those checks for new routes.

Use the shared `flex check --asset` for new routes and read its explicit coverage.
Unlike the press's original fixture-specific tests, it never omits whole end
zones from pair/obstacle inspection, and `--block` includes neighbouring hoses.
The [constraint lab](../../examples/flex/constraint-lab/README.md) measures real
LSynth output for bends, return loops and bundles, including a deliberately bad bend.

Start flex studies with `review --contacts none`. Bounds, source checks, previews and BOM comparison still run, but connectivity and material clearance are not established. Posed parts have no verified connector metadata, stock length, tension, minimum bend radius or elasticity. Inspect the route, endpoint seating, obstructions and link engagement in the actual assembly; generic AABB overlaps cannot certify these. `physical_validity` stays `not_proven`.

The tested port is **lsynth-nova 3.1.0**, with its bundled definitions. This adapter currently uses default resolution: that version reads the wrong argument positions for `HOSE_RES` and `BAND_RES`, so custom resolution records are rejected. GHOST inputs are also unsupported. The standalone LSynth CLI remains available for other workflows; its raw output needs separate review before reuse here.

Legacy compatibility is confined to embedded copies: LS22's Latin-1 author header becomes UTF-8, and LS50/LS51's invalid `BFC CERTIFY INVERTNEXT` becomes `BFC INVERTNEXT`. Original hashes and changes are recorded; authorship, licence notices and geometry remain. Some bundled examples also contain missing legacy parts, nonrigid source placements or impossible pulley routes. A successful LSynth exit alone does not make those assemblies valid.
