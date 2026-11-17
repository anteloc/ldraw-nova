# Technic overhaul, November 2026: measurements

**What was measured.** The changes below are on branch `fable-technics`, uncommitted, on top of `3d744a1e`. That commit is itself a work-in-progress snapshot of the first part of this work (faster bounds and the start of port derivation). The baseline before any of this work is `d1e93d73`. Measurements were taken on 2026-11-16 and 2026-11-17.

**Who made the changes.** The work ran in Claude Code 2.1.325. Claude Fable 5.2 wrote the plan and started the work; from 2026-11-17 11:49 UTC Claude Opus 5.5 continued it.

**What the work set out to do.** An agent should be able to:

- seat any common Technic part by naming its holes;
- get build errors for the defects a Technic builder would spot;
- build mechanisms that follow mechanical-engineering practice, checked in the built pose without simulation;
- start from recipes it can copy;
- wait seconds, not minutes, for each rebuild.

**How numbers are labelled.** *Measured* means run on this checkout. *Target* is the gate in the plan.

## Summary

| Metric | Before | After | Target | Status |
|---|---|---|---|---|
| `build` of `examples/workshop-machine` (160 placements), same machine, warm | 16.9 s | 7.1–8.2 s (3 runs) | ≤ 10 s | met |
| Technic placements in 215 official sets that can be seated by port | 56.7% (39 reviewed parts) | 98.3% (1,646 parts) | ≥ 95% | met |
| Pins and axles in those sets that seat under the fit rules | — | 94.4% (93,376 of 98,886) | — | measured |
| Probe defects that fail `build` (overlapping beams, axle through plastic, gear 2.5 LDU short) | 0 of 3 | 2 of 3 fail outright; the gear gap is a named warning, and fails the build when the section declares a `mechanism` | 3 of 3 | partly met |
| Seeded mutations reported by name | — | 5 of 5 | ≥ 90% | met |
| Error-level checks firing on official sets | — | `through_solid` 0.34, `cell_overlap` 0.22, `occupied_hole` 0.43, `occupied_span` 0.19; `invalid_seating` 1.30; `invalid_transform` 343 (rounded matrices in old files, the same rule as `assembly.nonrigid`) | < 1 per 1,000 placements each | met except `invalid_seating` and `invalid_transform` |
| Walker1 cross-check against LegoTechnicSimulation | — | 42 of 42 joints, 5 of 5 meshes, same ratios | match | met |
| Technic golden queries with a copyable recipe in the top three | 1 of 10 | 9 of 10 | 10 of 10 | missed by one (differential) |
| Reading for a Technic brief (AGENTS.md and the plan, Technic, checks and review cards) | about 12,900 tokens | 6,469 tokens | ≤ 6,500 | met |
| Test suite | 798 passed | 850 passed (52 new) | all pass | met |

The first build measurement, taken during planning, was 64.7 s. Its conditions were not recorded, and the comparison harness later measured 16.9 s for the same commit. The like-for-like comparison is 16.9 s → 7.1–8.2 s, with byte-identical MPDs and reports. `examples/pneumatic-press` went from 9.0 s to 5.2–5.3 s under the same harness.

## Speed

- **NumPy bounds.** `connection_adapter.transformed_bounds` replaces pyldraw3's per-point loop and gives bit-identical results; it is pinned to pyldraw3 1.7.0.
- **Shared part geometry.** `document.share_library_geometry` lets document overlays reuse library part geometry instead of reloading it.
- **Not done.** Memoising `inspect_connections` and a disk cache for part geometry were not needed to meet the gate.

## Ports

**Where ports come from.** `scripts/technic_ports.py` derives pin, axle and nozzle ports from the LDCad shadow metadata into `ldraw_tools/data/technic-ports.json`: 1,646 parts, 8,765 ports and 119 aliases. The derivation reproduces all 150 hand-reviewed ports. The 39 reviewed parts stay authoritative.

**Which ports are kept.** `scripts/technic_corpus.py ports` checks each derived pin and axle against the official sets in `data/models-annotated`:

- **Withheld:** ports of 4 parts (2739a, 32005, 32293, 4261) that rarely seat in real sets. They stay in the table, marked as withheld.
- **Left in place:** 20 weak ports that seat in under 90% of their uses.
- **Why the rest do not seat:** 5,510 male ports do not seat. 893 of them stand at an aligned hole and fail a rule: engagement 714, grip 126, connector family 53. The other 4,617 have no hole at all, such as axle ends and free pin halves.

| Measure | Value |
|---|---|
| Official sets read | 215 |
| Technic placements | 105,427 |
| Covered by the reviewed table alone | 56.65% |
| Covered by the merged table | 98.33% |
| Pin and axle ports that seat | 94.43% (93,376 of 98,886) |
| Distinct Technic parts seen | 452 |

**New placement forms.** These need no coordinate arithmetic:

- **`on: {to, hole, pin}`** seats a part on a named hole. Options:
  - `side`, `end` and `past` set which way the part runs and how far it goes.
  - `next_to` places a part flush against its neighbour on the same axle.
  - `slide` moves it along the axle; `roll` and `flip` turn it.
- **`join`** lays a beam or connector on matching holes and inserts its pins, which are named `ID-pin-N`.
- **`mirror`** on a section placement makes the other-hand copy of a module with proper rotations.

## Checks

`build` runs the Technic checks whenever table parts are present, with no opt-in. Thresholds come from the official sets. For example:

- **Overhung gear:** 40 LDU one-sided; 92% of official gears comply.
- **Bearing span:** 160 LDU between bearings; 95% of official gears comply.

An error-level code must fire less than once per 1,000 official placements; anything noisier ships as a warning.

- **Removed:** `technic.gear_slides` fired on about half of all official gears, so it was dropped.
- **Narrowed:** `technic.thrust_unbacked` applies only to worms, for the same reason.

**Rates on official sets.** These were measured by `scripts/technic_corpus.py checks` on the 159 Technic-heavy sets it reads within its 300 s budget (41,628 placements, 959 gears, 308 meshes). "Errors" counts only the findings that fail a build.

| Code | Findings per 1,000 placements | Errors per 1,000 placements |
|---|---|---|
| `technic.invalid_transform` | 343 | 343 (see below) |
| `technic.invalid_seating` | 13.1 | 1.30 |
| `technic.loose_axle` | 5.45 | warning |
| `technic.open_pin` | 2.47 | warning |
| `technic.incomplete_grip` | 1.97 | warning |
| `technic.occupied_span` | 1.56 | 0.19 |
| `technic.occupied_hole` | 1.32 | 0.43 |
| `technic.unbraced_mesh` | 1.20 | warning |
| `technic.misaligned` | 1.01 | warning |
| `technic.unsupported_shaft` | 0.65 | warning |
| `technic.through_solid` | 0.34 | 0.34 |
| `technic.gear_gap` | 0.34 | warning |
| `technic.gear_clash` | 0.26 | warning |
| `technic.cell_overlap` | 0.22 | 0.22 |
| `technic.overhung_gear`, `technic.locked_shaft` | 0.17 each | warning |
| `technic.thrust_unbacked` | 0.02 | warning |

**Seating errors were not measured until late.** Until 2026-11-17 the corpus run counted only the new checks. The seating errors from the joint review (`technic_review.py`) went unmeasured. They predate this work, but their scope grew from 39 reviewed parts to every derived part. Measured for the first time, they fired far above the gate:

| Code | Rate per 1,000 |
|---|---|
| `technic.invalid_transform` | 435 |
| `technic.invalid_seating` | 18.2 |
| `technic.occupied_span` | 10.0 |
| `technic.incomplete_grip` | 2.0 |
| `technic.occupied_hole` | 1.2 |

That measurement found four causes, all now fixed and tested:

1. **Turned crosses.** Derived ports recorded no roll, so a cross was assumed square to the part. On the bent end of the 53.13° liftarms (32271, 32348, 6629) the cross is turned 36.87° from the part's axes. 121 official axles there failed keyed roll, 120 of them by 35–40°. Ports now carry the `radial` from the shadow metadata; 12 parts gained one.
2. **Rounded lengths.** Derived hole lengths round thin parts up to 10 LDU (a 7 LDU bevel gear, 8 LDU plates). Neighbours on one shaft therefore seemed to overlap by 2–3 LDU. Span conflicts now allow 3 LDU of slack.
3. **Over-strict roll and pin rules.**
   - Keyed roll tolerated 0.5°, but official files leave bushes and axles 0.5–5° off; it now tolerates 5°. A wrongly rolled part is 45° or 90° off and still fails.
   - A pin part-way into a hole, with at least a plate's depth inside, is now a warning. A tip barely touching, or the collar in the bore, stays an error.
   - A half-filled grip is now a warning. Plates on bricks do both throughout studded sets.
4. **Unreviewed evidence.** Seating findings are errors only when every part involved has hand-reviewed ports. Derived ports give warnings.

**What remains above the gate.**

- **`technic.invalid_seating`** errors, at 1.30 per 1,000, are just above it. These are pairs of reviewed parts; see the gaps.
- **`technic.invalid_transform`** now applies the same rule as the general validator's `assembly.nonrigid`: six-place rounding is accepted. Before, it used a tighter 1e-6 tolerance. It flags the rotations written with three or four decimals in older official files, which fail general validation anyway. Plans built with `orient`, `on` and `join` produce exact rotations and never trigger it.

**Mutation test** (`tests/test_technic_checks.py`). Five defects are seeded into a correct gear train with a lever, and each must be reported under its own code: 5 of 5 are.

| Defect seeded | Code reported |
|---|---|
| Gear moved 5 LDU | `technic.gear_gap` |
| Beam moved half a stud | `technic.through_solid` |
| Bush removed | `technic.loose_axle` |
| Axle turned 45° | `technic.invalid_seating` |
| Pivot joined with friction pins | `technic.pivot_locked` (mechanism contract) |

## Mechanisms

`ldraw_tools/mechanism.py` builds a kinematic graph of the built pose and analyses it:

- **Rigid groups:** formed by studs, friction pins and keyed axles.
- **Revolute joints:** from frictionless pins and axles in round holes.
- **Prismatic joints:** telescoping parts (shock absorbers, cylinders, linear actuators) are split into a barrel and a rod joined by a prismatic joint.
- **Gear couplings:**
  - parallel gears by the pitch rule;
  - perpendicular gears from a table mined from the official sets;
  - worm and rack arrangements.

  The mesh evidence: 700 of the 717 parallel gear pairs within 3 LDU of meshing in 165 official models stand exactly at 1.25 × (Na + Nb).
- **Mobility:** the rank of the constraint matrix at the built pose.

A section can declare `mechanism: {ground, input, outputs, pivots, dof}`. `build` then reports one of these when the built pose disagrees with it:

- `technic.mechanism_locked`
- `technic.mechanism_uncoupled`
- `technic.mechanism_loose`
- `technic.mechanism_dof`
- `technic.pivot_locked`

`./ldraw-agent technic trace` prints the graph. Nothing is animated.

**Cross-check against LegoTechnicSimulation's Walker1.** That project is a sibling checkout, MIT licence, read in place and never copied.

- **Joints and meshes:** Nova finds the same 42 revolute joints and the same 5 meshes, with ratios 8:24, 12:14 (twice), 20:12 and 24:24.
- **Rigid groups:** Nova's grouping differs only at four 32013 angle connectors. There, Walker1's axles miss the pin hole by 2 LDU. Nova seats within 0.2 LDU and the other project within 3, so Nova leaves the connectors on their own. Without them, Nova has 32 groups against the other project's 31; the other project makes one extra merge through those connectors.

## Knowledge and reading

**Recipes.** Eight seat-based recipes in `examples/recipes/technic-*`. Each one passes every check and its mechanism contract, was rendered and inspected, and rebuilds byte-identically in `tests/test_construction_recipes.py`:

- pin frame;
- 8:24 gear pair;
- rack-and-pinion steering;
- wheel on an axle;
- bevel corner;
- worm drive;
- suspension arm with a shock absorber;
- lever raised by a pneumatic cylinder.

**Golden queries.** Nine of the ten Technic queries in `tests/test_knowledge_ranking.py` rank a recipe in the top three. The exception is a differential: no recipe exists, because the differential's spider gear rides on a post that is not a pin or axle port.

**Reading path.** The Technic card is the one card a Technic brief requires. `AGENTS.md` sends Technic briefs to it instead of the SNOT card. `docs/agent/reference/technic-parts.md` is generated and lists the 148 most-used parts with their ports.

## Dogfood: the `steering-chassis` brief

The model, previews, xray boards and per-stage timings are in `output/steering-chassis/`. It was built by Claude Opus 5.5, the same agent that wrote the recipes, so it is not a measure of a fresh agent.

| Measure | Value |
|---|---|
| Wall time | 15 min 30 s, of which 3 min 29 s was automatic context compaction |
| Plan and generator authoring | 168 s |
| Build, check and repair | 123 s |
| `ldraw-agent` time | 31.7 s over 8 calls |
| Repairs | 3 in building: rim without tyre-seat data, rim orientation, rack facing away from the pinion. The last was caught by `technic.mechanism_uncoupled`, which named the moving chain. |
| Result | 53 parts. All checks pass. 4 degrees of freedom: steering, rear axle, two front wheels. Turning the steering wheel moves the rack and both front hubs. 2 meshes; all 39 pins and axles seated. |

## Smoke trial

Four runs were made one at a time: the two 15-minute micro briefs, each by Claude Haiku 5.5 and by Claude Opus 5.5.

**How the runs were made.**

- **Harness:** each run was a fresh `general-purpose` subagent started through Claude Code's Agent tool, with the bench harness prompt plus "Budget: 15 minutes." This is not `bench/run.py`: the subagents had every tool, and there was no budget cap or timeout.
- **Scoring:** `bench/score.py run` on each folder. Active time and token counts come from each subagent's transcript.
- **Interruption:** the Haiku gearbox run was stopped by the account usage limit for 5 h 36 min and then resumed; its time excludes that pause.
- **Toolkit:** fixes found by the first two runs (listed below) were applied before the last two.

| Brief | Model | Result | Brief checks | Parts | Placed by port | Pins and axles seated | Technic errors | Active time | Output tokens | Builds | Images opened |
|---|---|---|---|---|---|---|---|---|---|---|---|
| micro-gearbox | Haiku | DONE | 4/4 | 11 | 91% | 2 of 3 | 0 | 5.2 min | 55,186 | 10 | 7 |
| micro-gearbox | Opus | DONE | 4/4 | 17 | 94% | 11 of 11 | 0 | 8.1 min | 45,527 | 6 | 14 |
| micro-swing-arm | Haiku | DONE | 4/4 | 9 | 80% | 10 of 10 | 0 | 6.5 min | 70,973 | 8 | 15 |
| micro-swing-arm | Opus | DONE | 4/4 | 12 | 85% | 11 of 11 | 0 | 7.8 min | 41,058 | 18 | 14 |

**Both gearboxes are sound.** Each has an 8:24 reduction and 1 degree of freedom, and the output turns with the input.

- **Haiku:** the beams stand on the shafts alone and are not tied to each other. That is buildable, and the agent named it as a caveat. The male left unseated is the short shaft moulded on the 2853a crank, which stands free.
- **Opus:** the beams are tied with pins and spacers, and the crank has a handle. Its first build drew two warnings: an open pin, and a false `technic.locked_shaft`. Lengthening the beams cleared both.

**Haiku's swing arm works but is crude.** The frame is a 1 × 16 Technic brick and the arm is a 1 × 4 brick on a frictionless pin. A 6.5L shock runs from the arm's lower hole to a 1 × 4 brick mount pinned to the frame. The mechanism has 1 degree of freedom, and all 10 pins seat. The arm is short, and four of its studs face sideways uncovered: the agent left the `appearance.exposed_side_studs` warning standing.

**Opus's swing arm is the most convincing model of the trial.** The frame is an upright 3 × 5 L-beam with a 3L mount pinned to it. A red 7L arm swings on a frictionless pin at the foot, and a 6.5L shock runs from arm hole 5 to the mount. A small wheel sits on the arm's end. The agent solved the arm's droop (7.31°) so that the shock's eyes sit exactly 110 LDU apart. One repair was needed: the shock's top pin shared a hole with a mounting pin (`technic.occupied_hole`), so the mount became a 3L beam.

**Across the four runs:**

- **Every run finished well inside its budget.** All delivered with 4 of 4 brief checks, no Technic errors and no hand-written matrices, in 5.2 to 8.1 minutes of a 15-minute budget.
- **Most parts were placed by port.** 80–94% of placements used Technic seats or `join`. Each model placed only its first frame piece by coordinates.
- **No agent wrote its own checker.**
- **Every agent wrote its own metadata script, and two broke line endings.** All four wrote a `finalize.py` for the delivery metadata. Two of the five finalizations in this work, the dogfood's and Opus's swing arm, first wrote LF line endings and had to be redone.

**Defects the runs found.** All are fixed and covered by tests:

1. **False `technic.locked_shaft`** (reported by the Opus run). When the frame was not declared, the frame was the group with the most structural members. A crank built from an arm, a pin and two round grips outranked the beams, so its gear counted as fixed to the frame. The frame is now the group whose holes the most shafts and pins turn in.
2. **Wrong gear spacing in the Technic card** (reported by the Opus run). The card said 8+40 teeth mesh 4 studs apart; it is 3. The whole-stud list is corrected and checked against `technic gears`.
3. **Finalization was hand-written every time.** The new `./ldraw-agent finalize MPD` adds the licence comment and keywords to every generated section, keeps CRLF and can be re-run safely. It checks the `[AI-GENERATED]` title and the authors, and it leaves imported sections alone. The review card now points to it; `tests/test_finalize.py` covers it. On the dogfood it reproduces the hand-finalized file byte for byte.

## Gaps

- **Three planned recipes are missing.** The plan named eleven recipes and eight were built. The retained shaft is covered by the gear pair. Still missing:
  - **Differential axle:** the spider gear's post is not a port, so there is no recipe and the differential golden query misses.
  - **Crank and piston.**
  - **System cladding on a Technic frame.**
- **No `friction_pivot` or `loose_structure` codes.** The plan listed both. A pivot is checked only when a `mechanism` contract names it, through `technic.pivot_locked`.
- **Hoses are not routed automatically.** The pneumatic aids are:
  - named nozzles for every pneumatic part;
  - a minimum radius and separation that a plan cannot lower;
  - a default 22 LDU straight lead at each fitting;
  - early warnings when two fittings face away or sit too close.
- **Mirroring needs a match.** A part is mirrored only when it has a plane of symmetry, a Left/Right partner, or is a sprung part whose ports survive the reflection. Anything else, such as a worm, stops the build with a message.
- **Motion is not simulated.** Mobility is computed at the built pose only. It ignores play, and it can mislead at singular poses.
- **`technic.invalid_seating` errors fire at 1.30 per 1,000 official placements, just above the gate.** All 54 are between hand-reviewed parts, and each is a geometric impossibility in the official file: pins with the collar in a bore or barely touching a hole (33), crosses rolled more than 5° (10), axles with too little inside the hole (6), tilted axes (3) and a pin in an axle hole (1). They were kept as errors because, for an agent, each is a real defect that a seat fixes.
- **Rounded rotations fail.** Old official files write rotations with three or four decimals, so `technic.invalid_transform` and the general `assembly.nonrigid` reject their submodels. Reusing such a submodel means re-placing its parts with `orient` or `on`.

## Run the full benchmark

From a terminal, outside Claude Code:

```sh
.venv/bin/python bench/run.py --suite technic-baseline --ref d1e93d73 --round 3 --family technic --model haiku --model opus --repeats 2 --jobs 1
.venv/bin/python bench/run.py --suite technic-candidate --round 3 --family technic --model haiku --model opus --repeats 2 --jobs 1
.venv/bin/python bench/score.py table output/bench/technic-baseline output/bench/technic-candidate
```

These run the seven Technic briefs (`steering-chassis`, `pneumatic-lift`, `winch-crane`, `twin-engine`, `differential-axle`, `micro-gearbox`, `micro-swing-arm`) twice per model, one agent at a time. That is 28 runs per arm.

- **Arms:** the candidate arm benchmarks HEAD plus the uncommitted working tree. The baseline arm checks out `d1e93d73`. Both are scored by the current toolkit.
- **Budgets:** the per-brief budgets in `bench/briefs.json` add up to 330 minutes and 46 USD per model and repeat. Each arm can therefore take up to 22 hours and 184 USD if every run uses its full budget.
- **Usage limits:** an account usage limit stopped one smoke run for five and a half hours. Run each arm in a window with enough quota, or split it by `--brief`.
