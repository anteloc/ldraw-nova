# Jev discovery of parts, models and reusable assemblies

Evaluated 2026-09-24 against the installed description database and `data/models-annotated`. This is the empirical follow-up to the [earlier TypeSafe assessment](typesafe-jev-ldraw-assessment.md). The building recreation remains paused.

**The strongest improvement is a discovery workflow that connects whole models, useful subassemblies and their constituent parts.** The new fields make that connection easier, and the source corpus contains useful construction techniques beyond the current procedural recipes. However, a high-ranking section is often a partial shell, a construction step, a different scale, or a part definition. Source inspection must sit between retrieval and reuse.

I recommend implementing a typed source resolver and assembly review cards first, fixing the demonstrated indexing issues, then adding diversity and role-specific ranking. Expanding the number of results or combining all three fields into one list does not adequately solve the problem.

The [evidence snapshot](jev-assembly-discovery-evidence.json) records queries, results, source hashes, baseline searches, usage and inspections. The local [visual review](../../output/jev-assembly-evaluation/review.html) presents eight extracted references and their checks. These are evaluated source copies, not additions to the approved example catalog. Production tooling was not changed for this assessment.

## What was actually tested

The initial experiment ran 17 Jev searches: 12 purpose-based queries across all three new fields, four comparisons with the original description fields, and one combined-field query. Three follow-ups tested explicit System landing-gear criteria, exhaustive model retrieval, and the full cached cab candidate ranking.

Every initial top-ten result was inspected: 50 part-result rows and 120 model/submodel-result rows, covering 77 distinct source files and 103 distinct model/section selections. One section initially failed parser lookup because of trailing whitespace; a separately recorded, unambiguous match resolved it. Eight representative sections were extracted, inspected, rendered in two views, opened visually and compared against LeoCAD BOMs. Additional source checks investigated the ranking failures.

All 1,821 indexed model files and all 28,451 indexed submodel names were checked for source correspondence. This corpus-wide check inventories headers and records; it is not corpus-wide physical validation. The database was read-only and its hash remained unchanged after the searches. The eight extracted originals also retained their recorded hashes.

The pilot is exploratory. The judgments below are based on descriptions, source records, BOMs and selected renders. There was no blinded relevance labeling, independent aesthetic panel, physical construction test or comparison of newly generated designs.

## What the new fields contain

These are SQLite **views**, each with a single `full_description` column:

| View | Rows | Actual expression |
|---|---:|---|
| `PARTS_DESCRIPTIONS_JEV` | 35,257 | `part || '|' || description` |
| `MODELS_DESCRIPTIONS_JEV` | 1,821 | `model || '|' || description` |
| `SUBMODELS_DESCRIPTIONS_JEV` | 28,451 | `model || '|' || submodel || '|' || description` |

The prose is unchanged from the original tables. The improvement is that Jev now sees the identifier and section name alongside that prose. This helps locate the source and can supply a meaningful name when a description is weak. It does not establish richer annotations or better relevance by itself.

The views have no primary keys. The current reranker returns synthetic `source.key._row_number_` values, generated without an explicit ordering. Those are snapshot locators, unsuitable as durable assembly identifiers. The existing agent instructions for reading `source.key.part` apply to the original parts table, not these views.

An adapter should split the parts/model value at its **first** pipe, and the submodel value at its **first two** pipes. There are 211 part descriptions containing additional pipes. Preserve the original value and use `(model, section)` or `part` as the logical identity, together with a source hash. Keep file resolution inside the configured source root.

### Corpus content needs classification

| Observed content | Count | Consequence |
|---|---:|---|
| Submodel entries ending in `.dat` | 5,375 | Embedded part definitions, not reusable multi-part assemblies |
| Other sections with type-1 placements | 22,723 | Candidates for inspection; this includes flexible geometry built from primitives |
| Other sections with raw geometry but no placements | 317 | Often generated hoses/bands; ordinary part counts and assembly checks are insufficient |
| Sections with neither placements nor raw geometry | 36 | No standalone visible construction to reuse |
| Models without `FILE` blocks | 39 | Valid single-section sources despite their `.mpd` filenames; current extraction requires `FILE` blocks |
| Model descriptions containing the wrong header | 38 | Database has `Name: ...` where the actual source has a descriptive first line |

All indexed model files and submodel headers were found. File existence alone therefore would not detect these problems.

The parts view also spans several kinds of content: 23,732 top-level library files, 8,737 subpart files, 2,786 primitives and two model redirects. Among the top-level files, 4,344 have alias/internal-style titles. The remaining 19,388 are only *initial physical-part candidates*: that group still includes incompatible product families and references requiring status checks. All 35,257 references were located when the model redirects were included.

The header issue is directly observable in `7911-1.mpd`: Jev receives `7911-1.mpd|Name: 7911 - Tugboat.ldr`, while the source starts with a description of a small red/orange tugboat. All 38 mismatches contain `Name:` values. This strongly suggests a single-section header extraction problem; the annotation producer itself was not modified or fully audited here.

## Retrieval findings

All initial searches used `jev-1.13.0`, `--top 10`, `--candidates 500`, `--show` and JSON output. Scores below are the returned semantic scores, not probabilities of buildability or suitability for direct import.

| Query purpose | Representative result | Finding |
|---|---|---|
| Moulded minifigure seat | `4079.dat`, 0.94 | Useful dedicated part; an obsolete seat alias and a Technic seat follow it |
| Arched building window | `5260.dat`, 0.83 | Good frame candidate; top ten also includes an internal half, a printed window motif and Duplo references |
| Passenger-jet engine housing | `s/4868s01.dat`, 0.75 | First result is an internal subpart; physical engine `43121.dat` appears third |
| System truck cab with interior | `10183 - 3 - cabin.ldr`, 0.76 | Attractive exterior shell, but its 24-part BOM contains neither a seat nor steering wheel |
| Boat hull, deck and wheelhouse | `4015 - ship.ldr`, 0.87 | Rich hull/deck reference, with a flexible-rope representation that defeats current BOM accounting |
| Brick-built aircraft landing gear | `42057 - land1.ldr`, 0.95 | 11 of 13 placements have Technic-prefixed part descriptions; outside the requested scope |
| Arched window bay | `10276 - bk3-step185.ldr`, 0.78 | A ten-piece open arch; seven of the top ten come from the same Colosseum model |
| Exterior fire escape | `10185 - First Floor - Fire Escape 2.ldr`, 0.88 | Useful bars/clips/ladder construction, but six arm transforms fail the assembly rotation check |
| Passenger-carriage bogie | `4547 - train car - wheels.ldr`, 0.92 | Strong reusable pattern: complete wheelsets, mounting pin, buffer beam and magnetic coupling |
| City bus | `10258-1.mpd`, 0.92 | A large 1,682-placement model; the city-scene source `7641-1.mpd` follows at 0.71. Target scale and requested scope need separate checks |
| Harbour tugboat | `7911-1.mpd`, 0.80 | Relevant but small, 34 placements, with weak database text; broader results quickly become unrelated |
| Ornate corner building | `10182-1.mpd`, 0.94 | Useful architectural precedent with 80 assembly sections; whole-model discovery can lead to more focused section searches |

### Better wording helps, but cannot enforce the brief

The original landing-gear top ten contained nine results with a majority of Technic-prefixed placements. An explicit yes/no criterion favoring ordinary bricks, plates, hinges and dedicated landing-gear parts moved `5980 - 5980-4-a.ldr` from sixth to first. Its inspected 24-placement BOM had no Technic-prefixed titles.

However, the revised list also admitted train bogies and `8856 - Front-Landing-Gear.ldr`. Another seemingly suitable result, `7893 - wheels.ldr`, contains two Technic tiles and a friction pin not mentioned in its description. Descriptions cannot enforce a BOM constraint.

For the user's scope, distinguish **a Technic model/mechanism** from **a System assembly using an incidental pin or axle**. Use source theme, construction and BOM evidence to make that distinction; do not silently turn “leave Technic aside” into an unrequested ban on every Technic-named element. Expose the actual exceptions, and support a strict zero-Technic-parts option if requested. The title-prefix counts in this pilot are diagnostic evidence, not a complete part taxonomy.

The cab search provides a useful counterexample to treating Jev as automatically superior to keyword search. BM25 ranked `6690 - Truck.ldr` first for the cab/interior keyword query. Jev ranked it 15th at 0.57, within the same 500-candidate pool. Its actual BOM includes two `4079.dat` seats, `3829c01.dat` steering, doors and a windscreen. It is larger than a cab-only module, but contains the requested details. The Jev winner lacks them. This is a ranking/granularity problem, not a candidate-recall failure.

### Identifier fields have not demonstrated an accuracy gain

| Same natural-language query, original vs new field | Shared results in top ten |
|---|---:|
| Seat | 7 |
| Arched window part | 10 |
| Truck cab | 6 |
| Window subassembly | 9 |

The identifiers change ordering and sometimes membership. These comparisons do not isolate scoring from candidate generation: field content changes both, ties can change top-ten membership, and one original-field search reused an existing score cache. There is no justified percentage improvement in accuracy to report.

The saved baseline includes both the current FTS `LIMIT` order and explicit BM25 order. Current model/submodel search has no `ORDER BY rank`; improving that is a useful, inexpensive baseline. The chosen keyword strings are hand-written, and FTS morphology matters: `window arch` returned no rows, while richer natural-language Jev retrieval found curved-top frames. This is evidence of a useful search interaction, not a controlled benchmark against optimized keyword queries.

### More candidates and mixed lists are not sufficient

Exhaustively scoring all 1,821 model descriptions for the tugboat query preserved the first two results. It introduced additional relevant watercraft, but also ranked `Allied Avenger`, `Saucer Centurion` and `Witch` at 0.54, 0.52 and 0.46. Their sources are a spacecraft, spacecraft and figure. Weak titles leave the semantic judgment underinformed; a larger candidate pool also exposes more false positives.

The combined-field cockpit query returned eight submodels and two whole models, with no parts. Its first result, `6852 - Vehicle - Cockpit.ldr`, has only two placements, while a 593-placement complete vehicle ranks third. One universal top-ten list therefore hides useful options at different levels. Query and present the three levels separately, then link them.

There is also repetition beneath apparently different filenames. Bogies from `4547-1` and `10002-1` have identical part-count fingerprints; so do `10013-1` and `10017-1`. A BOM fingerprint identifies possible duplicates, not geometric equivalence. Parent-model grouping plus a placement/shape comparison should preserve meaningful variants while suppressing repeated constructions.

## What inspecting the source changes

The [review gallery](../../output/jev-assembly-evaluation/review.html) contains both views of each case, its MPD, source inventory and BOM comparison. The following counts are expanded placements as currently calculated; the patrol-boat exception is intentional evidence of a limitation.

| Extracted section | Placements / dependency sections | Review outcome |
|---|---:|---|
| Truck cab, `10183 - 3 - cabin.ldr` | 24 / 1 | Assembly checks and BOM agree. Exterior-only module; parent supplies context |
| Patrol boat, `4015 - ship.ldr` | 163 / 3 | Python counts 92 rope cylinders as parts; LeoCAD exports 71 placements. One rounded rotation repairs, rope errors remain |
| Small boat, `2882 - boat.ldr` | 17 / 1 | Assembly checks and BOM agree. Visible windscreen, steering wheel and shaped bow |
| Technic gear, `42057 - land1.ldr` | 13 / 3 | Eight bounded rotation repairs and seven BFC-comment repairs make assembly checks pass; semantic scope still disqualifies it |
| Colosseum arch, `10276 - bk3-step185.ldr` | 10 / 1 | Assembly checks and BOM agree. Bounds 80 × 156 × 20 LDU: four studs wide, one deep, with no glazing |
| Flatiron detail, `21023 - 1 - 4 - 1.ldr` | 14 / 1 | Assembly checks and BOM agree. Bounds approximately 160 × 24 × 60 LDU; a shallow strip in local coordinates, not a freestanding glazed bay |
| Fire escape, `10185 - First Floor - Fire Escape 2.ldr` | 37 / 2 | BOM agrees, but six arm matrices have orthogonality error about 0.0904; too large for the existing 0.002 repair tolerance |
| Train bogie, `4547 - train car - wheels.ldr` | 8 / 1 | Needs a black root placement to resolve colour 16. Then assembly checks and BOM agree; aliases/obsolete references still need review |

Four of the eight raw extracts pass assembly checks. Six pass after the documented preparation; seven have matching BOMs. Passing these checks is not proof of complete physical validity. Contacts were deliberately skipped for this source-discovery assessment.

Three cases initially reported incomplete geometry because connection-shadow features were rejected under transforms. Repeating those inspections with connection shadows disabled produced complete geometry expansion. This distinguishes a connector-metadata limitation from a missing mesh. Future review cards should report mesh expansion, connector coverage, assembly checks and physical-part accounting separately, rather than collapsing them into one “valid” flag.

Two further source-handling issues matter:

- `6540 - police boat.ldr ` exists with trailing whitespace in the indexed/raw header; the parser names it without that whitespace. Exact lookup fails. Resolve original and parsed identities explicitly, allowing only unambiguous normalization and preserving provenance.
- The fire-escape example visibly supplies a richer construction vocabulary but is not ready for direct import. Keep a route for **studying a technique and rebuilding it** as well as copying an assembly. Attractive source geometry is not necessarily a valid reusable asset.

## Recommended tooling changes, in priority order

| Priority | Concrete change | Why it comes first |
|---|---|---|
| 1 | Add a typed resolver for the three Jev fields: stable logical ID, kind, exact source/section, raw text, score, hashes and lookup status | Makes every result actionable; fixes the synthetic-key and whitespace traps |
| 1 | Fix single-section description ingestion and support extracting a single-section source through an attributed wrapper | Recovers 38 existing descriptions and makes 39 sources accessible through the reuse workflow |
| 1 | Classify parts, assemblies, embedded definitions, flexible geometry and empty sections before presenting reusable candidates | Prevents subparts, custom hull definitions and rope cylinders being treated as ordinary assemblies or BOM parts |
| 2 | Add assembly review cards using existing `study`, section inspection, `extract`, `render` and BOM comparison | Exposes dimensions, actual contents, parent context, dependencies, inherited colour and source defects before selection |
| 2 | Add role and scale constraints plus separate model/submodel/part result groups | Prevents a shell, a complete vehicle and a moulded cockpit being treated as interchangeable answers |
| 2 | Diversify by parent model and construction fingerprint; retrieve a larger pool before filtering | Produces real alternatives instead of seven Colosseum sections or left/right variants |
| 3 | Promote inspected constructions into the existing detail/vehicle catalogs with authored interfaces | Turns discoveries into repeatable design options without making every generation rediscover source defects |
| 3 | Evaluate selection and adaptation on completed builds against ranked FTS and current recipes | Determines whether discovery actually improves variety, time and appearance |

These can extend [resources.py](../../ldraw_tools/resources.py), [document.py](../../ldraw_tools/document.py), [catalog.py](../../ldraw_tools/catalog.py) and the existing example catalogs. The sibling reranker can remain a bounded semantic-ranking service. For a stable upstream contract, expose source key columns separately from `full_description` or support explicit view keys; an adapter parsing these three known formats is a reasonable first step.

A useful review card should contain: source identity/hash and attribution; subject and role; parent/child links and local-to-parent transform; measured bounds and counts; actual special parts; inherited colours; dependencies; aliases and flexible/custom geometry; diagnostic and rendering status; and a decision such as **reuse after preparation**, **adapt/rebuild**, **technique reference**, or **reject for this brief**. Scale and connection anchors should be authored or marked unknown, not inferred from a set number or relevance score.

For diversity, start with a configurable parent cap and possible-duplicate grouping on a larger shortlist, then inspect the surviving constructions. Do not hard-cap every parent before checking quality: a good source may legitimately supply both a seat and a dashboard. Do not pad the display with low-relevance results merely to return ten.

For semantic decisions, keep subject relevance, functional completeness, scale/style compatibility and adaptation effort separate. Code should own hard source/BOM checks and explicit weighting. This follows the separation in TypeSafe's [reranking cookbook](https://docs.typesafe.ai/cookbooks/rerank_typesafe) and [composite-scoring pattern](https://docs.typesafe.ai/patterns/composite-scoring). Neither document supplies an LDraw accuracy result; the evidence here is the local experiment.

## Practical workflow available now

Use model search for precedent, submodel search for a construction role, and part search for individual fittings. Query each level independently:

```sh
jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field MODELS_DESCRIPTIONS_JEV.full_description \
  --query 'a System city bus with a passenger cabin, seats and doors' \
  --top 10 --candidates 500 --model jev-1.13.0 --show --json

jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field SUBMODELS_DESCRIPTIONS_JEV.full_description \
  --query 'a train bogie with paired wheels beneath a passenger carriage' \
  --top 10 --candidates 500 --model jev-1.13.0 --show --json

jev-rerank \
  --db "data/ldraw-info.db" \
  --table-field PARTS_DESCRIPTIONS_JEV.full_description \
  --query 'a moulded seat for a minifigure vehicle cabin' \
  --top 10 --candidates 500 --model jev-1.13.0 --show --json
```

For example, the retrieved small boat can already be inspected without new tooling:

```sh
./ldraw-agent sections "data/models-annotated/2882-1.mpd" \
  --section '2882 - boat.ldr'
./ldraw-agent extract "data/models-annotated/2882-1.mpd" \
  --section '2882 - boat.ldr' --namespace ref-boat \
  --output output/boat-study/boat.mpd
./ldraw-agent inspect output/boat-study/boat.mpd --detail summary --contacts none
./ldraw-agent render output/boat-study/boat.mpd \
  --outdir output/boat-study/renders --views home top
```

Read diagnostics and open the renders before adapting it. Once selected, measure and author its attachment interface, resolve legacy references and colours, then validate the composed model with contacts and visual review. Prefer reusing the construction idea when the source cannot satisfy those checks.

## Reproducibility, usage and acceptance criteria

Inspected revisions: `ldraw-nova` `115c97cb1de535f7533bbb738f2277c6d0e7be51`; sibling `jev-rerank` `1e9bc79ff3d01773bdba40890a27e701be5196c8`. Database SHA-256: `5472f2479da929c06d4a39dd94c04aa58c3065306441e1746fc6cc4a8bd49e02`.

Across all 20 invocations, Jev reported 11,321 candidate evaluations: 9,821 API calls and 1,500 cache hits, with 5,151,947 input tokens and 216,062 output tokens. These are repeated query/candidate evaluations, not unique source records. Summed CLI-reported time was 166.62 seconds; subprocess wall time was 169.47 seconds. Fresh 500-candidate pilot searches took approximately 8.06–10.32 seconds. This is not end-to-end agent time or a throughput benchmark. Dollar costs were not estimated.

The exhaustive model follow-up required 1,321 additional API calls, reusing 500 cached scores. The full cab-candidate audit reused all 500 scores. Initial corpus indexes were already available; this does not measure a cold index build.

The committed evidence snapshot preserves the material results. The ignored local [artifact directory](../../output/jev-assembly-evaluation/) additionally contains raw stdout/stderr, exact commands, [query runner](../../output/jev-assembly-evaluation/run_queries.py), [follow-up runner](../../output/jev-assembly-evaluation/run_followups.py), source audits, extraction manifests, MPDs and renders. Reruns may produce different semantic scores; exact source identities, hashes and deterministic checks make the observed conclusions reviewable.

Before promoting a new discovery command into the agent workflow, verify that it resolves every returned identity, separates incompatible source kinds, reports missing/partial evidence, and never treats a semantic score as an import approval. Then compare a labeled set of roles against ranked FTS, including dedicated fittings, architectural details, watercraft, aircraft, trains and negative examples.

Measure usable distinct constructions in the shortlist, hard-constraint violations, time to a reviewed adaptation, and diversity across completed models. Finally compare completed builds with the current recipes using independent visual judgments. The present evidence supports investing in assembly discovery and source preparation; improvement in final model aesthetics remains to be demonstrated.
