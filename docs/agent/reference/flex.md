# Flexible placement fields and LSynth contracts

## Connect actual fittings

An inline flex placement goes into the same `steps` arrays as rigid parts:

```json
{
  "id": "supply",
  "colour": 0,
  "flex": {
    "method": "TECHNIC_PNEUMATIC_HOSE_BEVELED",
    "from": {"part": "controls/pump", "port": "outlet", "lead": 22},
    "to": {"part": "controls/valve", "port": "inlet", "lead": 22},
    "checks": {"min_radius": 15, "tube_radius": 5, "min_separation": 10}
  }
}
```

`part PART` lists the measured named ports and whether their geometry matches.
The initial set covers pump `2797c01-f1` (`outlet`), valve `4694c01-f1`
(`upper`, `inlet`, `lower`) and extended cylinder `74981-f2` (`base`, `rod`).
Names describe fitting locations, not a verified pneumatic control circuit.

Use `feature` instead of `port` for an explicitly inspected library connector.
For a measured interface without metadata, use `at` and `outward` instead;
both are local to the referenced part. Optional `up` is also part-local.
These escape hatches require inspection; a generic pin is not automatically a
hose nozzle. No coordinates are inferred from appearance.

Endpoint directions point **out** of both fittings. `lead` is the straight
departure in LDU. Optional `via` points are in the containing section's frame:
either `[x,y,z]` or `{"at":[x,y,z],"direction":[dx,dy,dz],"up":[ux,uy,uz]}`.
Waypoint directions follow travel. Omit direction for an inferred tangent;
flat cables need deliberate roll. Moving a module composes every parent transform.

The shown limits belong to the pneumatic example, not every LEGO material.
`flex guide TYPE` explains other families. Python's `corner_waypoints`,
`return_waypoints` and `offset_waypoints` produce ordinary waypoint data for
tested control layouts; use `jsonable()` to put it in a plan. Their control radius
does not promise the synthesized bend radius. LSynth and the actual-output
checks remain authoritative for the selected geometric criteria.

## Wrap mounted wheels

```json
{
  "id": "chain",
  "colour": 72,
  "flex": {"method": "TECHNIC_CHAIN_LINK", "wheels": ["drive-gear", "idler-gear"]}
}
```

The wheels are existing rigid placements, including their actual rotations.
Routing copies are hidden automatically: each wheel appears once in the BOM.
Interleave `{"control":"INSIDE"}`, `OUTSIDE` or `CROSS` when required by a
studied layout. Do not append the first wheel to close the loop. The
[chain drive](../../../examples/workshop/chain-drive/model.plan.json) supplies the
bearings, spacers, stops and hand crank missing from an isolated loop fixture.

Wheel planes and source controls are checked before synthesis. Link rotations
remain rigid. Inspect closure and engagement: the output file's placement order
is not loop traversal order, and there is no automatic closure certification.

## Review the affected assembly

```sh
./ldraw-agent review output/machine.plan.json --section chain-drive.ldr --no-render
./ldraw-agent review output/machine.plan.json --views home front back top
```

Use `--force` for a generated review rerun. Scoped reviews have a separate
default directory and explicitly exclude parent/sibling interfaces. Finish with
the whole-model review and open its images.

The builder resolves rigid parts first, writes ordinary LSynth constraints,
checks and synthesizes them, then inserts the generated geometry at the authored
STEP. A rigid part cannot depend on generated flex geometry. External sources
and prebuilt assets remain supported and retain their ownership conventions.

`validation.json` contains the source map, named structural failures, route
measurements and interaction checks. Reports name the source file, JSON
location and placement whenever available. Original plans, generated constraints,
assets and contracts are frozen and hashed in the review bundle. Python-generator
dependencies and the complete installed parts library are not snapshotted.

Inline hoses are compared across module instances in the reviewed assembly's
frame. Explicit minimum separation applies to each pair; when both tube radii
are supplied, their sum also sets a lower bound. Without a limit, distance is
measured but no clearance acceptance is claimed. A tube radius also enables
conservative obstacle candidates. These include fitting regions and holes;
inspect the named candidates rather than treating bounding boxes as material.

Repair the first failed prerequisite. After two unsuccessful corrections,
inspect an isolated route/module and change the approach or available space.
Keep the limits and requested features intact. Unchanged synthesis is cached,
but current library checks and assembly interactions run again.

## Author hoses from interfaces

`Endpoint.outward` points **out of the fitting** at both ends. `Waypoint.direction`
points **along the route**. The helper reverses the final outward direction once.
`lead` is a straight departure distance in LDU, chosen for the actual fitting.
It is not a universal value or an extra part.

```python
from pathlib import Path
from ldraw_tools.flex_authoring import Endpoint, Waypoint, document, hose

# These coordinates are a geometry fixture. In a model use measured fittings.
start = Endpoint((0, 0, 0), (1, 0, 0), lead=22, up=(0, 0, 1))
end = Endpoint((140, -100, 0), (0, 1, 0), lead=22, up=(0, 0, 1))
source = document(hose(start, end, via=[
    Waypoint((80, 0, 0), (1, 0, 0), up=(0, 0, 1)),
    Waypoint((140, -60, 0), (0, -1, 0), up=(0, 0, 1)),
], name="valve-to-cylinder"))
Path("output/my-hoses.ldr").write_bytes(source.encode())
```

For a measured local interface, use
`Endpoint.on_part(part_at, part_matrix, local_at, local_outward, lead=22)`.
For an explicitly identified connector from `part PART`, use
`Endpoint.from_feature(parts, part_code, feature_id, at=part_at,
matrix=part_matrix, lead=22)`. This follows the actual part placement; it does not
guess which generic pin/stud is a nozzle. Inspect the chosen feature and its axis.
Use the same placement variables for the rigid part and endpoint.

The CLI is convenient for simple paths:

```sh
./ldraw-agent flex hose --start 0 0 0 --start-direction 1 0 0 \
  --end 160 0 0 --end-direction -1 0 0 --lead 22 \
  --output output/lead.ldr
./ldraw-agent flex build output/lead.ldr \
  --min-radius 15 --tube-radius 5 --report output/lead-check.json
./ldraw-agent review output/lead.mpd --contacts none
```

The radius 5 is the round LS23 tube used here. The bend limit 15 is a chosen
geometric criterion used by the press fixture, **not a certified LEGO material
limit**. Select limits and cross sections deliberately for other families.
`--via x y z` is repeatable. Use Python `Waypoint` for deliberate tangent/roll
control; the CLI infers intermediate tangents. Specify consistent `up` vectors
for flat cables. An up vector parallel to travel is invalid. Keep endpoint and
waypoint coordinates in one frame; never mix a local cylinder frame and world
coordinates in a block.

## Author loops from the mounted wheels

```python
from ldraw_tools.flex_authoring import band, document, placement

source = document(band([
    placement("4019.dat", (-60, 0, 0)),
    placement("4019.dat", (60, 0, 0)),
], method="TECHNIC_CHAIN_LINK", name="drive-chain", hide=True))
```

This example assumes the rigid assembly already owns the two gears. Omit
`hide=True` if the asset owns them. Each physical wheel must occur exactly once.
The loop closes automatically: do not repeat the first wheel just to close it.
If a studied route intentionally revisits a wheel, keep one physical wheel and
hide the routing constraints.

Interleave `"0 SYNTH OUTSIDE"`, `"0 SYNTH INSIDE"` and `"0 SYNTH CROSS"` with the
wheel rows when needed. These affect routing; they do not mount or align wheels.
INSIDE/OUTSIDE select the wrap side; CROSS toggles it for following wheels.
Controls after the last wheel also affect the closing run back to the first.
Use the actual wheel placements and the definition's effective wheel planes.
LSynth flattens band constraints into its first wheel's plane; `flex check`
detects offsets and inconsistent axes before that error becomes invisible.
Supply shafts, bearings, retention and compatible wheels yourself. Inspect the
closure seam and both runs after synthesis. LSynth's band output order is not
traversal order: it emits a straight run before the arc around that run's wheel.
Do not join successive file records to infer loop length, curvature or closure.

## Read the check's coverage

`flex check SOURCE` checks control structure, recognized constraints, rotations,
marker coincidence, suspicious tangent directions, band planes and tangent
existence. It cannot establish a collision-free or physically usable route.

`flex check SOURCE --asset ASSET.mpd` requires the matching manifest and measures
actual generated placements. For hoses it reports bend samples, adjacent segment
turns, segment spacing and length. For bands it reports placement counts and
origin bounds; closure and engagement require inspection. Single stretched cable
spans are measured from their generated transform. Other lengths are measured
along successive segment origins; they omit family-specific end offsets and are
not stock lengths. Use `--length` and `--length-tolerance` for an explicit geometric
target on one hose. Do not compare different measurement bases as physical lengths.

`--min-radius`, `--max-turn`, `--tube-radius` and `--min-separation` add explicit
criteria. Round-envelope self checks exclude nearby arc-length neighbours;
local bend and segment-turn review remain necessary. Other cross sections need
their own inspection. Sleeve matching is calibrated for the beveled pneumatic
family only, against source markers; the actual fittings still need review.

`--block N` measures one block and checks it against its same-section hose
neighbours. Different FILE sections use different local frames: combine routes
into the same frame to check them together. Final review must cover all blocks.

`--obstacles rigid.mpd --tube-radius R` flags conservative oriented-box candidates
in the **same coordinate frame**. `--obstacle-section NAME` selects a local
submodel. These boxes include holes and mating regions, so overlaps are warnings
to inspect, not proven material collisions. Missing obstacle geometry fails.
No endpoint regions are exempted. Use a rigid-only model or section to avoid
treating the hose itself as an obstacle. Multiple route frames require `--block`.

Exit 0 means selected automatic checks passed; warnings, unmeasured properties
and image inspection remain explicit. Exit 1 means a check failed; 2 means an
input/dependency/execution failure. Reports include source/output hashes and the
selected limits. Read `coverage` and `diagnostics`, not just `checks_passed`.

## Install and try

Install the pinned **lsynth-nova 0.5.0** release wheel from `anteloc/lsynth-nova` (no separate checkout needed). Setup uses uv when available, with pip as a fallback:

```sh
./setup.sh --with-lsynth
./ldraw-agent flex types
./ldraw-agent flex guide TECHNIC_PNEUMATIC_HOSE_BEVELED
./ldraw-agent flex build examples/flex/hose.ldr --output output/flex/hose.mpd
./ldraw-agent review output/flex/hose.mpd --contacts none
```

Open the review's previews. [Small examples](../../../examples/flex/README.md) cover a hose, a rubber band and a chain. Copy a constraint file into your own `output/` directory before editing it. `doctor` reports whether the optional package is installed. Ordinary setup and builds do not require LSynth. When syncing directly, use `uv sync --locked --extra test --extra lsynth` to retain both testing and synthesis tooling; syncing without the `lsynth` extra removes it.

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

For a model plan, [declare the constraints directly in `assets`](flex.md#generated-flexible-assets). Then `review PLAN` handles constraint checks, synthesis, measurements, model validation and previews. The [pneumatic press](../../../examples/flex/pneumatic-press/README.md) demonstrates this complete loop. Keep editable constraints beside the plan and use the same measured fitting/wheel placements for both rigid geometry and routes.

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

The [pneumatic press](../../../examples/flex/pneumatic-press/README.md) places hose ends on the nozzle frames from each part's shadow data. Its test measures sleeve seating, minimum bend radius, tube-to-tube distance and part clearance; reuse those checks for new routes.

Use the shared `flex check --asset` for new routes and read its explicit coverage.
Unlike the press's original fixture-specific tests, it never omits whole end
zones from pair/obstacle inspection, and `--block` includes neighbouring hoses.
The [constraint lab](../../../examples/flex/constraint-lab/README.md) measures real
LSynth output for bends, return loops and bundles, including a deliberately bad bend.

Start flex studies with `review --contacts none`. Bounds, source checks, previews and BOM comparison still run, but connectivity and material clearance are not established. Posed parts have no verified connector metadata, stock length, tension, minimum bend radius or elasticity. Inspect the route, endpoint seating, obstructions and link engagement in the actual assembly; generic AABB overlaps cannot certify these. `physical_validity` stays `not_proven`.

The pinned port is **lsynth-nova 0.5.0**, with its bundled definitions. This adapter supports default resolution only; custom `HOSE_RES` and `BAND_RES` records are rejected. GHOST inputs are also unsupported. The standalone LSynth CLI remains available for other workflows; its raw output needs separate review before reuse here.

Legacy compatibility is confined to embedded copies: LS22's Latin-1 author header becomes UTF-8, and LS50/LS51's invalid `BFC CERTIFY INVERTNEXT` becomes `BFC INVERTNEXT`. Original hashes and changes are recorded; authorship, licence notices and geometry remain. Some bundled examples also contain missing legacy parts, nonrigid source placements or impossible pulley routes. A successful LSynth exit alone does not make those assemblies valid.

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

Review records these results in `validation.json` under `flex`, and copies constraints, MPDs and manifests into `flex/` in its output bundle. Keep your editable sources beside the plan. See the [complete pneumatic press](../../../examples/flex/pneumatic-press/README.md) and [constraint authoring](../guides/flex.md).

Existing `"assets": ["hoses.mpd"]` entries remain portable and do not require LSynth. For manual generation, `flex build hoses.ldr` writes `hoses.mpd` and its manifest after the same checks.

