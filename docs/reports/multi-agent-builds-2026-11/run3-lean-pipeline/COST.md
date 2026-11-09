# Run 3: cost and results (final, after the quality pass)

The measured costs come from `costs.jsonl`: each headless `claude -p` call's `total_cost_usd`. The solo-Opus figures and the orchestrator-session figures are **estimates**.

## Measured agent costs

| Phase | Calls | Cost (USD) | Largest prompt |
|---|---|---|---|
| Pass 1: 16 Haiku build tasks | 16 | 0.370 | 73.7 k |
| Pass 1: repairs, 2 rounds (Haiku) | 16 | 0.358 | 105 k (one call crossed the 100 k tier) |
| Pass 1: Opus reviews (one wasted) | 2 | 0.258 | 18 k |
| Quality pass: 16 tasks (3 Sonnet 5.5: $0.44; 13 Haiku: $0.23) | 16 | 0.670 | 75 k |
| Quality pass: Opus close-up review | 1 | 0.215 | 18 k |
| Quality pass: repairs (Haiku and Sonnet) | 5 | 0.094 | 29 k |
| **All agents** | **56** | **1.96** | |

## Orchestrator session (this conversation, Opus 5.5) — estimate
- **Supervision, diagnosis, fixes and visual audits** across both passes: about **$6**. Most of that is cache reads of a context of about 400–450 k tokens that carries two earlier experiments.
- **One-off infrastructure:** about $5, not counted.

## Solo Opus 5.5 — estimate (`cost_model.py`, same measured token profile repriced)

| Estimate | USD |
|---|---|
| Lower bound (impossible fresh contexts, × 0.6 turns) | 6.72 |
| Realistic (one accumulating context, compaction at 200 k, × 0.6) | 16.17 |

## Verdict

| | USD | vs lower bound | vs realistic |
|---|---|---|---|
| Agents only | 1.96 | 3.4× cheaper | 8.3× cheaper |
| Agents + this orchestrator session | about 7.96 | **1.2× more expensive** | 2.0× cheaper |

- **The agent work is clearly cheaper than one Opus agent.** Counting the human-facing Opus session, the setup beats the realistic solo estimate but not the lower bound.
- That session is the cost to cut. Launch `orchestrate.py` from a fresh session, or fully headless, and review only the final module close-ups. That would put the total at about $2.5–3.
- It took two passes. The first pass's low quality, which the user caught, required new visual checks, quality rules and Sonnet for three façade tasks.

## Quality (final `linden-row.mpd`; `review/`; `AUDIT.md`)
- **Build:** 0 errors, 1655 parts. Validation passed; BOM matches LeoCAD.
- **Contract checks:** 48/49. The one FAIL: two floor-3 rear window frames are not connected.
- **No visual-check failures:** no blocked windows, no bare outward studs, no deep interpenetration.
- **Main contact group:** 1615 of 1655 parts.
- **Visual: about 3.5 out of 5** (run 2: 3.9).
  - Good: striped canopy, open windows with tiled surrounds, smooth cornices and pilasters, dentils.
  - Weak: no readable sign, sideways window-box flowers, blocky interiors, stacked-brick lamps, a loose beam on the roof.

## Time
| Phase | Clock | Duration |
|---|---|---|
| Pass 1 | 01:17–01:34 and 01:47–02:08 | 37 min |
| Quality pass | 02:35–02:52 | 17 min |
| My diagnosis and fixes in between | — | about 1 h |

There was no quota stall.
