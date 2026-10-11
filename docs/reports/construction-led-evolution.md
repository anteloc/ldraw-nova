# A more practical direction after Willow Quay

Subsequent implementation: [construction stages, fitting calibration and test evidence](construction-stages-implementation.md). The results below describe the original experiment before that implementation; its raw reports remain unchanged.

**Keep master's design process, and make construction reuse and staged verification the working foundation.** An agent should choose and refine the architecture, then compose inspected constructions with deterministic placement. New construction remains possible, but it needs a small successful example before it is repeated throughout a large model.

The earlier hybrid was insufficient. It restored visual instructions and supplied optional placement helpers, but still let one agent invent thousands of placements and defer the decisive construction check. The Willow Quay run demonstrates that this is not a dependable workflow for the tested agent. More instructions or a different coordinate DSL alone will not solve it.

## What failed

The frozen Willow Quay contains 2,694 parts. Source validation, the older geometry check and LeoCAD import passed. The independent newer check reported 178 collisions, two seating errors, 48 overlap reviews and 2,364 parts outside its largest recognized connected group. The latter count is a diagnostic, not proof that each of those parts physically floats. Matching window inserts can also trigger misleading findings.

However, the model has directly inspectable construction defects. A two-part extraction reproduces a wall brick intersecting a storefront frame. The selected lowest front-wall brick ends at Y=-16 while the underlying foundation's top is Y=-8; no pad touches its underside. The canopy is four studs deep but ends half a stud before the front face of the door frame. These are failures of construction and feature relationships, not merely strict checker output. [Measurements and source lines](../../output/hybrid-benchmark/willow-quay-sol/evaluation/confirmed-interface/measurements.json) · [isolated intersection views](../../output/hybrid-benchmark/willow-quay-sol/evaluation/confirmed-interface/preview/look.png).

The appearance also regressed: extensive repetitive wall grids, small openings relative to the walls, striped roof courses and sparse landscaping. Adding more of those parts did not create richer architecture. The agent did not preserve master's stronger façade vocabulary through reference-based construction study. It omitted the required newer whole-model check, despite spending time on repeated older checks.

The independent static check took 7.93 seconds including CLI startup; checking itself was not the dominant cost. Reliable uninterrupted generation time cannot be recovered because the run includes an account-limit interruption and a later unexplained clock gap. The recorded first draft arrived after about 75 seconds. The failure was that the subsequent construction and repair process did not converge to an acceptable model.

## A concrete alternative was tested

I used the existing Copper Lane design as a construction-reuse control. This deliberately preserves an attractive composition the repository already has. It is an adaptation experiment, **not** a claim that an agent invented a new attractive building in seconds, and it does not demonstrate open-ended creative generalization.

The unchanged newer checker found two collisions, 15 disconnected parts and 44 overlap reviews in the original 1,655-part Copper Lane. Inspection identified two local repairs:

1. Move the lamps forward by 40 LDU, together with their exposed pavement mounting openings. This clears the awnings while preserving actual attachments.
2. Raise the vertical BOOKS tile by 10 LDU. Its two socket rows had been centred around the side studs, rather than placing a row on them. The repair aligns one socket row with all four studs.

The scripts regenerate copied plans at three sizes. They preserve the original example and all model features. Neither checker code, tolerances nor part metadata were changed.

| Construction variant | Physical parts | Reported collisions / seating / duplicates | Raw disconnected parts | Raw overlap reviews | Generate, assemble and check |
|---|---:|---:|---:|---:|---:|
| Three-storey bookshop + two-storey house | 1,655 | 0 / 0 / 0 | 14 | 44 | 5.16 s |
| Four-storey bookshop + three-storey house | 2,153 | 0 / 0 / 0 | 22 | 60 | 4.44 s |
| Five-storey bookshop + four-storey house | 2,651 | 0 / 0 / 0 | 30 | 76 | 5.38 s |

These are one warm-cache run, excluding library initialization, design, reference study, repair-code development and rendering. They establish that increasing model size need not require an agent to perform proportionally more coordinate reasoning. They do not establish end-to-end agent latency.

Every remaining finding matches one of four exact frame/insert relative poses in `data/models-annotated/10270-1.mpd`: `60592`/`60601`, `60596`/`57895`, and the two `60594`/`60608` pane positions. The evidence records source hashes, actual reference records and the matching occurrence in the new assembly. Incorrectly shifted panes are not accepted. This is corroboration from an annotated LDraw reference, not independent proof of real-world fit.

**The full models' raw verdict remains FAIL.** No evidence was hidden or converted into an automatic pass. The three-storey model has 58 reference-supported findings; the largest has 106. No other finding remained in these reports. Fixing this known fitting coverage is a bounded checker task, substantially different from repairing a building's unsupported walls and occupied openings.

Controls help distinguish construction evidence from a permissive check:

- A diagnostic copy without the window inserts passes for its remaining 1,597 parts. This isolates the issue; the actual models keep all glazing.
- Restoring the half-stud sign mistake fails and identifies the disconnected sign.
- Raising the roof one plate fails and identifies a disconnected roof assembly.
- Moving an arched-window pane half a stud fails and no longer matches the reference pose.

Python and LeoCAD BOMs match exactly for the 1,655- and 2,651-part models. I opened the revised three-storey home, front and back views and the largest variant's home view. The original arched bays, projecting cornices, awnings, sign, contrasting roofs and landscaping remain. The taller variant is a repetition stress test; its repeated elevations are less interesting, and it is not offered as a superior composition. Rear elevations remain plain. This study also retains Copper Lane's stated scope: simple interiors and removable floors, without stairs.

[Three-storey model](../../output/construction-approach-study/reuse/3-floors/copper-lane-study.mpd) · [preview](../../output/construction-approach-study/reuse/3-floors/preview/home.png) · [raw check](../../output/construction-approach-study/reuse/3-floors/check.json) · [reference evidence](../../output/construction-approach-study/reuse/3-floors/reference-evidence.json) · [BOM comparison](../../output/construction-approach-study/reuse/3-floors/bom-comparison.json).

[2,651-part model](../../output/construction-approach-study/reuse/5-floors/copper-lane-study.mpd) · [preview](../../output/construction-approach-study/reuse/5-floors/preview/home.png) · [timings and source hashes](../../output/construction-approach-study/reuse/experiment.json) · [controls](../../output/construction-approach-study/reuse/3-floors/controls/summary.json) · [reproduction scripts](../../examples/construction-studies/copper-lane/README.md).

## What the approach should become

**Creative composition is the first decision; engineering begins before detailed repetition.** The designer chooses the building's silhouette, proportions, setbacks, materials, roof character and focal features. A lightweight render establishes whether those choices are attractive. The engineering stage then finds constructions that realize that intent. If one cannot work, change that assembly while its cost is small and review the visual consequence.

The reusable unit should normally be a construction technique: a bonded floor, glazed bay, wall corner, stair/landing, supported roof section, dormer or chimney opening. It should not be a mandatory whole-house recipe. Several structural and visual alternatives are needed so every design does not become Copper Lane. Novel assemblies remain allowed; they enter as small studies with explicit unresolved status until inspected.

Each reusable construction needs exact parts and relative placement, actual mounting surfaces, occupied and reserved volumes, supported parameter ranges, assembly steps, reference provenance, and positive/negative checks. Reusing an assembly without its parent interface or shrinking it arbitrarily loses the relevant evidence. Parameterized generators should derive wall openings and attachment grids from those measured parts.

A deterministic builder then repeats and places established assemblies. The agent spends its reasoning on composition, selecting constructions and a limited set of genuinely new joins. A less capable agent can implement or revise one bounded module with an explicit parent interface instead of inventing an entire building's coordinate system at once.

Module checks must run both in isolation with test supports and in their actual parent. The assembled model still requires collision checks, attachment evidence, feature relationships and a visual pass. A large scene made from valid subassemblies can still have invalid joins.

## Implementation priorities

1. **Establish a small architectural construction library.** Begin with the patterns implicated by this failure: bonded base/walls, fully reserved glazed openings, floor/stair interfaces, supported roofs, dormer/chimney openings and useful canopies. Adapt master's strongest constructions and inspected references; add contrasting styles and parameter-boundary tests. This is reusable geometry with evidence, not another long prompting guide.
2. **Make stage checks automatic across authoring routes.** A stage runner should accept ordinary MPD, Python or JSON output, always run the same checks, render the affected interface, and bind results to the source hash. It should prevent promotion of a failed repeated assembly while allowing visual drafts. The current kit gate only protects kit users; Sol's custom generator bypassed it.
3. **Resolve legitimate fittings narrowly.** Use exact part identities, transforms, library versions and inspected reference evidence for window inserts and similar special fits. Keep collisions with surrounding walls active. Do not reinstate family-wide overlap exemptions or silently increase tolerances. The study's evidence script is an inspection prototype, not this production capability.
4. **Preserve feature and visual acceptance.** Check canopy coverage, roof openings, door clearance, stair access and other promised relationships. Review composition before detailed expansion, then again after engineering and decoration. Aesthetic quality remains a separate human/visual judgment; connectivity and part-count targets cannot substitute for it.
5. **Retest Sol on new compositions using the established constructions.** Keep model/library settings fixed, cap the initial prototype effort, record retries and separate design time from tool time. Include a new risky feature to test how it handles unfamiliar construction. Repeat across several designs before claiming reliability or a speed improvement.

This turn adds the reproducible study and updates [the working instructions](../../instructions.md) and [large-model workflow](../agent/construction-workflow.md) to establish constructions before repetition. It does not pretend the construction registry, universal stage runner or special-fitting calibration already exist.

The revised Copper Lane is materially closer to a buildable model than Willow Quay under the available evidence. Static checks and reference agreement still do not establish strength, every insertion order or purchasable part/colour combinations. Those require further inventory/instruction checks and, for a firm physical claim, a real assembly trial.
