**Definitive plan: improve agent design, construction and learning from examples**

Prepared 2026-10-12 after drafting and a second review against the implementation and Alder Court evidence. This document proposes work; it does not implement the changes or claim they have improved performance.

The objective is an agent that can design an attractive, distinctive large System model, preserve that design while making it geometrically coherent, and finish with substantially fewer repair cycles. Keep the master-led approach: composition, references and visual exploration lead; construction knowledge helps realize and revise those choices. Python generators, the optional kit, ordinary JSON and MPD authoring remain supported. A template library or compulsory DSL must not become the boundary of what agents can design.

**What the benchmark establishes**

The [benchmark report](../reports/alder-court-sol-benchmark.md) records a 2,979-part, 64×48-stud model with a final static PASS and matching BOMs, but a parent aesthetic score of 2.7/5, an empty inaccessible reading nook, and 19 numbered full-model iterations. Approximately 43 active minutes included supervision; quota interruptions prevent an uninterrupted latency claim. These results identify failure modes, not their prevalence across all agents or a controlled improvement over master.

| Observed failure | Implication for this plan |
|---|---|
| Passing prototypes did not survive changes to floor construction and storey height | Teach and support adaptation in the real parent assembly, not just copying an isolated example. |
| Raising windows produced 1,394 disconnected placements; the builder reverted the visual improvement | Provide coordinated edits to openings, bonds and supports so better proportions remain practical. |
| Low windows, plain roofs, weak interiors and planting persisted | Improve visual example discovery and review a representative façade/interior/landscape early. Geometry checks cannot supply taste. |
| Eight feature checks passed despite a sealed, empty room | Separate declared envelope checks from feature completeness and geometry-backed room access. |
| Schema/CLI errors and repeated legacy builds consumed time | Supply one executable workflow, accurate help and actionable diagnostics. |
| More than half the placements were ordinary 1×2 bricks | Do not reward part count as architectural richness. |

The repository already contains 21 building examples, 18 detail examples, reference discovery, extraction, manual review, construction manifests and hash-bound stage acceptance. Existing guides already discuss creativity, actual neighbours and retained features. The first intervention is to make this material usable and trustworthy, not add another general manual or rebuild these systems.

**Delivery sequence**

| Package | Main output | Dependency and decision point |
|---|---|---|
| 1. Clear entry path | Short guidance, runnable starter, corrected CLI/status interpretation | Start here. |
| 2. Curated knowledge | Small diverse reference pack with explicit evidence | Together with 1, test discovery and use before expanding the catalog. |
| 3. Safe construction edits | Bounded bay/corner and floor/stair constructions with shared dimensions | Use the shortlist and observed edit failures to choose implementations. |
| 4. Complete worked section | Attractive, furnished, supported section plus a demonstrated design revision | Uses 3; must transfer into a different parent context. |
| 5. Feature and access evidence | Brief-to-evidence ledger and scoped passage checks | Ledger can start in 1; geometry additions accompany 3–4. |
| 6. Roof construction | Pitched roof, dormer and chimney study | Required before claiming the original roof failures are addressed. |
| 7. Transfer evaluation | Matched microtasks, then large fresh-agent trials | Run small trials after 1–2 and after 3–6; large trials only after these pass. |

**1. Make the recommended workflow short, executable and unambiguous**

Revise [instructions.md](../../instructions.md), [construction-workflow.md](../agent/construction-workflow.md), [complex-models.md](../agent/complex-models.md), [tooling.md](../agent/tooling.md) and [kit.md](../agent/kit.md). Keep one entry path, a compact large-building workflow and links to reference material on demand. Remove duplicated rules from the entry path; preserve subject-specific guidance. Aim for an entry document of roughly 100–120 lines rather than making every agent read the current collection before designing.

Provide a runnable starter under the construction studies, using existing authoring APIs: legal IDs and step arrays, named colours, separate modules, reproducible output and explicit generation-before-check sequencing. Show draft rendering, local construction checking, parent checking and final `stage prepare` → viewed images → `stage review` → `stage export`. Early massing remains renderable without passing construction checks. A generator must finish before dependent checks run.

In [cli.py](../../ldraw_tools/cli.py), correct `construction export --parameters` help: it currently says “JSON object” while the handler reads a file. Clarify that legacy `build` validation is not the modern construction check; update the main complex-model example accordingly. Preserve compatibility instead of silently redefining every legacy command. Use existing direct JSON input to `stage prepare` where appropriate.

Document and expose clearly the distinction between source errors, construction failures, unresolved findings and pending visual review. A `--no-render` stage can have passing technical checks while remaining unreviewed and unexportable; wrappers must not report that simply as a broken build. Improve common schema diagnostics with the offending field and one valid example.

Acceptance: all starter commands run in sequence; the starter reaches modern checks without malformed plans or guessed colour codes; an unreviewed stage still cannot export. CLI regressions cover the actual parameter-file and status mistakes. Validate documentation commands and links rather than adding tests for prose wording.

**2. Turn existing examples into usable construction and visual knowledge**

Use [building-atlas/catalog.json](../../examples/building-atlas/catalog.json), its [catalog generator](../../examples/building-atlas/catalogue.py), [examples.py](../../ldraw_tools/examples.py), the existing reference atlas and [manual/extraction workflow](../agent/build-manuals.md). Add an atlas entry guide and role-based discovery; do not introduce a second knowledge database.

Start by auditing six to eight entries covering contrasting façades, a floor/stair relationship, a roof detail, furniture and planting. Select for teaching value and stylistic variety, not historical `checks_passed` alone. Existing metadata sometimes records passing checks with no visual review. Preserve historical evidence, but label its scope and revision; absence of a current review must remain visible.

Each selected entry should provide:

- A useful exterior/detail view and a view showing supports or the surrounding assembly.
- Editable source, exact part references, named palette roles and source attribution.
- Mounting coordinates, occupied and reserved space, parent dependencies, checked dimensions and permitted edits.
- A brief explanation of the visual effect and an annotated failure or unsuitable use.
- Separate evidence for source validity, construction checks and visual review, bound to the relevant revision, parameters and context.

Keep inspiration available even when it lacks construction evidence. Search results must distinguish those cases and return a small relevant shortlist with preview and adaptation links. Provide alternatives for the same role so agents can learn a technique without reproducing one house style. Audit existing furniture and tree details before commissioning replacements.

Acceptance: fresh-agent microtasks find, inspect and adapt relevant entries without reading the full atlas or treating a historical pass as current approval. Every selected entry has reproducible evidence or an explicit limitation. If agents still ignore or misuse the shortlist, fix its retrieval and presentation before adding dozens of examples.

**3. Make common visual edits preserve construction**

Extend [constructions.py](../../ldraw_tools/constructions.py) and the relevant kit/generator helpers in two bounded increments: first a bay plus its neighbouring wall/corner, then a supported floor with stairwell, stair and landing. The current three construction families do not provide these adaptations.

Use one shared parameter source for sill, lintel and storey levels, floor build-up, opening size and stair destination. The assembly responsible for a window opening must regenerate the surrounding wall courses and bonds; a detached window helper cannot promise to repair an unrelated wall generator. Likewise, changing the upper-floor level must update stairs, landing, supporting floor and reserved headroom together. Publish these ownership boundaries and parent interfaces.

Support an explicit small set of real part/dimension combinations, including representative low/high sill variants and a change corresponding to Alder's 160-to-208-LDU stair rise. Reject unsupported combinations with useful alternatives. Do not scale parts or imply that arbitrary dimensions work. Keep decorative treatment and overall layout independently editable.

Recheck the edited assembly with actual neighbouring parts and the complete model. Bind reusable evidence to parameters, relevant generator/part hashes and parent-interface geometry. Existing stage freshness machinery should be reused; no general dependency solver or incremental geometry cache is needed here.

Add compact diagnostics grouped by responsible assembly and repeated cause, with a representative source-linked pair and a pointer to full findings. Preserve all errors. Report “many descendants disconnected after this interface changed” only when supported by the connection evidence; do not invent an automatic root cause or silently modify the design.

Acceptance: meaningful integration tests raise a bay, change storey/stair height, turn a corner and repeat translated/rotated instances beside real neighbours while retaining support and clearance. Negative controls still reject missing bonds, shifted inserts, occupied openings and unsupported dimensions. Extend [existing construction tests](../../tests/test_construction_stages.py), which already cover supported variants, stale evidence and several negative cases.

**4. Teach a complete building section and its revision**

Create a proposed `examples/construction-studies/adaptable-building-section/` study. It should combine a corner, façade bay, entrance, actual-height floor/landing/stair, supported roof edge, nearby furniture and a small landscape fragment. The point is the interaction between these parts, not a larger catalog of isolated successful fragments.

Show a compact design brief, alternative visual treatments, the chosen composition, open construction views and the actual source edits. Demonstrate one substantial aesthetic revision—such as raising windows—and retain both better proportions and passing construction. Reuse that revised section in a different arrangement, with changed neighbours, before presenting it as a transferable example.

Update [visual-design.md](../agent/visual-design.md) with a few annotated comparisons: proportions and blank wall balance, roof treatment, depth, interior scale and planting. Explain why each choice serves its particular building; do not prescribe universal window ratios, mandatory ornament or detail-density scores.

The recommended workflow should now be concrete: compose freely, establish one convincing section with real interfaces, make an edit safely, then expand. Agents perform these reviews without mandatory user approval pauses. A novel technique remains welcome; it needs local evidence before large-scale repetition.

Acceptance: another fresh agent can make the demonstrated edit and transfer it to a different footprint without copying a complete building. Exterior and open-interior images support a visual judgment, and both local and full checks remain satisfactory. Include assembly-order and support notes; static connectedness alone must not be presented as physical strength evidence.

**5. Make omitted features and sealed rooms visible**

Extend [design-brief.md](../agent/design-brief.md) into a concise worked feature ledger. Before construction, map each core feature to intent, responsible assembly and expected evidence. At review, record met, partial, missing or unverified, with source/check/image links. A room named “reading nook” is not evidence of furnishings or an entrance. Preserve the original requirement when recording a design change.

In [requirements.py](../../ldraw_tools/requirements.py), add an explicitly scoped path for scene-wide obstacle checks on declared passage volumes. Current selected-part AABB checks cannot establish circulation. Start with ordinary axis-aligned System walls, real openings through the full wall thickness, connected passage segments and landing/headroom volumes. A declared room graph alone must never pass a room sealed by geometry.

Account for furniture and neighbouring modules, not only the floor selector used by the builder. State the clearance envelope being checked. Shaped frames, opening door leaves, unsupported orientations or uncertain geometry must remain REVIEW or require additional evidence; this is not a universal pathfinder or door-motion simulator.

Reuse stage review to display outstanding core features and evidence coverage. Structured completeness can reject missing records; image review still judges whether the feature actually fulfills its intended role. Do not claim automatic understanding of an arbitrary natural-language brief.

Acceptance: a fully connected but sealed furnished room fails its declared access requirement; an empty room fails the feature review; furniture from another module blocks a declared route; a supported open route passes within stated coverage. Incomplete evidence cannot masquerade as eight checks proving the entire brief.

**6. Close the original roof/dormer/chimney gap**

Create a bounded pitched-roof study using inspected existing roof examples and actual parts. Specify supported roof geometry, gable/ridge/edge construction, supports, a dormer replacing the appropriate roof area, and a chimney supported through a reserved roof opening. Keep visual proportions editable within checked construction combinations.

Include roof-off, sectional and exterior views, source-linked checks and an assembly sequence. Verify that the chimney continues to support instead of resting on a smooth peak, that roof material does not remain inside the dormer/chimney opening, and that surrounding roof sections remain supported. Publish unresolved physical questions explicitly.

Acceptance: a held-out cottage probe adapts this study to a different composition, with convincing chimney/dormer proportions and satisfactory construction evidence. This is a required milestone for roof coverage. Alder's flat roofs cannot validate these claims, even if the next Alder run improves.

**7. Evaluate whether agents benefit, not whether the new examples pass**

Freeze task briefs, rubric and baseline before implementation. Use the benchmark toolkit revision `d471bc0f170a7b0ef1e9881b3575682caee924da` as the baseline, with a fixed parts library and renderer. Keep fresh runs away from prior benchmark outputs and solutions. Pin GPT-6 Sol at medium reasoning where available; record exact configuration. If unavailable, use the same replacement for both arms and label the change.

First run short tasks for discovery, raising a bay, changing a storey/stair, detecting a sealed/blocked route, and producing contrasting façade treatments. Compare baseline, guidance/curated-knowledge changes alone, and the complete candidate. Repeat failures and promising results to distinguish an incidental success from a useful improvement. Add the roof adaptation probe when package 6 is ready. A second agent capability level on these short tasks is needed before claiming broader agent transfer.

Then run a pilot of four large builds: baseline and candidate on the original Alder brief, and baseline and candidate on a held-out large building with a different style/layout. Keep model, reasoning, tools, library, budget and assistance equal within each pair. Prefer autonomous runs without bespoke parent design coaching; if checkpoints are used, predeclare the same protocol and log every intervention. This is a new matched experiment, not a timing comparison against the interrupted historical run.

Retain Alder's original scope for its matched regression. For the held-out brief, define size through footprint, occupied floors and required architectural/interior/landscape relationships; record part count without rewarding fragmentation. Allow 45 active minutes per large run, including tool and review waits. Report quota interruptions separately; interrupted runs can inform quality but cannot establish uninterrupted speed.

Record time to first usable and accepted model, design/research/repair time, command errors, full-model revisions, lost features, visual-review compliance and final evidence. At least one evaluator other than the builder should assess identically rendered anonymous outputs, blinded to toolkit arm where practical. Use the existing five visual dimensions with concrete observations; these remain judgments, not an objective beauty metric.

Acceptance for each successful large model: static PASS without broad exemptions, matching BOM, all core features fulfilled, reproducible source, current final views, aesthetic mean ≥3.5/5 and no dimension below 3, within the budget. Count failures explicitly. Claim improved efficiency only when matched results support it; a baseline that never finishes does not supply a completion time for a percentage speedup. Four builds are a pilot, so repeat before making reliability claims.

**Scope, stopping rules and review outcome**

Implement packages 1–2 as the first milestone and use microtasks immediately. Continue to the bounded capabilities when the missing operations are confirmed; do not spend weeks expanding an unused library. The next milestone is one attractive complete section that survives a real design edit. Large-scene acceptance and the cottage roof probe then determine whether to expand coverage.

Defer a new DSL, a universal architectural solver, automatic aesthetic scoring, broad collision exemptions, general pathfinding, incremental-check caching and an extensive telemetry platform. The measured final static check was about 1.3 seconds; preserving good design through edits is the higher-value problem. Physical strength, practical assembly and real part/colour availability require their own evidence beyond static PASS.

The [initial draft](../../output/toolkit-improvement-plan/draft.md) was reviewed in a separate [second-pass critique](../../output/toolkit-improvement-plan/review.md) by the primary agent. The review changed this plan materially: it reduced new prose/library expansion, specified ownership of coupled construction edits, replaced graph-only room access with geometry-backed coverage, preserved authoring freedom, added matched trials and a mandatory roof milestone, and moved small agent tests ahead of a broader implementation. The final plan separates documentation improvements from capabilities that require code; more instructions alone are not the proposed remedy.
