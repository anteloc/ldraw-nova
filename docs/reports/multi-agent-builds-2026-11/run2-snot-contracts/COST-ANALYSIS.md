# Why run 2 was slow and expensive — and how to fix it with subagents

Run 2 (SNOT and 49 named submodels) produced the best house of these experiments: every submodel check passed, integration found no structural defects, and it scored 3.9 visually. But it cost about 67 min of active time and about 2.3 M worker context tokens. It also ran into the 5-hour usage quota, which stalled the run for 2 h 24 min.

This page explains where that cost came from and what to change. Every number comes from:
- the worker logs (`logs/H*.md`);
- the per-agent usage lines in `timing.md`;
- measurements taken on the finished files on 2026-11-08.

Figures marked *estimate* are projections, not measurements.

## 1. Measurements

### The tools are fast; the agents are slow

| Operation (floor2 module, 187 parts) | Time |
|---|---|
| `ldraw-agent build` | 4.2 s |
| `contract_check.py`, one module | 3.4 s |
| `contract_check.py`, whole house | 17.6 s |
| `ldraw-xray render`, 2 views | 4.0 s |
| `ldraw-agent review`, whole house | ~27 s |

A worker's tool time adds up to roughly 3–5 min out of its 22–34 min. The rest is model turns:
- each worker made **59–94 tool calls** in the build phase;
- each finished with a context of **450–470 k tokens**.

### Where each worker's build-phase time went

| Worker | Start to first build | Build/fix iterations | Audit and evidence | Total |
|---|---|---|---|---|
| H1 ground | 14.0 min | 4 min | 4.3 min | 22.3 min |
| H2 floor2 | 13.7 min | 7 min | 4.8 min | 25.1 min |
| H3 floor3 | 13.6 min | 8 min | 12.7 min (about 6 spent on an outdated FAIL) | 33.9 min |
| H4 roof | 21.1 min | 6.5 min | 5 min | 32.6 min |
| H5 street | 11.8 min | 10.5 min | 2.6 min | 24.9 min |
| **Mean** | **14.8 min (53 %)** | **7.2 min (26 %)** | **5.9 min (21 %)** | **27.8 min** |

### What filled the contexts

- **Reading.** Every worker read the same ~25 k tokens:

  | File | Tokens | Note |
  |---|---|---|
  | CONTRACTS.md | 5.2 k | all 49 rows, but each worker needs about 10 |
  | architecture.py | 4.1 k | |
  | ldraw-xray README | 3.8 k | |
  | snot.md | 2.6 k | |
  | conventions.md | 1.7 k | |
  | ldraw-xray AGENTS | 1.7 k | |
  | common.py | 1.4 k | |

  Each worker then re-inspected the same parts and designed its module from an empty `generate.py`.
- **Images.** Workers rendered **337 PNGs** in total:

  | Module | Images |
  |---|---|
  | ground | 40 |
  | floor2 | 50 |
  | floor3 | 107 |
  | roof | 74 |
  | street | 66 |

  Each worker opened roughly 25–50 of them, at about 1.4 k tokens per panel and about 3 k per board. That is about 50–150 k tokens of images in each context, carried into every later turn.
- **Tool output.** `ldraw-agent build --detail summary` still prints **about 350 KB of JSON**; the source map alone is 245 KB, roughly 60–85 k tokens. Workers saved it to files (0.4–2.5 MB of build logs under `modules/`), but every look into those files costs tokens. A single unredirected build adds about 85 k tokens at once.
- **Turns × context.** Each turn re-reads the whole context, so the cost compounds. *Estimate:* about 80 turns at an average context of 250 k tokens is about 20 M input tokens per worker, and about 100 M across five. Most of this is cache reads, which are cheaper but still count against the 5-hour quota. Five such workers in parallel exhausted the quota in **both** runs.

### Other losses

- **Mistakes in my contract.** Three of my size limits were wrong for SNOT:
  - studs that protrude past the wall face;
  - studs that are recessed into it;
  - a kerb too low for its cap tile.

  Each came up mid-build and caused re-checks. One of them sent H3 on a 6-minute detour. A 5-minute test model built from the kit would have caught all three before launch.
- **Duplicated structure.** The slab (four 6×16 plates), the wall core with side-stud courses, and the top ring are nearly identical across the three storeys. Three workers each wrote and debugged their own copy.
- **Uneven workloads.** The build phase lasts as long as the slowest worker. Roof (13 submodels, 21 min before its first build) and floor3 took 33–34 min; the fastest took 22 min.
- **Expensive repairs.** Each repair round resumed a worker with its full 450 k context for a 2–8 minute fix.
- **Defects the checker could have caught.** The 3 integration findings that workers could have caught but didn't report are all detectable from geometry:
  - bare side studs on the ground-floor rear wall, which show up as side-stud connectors facing outward with nothing attached;
  - solid wall seen through glass (×2), which shows up as an opaque body close behind a window pane inside the room.

## 2. The main cost factors, ranked

1. **Contexts grow without limit.** Images, verbose JSON and repeated reading push each context to about 450 k tokens, so every turn is slow and expensive. This is also why the quota ran out.
2. **Onboarding is done five times over.** Each worker spent about 15 min (53 % of its build phase) reading the same documents and designing from nothing.
3. **Too many turns go to proving the work rather than doing it.** For every submodel on every iteration, workers made an isolated render, an in-parent render and a stud map, then wrote logs, defect tables and timestamps by hand.
4. **Parallel heavy contexts exhaust the quota.** The 2–4 h stall was the largest single item of wall-clock time in both runs.
5. **Rework from contract mistakes and duplicated structure.** In addition, the slowest module sets the length of the build phase.
6. **Small repairs are handed to large agents.**

## 3. How to improve the subagent setup

| # | Change | Fixes factor | Expected effect (*estimate*) |
|---|---|---|---|
| 1 | **Small, short-lived task agents.** One agent per submodel (or small group of submodels), given a 2–4 k-token brief: its contract rows, a ~40-line API cheat sheet, the kit snippet and the exact commands. Each repair goes to a fresh small agent with just the submodel file and the finding. | 1, 6 | Context 30–60 k instead of 450 k; each turn about 8× cheaper and faster |
| 2 | **The orchestrator writes the skeleton.** One `generate.py` per module with a function per contracted submodel (correct names, anchors, `export`). The storey core (slab, walls with side-stud courses, ring) is written once as a shared library function. | 2, 5 | First build in about 2 min instead of about 15; about 30 % fewer submodels for workers to write |
| 3 | **Quiet tool wrappers.** `check.sh <module> [submodel]` runs build, contract check and validation, and prints at most 10 lines: PASS/FAIL and the reasons. Add a `--quiet` option to `ldraw-agent build` that leaves out the source map. | 1 | Removes about 85 k tokens per accidental print and most JSON reading |
| 4 | **Automate the visual checks and render less.** Add to `contract_check`: exposed side studs, glass backed by an opaque body, furniture facing, and props standing on tiles. Workers render one module board at two milestones, at about 800 px, re-rendering only submodels that changed. The orchestrator keeps the whole-house visual review. | 1, 3 | 10–15 images per worker instead of 25–50; the 3 unreported integration findings would have been caught at build time |
| 5 | **Test the contract before launch.** Build a contract test model from the kit and storey core (a full wall with every SNOT mount type, plus slab, ring and kerb) and run `contract_check` on it. | 5 | All 3 contract mistakes caught in about 5 min, before any worker starts |
| 6 | **Concurrency within a budget.** Give each task a turn budget (about 40 turns). Run 3 agents at once, or stagger them. Track tokens from the usage lines. | 4 | With contexts about 8× smaller, the quota stops being the limit |
| 7 | **Balance the load and match model to task.** Split large modules (roof becomes structure plus features). Give routine structure and props to a cheap agent, and spend reasoning on the SNOT façades. Use the strong model only for orchestration and integration review. | 5 | Build-phase length set by about a 15-min task, not a 34-min module |
| 8 | **Let the tools produce the evidence.** The checker writes the defect table (JSON to Markdown) and timestamps its own runs; agents add only design notes. | 3 | Saves about 5 min per worker of hand-written logs and tables |

### Projected effect (*estimate*, to be confirmed by a third run)

| | Run 2 (measured) | With changes 1–8 (*estimate*) |
|---|---|---|
| Context per agent | 450–470 k | under 60 k |
| Turns per module | 59–94 | 25–35, split across 2–3 tasks |
| Worker tokens | about 2.3 M final contexts; about 100 M cumulative reads | about 5–10× lower |
| Quota stall | 2 h 24 min | none expected |
| Build-phase wall-clock | 34.7 min | 12–15 min |
| Total active time | about 67 min | 25–35 min |
| Structural quality | 49/49 PASS, 0 structural findings | same contracts and checker, so the same |

**Main risk:** small agents see less of the surrounding model, so cross-submodel problems could slip through. To counter that, keep the in-parent checks inside `contract_check` (scene mode, forbidden zones, interface contacts) and keep one integration review by the orchestrator.

## 4. Suggested next step

A third run that implements changes 1–5 on the same brief and contracts would test these projections directly. Changes 6–8 are configuration and can follow.
