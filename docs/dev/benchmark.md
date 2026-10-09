# Generation benchmark

Use this benchmark before and after a toolkit, documentation or harness change. A change is an improvement only if it moves these numbers on the same prompts and agent tiers.

## Prompts

Run each prompt in a fresh session or chat, starting with "Read instructions.md, then ...".

| ID | Family | Prompt |
|---|---|---|
| B1 | Building | build me a cosy two-storey house with a garden |
| B2 | Street | build me a modular street corner with three shops |
| V1 | Road vehicle | build me a classic pickup truck at minifigure scale |
| S1 | Spaceship | build me a starfighter with a cockpit and two engines |
| T1 | Technic vehicle | build me a Technic off-road buggy with steering and suspension |
| M1 | Machine | build me a small Technic machine with a working gear train |

## Agent tiers

| Tier | Example models | Harness |
|---|---|---|
| High | Opus 5.5, GPT-6 Astra | Claude Code / web app |
| Mid | Sonnet 5.5, Gemini Pro | Claude Code / web app |
| Low | Haiku 5.5, Qwen3.8-27B, Gemini flash-lite | Web app, 150-step cap |

## Metrics

Collect process metrics with `.venv/bin/python scripts/session_stats.py PATH...` and model metrics with the toolkit checks on the delivered MPD.

| Metric | Source | Target |
|---|---|---|
| Completed (delivered MPD matching the prompt) | Transcript, output | Mid tier: 6/6. Low tier: B1, B2 and V1 |
| Wall time, tool minutes, tool calls, cost | `session_stats.py` | Below the baseline |
| Docs read (kchars), images viewed, helper scripts written | `session_stats.py` | Helpers ≈ 0 |
| Floating parts, collisions | `check` on the delivered MPD | 0 and 0 |
| Visual score 1–5 (silhouette, proportions, detail) | User review of the contact sheet | ≥ 3 for the mid tier |

## Baselines (before the 2026-10 rework)

Measured from existing transcripts and chats. "Defects" were re-checked with `validate --contacts all`.

| Run | Tier | Wall | Cost | Tool calls | Tool min | Docs read | Helpers | Outcome |
|---|---|---|---|---|---|---|---|---|
| Crane (T1-like), Opus 5.5 | High | 1.6 h | $21.6 | 185 | 40.8 | 129k | 3 | Delivered; 350 isolated parts undetected |
| An-225 (V1-like), Opus 5.5 | High | 4.2 h | $32.9 | 267 | 61.3 | — | 5 | Delivered |
| Spaceship (S1), Sonnet 5 | Mid | 1.7 h | $14.2 | 164 | 47.3 | 142k | 3 | Rated "not good" |
| Cottage (B1), Qwen3.8-27B, attempt 1 | Low | 3.0 h | — | 171 | 21.1 | 15k | 1 | Stopped at the 150-step cap |
| Cottage (B1), Qwen3.8-27B, attempt 2 | Low | 5.2 h | — | 118 | 8.5 | 26k | 1 | Decent 1,124-part model |
| Buggy (T1), Gemini Pro | Mid | 1.4 h | — | 40 | 2.6 | 4k | 0 | 154 parts; floating, crossing beams |
| Crawler (T1), Gemini 3.1 flash-lite | Low | 0.1 h | — | 43 | 1.0 | 4k | 0 | 9 parts |
| House (B1), Gemini 3.1 flash-lite | Low | 0.03 h | — | 25 | 0.3 | 0 | 0 | 3 parts |
| *Reference: ldraw-mecha rig, Sonnet 5.5* | Mid | 0.5 h | — | 132 | 5.9 | 30k | 4 | Success |
