# Model authoring simplification: verification record

The candidate workflow uses ordinary JSON plans, named placement paths, inline
joint contracts and inline LSynth routes. It keeps the existing `review` loop,
pyldraw3 parser/writer, LSynth engine, external sources and numeric contracts.
The default entry guide remains unchanged until the independent trials pass.

## Implemented evidence

- Placement paths and original JSON locations survive includes, nested modules,
  repeats and unrelated reordering. They are generated during building, without
  interpreting comments. Missing references fail explicitly.
- Named contracts compile to occurrence contracts bound to the resulting model.
  Fixed structures retain the old checking scope; `scope: joints` checks declared
  seating and mounts in a static pose. Explicit retained axles require actual
  touching stops. Stale external contracts remain errors.
- Inline hoses follow complete fitting transforms and fingerprinted nozzle
  frames. Wheel routing hides copies of the assembly-owned wheels. Current
  checks run on synthesis cache hits; successful validation is not cached.
- Scoped reviews build the selected dependency closure and mark their coverage.
  Their evidence cannot claim whole-model coverage. Source and geometry failures
  keep available identity; unavailable measurements are explicitly unavailable.

## Construction evidence

| Construction | Physical placements | Evidence |
|---|---:|---|
| Named service platform | 55 | [Plan](../../examples/workshop/mounted-frame/model.plan.json), [review](../../examples/workshop/mounted-frame/review/review.json), [visual notes](../../examples/workshop/mounted-frame/visual-review.json). MPD byte-identical to the original service platform. |
| Retained chain drive | 58 | [Plan](../../examples/workshop/chain-drive/model.plan.json), [review](../../examples/workshop/chain-drive/review/review.json), [visual notes](../../examples/workshop/chain-drive/visual-review.json). Two actual wheels and 24 individual links. |
| Named pneumatic press | 41 | [Plan](../../examples/flex/pneumatic-press/named.plan.json), [review](../../examples/flex/pneumatic-press/named-review/review.json), [visual notes](../../examples/flex/pneumatic-press/named-visual-review.json). Rigid geometry and BOM match the original fixture. |
| Workshop conveyor and pneumatic stop | 160 | [Plan](../../examples/workshop/workshop/model.plan.json), [review](../../examples/workshop/workshop/review/review.json), [visual notes](../../examples/workshop/workshop/visual-review.json). Real LeoCAD previews and matching BOMs. |

The machine's three sampled minimum bend radii are 20.12, 19.82 and 21.81 LDU,
against 15 LDU. Pair separations are 12.53, 12.53 and 11.20 LDU, against 10 LDU.
The six conservative obstacle candidates are its six endpoint fitting regions;
contextual home/front/back/underside views were opened. The initial layout
needed higher control mounts to clear the chain base and preserve hose spacing;
limits were retained throughout repair.

The original [constraint experiments](../../examples/flex/constraint-lab/README.md)
cover straight, corner, return and parallel routes with measured synthesis.
Their corner/return constructions now use shared waypoint helpers. The tight
corner remains an expected failure. Existing original fixtures and attribution
are retained.

The reviewed interface registry now covers the starter pump's four bottom stud
sockets, the cylinder eyes, the selected sprocket, crank ends and gantry beam.
This intentionally improves coverage: the original press's connectivity report
has four groups rather than seven (one rigid assembly and three continuous
hoses). Its model bytes are unchanged. Motion, strength, manufactured hose length,
material collision freedom and availability of every part/colour are not proved.

## Automated regressions

The preserved baseline passed 431 tests before implementation. The new tests
exercise named references, nested/repeated/include identity, stale or moved
mounts, invalid transforms, geometry fingerprints, inline endpoint transforms,
wheel planes/ownership, rigid-link counting, route crossings in assembly space,
scoped coverage, included-schema diagnostics and structured synthesis failures.
Existing tests retain byte regressions, stricter cache-hit checks, dependency
failures and atomic publication/artifact protection. The final full suite passed **451 tests in 188.60 seconds**, using the installed
official library and LSynth. Targeted lint and `git diff --check` pass. The new
schema-failure report intentionally adds `validation.json` with `geometry: null`
instead of publishing only an opaque exception. Its regression asserts that no
model or unavailable geometry is marked as passing.

## Independent trial protocol

Three fixed briefs run against separate baseline and candidate snapshots using
fresh agents with the same inherited model/settings, no model overrides and no
expert repairs. Agents may change model sources under their own output folder,
not toolkit code. Adaptations have 30 minutes each; the complete machine has
90 minutes of active work. A trial must deliver reproducible source, editable
MPD, passing applicable checks, matching BOMs and opened contextual images with
every requested feature. Time, repair cycles and interventions are recorded
separately. These six cases are descriptive comparisons, not a statistically
established completion rate.

Trial results are pending; the candidate is not yet promoted as the default.
