# TypeSafe documentation reading audit

Completed 2026-09-23 for the [LDraw assessment](typesafe-jev-ldraw-assessment.md).

All **111 documents** in the captured [llms.txt](https://docs.typesafe.ai/llms.txt) returned HTTP 200 and were read, including the 18 cookbook implementations/results and both SDK reference trees. Fetching alone was not treated as reading. Large pages were read in sequential chunks; truncated tool output was reread. The [machine-readable audit](typesafe-jev-reading-audit.json) records every URL, retrieval time, source SHA-256, local cache path and reading status. Source snapshots remain in `output/typesafe-research/sources/`; they are research cache, not a bundled copy of the vendor website.

Scope is the complete set of **indexed Markdown documents**, not every external link reachable from them. Presentation-only React/CSS and encoded playground URLs were normalized for reading. Question examples, cookbook code, output tables and SDK schemas were retained; the confidence/score explorer data and calculations were inspected separately. Embedded videos, external legal agreements, linked datasets, and image-only plot details were not independently audited. No cookbook was rerun and no new paid inference was performed.

The installed [TypeSafe skill](/Users/captain/.agents/skills/typesafe-ai/SKILL.md) was read. Its usual targeted-reading advice was superseded by the user's request to read the full index. The skill provides engineering guidance; it is not an additional inference product or an automatic model-building service.

| ID | Indexed document — read | Relevance or limitation recorded |
|---|---|---|
| 001 | [Introduction](https://docs.typesafe.ai/introduction.md) | Programming model: typed judgments consumed by code; no automatic model authoring. |
| 002 | [Quick start](https://docs.typesafe.ai/introduction/quickstart.md) | Request construction, environment key and direct SDK/API entry points. |
| 003 | [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents.md) | The skill teaches the coding agent an API; Jev does not replace that agent. |
| 004 | [Example use cases](https://docs.typesafe.ai/concepts/use-case-map.md) | Use cases surveyed across industries; transfer patterns, not claimed domain accuracy. |
| 005 | [System One](https://docs.typesafe.ai/concepts/system-one.md) | Fast bounded decisions; reserve multi-step invention for a generative model. |
| 006 | [State](https://docs.typesafe.ai/concepts/state.md) | Send compact structured evidence, preserving observed versus inferred fields. |
| 007 | [Primitives (Questions)](https://docs.typesafe.ai/primitives.md) | Three primitive families; batch independent questions on shared state. |
| 008 | [Choice](https://docs.typesafe.ai/primitives/choice.md) | Relative selection; include no-match and do not compare probabilities from different menus. |
| 009 | [Score](https://docs.typesafe.ai/primitives/score.md) | Ordered self-contained levels; expected score is not a geometric measurement. |
| 010 | [Noul](https://docs.typesafe.ai/primitives/noul.md) | Yes probability, not degree or a separate confidence field. |
| 011 | [Advanced: structure](https://docs.typesafe.ai/primitives/advanced.md) | Structured instructions and criteria can carry local candidate data. |
| 012 | [Confidence](https://docs.typesafe.ai/confidence.md) | Retain probabilities; confidence is a derived statistic, not observed LDraw accuracy. |
| 013 | [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md) | Atomic questions, bounded decisions and explicit composition; candidate coverage first. |
| 014 | [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer.md) | Vendor explanation of calibration-oriented training; validate target-domain calibration. |
| 015 | [Patterns](https://docs.typesafe.ai/patterns.md) | Pattern index read; individual linked pattern pages also read. |
| 016 | [Speculative fan-out](https://docs.typesafe.ai/patterns/fan-out.md) | Independent speculative questions share state; consume only applicable branches. |
| 017 | [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing.md) | Escalation thresholds must be tuned to downstream losses and coverage. |
| 018 | [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring.md) | Weights in code can change without asking unchanged questions again. |
| 019 | [Intent routing](https://docs.typesafe.ai/patterns/intent-routing.md) | Route to known handlers; the handler owns execution and deterministic rules. |
| 020 | [Cookbooks](https://docs.typesafe.ai/cookbooks.md) | Cookbook index read; all 18 indexed cookbooks read, including code and outputs. |
| 021 | [Self-consistency: nouls](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | Repeatability experiment is not accuracy; changing a unique state ID also changes input. |
| 022 | [Self-consistency: choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | Gate increases agreement while reducing automatic coverage; repeated examples are not an LDraw benchmark. |
| 023 | [Parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | Long shared-state batching example; latency compares sequential calls, not an optimized concurrent baseline. |
| 024 | [Re-ranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | 40 legal queries with BM25 shortlists; useful benchmark, not transferable LDraw effect size. |
| 025 | [Line-by-line search](https://docs.typesafe.ai/cookbooks/semantic_find.md) | Presence Noul handles absent evidence even when a line Choice produces a confident winner. |
| 026 | [Structure recovery](https://docs.typesafe.ai/cookbooks/autoformat.md) | Recover structure then assemble in code; printed cost and prose disagree. |
| 027 | [Function calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | Select functions and bounded arguments; consume relevant branches and handle absent values explicitly. |
| 028 | [Skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | Shortlist and recheck; synthetic skill-routing evaluation does not establish assembly-selection accuracy. |
| 029 | [Knowledge graph entity alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | Semantic entity matching; do not infer physical interchangeability of parts from text. |
| 030 | [Classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md) | Separate passage relevance, evidence and contradiction; filtering can lose useful evidence. |
| 031 | [Double-checking citations](https://docs.typesafe.ai/cookbooks/citation_check.md) | Exact quote checks in code before semantic entailment; small planted-error demonstration. |
| 032 | [Guardrails for LLMs](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) | Probability-based guardrails are fallible; broad moderation is not a current LDraw need. |
| 033 | [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | Generator/verifier/escalation pattern; no measured LDraw savings and no universal quality guarantee. |
| 034 | [Date extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | Extract bounded components, then perform calendar arithmetic in code; analogous to dimensions. |
| 035 | [Pre-parsed value extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | Code finds spans, Jev selects, code normalizes; missing candidates cannot be recovered. |
| 036 | [Hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | Four hierarchy examples; beam search is a ranking heuristic, not a calibrated leaf probability. |
| 037 | [Autoresearch feature discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | 2000 wine reviews; held-out improvement is real within that example, not evidence about visual model quality. |
| 038 | [Classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | 60 filtered filings; broader labels improve a different, coarser outcome; threshold is domain-specific. |
| 039 | [Demos](https://docs.typesafe.ai/demos.md) | Demo index read. |
| 040 | [Smart home assistant demo](https://docs.typesafe.ai/demos/smart-home.md) | Speculative fan-out and generative fallback; embedded video not transcribed or independently reviewed. |
| 041 | [Models](https://docs.typesafe.ai/models.md) | Pricing, rate/context limits, text-only input, model aliases and no customer fine-tuning. |
| 042 | [API reference](https://docs.typesafe.ai/api.md) | HTTP request/response shapes, option/level caps and error handling. |
| 043 | [Agent skill](https://docs.typesafe.ai/agent-skill.md) | Skill installation and workflow; instruction package, not inference infrastructure. |
| 044 | [Legal](https://docs.typesafe.ai/legal.md) | Legal overview read; linked external legal contracts are outside this indexed-document audit. |
| 045 | [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md) | Literal reading, arithmetic, indirection, context distraction and structural invariants constrain proposals. |
| 046 | [Client SDKs](https://docs.typesafe.ai/sdk.md) | SDK index read; Python and JavaScript documentation followed in full. |
| 047 | [TypeSafe Python SDK](https://docs.typesafe.ai/sdk/python.md) | Python install and sync/async quickstarts. |
| 048 | [Usage](https://docs.typesafe.ai/sdk/python/usage.md) | Typed response models, model selection, gateways, logging and forward compatibility. |
| 049 | [Changelog](https://docs.typesafe.ai/sdk/python/changelog.md) | Version 0.6 changes Score criteria; 0.7 switches to Pydantic; 0.7.1 validates keys early. |
| 050 | [API reference](https://docs.typesafe.ai/sdk/python/api.md) | Python API index read; all referenced indexed API pages read. |
| 051 | [Asynchronous client](https://docs.typesafe.ai/sdk/python/api/clients/async.md) | Async client ownership, overrides, response models, request errors and models resource. |
| 052 | [Synchronous client](https://docs.typesafe.ai/sdk/python/api/clients/sync.md) | Sync equivalent; extra_body can override reserved top-level fields. |
| 053 | [Questions](https://docs.typesafe.ai/sdk/python/api/types/questions.md) | Python question schemas and raw dictionaries; SDK permissiveness differs from HTTP docs. |
| 054 | [Answers and responses](https://docs.typesafe.ai/sdk/python/api/types/responses.md) | Typed answers, integer Score keys, request IDs, raw response and nullable token usage. |
| 055 | [Retries](https://docs.typesafe.ai/sdk/python/api/retries.md) | Default retries/backoff and a total retry budget; avoid unbounded application retry loops. |
| 056 | [Common types](https://docs.typesafe.ai/sdk/python/api/types/common.md) | JSON content versus nested scalar/null types. |
| 057 | [Exceptions](https://docs.typesafe.ai/sdk/python/api/exceptions.md) | Transport, status and response-validation failures must remain distinct from low suitability. |
| 058 | [Constants](https://docs.typesafe.ai/sdk/python/api/constants.md) | Environment names and default timeout/model. |
| 059 | [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript.md) | Node 20+, typed JavaScript client and ESM/CommonJS support. |
| 060 | [Changelog](https://docs.typesafe.ai/sdk/javascript/changelog.md) | JavaScript Score-criteria migration in 0.6.0. |
| 061 | [API reference](https://docs.typesafe.ai/sdk/javascript/api.md) | JavaScript API index read; all 50 indexed member pages read. |
| 062 | [Class: APIConnectionError](https://docs.typesafe.ai/sdk/javascript/api/classes/APIConnectionError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 063 | [Class: APIError](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 064 | [Class: APIPromise<T>](https://docs.typesafe.ai/sdk/javascript/api/classes/APIPromise.md) | Raw-response versus parsed-response ownership; request identifiers support traceability. |
| 065 | [Class: APITimeoutError](https://docs.typesafe.ai/sdk/javascript/api/classes/APITimeoutError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 066 | [Class: APIUserAbortError](https://docs.typesafe.ai/sdk/javascript/api/classes/APIUserAbortError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 067 | [Class: AuthenticationError](https://docs.typesafe.ai/sdk/javascript/api/classes/AuthenticationError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 068 | [Class: BadRequestError](https://docs.typesafe.ai/sdk/javascript/api/classes/BadRequestError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 069 | [Class: InternalServerError](https://docs.typesafe.ai/sdk/javascript/api/classes/InternalServerError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 070 | [Class: NotFoundError](https://docs.typesafe.ai/sdk/javascript/api/classes/NotFoundError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 071 | [Class: PermissionDeniedError](https://docs.typesafe.ai/sdk/javascript/api/classes/PermissionDeniedError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 072 | [Class: RateLimitError](https://docs.typesafe.ai/sdk/javascript/api/classes/RateLimitError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 073 | [Class: TypeSafeClient](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeClient.md) | JavaScript client options, typed systemOne and models resource. |
| 074 | [Class: TypeSafeError](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 075 | [Class: UnprocessableEntityError](https://docs.typesafe.ai/sdk/javascript/api/classes/UnprocessableEntityError.md) | Full JavaScript error class, constructors, inherited fields and status mapping read. |
| 076 | [Interface: ChoiceQuestion<T>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ChoiceQuestion.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 077 | [Interface: ChoiceResponse<T>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ChoiceResponse.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 078 | [Interface: Logger](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Logger.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 079 | [Interface: ModelCard](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ModelCard.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 080 | [Interface: Models](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Models.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 081 | [Interface: NoulQuestion](https://docs.typesafe.ai/sdk/javascript/api/interfaces/NoulQuestion.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 082 | [Interface: NoulResponse](https://docs.typesafe.ai/sdk/javascript/api/interfaces/NoulResponse.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 083 | [Interface: Questions](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Questions.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 084 | [Interface: RequestOptions](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RequestOptions.md) | Per-request timeout is milliseconds; no total retry budget in JS. |
| 085 | [Interface: RetryPolicy](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RetryPolicy.md) | Default retries and retry-after cap; differs from Python total retry budget. |
| 086 | [Interface: ScoreQuestion<T>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ScoreQuestion.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 087 | [Interface: ScoreResponse<T>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ScoreResponse.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 088 | [Interface: SystemOneRequest<Q>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneRequest.md) | JS accepts nullable state in its type; use portable non-null structured state. |
| 089 | [Interface: SystemOneRequestPayload](https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneRequestPayload.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 090 | [Interface: SystemOneResult<Q>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneResult.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 091 | [Interface: TypeSafeClientConfig](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig.md) | Server-side configuration; browser exposure off by default and bodies unredacted in debug. |
| 092 | [Interface: Usage](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Usage.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 093 | [Interface: WithResponse<T>](https://docs.typesafe.ai/sdk/javascript/api/interfaces/WithResponse.md) | Full JavaScript interface properties, generics and result/option semantics read. |
| 094 | [Type Alias: ChoiceCriteria](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria.md) | Full JavaScript type/constant definition and nullability read. |
| 095 | [Type Alias: Description](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/Description.md) | Full JavaScript type/constant definition and nullability read. |
| 096 | [Type Alias: EntryType](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType.md) | Full JavaScript type/constant definition and nullability read. |
| 097 | [Type Alias: EnvVar](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EnvVar.md) | Full JavaScript type/constant definition and nullability read. |
| 098 | [Type Alias: Fetch](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/Fetch.md) | Full JavaScript type/constant definition and nullability read. |
| 099 | [Type Alias: JsonValue](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/JsonValue.md) | Full JavaScript type/constant definition and nullability read. |
| 100 | [Type Alias: LogLevel](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/LogLevel.md) | Full JavaScript type/constant definition and nullability read. |
| 101 | [Type Alias: Question](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/Question.md) | Full JavaScript type/constant definition and nullability read. |
| 102 | [Type Alias: ResultFor<T>](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ResultFor.md) | Full JavaScript type/constant definition and nullability read. |
| 103 | [Type Alias: ScoreCriteria](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria.md) | Full JavaScript type/constant definition and nullability read. |
| 104 | [Type Alias: ScoreLegend<T>](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreLegend.md) | Full JavaScript type/constant definition and nullability read. |
| 105 | [Type Alias: ScoreOf<T>](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreOf.md) | Full JavaScript type/constant definition and nullability read. |
| 106 | [Variable: ENV](https://docs.typesafe.ai/sdk/javascript/api/variables/ENV.md) | Full JavaScript type/constant definition and nullability read. |
| 107 | [Variable: LOG_LEVELS](https://docs.typesafe.ai/sdk/javascript/api/variables/LOG_LEVELS.md) | Full JavaScript type/constant definition and nullability read. |
| 108 | [Variable: VERSION](https://docs.typesafe.ai/sdk/javascript/api/variables/VERSION.md) | Documented JavaScript SDK version 0.6.0. |
| 109 | [Function: choice()](https://docs.typesafe.ai/sdk/javascript/api/functions/choice.md) | Full typed helper signature, argument types and return type read. |
| 110 | [Function: noul()](https://docs.typesafe.ai/sdk/javascript/api/functions/noul.md) | Full typed helper signature, argument types and return type read. |
| 111 | [Function: score()](https://docs.typesafe.ai/sdk/javascript/api/functions/score.md) | Full typed helper signature, argument types and return type read. |
