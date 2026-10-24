# Design and repair LSynth constraints

Read this when a model needs hoses, cables, strings, flexible axles, belts, chains
or treads. Start with `./ldraw-agent flex guide TYPE`: it reads the installed
definition and gives the relevant family, endpoint/segment parts, constraints,
design rules, inspection points and reference. `flex guide` lists all families.
The [integration guide](flexible-parts.md) covers installation and MPD assets.

## The working loop

1. Pick the actual family and fittings. Define the delivered poses and which
   properties must be checked. A curve, a fixed-length item and a moving circuit
   have different acceptance conditions.
2. Place the rigid hardware, including mounts, shafts, retainers and plugs. Read
   its actual local interfaces with `part PART` or `connections MODEL`. Reserve
   a passage and end approaches before adding nearby bodywork.
3. Write visible constraints for one route or interacting group. Run `flex check`
   to catch source and layout mistakes before synthesis.
4. Run `flex build` immediately. Run `flex check --asset` on the actual result,
   then render it with its fittings and neighbouring geometry. Open the images.
5. Repair the reported span or fitting. Recheck nearby routes. If two corrections
   leave the same defect, change the passage, loop or hardware orientation.
   Preserve the last accepted route; broad random parameter searches are not the
   normal authoring method.

Constraints express geometric intent. They do not automatically avoid obstacles,
produce gravity sag, maintain physical length or establish mechanical connections.
Good constraints make the passage and directions unambiguous with few markers.
More markers are useful only when they specify a necessary feature of the route.

## Choose the right kind of route

| Family | What to author and inspect |
| --- | --- |
| Pneumatic tubing | Pump/valve/tee/cylinder ports, straight departures, useful slack, separated lanes. Seat the actual end sleeves. Branch only at actual fittings. |
| Electrical leads | Plugs, motors, batteries and junctions first. Preserve the flat cable's roll; leave connector insertion and battery access. Check both branches of a light lead. |
| Optical fibres | Correct distributor and end fittings, thin versus broad guide cross section, ordered fan-out. Missing legacy parts remain errors. |
| Flexible axles and Flex-System | Distinguish rotating axle ends, inner cable ends and fixed outer guide supports. Provide actual retention and travel space. |
| Ribbed/corrugated hoses | Broad curves and correct end seats. Inspect ring gaps and intersections, not just the centreline. Fixed segment counts do not certify stock length. |
| String and rope | Actual anchors, sheaves, supported drum and hook. Author slack explicitly; respect grips and a chosen length. `STRING_BAND` uses wheel constraints. |
| Minifigure chain | Real end links, alternating links and a plausible span. One complete chain remains one BOM item. |
| Rubber bands/belts/moulded treads | Coplanar mounted wheels, correct routing order and both loop runs. The output is one posed item; size and tension need separate evidence. |
| Rigid chain/tread links | Compatible wheel/link family, closure seam, pitch, engagement, supports and return-run clearance. Each link stays rigid and separate in the BOM. |
| Brick arcs | Shape studies only until real brick connections are supplied. The installed port's straight BRICK_ARC fixture emits reflected bricks and fails rigid validation. Do not bypass that failure. |

Aliases and product nicknames are resolved by the installed definitions, not
guessed from similar names. A wheel listed in the global band table is not
necessarily compatible with every belt or chain. Use a demonstrated family pair;
substituting a wheel requires checking its engagement, radius and mounting stack.

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
./ldraw-agent flex check output/lead.ldr
./ldraw-agent flex build output/lead.ldr --output output/lead.mpd
./ldraw-agent flex check output/lead.ldr --asset output/lead.mpd \
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

## Use diagnostics to make a local repair

| Diagnostic or symptom | Action |
| --- | --- |
| Unknown method, ignored part, insufficient markers | Use `flex guide TYPE`; move rigid context outside SYNTH and use recognized constraints. Check exact aliases. |
| Hidden/source controls, synthesized input | Restore the editable visible constraints. `SYNTH HIDE` hides output wheels; commented type-1 input is ignored. |
| Nonfinite, scaled, sheared or reflected constraint | Recreate a proper rotation from directions; do not normalize an arbitrary distorted part. |
| Coincident markers | Remove duplicates, or shorten a lead that reaches the next waypoint. A reversal needs a real loop. |
| Backward tangent / hairpin | Check the final endpoint sign and the marked span. Choose the other side of the obstacle or a wider return. A warning may be intentional; inspect it. |
| Bend too tight | Inspect the actual reported location. Increase space or change the approach. Adding a midpoint can tighten the bend. |
| Ribbed hose gaps | Inspect adjacent segment turns and ring geometry; use a broader curve. A continuous pneumatic rendering is not a physically equivalent substitution. |
| Flat cable twists | Keep deliberate roll/up directions, inspect plug orientation, and route with fewer unnecessary twists. |
| Pair/self intersection | Change lane or loop at the reported crossing. Pair checks include endpoint regions; do not exempt an entire short hose. |
| Wheel-plane mismatch | Align the effective wheel planes, including configured offsets; rotate the complete mounted wheel correctly. |
| No tangent / warning despite exit 0 | Inspect wheel order, spacing, routing controls and actual radii. The adapter treats LSynth warnings as failure. |
| Link gap, overlap or wrong engagement | Verify the wheel family and spacing, inspect the closure seam and change the layout. Never stretch or mirror rigid links. |
| Stale asset report | Rebuild from the saved source. Source, output and definition hashes must match. |
| Missing legacy geometry | Locate the correct part or make an explicit inspected substitution. Do not hide the missing reference. |
| Custom resolution / GHOST rejected | Use the supported defaults and visible input. See the adapter's documented version-specific restrictions. |
| Material length changes between poses | Add and account for actual slack or revise the layout. Different regenerated curves do not establish one moving physical hose. |

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

## Learn from actual synthesis

The [constraint lab](../../examples/flex/constraint-lab/README.md) contains
executable straight, bend, return and bundle experiments plus a deliberately
failing tight bend. It calibrates through actual LSynth output, not a duplicate
curve algorithm. Change one feature, synthesize and compare measurements and
images. Supported fixture results do not automatically generalize to a new size,
marker orientation, cross section or crowded assembly.

For a new family, run its guide and a small isolated route first; then seat it on
the actual fittings and inspect it in context. Reuse the complete
[pneumatic press](../../examples/flex/pneumatic-press/README.md) for the latter
step. Complete the normal assembly/BOM/image review after the last route edit.

For multiple poses, preserve the physical part identities and required lengths,
regenerate each pose and inspect extremes plus intermediate configurations where
clearance is uncertain. A sampled sweep is not a proof of continuous motion.
If fixed material lengths, routing space or necessary connections cannot be
established, report that construction as unresolved; do not silently reduce the
requested features or relax checks to obtain a pass.
