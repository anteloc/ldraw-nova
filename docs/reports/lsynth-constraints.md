# LSynth constraint authoring and repair — 2026-10-24

Agents now have one route through LSynth work: choose the family, measure the
interfaces, author constraints, check them, synthesize, measure the actual asset,
and inspect it in its assembly. The implementation extends the existing CLI,
MPD adapter and review process. It does not add a competing curve generator or
require a model-specific optimizer.

Start with the [agent guide](../agent/flex-constraints.md). The
[constraint lab](../../examples/flex/constraint-lab/README.md) supplies executable
experiments and inspected images. Instructions route agents to these when
flexible parts are required.

## Implemented support

| Capability | Entry point |
| --- | --- |
| Choose a family and inspect its actual installed definitions | `flex guide [TYPE]` |
| Create a simple route from outward-facing fitting directions | `flex hose` |
| Transform local interfaces, specify tangents/roll and write wheel loops | `ldraw_tools.flex_authoring` |
| Diagnose visible source, control records, marker frames and effective wheel planes | `flex check SOURCE` |
| Measure generated hoses, check explicit geometric limits and identify local repairs | `flex check SOURCE --asset ASSET` |
| Flag potential rigid-obstacle overlaps, with no endpoint exclusions | `--obstacles RIGID_MODEL --tube-radius R` |
| Repeat straight, bend, return, bundle and all-definition synthesis experiments | `examples/flex/constraint-lab/generate.py` |

Diagnostics identify the route, source line or measured location and suggest an
action. Actual-output checks require matching source, asset and configuration
hashes. Measuring one block still checks it against neighbouring hoses in the
same coordinate frame. Existing build output remains compatible; manifest
metadata now also locates generated links by section and physical piece range.

Guidance covers pneumatic and electrical leads, optical fibres, flexible axles,
Flex-System, segmented hoses, string, minifigure chains, continuous bands/treads,
separate chain/tread links and brick shape studies. It includes ownership,
fittings, roll, crossings, slack, missing legacy parts, unsupported controls,
stock length and multiple-pose limitations. No additional reference models were
needed for this implementation.

## Evidence and lessons

Tested with **lsynth-nova 3.1.0** and its bundled definitions. The final project
suite passed **402 tests**. The focused suite passed **108 tests**, including
real synthesis, negative cases, actual connector
frames, transformed routes, stale assets, report reuse, obstacle candidates,
pair crossings, band controls and legacy adapter/press regressions.

The all-definition experiment exercises **45 methods**. **44** fixtures generate,
package and pass their selected automatic checks. `BRICK_ARC` emits reflected
physical brick placements and is rejected. This is deliberately retained as a
failure; rigid validation was not relaxed. These simple fixtures establish
software coverage, not approval of every shape, manufactured length or
wheel/link pairing.

The eight pneumatic experiments use an explicit geometric bend threshold of
15 LDU and a round envelope radius of 5 LDU. These are fixture criteria, not
certified material limits. Seven pass; the deliberately tight corner fails.

| Corner constraint geometry | Minimum sampled output radius, LDU |
| --- | ---: |
| Nominal 6 | 5.83 — rejected |
| Nominal 24 | 15.74 |
| Nominal 32 | 20.59 |
| Nominal 32 plus midpoint | 16.64 |
| Nominal 48 | 38.68 |

The extra midpoint makes this bend tighter. Increasing marker count is not a
reliable repair strategy. The return loop and separated pair also pass their
chosen criteria. The tight corner passes ordinary assembly/BOM review but
fails the dedicated bend check: neither review replaces the other.

Home and top views of the tight corner, larger corner, return and pair were
opened. Top views are edge-on to these XY routes and cannot establish bend
quality alone. The retained images and source/asset/image hashes are in the
lab's [visual record](../../examples/flex/constraint-lab/visual-review.json).
The existing pneumatic press supplies the mounted-fitting reference; the new
experiments deliberately isolate geometry effects.

Two engine details matter for reliable diagnostics:

- `CROSS` toggles the wrap side for subsequent wheels. Controls after the last
  wheel affect the closing run too. Regression cases compare the checker with
  actual synthesis, including impossible tangents.
- Band emission order is not loop traversal order: each outgoing straight run
  precedes the arc around its wheel. Joining file-order origins invents false
  lengths and closure gaps. Band reports therefore give counts and origin
  bounds, with closure and engagement explicitly left for inspection.

Reproducible experiment outputs are retained in this checkout under
`output/flex-constraint-lab/`, `output/flex-family-coverage/` and
`output/flex-cli-acceptance/`. Regenerate them with the lab commands when the
engine or definitions change. The CLI acceptance run covers source creation,
checking, synthesis, saved measurement reports and a failing-bend exit status.

## What remains unproven

The tooling establishes useful geometric checks and makes omissions explicit.
It does not certify physical bend limits, stock lengths, tension, elasticity,
contact, torque transmission or continuous motion. Obstacle boxes are
conservative candidates for inspection, not material-collision verdicts.
Family-specific end geometry is automatically calibrated only for the beveled
pneumatic sleeve; other ends require contextual inspection.

This is tooling and reusable knowledge, not model-weight training or evidence
that every agent is now an expert. Independent mid-range-agent adaptation
trials have not been run. The lab describes the next evaluation: changed
fitting frames, unseen passages and neighbouring routes, recording correctness,
repair count, active time and expert intervention. Such trials should establish
how reliably agents use the support before claiming a generation-speed or
quality improvement.
