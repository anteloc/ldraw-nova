# Build and repair mounted flexible parts

Start with the actual material family, rigid fittings and required poses. Run `./ldraw-agent flex guide TYPE` for installed definitions and family limits. For new plans, use [named endpoints and wheels](../reference/flex.md); external constraints remain supported. Install the optional pinned engine with `./setup.sh --with-lsynth`.

Study the [portal-frame pneumatic press](../../../examples/flex/pneumatic-press/README.md), [retained chain drive](../../../examples/workshop/chain-drive/README.md) or [complete workshop](../../../examples/workshop/workshop/README.md) for mounted static routes. The small hose/band/chain files teach syntax and BOM ownership. The [constraint lab](../../../examples/flex/constraint-lab/README.md) is diagnostic; the [legacy LSynth corpus](../../../lsynth-examples/README.md) is optional research with family-specific missing hardware and invalid-source cases.

## The working loop

1. Pick the actual family and fittings. Define the delivered poses and which
   properties must be checked. A curve, a fixed-length item and a moving circuit
   have different acceptance conditions.
2. Place the rigid hardware, including mounts, shafts, retainers and plugs. Read
   its actual local interfaces with `part PART` or `connectors MODEL --occurrence N`. Reserve
   a passage and end approaches before adding nearby bodywork.
3. Write visible constraints for one route or interacting group. Declare them in
   the [plan assets](../reference/flex.md#generated-flexible-assets), with the needed geometric limits.
4. Run `review PLAN`: it checks constraints, synthesizes, measures the result and
   renders the assembly. For a standalone route, use `flex build SOURCE` with
   the same limits, then review it with its fittings. Open the images.
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

## Learn from actual synthesis

The [constraint lab](../../../examples/flex/constraint-lab/README.md) contains
executable straight, bend, return and bundle experiments plus a deliberately
failing tight bend. It calibrates through actual LSynth output, not a duplicate
curve algorithm. Change one feature, synthesize and compare measurements and
images. Supported fixture results do not automatically generalize to a new size,
marker orientation, cross section or crowded assembly.

For a new family, run its guide and a small isolated route first; then seat it on
the actual fittings and inspect it in context. Reuse the complete
[pneumatic press](../../../examples/flex/pneumatic-press/README.md) for the latter
step. Complete the normal assembly/BOM/image review after the last route edit.

For multiple poses, preserve the physical part identities and required lengths,
regenerate each pose and inspect extremes plus intermediate configurations where
clearance is uncertain. A sampled sweep is not a proof of continuous motion.
If fixed material lengths, routing space or necessary connections cannot be
established, report that construction as unresolved; do not silently reduce the
requested features or relax checks to obtain a pass.

## Complete the rigid construction

A loop needs a carrier with bearings, spacers, retainers and a supported return run. A cable needs actual end anchors; a hose needs matching fittings and accessible controls. Preserve a clear assembly order and clearance for the delivered pose. Optical distributors, electrical plugs and pneumatic valves have different roles; a similar-looking source part does not establish interchangeability.

Measure the synthesized geometry, then open the route alone and on its actual fittings. Preserve physical identities and lengths across poses. A sequence of regenerated curves is not proof of one flexible item moving through them. Use the [flex reference](../reference/flex.md#read-the-checks-coverage) to interpret measured limits and untested properties.

