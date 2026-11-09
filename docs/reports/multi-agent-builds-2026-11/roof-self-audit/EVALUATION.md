# Roof self-audit exercise — evaluation

**Question:** can a builder agent (Haiku 5.5) find the defects in its own work *before* delivery, if it first splits the model into fine-grained submodels and then audits each one analytically and with ldraw-xray?

## Method
- **Setup.** A fresh Haiku 5.5 agent, told "you built this roof, you have not delivered it yet", working **blind**: no hint of known defects. It worked on a copy (`modules/roof-audit/`) that rebuilt byte-identically to the delivered house.
- **Stage 1 — split.** Split `roof.ldr` into submodels, proving that no geometry changed.
- **Stage 2 — audit.** Audit each submodel, isolated and in its parent, using an analytical and visual checklist.
- **Stage 3 — report.** List the defects and the affected submodels.
- **Stage 4 — fix.** Fix the defects, re-audit, and check for regressions.
- **Orchestrator.** Recorded its own blind list first (`orchestrator-blind-list.md`), then verified independently.

## Time and cost (auditor A1)

| Stage | Time | Duration |
|---|---|---|
| Read docs, set up | 19:00:30–19:01:22 | ~1 min |
| 1. Subdivide + prove identity | 19:01:22–19:07:23 | 6.0 min |
| 2–3. Audit + defect report | 19:07:23–19:18:27 | 11.1 min |
| 4. Fix + re-audit + regression | 19:19:07–19:23:31 | 4.4 min |
| **Total** | | **22.7 min**; 90 tool uses; ~405 k tokens context |

Orchestrator setup took ~1 min and verification + swap ~8 min.

## Result
- **Split:** 15 submodels (+ door4), with all 380 world placements identical. The agent proved this, and I re-proved it independently: 380/380 identical.
- **Defects:** 7 reported, 6 fixed and 1 left as a design choice. Checked by the orchestrator: all 6 fixes are real and visible in `after-iso/` vs `before-iso/`, with no regressions.
  - The roof went from 2 parts outside the scene's main connected group to 0.
  - Non-roof modules are byte-identical.
  - The whole-house review passes and the BOM matches (1390 = 1390).

| id | submodel | kind | found by | status | orchestrator check |
|---|---|---|---|---|---|
| D1 | front-corner-piers | structural: urn caps 6141 unclutched | inspect contacts + check_floating, confirmed by xray close-up | fixed (98138 round tile) | TP, verified |
| D2 | bistro-set | geometric: side chairs face away, backs 5 LDU into the table | analytical (rotation vectors + overlap depth) | fixed | TP, verified in top view |
| D3 | front-parapet, pediment | contract: coping/cap project to Z -9 (only the cornice may) | analytical (envelope by part) | fixed | TP; I had missed it, even after checking bounds, because I checked the envelope rather than which part owns it |
| D4 | front-parapet | visual: dentil pattern not symmetric | xray render | fixed | TP, verified |
| D5 | skylight | contract: studs reach h204 > 200 | analytical (max top) | fixed (tiles) | TP |
| D6 | pergola | geometric: slats 0.5 stud off-centre | analytical (arithmetic) | fixed | TP; now symmetric, though spacing is uneven (3-stud middle gap) |
| D7 | planters | visual: plants read as drums | xray render | not fixed (design) | TP, matches my O5 |

## Against the orchestrator's blind list (`orchestrator-blind-list.md`)
- O5 (planter plants look like drums): found by the agent as D7, but not fixed.
- O8 (urn caps): found and fixed as D1.
- O6 (dark chairs unreadable): the agent found the real defect underneath, chairs facing the wrong way (D2), and fixed that. The chairs are still dark minifig seats.
- O7 (pergola front support): the agent rated the pergola clean apart from slat centring. I confirmed four posts in the after renders.
- O1–O4 (envelope protrusions): my own false positives, an illusion of the perspective "top" view. The agent made none of these; it checked envelopes analytically.
- **The agent found 4 issues I did not**: D2's actual cause, D3, D4 and D5.

## Against the user's spotted defects
_Pending: user to list the roof defects they saw. Each will be classified as found + fixed, found + not fixed, or missed._

## Observations
- **Splitting the model helped the audit.** The per-submodel overview boards (16 mosaics) and per-section `inspect` turned a 380-part blob into small, explainable units. Each defect landed in a named submodel, so fixes stayed local, and regressions could be checked per section.
- **The analytical checks did most of the work:** 5 of 7 defects came from metrics (contacts, envelope by owner, max height, rotation vectors, symmetry arithmetic). xray contributed the visual-only items (D4, D7) and confirmed the analytical ones.
- **Proof discipline was good.** The agent proved geometry identity, then wrote the before/after evidence for each defect, with honest limits: `connections` ignores submodels, many contacts are only heuristic, and it did not fix the design issue.
- **Weak spot: taste.** The agent did not judge the composition. It accepted heavy plain elements: the stair-house is a plain grey box, the pediment a red block behind the parapet, and the chairs dark minifig seats. It also left the "drum" plants unfixed. Aesthetic quality still needs a reviewer with a design brief, or explicit aesthetic criteria in the checklist.
- **Cost:** 22.7 min and ~405 k tokens to audit and fix one 380-part module, about 1.5× the time it took to build it. Across five modules in parallel, that is roughly +23 min of wall-clock per delivery.

## Recommendation
Make "split, then audit per submodel" a standard pre-delivery step for workers. These checklist items earned their cost:
- inspect contacts per section, plus the whole-scene `check_floating`;
- the envelope check reported by **owning part**, not just bounds;
- max-height and stud-grid checks;
- rotation/facing vectors for furniture-like parts;
- left/right symmetry;
- per-submodel overview boards.

Also add explicit aesthetic prompts ("does every element read as what it is?") and require the agent to fix design-level findings rather than just record them.
