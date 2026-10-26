# Named joints and flexible routes

Use an ordinary JSON plan and `review`. Placements, required connections and
flexible routes can now share names, so editing a part does not require updating
an occurrence-index table or a second set of endpoint coordinates.

Start with the [workshop constructions](../../examples/workshop/README.md) or the
[pneumatic press plan](../../examples/flex/pneumatic-press/named.plan.json).
The existing [plan format](plans.md), external assets and Python APIs still work.

## Name the intended connections

Each placement already has an `id`. A path such as `ram/cylinder` selects that
part through its parent placement. Paths are relative to the containing section;
use every parent ID. Repeated placements use their expanded `id-0`, `id-1` names.
Names refer to the current source, not the order of parts in an inspection.

Put the structural intent directly on the section:

```json
"structure": {
  "require_rigid": true,
  "required_joints": [
    {"between": ["pin", "left"]},
    {"between": ["pin", "right"]}
  ],
  "assembly": [{"connector": "pin", "before": ["right"]}]
}
```

This checks the two actual joints and requires an earlier STEP for the pin.
The existing Technic seating, occupied-span and restraint rules still apply.
Use `"retained_axles": ["drive-axle"]` when both axial stops are required;
a still-engaged bush with a gap against its supported stack then fails review.
Use `"scope": "joints"` for mounts in a delivered mechanism pose; it checks
declared connections and seating without claiming that the whole machine is
rigid. Keep `require_rigid` off in that scope. Neither scope verifies motion.

Old `"structure": "frame.structure.json"` files retain their numeric indices
and revision checks. Imported MPDs retain their numeric inspection selectors;
named paths require authored plan placements. A path to a whole module does not
identify one physical joint: select its actual mating part.

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
[chain drive](../../examples/workshop/chain-drive/model.plan.json) supplies the
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
