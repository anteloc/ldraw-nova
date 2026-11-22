---
name: flexible-parts
description: 'Builds and repairs mounted flexible parts with LSynth: hoses, pneumatic tubes, cables, bands, chains and treads, routed between named rigid fittings or wrapped around mounted wheels. Covers flex guide TYPE, inline flex placements in plan steps, route kinds, flex diagnostics and local repairs, generated flexible assets, and worked references (flex basics, pneumatic press with three hoses, retained chain drive, workshop machine). Use when a model needs a hose, cable, chain, belt or tread, or when fixing a flex.* diagnostic.'
---

# Flexible parts

Build and repair mounted flexible parts with LSynth: pneumatic hoses, electrical leads, optical fibres, flexible axles, ribbed hoses, string, chains, rubber bands, belts and treads. You author constraints between real rigid fittings (or around mounted wheels); the toolkit checks the constraints, synthesizes the route, measures the result and embeds it in the MPD. Hoses go on last, after the rigid construction ([technic](../technic/SKILL.md)). `./setup.sh` installs the pinned **lsynth-nova 0.5.0** engine in `.venv` and the standalone CLI at `bin/lsynth`; `doctor` reports both.

```sh
./ldraw-agent flex types                                    # methods, product aliases, marker parts
./ldraw-agent flex guide TECHNIC_PNEUMATIC_HOSE_BEVELED     # installed definitions and family limits
```

## The working loop

1. **Pick the actual family and fittings.** Define the delivered poses and which properties must be checked. A curve, a fixed-length item and a moving circuit have different acceptance conditions.
2. **Place the rigid hardware** first: mounts, shafts, retainers, plugs. Read its interfaces with `part PART` or `connectors MODEL --occurrence N`. Reserve a passage and end approaches before adding nearby bodywork.
3. **Write visible constraints** for one route or interacting group, inline in the plan or as declared assets, with the needed geometric limits.
4. **Run `review PLAN`**: it checks constraints, synthesizes, measures and renders. Open the images.
5. **Repair the reported span or fitting**, then recheck nearby routes. If two corrections leave the same defect, change the passage, loop or hardware orientation. Keep the last accepted route; broad random parameter searches are not the normal method.

Constraints express geometric intent. They do not avoid obstacles, produce gravity sag, maintain physical length or create mechanical connections.

## Hose between fittings (inline)

An inline flex placement goes in the same `steps` arrays as rigid parts:

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

- `part PART` lists hose fittings under `hose_nozzles` (or `flex_ports`). Measured names: pump `2797c01-f1` (`outlet`), valve `4694c01-f1` (`upper`, `inlet`, `lower`), extended cylinder `74981-f2` (`base`, `rod`). The other ~60 pneumatic parts have `nozzle-0`, `nozzle-1`… from LDCad metadata. Names describe locations, not a verified circuit.
- Pneumatic routes always run with at least `min_radius` 15 and `min_separation` 10 LDU; a plan may raise but not lower them. Without `lead`, an endpoint leaves its fitting straight for 22 LDU.
- Pre-synthesis warnings: `flex.ports_face_away` (a fitting points away; the hose must loop) and `flex.ports_too_close` (closer than two bend radii plus the leads).
- Escape hatches, only after inspection: `feature` instead of `port` for a library connector; `at` + `outward` (part-local) for a measured interface without metadata; optional `up`.
- Endpoint directions point **out** of both fittings. Optional `via` points are in the containing section's frame: `[x,y,z]` or `{"at":[x,y,z],"direction":[dx,dy,dz],"up":[ux,uy,uz]}`. Waypoint directions follow travel. Flat cables need deliberate roll.

## Loop around mounted wheels (inline)

```json
{
  "id": "chain",
  "colour": 72,
  "flex": {"method": "TECHNIC_CHAIN_LINK", "wheels": ["drive-gear", "idler-gear"]}
}
```

- The wheels are existing rigid placements with their real rotations; routing copies are hidden, so each wheel appears once in the BOM.
- Interleave `{"control":"INSIDE"}`, `OUTSIDE` or `CROSS` when a studied layout needs it. **Do not append the first wheel to close the loop.**
- Wheel planes and controls are checked before synthesis; link rotations stay rigid. Inspect closure and engagement yourself: output order is not traversal order and closure is not certified.
- Supply shafts, bearings, spacers, retention and a supported return run. `examples/retained-chain-drive/model.plan.json` adds the bearings, spacers, stops and hand crank an isolated loop lacks.

## Review

```sh
./ldraw-agent review output/machine.plan.json --section chain-drive.ldr --no-render
./ldraw-agent review output/machine.plan.json --views home front back top
```

- Rigid parts resolve first; generated geometry goes in at the authored STEP. A rigid part cannot depend on flex geometry.
- `validation.json` holds the source map, structural failures, route measurements and interaction checks; review copies constraints, MPDs and manifests into `flex/`.
- Hoses are compared across module instances in the assembly frame. A tube radius enables conservative obstacle candidates (including fitting regions and holes): inspect the named candidates.
- Start flex studies with `review --contacts none`; connectivity and material clearance are then not established and `physical_validity` stays `not_proven`.
- Finish with a whole-model review. Scoped reviews exclude parent/sibling interfaces.

## Choose the route by family

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
| Brick arcs | Shape studies only. The installed BRICK_ARC fixture emits reflected bricks and fails rigid validation: do not bypass that failure. |

Aliases are resolved by installed definitions, not guessed. A wheel in the global band table is not compatible with every belt or chain: use a demonstrated family pair.

## Repair by diagnostic

| Diagnostic or symptom | Action |
| --- | --- |
| Unknown method, ignored part, insufficient markers | Use `flex guide TYPE`; move rigid context outside SYNTH and use recognized constraints. Check exact aliases. |
| Hidden/source controls, synthesized input | Restore the editable visible constraints. `SYNTH HIDE` hides output wheels; commented type-1 input is ignored. |
| Nonfinite, scaled, sheared or reflected constraint | Recreate a proper rotation from directions. |
| Coincident markers | Remove duplicates, or shorten a lead that reaches the next waypoint. A reversal needs a real loop. |
| Backward tangent / hairpin | Check the final endpoint sign and the marked span. Choose the other side of the obstacle or a wider return. |
| Bend too tight | Inspect the reported location. Increase space or change the approach; adding a midpoint can tighten the bend. |
| Ribbed hose gaps | Rings sit ~5.5 LDU apart and gap once neighbours turn more than ~7°: use a broader curve. |
| Flat cable twists | Keep deliberate roll/up directions, check plug orientation, remove needless twists. |
| Pair/self intersection | Change lane or loop at the crossing. Pair checks include endpoint regions. |
| Wheel-plane mismatch | Align effective wheel planes, including configured offsets; rotate the complete mounted wheel. |
| No tangent / warning despite exit 0 | Inspect wheel order, spacing, controls and radii. The adapter treats LSynth warnings as failure. |
| Link gap, overlap or wrong engagement | Verify wheel family and spacing, inspect the closure seam, change the layout. Never stretch or mirror links. |
| Stale asset report | Rebuild from the saved source; source, output and definition hashes must match. |
| Missing legacy geometry | Locate the correct part or make an explicit inspected substitution. |
| Custom resolution / GHOST rejected | Default resolution only: `HOSE_RES`/`BAND_RES` and GHOST inputs are unsupported. |
| Material length changes between poses | Add and account for real slack or revise the layout. |

## Declared flexible assets

Alternatively keep LSynth constraints in a separate file and declare them; `build` and `review` prepare them:

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

- A single-section LDR source's root is `NAMESPACE.ldr`; MPD sources keep their FILE names. Use distinct namespaces.
- `timeout` (seconds, default 90). `checks` accepts `min_radius`, `max_turn`, `tube_radius`, `min_separation`, `length`, `length_tolerance`, `block`, `obstacles`, `obstacle_section` (LDU; chosen limits, not material properties).
- Cache: `.cache/flex-assets/` and `.cache/flex-synthesis/` (delete to discard). The current library and limits are checked every time.
- Existing `"assets": ["hoses.mpd"]` entries stay portable without LSynth.

### Constraint syntax

```text
0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4
1 4 -60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 0 -40 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
0 SYNTH END
```

- At least two visible constraints in path order. Each marker's local **−Y points along the path** (away from the start, into the end).
- A band uses real pulley/wheel/gear placements (only parts under `band_constraints`) in loop order; `0 SYNTH INSIDE`, `OUTSIDE`, `CROSS` control wrap side. LSynth flattens a band into its first wheel's plane; `flex check` catches offsets first.
- Explicit colour in each `SYNTH BEGIN`. Keep the original visible constraints (LSynth comments markers out in output). Blocks stay within one FILE section.

### Python and CLI authoring

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

```python
from ldraw_tools.flex_authoring import band, document, placement

source = document(band([
    placement("4019.dat", (-60, 0, 0)),
    placement("4019.dat", (60, 0, 0)),
], method="TECHNIC_CHAIN_LINK", name="drive-chain", hide=True))
```

- `Endpoint.on_part(part_at, part_matrix, local_at, local_outward, lead=22)` for a measured interface; `Endpoint.from_feature(parts, part_code, feature_id, at=part_at, matrix=part_matrix, lead=22)` for a connector from `part`. Use the same placement variables as the rigid part.
- `hide=True` when the rigid assembly already owns the wheels. An `up` vector parallel to travel is invalid. Never mix local and world frames in one block.
- `corner_waypoints`, `return_waypoints`, `offset_waypoints` produce waypoint data; `jsonable()` puts it in a plan. Their control radius does not promise the synthesized radius.

```sh
./ldraw-agent flex hose --start 0 0 0 --start-direction 1 0 0 \
  --end 160 0 0 --end-direction -1 0 0 --lead 22 \
  --output output/lead.ldr
./ldraw-agent flex build output/lead.ldr \
  --min-radius 15 --tube-radius 5 --report output/lead-check.json
./ldraw-agent review output/lead.mpd --contacts none
```

`flex build` checks, synthesizes, measures, then publishes the MPD and `.manifest.json`; on any failure the previous MPD stays. `--force` replaces output after successful checks, `--no-cache` reruns the engine, `--timeout` bounds synthesis, `--namespace` sets the prefix. Place the returned `root` via `"assets": ["my-hose.mpd"]`. Regenerate after moving endpoints relative to each other. Never run `lsynth --install-parts`.

## Check coverage

- `flex check SOURCE`: control structure, recognized constraints, rotations, coincidence, tangent directions, band planes. It cannot prove a collision-free route.
- `flex check SOURCE --asset ASSET.mpd`: measures generated placements (bend samples, segment turns, spacing, length for hoses; counts and bounds for bands). Lengths along segment origins are not stock lengths. `--length`/`--length-tolerance` set a geometric target.
- `--min-radius`, `--max-turn`, `--tube-radius`, `--min-separation` add criteria. `--block N` checks one block against same-section neighbours. `--obstacles rigid.mpd --tube-radius R` (with `--obstacle-section NAME`) flags oriented-box candidates in the same frame: warnings to inspect, not proven collisions.
- Exit 0: selected checks passed; 1: a check failed; 2: input/dependency/execution failure. Read `coverage` and `diagnostics`, not just `checks_passed`.
- Continuous hoses, cables, bands and one-piece treads become **one posed embedded part per block**; Technic chain/tread links and BRICK_ARC bricks stay rigid placements. Posed parts have no verified connector metadata, stock length, tension or elasticity.

## Worked references

| Example | Lesson |
|---|---|
| `examples/flex-basics/` (`hose.ldr`, `band.ldr`, `chain.ldr`) | Syntax, synthesis and BOM ownership only; no frames, length or engagement. `flex build examples/flex-basics/hose.ldr --output output/hose.mpd` |
| `examples/pneumatic-press/named.plan.json` | Pump `2797c01-f1`, valve `4694c01-f1`, extended cylinder `74981-f2` on a portal frame, three `TECHNIC_PNEUMATIC_HOSE_BEVELED` hoses, nozzle references and mounting contracts. Measured: sleeves coaxial, min bend radius 16.9 (limit 15), tube distance ≥ 11.2 (limit 10). |
| `examples/retained-chain-drive/` | Supported static chain loop: side rails, bearing caps, shaft spacers/stops, hand crank. Keep wheel spacing and mounting grid. |
| `examples/workshop-machine/` | Complete integration: trestles, workbench, retained chain module under a portal-mounted cylinder, pump/valve pads, three hoses; every child reviewed alone and in its parent. |

```sh
cp examples/pneumatic-press/named.plan.json output/press.plan.json
./ldraw-agent review output/press.plan.json --views home front back top
```

The press shows the hose recipe: first marker on the nozzle base pointing out, a second 22 LDU further out so the hose runs straight before bending, optional waypoints, then the mirror at the target. Moving a fitting away from its supports fails its required joint even if the hose follows. Its first attempt failed with ribbed hose turning 36–56° between rings: always check bend radius.

For multiple poses, keep part identities and required lengths, regenerate each pose and inspect extremes plus intermediates. A sampled sweep is not proof of motion. If lengths, space or connections cannot be established, report the construction as unresolved rather than dropping features or relaxing checks.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/flex.md](references/docs-agent-guides-flex.md)
- [docs/agent/reference/flex.md](references/docs-agent-reference-flex.md)
- [examples/flex-basics/README.md](references/examples-flex-basics-README.md)
- [examples/pneumatic-press/README.md](references/examples-pneumatic-press-README.md)
- [examples/retained-chain-drive/README.md](references/examples-retained-chain-drive-README.md)
- [examples/workshop-machine/README.md](references/examples-workshop-machine-README.md)
