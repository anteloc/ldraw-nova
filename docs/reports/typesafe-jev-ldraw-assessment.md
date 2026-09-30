# TypeSafe and Jev for automated LDraw generation

Prepared 2026-09-23. Workload: **automated production above 100 models/month**, with scenarios at 100, 1,000 and 10,000. Dollar amounts are USD.

Follow-up: the [2026-09-24 assembly-discovery evaluation](jev-assembly-discovery-assessment.md) reports live Jev queries against the three `full_description` views, source audits and rendered assembly inspections. The discussion below retains its original scope and estimates.

Your concern is justified. **The cathedral demonstrated a narrow retrieval use, not an improvement in model quality. TypeSafe's broader advantages were substantially underused, but using more features would not by itself produce a better cathedral.** The most promising extension is to select reusable assemblies with explicit evidence and check whether a generated design meets its brief. Better part retrieval is a smaller, useful experiment. Replacing geometry checks or visual review with Jev would make the process less trustworthy.

For a fully automated workload, I recommend a bounded benchmark first, then assembly selection and brief coverage checks if they beat simpler baselines. A cheaper-generator/escalation workflow could eventually save more operating money, but needs stronger evaluation. I would defer learned aesthetic scoring and automatic feature discovery until there are enough independently reviewed builds.

**How to read the estimates.** Historical usage and inspected repository behavior are observations. API contracts and cookbook results are vendor documentation. Every future LDraw benefit, workload budget, implementation estimate and break-even figure below is an explicitly hypothetical planning scenario. No new Jev inference, model generation, or A/B experiment was performed for this assessment. There is no measured LDraw accuracy lift to report.

The accompanying [reading audit](typesafe-jev-reading-audit.md) covers all **111 indexed documents**, including all 18 cookbooks and both SDK reference trees. Its [JSON manifest](typesafe-jev-reading-audit.json) records URLs, retrieval times, hashes and page-specific findings. All narrative, examples, cookbook implementations/results and SDK contracts were read. Presentation markup was normalized; linked external datasets, contracts and videos were not exhaustively reviewed. This establishes documentation coverage, not practical mastery proved by deployments.

## What the cathedral actually established

The [historical usage report](../../output/cathedral/JEV_TYPESAFE_USAGE_REPORT.md) records three successful searches, 1,500 Jev calls and 752,364 input tokens. Each search scored up to 500 descriptions and returned ten alternatives. Four retrieved references appeared in 253 of the final 5,394 placements. The rose-window wheel search did not supply the final dish solution.

That is evidence of candidate discovery and reuse. It does **not** establish that those parts were better than ordinary search results, that Jev saved time, or that the final model improved. The 4.69% placement share measures provenance, not artistic contribution: a single focal part can matter more than hundreds of wall bricks. No matched baseline or blind visual comparison was recorded.

At the currently published input price, the successful cathedral calls would cost **$0.031599288**. This is a present-price calculation, not a verified historical invoice; failed attempts and their unknown usage are excluded. The recorded CLI times sum to 28.48 seconds, not an end-to-end generation time or a sustained-throughput benchmark. The concurrent cache-lock failure is a real production concern even though its inference cost was small.

The [TypeSafe skill](https://docs.typesafe.ai/agent-skill) is guidance for the coding agent. It is not another model, executable build service or runtime integration. Its value here should be a better decomposition of decisions and evidence. The historical work applied narrow relevance scoring, but not shared-state batching, multiple reusable judgments, calibrated escalation, bounded handler selection, assembly retrieval or outcome evaluation.

## What the current tools already provide

Inspected revisions: `ldraw-nova` at `de65bcaf62f6659312b50b59c4d8ed514241c5b2`; sibling `jev-rerank` at `1e9bc79ff3d01773bdba40890a27e701be5196c8`. These identify the current inspection, not the exact source used by every historical cathedral HTTP request.

| Current capability | Evidence | Consequence for a proposal |
|---|---|---|
| Exact/keyword part search; category symbols; installed availability; legacy filtering; optional measurements | [catalog.py](../../ldraw_tools/catalog.py), [tool reference](../agent/tooling.md) | Extend retrieval; do not rebuild known metadata with AI. Snapshot dimensions are hints, not attachment geometry. |
| Model/submodel FTS search; source sections; study and dependency-closed extraction | [resources.py](../../ldraw_tools/resources.py), [complex models](../agent/complex-models.md) | There is already a reuse path. Jev can rank its candidates; extraction and attribution stay deterministic. |
| 21 building examples and 18 detail entries, with interfaces, bounds and review metadata | [atlas catalog](../../examples/building-atlas/catalog.json), [examples.py](../../ldraw_tools/examples.py) | Start with this small corpus; a complex taxonomy is unnecessary at this size. |
| Procedural modules, named anchors, palettes and detail recipes | [architecture.py](../../ldraw_tools/architecture.py), [details.py](../../ldraw_tools/details.py), [builder.py](../../ldraw_tools/builder.py) | A closed set of template choices can become executable decisions. Freeform design still needs generation. |
| Schema/reference/transform checks, partial geometry and connector evidence, snapping | [validation.py](../../ldraw_tools/validation.py), [geometry.py](../../ldraw_tools/geometry.py), [connectivity.py](../../ldraw_tools/connectivity.py) | These own arithmetic and placement constraints. A semantic answer cannot extend their coverage. |
| Part boards, multi-view renders, BOM comparisons and written visual review | [visual design guide](../agent/visual-design.md) | Actual images remain necessary to judge appearance. A purpose string is not proof of visibility or quality. |
| One Noul per candidate; persistent cache; bounded concurrency; explicit yes/no criteria | Jev reranker and query parser inspected for this report; use the global `jev-rerank` CLI | Better criteria are possible immediately; batching and multidimensional results need code changes. |

An important counterexample is the atlas [battlement validation](../../examples/building-atlas/details/battlement/validation.json): `checks_passed: true` accompanies a disconnected-evidence warning, 17 inferred groups and `physical_validity: not_proven`. Its [visual review](../../examples/building-atlas/details/battlement/visual-review.json) covers an isolated view. A module catalog must preserve those qualifications; calling the whole atlas “physically verified” would be false.

The sibling project currently pins `typesafe-sdk>=0.5.7,<0.6`. Current docs describe Python 0.7.1; 0.6 changed Score criteria to ordered lists and 0.7 changed serialization to Pydantic. Existing Noul operation does not require an emergency migration, but a new integration must deliberately select and test its SDK contract. [Python changelog](https://docs.typesafe.ai/sdk/python/changelog).

## Product capabilities that matter here

Jev evaluates text or structured textual state and returns typed judgments. `Choice` selects among named alternatives; `Noul` returns the probability of a yes/no condition; `Score` returns an expected position on an ordered descriptive rubric. Choice supports up to 255 options; Score supports up to ten levels. These are useful interfaces, not guarantees that the judgment is true. [API contract](https://docs.typesafe.ai/api), [primitives](https://docs.typesafe.ai/primitives).

The current model is `jev-1.13.0`, priced at **$0.042 per million input tokens**, with free output. Published limits are **1,200 requests/minute**, **250,000 tokens/second**, 64k total request context and 32k for state plus the longest question. Limits can change. Input is text only; customer-specific fine-tuning/LoRA is not offered. Pin the version when evaluating thresholds. [Models](https://docs.typesafe.ai/models).

Useful design rules, applied to this repository:

1. **Measure first, judge second.** Code supplies actual dimensions, known connector types and named colour properties. Jev may judge whether a described motif suits a Gothic facade; it should not calculate stud spacing, count placements or interpret a rotation matrix. The vendor explicitly documents weaknesses in arithmetic, indirection and long irrelevant state. [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).
2. **Separate independent decisions.** Role relevance, descriptive stylistic match and whether evidence is sufficient can be separate questions. A broad “is this a good part?” hides the reason for failure. Independent questions can share a request; answers cannot refer to other answers in that request. [Building guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one), [fan-out](https://docs.typesafe.ai/patterns/fan-out).
3. **Preserve the distributions.** A Noul near 0.5 means uncertainty about yes, not medium artistic suitability. A Score is an expectation over described levels, not a calibrated beauty percentage. Choice probabilities are relative to that option menu; do not compare winners from separate shortlists as if their probabilities were absolute suitability. [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [Choice](https://docs.typesafe.ai/primitives/choice).
4. **Keep a no-match path.** A confident Choice still picks something when every offered candidate is wrong unless the menu/policy permits rejection. Gate the selected candidate's suitability, not merely whether some candidate passes. Several equally acceptable decorations need not trigger human review just because the Choice is uncertain. [Skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion), [semantic find](https://docs.typesafe.ai/cookbooks/semantic_find).
5. **Keep policy and reuse in code.** Normalize a Score by its maximum level before mixing scales; weight only compensating preferences. Missing required features and known invalid geometry should not be averaged away by attractive decoration. Cache raw judgments by evidence, question/rubric and model version; changing weights alone need not rerun inference. [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring).
6. **Validate confidence locally.** A confidence value is derived from the returned distribution, not a measured probability that the complete build is correct. Select operating thresholds from held-out LDraw outcomes and the cost of errors. Do not assume separately asked conditions are statistically independent or complementary. [Confidence](https://docs.typesafe.ai/confidence), [confidence routing](https://docs.typesafe.ai/patterns/confidence-routing).

## Proposed use cases

The eleven cases below are alternatives and extensions, **not a recommendation to implement all eleven**. The shared foundation and individual costs follow this section. Benefits mean incremental improvement over the named simpler baseline, not all the benefit of search, reusable modules or validation in general.

### U1 — Select parts using several narrow judgments

**Change.** Introduce a retrieval adapter around `catalog.search_catalog` and the sibling reranker. Union lexical/category candidates for one role, remove known unsuitable record types in code, and obtain current metadata for finalists. Evaluate role match with Noul and one or two descriptive dimensions with Score. Let code produce a ranked shortlist with dimensions, evidence and explicit rejection reasons. Preserve `part` inspection and `part-board` review.

For the cathedral, “a circular radial ornament for a cathedral rose window” leaves room for a dish, grille or wheel. “A wheel” unnecessarily restricts both candidate retrieval and semantic judgment. No reranker can recover a dish omitted from the shortlist. Compare candidate recall before reducing the existing 500-candidate budget to the proposed 50. Known IDs, aliases and numeric filters remain exact operations.

**Baseline and benefit hypothesis.** Compare against both the current one-Noul CLI and keyword/category search with the same filters. Working scenario: avoiding one $5 selection/rebuild failure per 50 generated models saves **$0.10/model gross**; explore $0–$0.50, including no improvement. A semantic feature can matter aesthetically, but this estimate does not attach a dollar value to an unmeasured visual preference.

**Cost and test.** 24–48 engineering hours, 8–16 reviewer hours; approximately 12 requests/240k input tokens per model for six roles × 50 candidates × three judgments, batched 25 candidates at a time. Target 1–5 seconds added retrieval latency under light load, to be measured. Keep only if acceptable-candidate recall is preserved and top-five suitability improves enough to lower total selection/rebuild cost. Stop if deterministic filtering accounts for the improvement. The likely failure is sparse descriptions that do not describe visible shape. [Reranking recipe](https://docs.typesafe.ai/cookbooks/rerank_typesafe), [structured questions](https://docs.typesafe.ai/primitives/advanced).

### U2 — Retrieve reusable assemblies and construction examples

**Change.** Rank atlas details and actual OMR submodel candidates using role, scale category and construction intent. Start with existing catalog/interface files, then add `study` metadata and source excerpts for a small shortlisted OMR set. Code checks source freshness, dependency closure, anchors and required footprint. Jev selects an appropriate construction pattern; `extract`, `includes` and `attach` implement reuse.

A suitable complete window bay or buttress can save more decisions than a better arch part. It also carries more risk: a reused module may have unresolved connector evidence or be incompatible with its new surroundings. Keep source warnings and original attribution. Revalidate the containing assembly after adaptation. This is semantic retrieval of assemblies, not geometric fit prediction.

**Baseline and benefit hypothesis.** Compare against the current 39-entry atlas search plus straightforward tags/FTS. Assume an additional 10% of models successfully reuse an assembly, avoiding $4 of generation/repair cost each: **$0.40/model gross**, sensitivity $0–$2.00. The word “additional” matters: credit only reuse that the baseline failed to find.

**Cost and test.** 48–96 engineering hours and 16–32 reviewer hours, assuming existing assets and a bounded pilot corpus; authoring missing assemblies is additional work. Budget four requests/150k input tokens per model, roughly 0.5–3 seconds for semantic selection, excluding source inspection/extraction. Measure accepted reuse, adaptation failures and downstream repair cost. Stop if simple tags retrieve the same modules or adaptation costs consume the saved generation. This is the strongest quality/process candidate, but the small current atlas may make a simpler search upgrade sufficient. [Skill selection](https://docs.typesafe.ai/cookbooks/skill_suggestion), [hierarchical selection](https://docs.typesafe.ai/cookbooks/hierarchical_classification).

### U3 — Interpret a brief into bounded template choices

**Change.** For routine supported requests, ask Choices for known building family, roof family and palette role; ask Nouls for independent features. Code extracts possible numbers/part IDs from the brief, Jev selects their semantic role, and code converts units and validates ranges. The controller calls known functions in `architecture.py`/`details.py`. Explicit absence and unsupported-request outcomes preserve a generative fallback.

This can turn “a small stone chapel with a gabled roof and two side windows” into choices among existing procedures. It cannot invent a cathedral assembly or infer exact dimensions from adjectives. Conflicting requirements need a recorded resolution or escalation, not silent defaults. Branch-specific questions can run together; unused branches are ignored.

**Baseline and benefit hypothesis.** A schema form, presets or the existing generator may already do this adequately. If 30% of production requests can skip a $0.20 planning step, gross savings are **$0.06/model**; sensitivity $0–$0.30. Creative variety can decrease if too many requests are forced into templates.

**Cost and test.** 24–48 engineering hours, 4–8 reviewer hours; one request/6k input tokens, approximately 0.2–1 second. Evaluate field accuracy, explicit omission handling and supported-request coverage. Retain only if downstream rework does not erase the skipped planning cost. Unknown templates always fall back. [Function calling](https://docs.typesafe.ai/cookbooks/function_calling), [span selection](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook), [component extraction with arithmetic in code](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook).

### U4 — Check semantic coverage of the brief before and after building

**Change.** Maintain a requirements ledger tied to evidence. At planning time, compare each requested feature with selected module descriptions. After building, compare against realized sections, resolved references, measurements and independently reviewed observations. Choice outcomes such as supported, contradicted and insufficient evidence make missing evidence visible. Code counts features and verifies numeric constraints.

For “two tall towers and a rose window,” code counts towers and measures heights; Jev can map natural-language requirements to known module roles. A placement named `rose-window` is weak evidence. Actual visibility, proportion and recognizability require render inspection. The final manifest should distinguish planned, present, visually reviewed and unresolved features.

**Baseline and benefit hypothesis.** Use an explicit checklist and deterministic plan assertions first. Working scenario: catch an additional 4% of models before a $5 rework event, saving **$0.20/model gross**; sensitivity $0–$1.00. False alarms add unnecessary edits, and false acceptance can preserve omissions.

**Cost and test.** 24–48 engineering hours, 8–16 reviewer hours; two requests/18k input tokens, approximately 0.4–2 seconds beyond evidence collection. Test on deliberately omitted, renamed, hidden and contradicted features, plus normal builds. Retain only if missed requirements fall without excessive false repair requests. This is the other first-priority experiment. [Evidence checks](https://docs.typesafe.ai/cookbooks/citation_check), [field-verification cascade](https://docs.typesafe.ai/cookbooks/sde_cascade).

### U5 — Select relevant construction guidance and source context

**Change.** Add semantic reranking after `resources.search_spec`, model-section search and documentation retrieval. Classify each passage for relevance and whether it supplies usable construction evidence. Keep conflicts available for resolution instead of filtering them away. Mandatory assembly, attribution and review instructions remain an explicit part of the controller's context policy.

**Baseline and benefit hypothesis.** Better chunking, source headings and tags are cheaper alternatives. A working case saves 4,000 billed generator input tokens/model, valued at an **assumed effective $5/million**, or **$0.02/model gross**; sensitivity $0–$0.10. That rate is a scenario input, not a quote for any generator. If the actual billing model does not charge marginal context this way, cash savings can be zero.

**Cost and test.** 16–32 engineering hours, 4–8 reviewer hours; four requests/36k tokens, approximately 0.4–3 seconds. Compare complete useful-source recall, consumed context and build errors. Stop if the documentation set is too small to create a context problem or filtering removes necessary exceptions. Reconstructing PDF structure with Jev belongs inside this case only if the existing `pdftotext` output proves inadequate; it is not a separate recommended project. [RAG passage classification](https://docs.typesafe.ai/cookbooks/classifying_rag_passages), [structure recovery](https://docs.typesafe.ai/cookbooks/autoformat).

### U6 — Use a cheaper generator for routine steps and escalate selectively

**Change.** In an explicit production controller, a cheaper generative model proposes a bounded plan or module. Deterministic checks run first. Jev checks selected semantic fields against the brief; ambiguous or failing cases go to a stronger generator. The final build and render checks remain. This requires programmable access to generators; invoking the TypeSafe skill alone does not create such orchestration.

**Baseline and benefit hypothesis.** Compare against always using the stronger generator and against cheaper generation with deterministic checks alone. Illustrative per-step costs: stronger $1.00; cheaper $0.20; 20% escalation to the $1.00 step. Gross saving before verification is **$0.60/model** for one eligible step per model. Sensitivity includes a loss: at 90% escalation the cascade costs $1.10 before verification, exceeding the $1.00 baseline. These are assumed aggregate step costs, not model-provider prices or measured acceptance rates.

**Cost and test.** 64–120 engineering hours, 16–32 reviewer hours; three verifier requests/18k input tokens in the budget, approximately 0.4–3 seconds plus generation. More complex orchestration can exceed this estimate. Establish a quality non-inferiority condition on blind final renders and brief coverage; measure missed semantic defects at the automatic-accept operating point. Jev can share a generator's mistaken interpretation, so a second model is not inherently an independent verifier. Do not deploy on cost savings alone. [Cascade recipe](https://docs.typesafe.ai/cookbooks/sde_cascade).

### U7 — Route ambiguous failures to a suitable repair procedure

**Change.** Handle known diagnostic codes with fixed rules. For residual mixed cases, present the diagnostic text, relevant module context and a closed menu such as inspect connectors, widen retrieval, regenerate module or request visual review. Jev chooses a route; tools compute the repair. Unknown or conflicting evidence stays unresolved.

**Baseline and benefit hypothesis.** Extend the existing diagnostic dispatch before introducing AI. If an additional 2% of all models avoid a $4 unhelpful repair cycle, gross savings are **$0.08/model**; sensitivity $0–$0.40. Wrong routing can add cycles or repeatedly blame geometry for missing metadata.

**Cost and test.** 24–48 engineering hours, 8–16 reviewer hours. Assume only 10% of models reach this route: one 6k-token request per affected model, averaging 0.1 requests/600 tokens across production; 0.2–1 second on affected cases. Measure time/cost to a verified resolution and repeat-loop frequency. Stop if deterministic codes explain nearly every failure. Do not ask Jev to certify whether a connector arrangement is physically legal. [Intent routing](https://docs.typesafe.ai/patterns/intent-routing).

### U8 — Rank already available design alternatives

**Change.** Compare bounded alternatives using brief-specific semantic rubrics and measured facts. Keep geometry eligibility separate. A text description of a render must come from actual independent observation; Jev cannot see the render. For three existing alternatives, reusable Scores can expose tradeoffs such as motif consistency or requirement coverage. Pairwise Choices are another experiment, but option order and non-transitive preferences need testing.

**Baseline and benefit hypothesis.** Compare blind human/vision review of the same alternatives and a simple requirement checklist. If selecting better avoids rework on 10% of models at $5 each, benefit is **$0.50/model gross**, sensitivity $0–$1.50. Generating two extra alternatives at an assumed $0.50 each costs **$1/model**, making the working scenario negative before engineering. Extra full-model rendering would increase this cost.

**Cost and test.** 32–64 engineering hours, 16–32 reviewer hours; three requests/30k input tokens, approximately 0.5–3 seconds after evidence exists. Vision summarization is an additional dependency/cost, not included in the Jev budget; use existing review notes for the first test. Retain only with a blind preference lift at an equal candidate-generation budget. Initially use alternatives already generated for other reasons. Text-only “beauty scores” are not a credible deliverable. [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring).

### U9 — Build reusable semantic annotations for parts and assemblies

**Change.** Offline, add missing functional/style tags and descriptive classifications to a small, versioned catalog: for example ornamental radial surface, masonry motif or projecting sill. Store inferred tags separately from measured data, with probabilities and review state. Existing aliases, categories, dimensions and colour codes stay authoritative code-derived fields. Hierarchical classification becomes useful only if the catalog grows enough to justify it.

**Baseline and benefit hypothesis.** Compare curated synonyms/tags plus existing descriptions. A working estimate avoids $5 of downstream cost on an additional 0.6% of models: **$0.03/model gross**, sensitivity $0–$0.20. Most benefit overlaps U1/U2; do not add it again when those gains already include annotated retrieval. Wrong tags can spread the same error to thousands of future builds.

**Cost and test.** 32–64 engineering hours, 16–32 reviewer hours. A 10,000-record pilot at 2k input tokens/record costs **$0.84 once**; refreshing 1,000 changed records/month costs **$0.084/month**, with no online inference in this case. At published request limits the initial 10,000 requests alone require at least 8.3 minutes of quota time; elapsed time includes indexing/retries. Human verification, not tokens, dominates. Retain only if held-out retrieval improves; inspect metadata uncertainty rather than semantically merging parts presumed interchangeable. [Entity alignment](https://docs.typesafe.ai/cookbooks/entity_alignment), [hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification), [coarser classification](https://docs.typesafe.ai/cookbooks/classification_using_confidence).

### U10 — Learn a downstream acceptance or preference model

**Change.** Collect independently reviewed outcomes and turn narrow Jev judgments plus deterministic features into inputs to a simple statistical model. Compare logistic/linear models before CatBoost or an LLM-driven feature-discovery loop. Features can include brief coverage and described stylistic coherence; observed geometry and counts come from tools. Actual visual preferences need image-derived observations or visual review labels. This trains a downstream model, not Jev.

**Baseline and benefit hypothesis.** Compare the same model using deterministic features alone, fixed semantic rubrics and, where available, direct review. Working estimate: an additional 3% of models avoid $5 rework, **$0.15/model gross**, sensitivity $0–$0.50. Labels from self-written flattering descriptions would teach self-presentation, not aesthetic quality. Splitting nearly identical building variants between training and test would exaggerate performance.

**Cost and test.** 80–160 engineering hours and 40–100 reviewer hours for a first 1,000–2,000-outcome pilot; adequate sample size remains empirical. Runtime budget: one request/6k input tokens per model, approximately 0.2–1 second plus local prediction. A 2,000-row, five-round discovery experiment at 6k tokens/row/round costs **$2.52 in Jev input**, plus an assumed $50 proposer/compute allowance and $10/month local compute allowance. These exclude any new paid vision labels. Use grouped/time-separated held-out tests, measure calibration and freeze a final test set. Defer until the simpler cases produce useful labeled data. [Feature-discovery cookbook](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).

### U11 — Check narrative delivery claims against recorded evidence

**Change.** Generate counts, filenames, render lists and validation status directly from artifact manifests. Only remaining freeform claims go to a semantic evidence check: for example whether “all requested features are visible” is supported by actual review notes. Return supported, contradicted or not established and revise the prose accordingly.

**Baseline and benefit hypothesis.** Deterministic report templates will handle most of this more reliably. Avoiding a $5 correction on an additional 0.2% of models yields **$0.01/model gross**, sensitivity $0–$0.05. High-confidence wording should never transform `physical_validity: not_proven` into buildability certification.

**Cost and test.** 16–32 engineering hours, 4–8 reviewer hours; one request/5k input tokens, approximately 0.2–1 second. Test deliberately overstated, missing and contradicted evidence. Prefer templates unless semantic checks catch enough residual errors to justify maintenance. This is a low-priority quality-control option. [Citation checking](https://docs.typesafe.ai/cookbooks/citation_check).
