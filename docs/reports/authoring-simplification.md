# Model authoring simplification: verification record

The default workflow now uses ordinary JSON plans, named placement paths, inline
joint contracts and inline LSynth routes. It keeps the existing `review` loop,
pyldraw3 parser/writer, LSynth engine, external sources and numeric contracts.
The [entry guide](../../instructions.md) was promoted only after compatibility,
render/BOM checks, all six comparative trials and a fresh corrected-starter trial
passed. The user's existing mechanism work and Mecha handoff are preserved.

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
Their corner/return constructions now use shared waypoint helpers. All eight
constraint sources are byte-identical to the baseline; the four archived assets
also reproduce their original hashes. The tight corner remains an expected
failure (5.83 LDU sampled radius); corner-32 measures 20.59 LDU, and the return
and parallel routes measure 38.68 LDU. Existing original fixtures and attribution
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
failures and atomic publication/artifact protection. The final full suite passed **452 tests in 190.89 seconds**, using the installed
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

The [fixed briefs](authoring-trials/briefs.json) and frozen toolkit fingerprints
([baseline](authoring-trials/baseline-toolkit.json),
[candidate](authoring-trials/candidate-toolkit.json)) are retained. Platform usage
limits interrupted the trials. Agents retained their original task/context;
pauses are recorded separately with estimated boundaries from command completion
and resumption. They are excluded from active-work budgets and are not counted
as workflow failures or expert repairs. Tool time means instrumented subprocess
wall time; image/read/orchestration time is included in active elapsed estimates
but is not separately fabricated.

All six comparative trials delivered reproducible source, editable MPDs, passing
applicable checks, matching BOMs and inspected images within their budgets.
Every delivered bundle was audited; the source, review and image hashes were
checked. No trial received an expert repair or modified toolkit code.

| Brief | Budget | Baseline active minutes | Candidate active minutes | Baseline / candidate subprocess seconds | Reported repair cycles | Interventions |
|---|---:|---:|---:|---:|---:|---:|
| Frame and retained drive | 30 min | 14.0 | 7.2 | 91.2 / 29.0 | 1 / 1 | 0 / 0 |
| Pneumatic fitting/passage adaptation | 30 min | 10.3 | 9.0 | 84.1 / 85.9 | 1 / 1 | 0 / 0 |
| Complete workshop machine | 90 min | 20.1 | 10.3 | 117.8 / 84.1 | 5 / 1 | 0 / 0 |

[Machine-readable results](authoring-trials/results.json) link to each raw result,
command log and audit. Repair definitions are retained rather than flattened:
the baseline frame repair was visual, the candidate frame repair followed an
automatic missing-mount error, and the candidate machine repair followed a
connectivity/visual inspection despite its initial selected checks passing.
Both pneumatic trials also recorded a separate post-pass cleanup/refinement.

The candidate used 22, 19 and 19 timed commands; the baseline used 34, 37 and 48.
These count instrumented commands, not every tool interaction. All runs used the
same shared machine; some independent work ran concurrently. Timing is descriptive
and includes estimated pause boundaries. Both workflows completed these briefs;
this is not a statistically established improvement in completion rate.

Coverage also differs. Baseline mechanical trials needed separate shaft witnesses
with moving parts omitted; baseline fitting mounts used manual coordinate/visual
evidence. The baseline complete machine did not select hose obstacle measurement.
The candidate reviews integrated named mounts, retained shafts and assembly-frame
route interactions. Manual physical and motion limits remain in every result.

The six original trial records remain unchanged. The additional corrected-starter
trial below passed before the new entry guide became the default.


## Starter defect found by the independent trial

Both candidate mechanical trials independently found that the supplied drive rails lay between
the base plate's stud rows. The initial contract checked shafts and gears but
omitted that foundation interface. The agent independently moved the base by
half a stud and added twelve support-stack joints, then delivered a passing
101-part assembly. No expert repair was supplied to that trial.

The shared recipe now carries the same base offset and checks both eight-stud
rail mounts, both courses, all bearings and caps. The workshop module is moved
to preserve its bench grid and clear the hoses. Its base-to-bench seams, gantry
feet/columns, stop face and control guard now also have explicit mount checks.
A regression recreates the old half-stud error and displaces the whole drive;
both fail named mount checks. The corrected examples were rendered and inspected
again with unchanged BOM counts and hose limits. Original fixtures remain intact.
The earlier machine trial remains frozen. An additional fresh agent completed
the same brief against the [corrected snapshot](authoring-trials/candidate-v2-toolkit.json),
with the same model/settings, restrictions and 90-minute active budget. Its
[173-part delivery](authoring-trials/candidate-v2-complete-machine/result.json)
passed whole-model review, four structural scopes, matching BOMs and seven
opened final contextual views in **543.89 active seconds** (about 9.1 minutes),
with one bodywork repair and zero expert interventions. Its saved generator
reproduced the reviewed plan byte for byte during the independent audit. The
corrected foundation remained intact. This additional starter regression trial
is retained separately; it does not replace or erase the original result.
