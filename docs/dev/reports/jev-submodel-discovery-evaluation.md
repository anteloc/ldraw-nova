# Jev search over models, submodels and parts: what it would change in agent-built models

Evaluated 2026-09-24 with `jev-1.13.0`:

- **Repositories:** `ldraw-nova` at `115c97c`, `jev-rerank` at `1e9bc79`, `ldraw-info.db` modified 2026-09-24 22:07.
- **Queries:** 29 queries, plus a 3,000-candidate rerun, an exhaustive run and 3 runs on a scratch table.
- **Checks:** all 170 submodel hits were inspected, and 4 references were extracted and rendered.

The evidence, scripts and every cited figure are in [output/jev-discovery-eval/](../../output/jev-discovery-eval/README.md). Relevance labels are my judgements, made from descriptions, measured data, parent models and renders. They are not a benchmark. Improvement levels are estimates.

## Summary

**Submodel search is the valuable one of the three views.** For common scene roles it returns 7–10 usable real LEGO assemblies per query: lamps, trees, stairs, truck cabs, roofs and ramps. For vehicle roles it returns good construction techniques, but often from the wrong subject: spaceship nacelles for an airliner engine, Technic struts for System landing gear. For a truly rare role, such as an opening cargo-plane nose, the collection has nothing.

**Most of the gain for generated models comes from locating and checking the source, not from better ranking.** The agent needs to go from a hit to its real section, repair the known annotation defect, measure it, render it, and then either reuse it or rebuild its technique at the model's own scale.

**Expected effect.** High for the detail and variety of subassemblies, and for props in minifig-scale scenes. Medium for novel-scale vehicles and overall recognisability. None for physical validity, which still rests on the existing checks. Cost is about $0.011 and 8 s per query.

### Improvements at a glance

The level is the estimated effect on the models the agent generates:

| Level | Meaning |
|---|---|
| Very low | No visible change |
| Low | Occasional small gains |
| Medium | One or two modules better or more varied in a typical relevant model |
| High | Several modules or the focal feature improved in most relevant models |
| Very high | Most models improve overall |

| # | What | How it changes the agent's work | Effect on models | Main dimension |
|---|---|---|---|---|
| A1 | Rank FTS results (`ORDER BY rank`) | Keyword searches show the best matches first, not the alphabetically first sets | Low | Effort; fallback when Jev is unavailable |
| A2 | Yes/no criteria for model and submodel queries | One query per module role says what counts and names the look-alikes to exclude | Medium | Better first reference |
| A3 | Filter by record type and measured content | Top-10 slots hold only placeable parts or System assemblies of a usable size | Medium | Options per query; less wasted inspection |
| A4 | Deduplicate and diversify | Top-10 slots hold 10 different designs, with "N variants" noted | Medium–High | **Variety** |
| A5 | Larger candidate budget when results are weak | Rare roles get a second pass over 3,000 candidates | Low–Medium | Recall for rare roles |
| A6 | Stable result keys | Hits carry `{model, submodel}` or `{part}` instead of row numbers | Very low (enabler) | Caching, provenance |
| A7 | Parent-model subject shown with each hit | The agent sees "in: Star Wars X-wing" beside a wing and can filter by subject | Low–Medium | Subject fit |
| A8 | Part ID inside the part text (new view) | Mixed ID/text queries find the part itself | Very low | — |
| B1 | Hit → source file, section and lines → repaired extract | Every hit can be inspected, rendered and reused with attribution | High (enabler) | Makes B2–B6 possible |
| B2 | Measured data on each hit | The agent picks references at its own scale and drops unusable ones before looking | Medium | Scale fit, fewer failed adaptations |
| B3 | Render board of candidate submodels | The agent sees the construction before choosing, which catches text-vs-shape errors | High | Detail, recognisability |
| B4 | Rebuild the technique at the model's own scale | The generator recreates a real LEGO construction in its own palette and grid | High | **Detail and variety** of novel models |
| B5 | Reuse a module directly (`extract` → `assets` → `attach`) | Minifig-scale scenes pull in real props and modules | High for minifig scenes; Low for novel-scale vehicles | **Variety** of props |
| B6 | Part suggestions drawn from matched submodels | The part shortlist includes parts real designers used for that role, with the sets that use them | Medium–High | Variety of detail parts |
| B7 | Whole-model references | The module checklist and story props come from real sets of the subject | Medium | Planning, story completeness |

**Combined** (A2–A4 with B1–B6): High for minifig-scale scenes and vehicles with common roles; Medium for novel-scale or rare subjects.

## 1. The three views

| View | Rows | Usable for building | Noise the agent must remove |
|---|---:|---|---|
| `PARTS_DESCRIPTIONS_JEV` = `part\|description` | 35,257 | **17,781** physical top-level parts (9,857 without prints) | 9,786 subpart rows (`s/…`); moved, alias and obsolete (`~ = _`) entries; stickers |
| `SUBMODELS_DESCRIPTIONS_JEV` = `model\|submodel\|description` | 28,451 in 1,758 models | 23,076 non-`.dat` rows; about 21,300 without minifigs | 5,375 embedded `.dat` part definitions (19%); 1,905 descriptions that only repeat the name (1,326 of them assemblies); 1,745 minifig rows; 3,177 copies across variant files of the same set; 3,093 rows whose description is identical to another row |
| `MODELS_DESCRIPTIONS_JEV` = `model\|description` | 1,821 (1,465 set numbers) | All 1,821 source files exist | 38 `Name:` placeholders; only 468 models join to a theme |

**Result keys.** All three are views, so Jev returns row numbers such as `{"_row_number_": 2437}`, which shift when rows change. The identifier survives only inside the text, before the first `|`. A scratch table with a primary key ([build_ctx.py](../../output/jev-discovery-eval/build_ctx.py)) returns `{"model": "4953-1.mpd", "submodel": "4953 - Plane S31.ldr"}`.

**Source defect.** In **407 of the 1,821** annotated models (22%), annotation comments sit between `0 BFC INVERTNEXT` and its type-1 line. `inspect` therefore fails on syntax before reading any geometry, even for a clean section, because the defect is in one of its embedded parts. 15 of the 170 hits needed repair. `extract --repair-bfc-comments` fixes it: the 10246 lamppost then gives `checks_passed: true` and renders correctly.

## 2. What the queries showed

Labels: **R** relevant new design; **D** duplicate of an earlier hit; **P** partial (Technic-heavy, a single part, a `.dat` definition, oversized, or technique only); **N** not relevant. "Air" counts hits whose parent model is an aircraft. Full reasons are in [labels.json](../../output/jev-discovery-eval/labels.json).

| Query | R | D | P | N | Air | Top score | Best hits |
|---|---:|---:|---:|---:|---:|---:|---|
| Street lamp | 6 | 4 | 0 | 0 | | 0.98 | 10246, 4554, 5766, 31038, 3316 |
| Tree | 10 | 0 | 0 | 0 | | 0.96 | 40782, 4208, 4886 (×3), 5766, 10246, 10251 |
| Staircase | 7 | 3 | 0 | 0 | | 0.96 | 10297, 10182 spiral, 10278, 21318 |
| Truck cab | 10 | 0 | 0 | 0 | | 0.89 | 6594, 4915, 60216, 10156, 744 |
| Dormer roof | 7 | 1 | 2 | 0 | | 0.86 | 21325, 10270, 10243, 10182 |
| Loading ramp | 7 | 0 | 3 | 0 | | 0.94 | 5893, 60018, 6981, 75053 |
| Window with shutters | 6 | 1 | 3 | 0 | | 0.94 | 6769, 4954 (the only two with shutters) |
| Same, 3,000 candidates | 6 | 0 | 4 | 0 | | 0.94 | adds 6067, 10224 S40 (4 with shutters) |
| Boat bow | 3 | 0 | 1 | 6 | | 0.95 | 6285, 31045, 10294; the rest are spaceship "hulls" |
| Jet engine, plain | 6 | 1 | 1 | 2 | 4 | 0.83 | 7141 (starfighter), 4953, 31045; 2 dragster engines |
| Jet engine, criteria | 7 | 1 | 1 | 1 | 3 | 0.95 | **7893 airliner engine**, 76042, 4953; 10174 (see render) |
| Jet engine, parent context | 7 | 1 | 1 | 1 | **7** | 0.75 | 4953, 31045, 31039 ×2, 76042 ×2; lost 7893 |
| Landing gear, plain | 2 | 0 | 7 | 1 | 5 | 0.95 | 5980, 7893; 7 of 10 more than half Technic |
| Landing gear, criteria | 3 | 0 | 7 | 0 | 6 | 0.91 | 5980, 7893, 6745 nose wheel; 5 of 10 still more than half Technic |
| Tail fin, criteria | 6 | 0 | 4 | 0 | 7 | 0.96 | 6745, 3063, 5892, 4918, 76042 |
| Swept wing, criteria | 7 | 3 | 0 | 0 | 6 | 0.94 | 6745, 31039, 5542, 10226; 3 mirror pairs |
| Aircraft nose | 6 | 1 | 2 | 1 | 2 | 0.93 | 10212 shells, 6933, 10226; mostly spacecraft |
| Opening nose door, criteria | **0** | 1 | 7 | 2 | 0 | 0.83 | Only generic hinged panels: the collection has none |
| Model: cargo aircraft | 2 | 0 | 5 | 3 | | 0.81 | 3181, 7732; exhaustive run adds nothing |
| Model: airliner | 10 | 0 | 0 | 0 | | 0.94 | 60101, 7893, 31039, 10159 |
| Model: modular building / ship / castle / train / car | 6 / 6 / 9 / 10 / 10 | | | | | 0.92–0.98 | common subjects are well covered |
| Part: nacelle (new / old field) | 1 / 0 | | 8 / 7 | 1 / 3 | | 0.78 / 0.77 | Only 43121 (new view, rank 9); the rest are subparts and hinges |
| Part: belly curve (new / old) | 4 / 3 | | 6 / 7 | | | 0.91 / 0.91 | 13547, 500, 42023, 32803 |

### Findings from the comparisons

- **Current FTS is unranked.** `search_models` in [resources.py](../../ldraw_tools/resources.py) runs `… MATCH ? LIMIT ?` with no `ORDER BY rank`, so results come back in rowid order, which is alphabetical by set.
  - "jet engine" has 68 matches. Today's first six are an AT-AT pod, B-wing pods, two Harley exhausts and two Porsche boxer engines.
  - Ranked by BM25, the first six are all jet-engine assemblies: 1787, 7784, 5980 ×2, 5983 ×2.
  - "tree" (150 matches) has the same problem: today it starts with a minifig in a palm-tree shirt.
- **Criteria improve role fit, not subject fit.**
  - For engines, criteria moved the best reference, the 7893 airliner engine, to rank 1 (0.95) and removed the dragster engines.
  - Aircraft-domain hits stayed at 3–4 of 10, because submodel descriptions rarely name the vehicle.
  - For landing gear, criteria reduced Technic-heavy hits from 7 to 5. Text criteria alone cannot remove them.
- **Parent context in the ranked text is a trade-off.** Adding "in: <model subject>" raised aircraft-domain engine hits from 3 to 7 of 10, but lost the 7893 engine and lowered window scores. Showing the subject beside each hit (A7) gets the benefit without the ranking loss.
- **Recall.** The default shortlist of 500 BM25 candidates misses rare phrasings. Rerunning the window query with 3,000 candidates doubled the hits with shutters, from 2 to 4, for about 6× the cost. An exhaustive run over all 1,821 models added nothing for cargo aircraft.
- **Duplication hides variety.**
  - 6 of the 10 lamps are built on the same 2×2×7 lamppost part (2039), in two exact recipes.
  - 4 of the 10 staircases use the same 7×4×6 staircase part (30134).
  - The wing query returned 3 mirror pairs.
  - The `3001` part query returned 9 printed variants of one brick.
- **Text is not shape.** 10174 "Engine pod assembly with jet fans" scored 0.93, but the [render](../../output/jev-discovery-eval/renders/eng10174.png) shows a flat grey AT-AT body slab with two fans set into it. The [7893 render](../../output/jev-discovery-eval/renders/eng7893.png) shows a true airliner pod: 43121 housing, 46667 fan, 3942c cone spinner, and a 44126 curved-slope pylon.
- **Part ID in the text.** `3001 brick 2 x 4` finds 3001 at rank 1 in the new view; the old field does not return it at all. Other part queries are similar in both.

## 3. Improvements in detail

### A. Better search

**A1 — Rank FTS results.**
- **What.** Add `ORDER BY rank` and report the match count in `search models|submodels`. Offer `--offset` for further pages.
- **How it helps.**
  - When Jev is unavailable, or when the vocabulary is exact ("lamppost", "dormer"), the first page holds the best matches.
  - It is also a free candidate source to combine with Jev.
- **Effect.** Low on models; Medium on search; trivial to build.

**A2 — Criteria recipe for submodels and models.**
- **What.** Document a criteria template per module role:
  - **yes:** "the subassembly is a <role> of a <subject> built from System parts";
  - **no:** "…not <look-alike roles>, Technic assemblies, minifigures".
- **How it helps.** The first reference the agent opens is the best one more often (7893 engine at rank 1).
- **Limit.** Criteria cannot know a submodel's parent vehicle or its measured Technic share. Combine them with A3 and A7.
- **Effect.** Medium on models; Medium–High on role precision.

**A3 — Filter by record type and measured content.**
- **What.**
  - **Parts:** keep only physical top-level parts (35,257 → 17,781).
  - **Submodels:** hide embedded `.dat` definitions and name-only descriptions. Hide minifigs unless the role asks for them.
  - **After measurement (B2):** limit the Technic fraction (for example ≤ 0.5) and the placement count (for example 2–500).
  - Filtering before ranking (a filtered view) keeps the 500-candidate shortlist for useful rows. Filtering after ranking needs `--top 30`, cut down to 10.
- **How it helps.** Every returned option can be placed or reused.
  - Today, 8 of 10 nacelle part hits are subparts.
  - 7 of 10 landing-gear hits are more than half Technic.
  - 2 of 10 window hits are part definitions.
- **Effect.** Medium on models (more real options considered per role); High on part-search precision.

**A4 — Deduplicate and diversify.**
- **What.**
  - Collapse mirror L/R pairs, variant files of one set, identical part recipes, and printed variants onto the base mould. Report "N variants".
  - Optionally re-rank for diversity by how much the part sets overlap.
- **How it helps.** Ten slots show ten different ideas. For street lamps that means 6 distinct designs instead of 2039 four times.
- **Effect.** Medium–High on variety, which is the stated goal; Medium on search.

**A5 — Larger candidate budget when results are weak.**
- **What.** When the top score is below about 0.85, or fewer than 5 hits survive A3/A4, rerun with `--candidates 3000`. That costs about $0.07 and 47 s, instead of $0.011 and 8 s.
- **How it helps.** It finds the rare phrasings: 6067 "castle side wall with shuttered window".
- **Effect.** Low–Medium; it only matters for rare roles.

**A6 — Stable keys.**
- **What.** Provide primary-key tables, or tables with a generated `full_description` column, instead of views, so results carry `{model, submodel}` or `{part}`.
- **How it helps.** Vetting, renders and provenance can be cached and cited by key. Until then, parse the text before the first `|`.
- **Effect.** Very low directly; it enables the automation in B.

**A7 — Show the parent-model subject with each hit.**
- **What.** Display, and optionally filter on, the parent model's subject ("Star Wars X-wing", "passenger airplane"), kept outside the ranked text.
- **How it helps.** The agent can prefer same-subject references. It can still pick an off-subject technique deliberately, since a spaceship nacelle can still teach nacelle construction.
- **Effect.** Low–Medium. Needs the benchmark in §7 before embedding context in the ranked text.

**A8 — Part ID in the part text.** Already in the new view. It helps mixed queries ("3001 brick"), but `part` and `search parts` already cover exact IDs. **Effect:** Very low.

### B. Locating submodels and their sources

**B1 — From hit to source to repaired copy.**
- **What.** Turn `model|submodel` into:
  1. `data/models-annotated/<model>`;
  2. `sections` for the original line numbers;
  3. `extract --section … --namespace … --repair-bfc-comments`, which produces an attributed copy with a manifest.
- **How it helps.** Without the repair step, 1 in 5 source models cannot be inspected or rendered by the agent. With it, all 170 hits could be checked.
- **Effect.** High as an enabler; nothing in B2–B6 works reliably without it.

**B2 — Measured data on each hit.**
- **What.** Attach, from `inspect --contacts all` on the repaired copy (about 1.6 s each):
  - placements;
  - size in studs × plates × studs;
  - Technic fraction;
  - connection groups and connector coverage;
  - source diagnostics.
- **How it helps.** The agent matches reference scale and construction style to its own model before looking. Examples:
  - The An-225 engine is a 4-stud 43121. 7893's pod (4.0 × 13.5 × 11.0, 12 parts) is directly on scale.
  - 10030's "hull" has 1,378 placements and is not a module.
  - In 6891's wing, 48 of 59 parts have no connector metadata, so its contact result carries little weight.
- **Effect.** Medium on models (fewer failed adaptations, better scale fit); High for choosing references.

**B3 — Render board of candidate submodels.**
- **What.** A `part-board` equivalent for sections: extract and render the home view of each shortlisted hit (about 6 s each with LeoCAD), then show them as one board.
- **How it helps.** The agent chooses by looking. It catches text-vs-shape errors such as 10174, and it sees the visual idea it will transfer, for example the 7893 fan and spinner.
- **Effect.** High on detail and recognisability, because the visual idea is what carries over into the model.

**B4 — Rebuild the technique at the model's own scale.**
- **What.** Study the chosen reference's parts and layout, then implement the same construction in the generator with the model's palette, grid and interfaces. This is design by reference, not copying.
- **How it helps.** Each module gets a proven real-world solution instead of the agent's first improvisation. Examples:
  - airliner nacelles with fan and spinner (7893);
  - a slope-brick tail fin with a curved tip (5892);
  - wing-plate wings (6745, 31039).
- **Effect.** High on detail and variety for novel-scale vehicles; this is the main quality channel there. Medium on construction soundness: real sets are proven, but the adaptation must be checked again.

**B5 — Reuse modules directly.**
- **What.** Use `extract` → plan `assets` → `attach` on measured anchors, keeping the original author and licence headers.
- **How it helps.** Minifig-scale scenes get real props immediately:
  - 6 distinct lamp designs;
  - 10 distinct trees (7–42 parts);
  - 7 staircases;
  - dormers, truck cabs and ramps.
  The agent spends its design effort on the focal feature.
- **Limits.** Copied modules are not original design. Connector coverage can be partial: the 5766 tree forms 13 optimistic groups, so it must be validated in place. For vehicles at other scales, the scale rarely matches.
- **Effect.** High for minifig-scale town and building scenes; Low for novel-scale vehicles.

**B6 — Part suggestions from matched submodels.**
- **What.** Tally the parts used across the relevant hits for a role, with the sets that use them. Then feed them into `part` / `part-board`.
- **How it helps.** The part shortlist includes parts real designers used for that role, not only parts whose names match the query.
  - For engines this gives 43121, 46667 (fan), 3942c (cone spinner), 4740 (inverted dish), 4589 (cone), 3475b (jet plate), 44126 (curved pylon slope) and 3713 (bushes).
  - Description-based part search for "nacelle" found only 43121, plus subparts and hinge plates.
- **Effect.** Medium–High on the variety of detail parts; High on role-appropriate recall.

**B7 — Whole-model references.**
- **What.** Model search (with criteria), then `study` for decomposition, module sizes and reuse counts.
- **How it helps.** Real sets show which modules and props make the subject read:
  - 7893 airliner = fuselage (358 parts) + engine ×4 (12 parts each) + wheel set ×2 + cabin, seats, bar, stairs and crew;
  - 3181 cargo plane = moulded fuselage + tow vehicle + radar + tow bar + ground crew.
  This feeds the module checklist and the story props.
- **Effect.** Medium on planning and story completeness; Low on geometry.

## 4. End-to-end agent workflow

| Step | Action | Who decides |
|---|---|---|
| 1 | From the brief, list module roles and detail roles | Agent |
| 2 | Model search with criteria for 2–3 subject references; `study` their decomposition (B7) | Jev ranks; code measures |
| 3 | Per role: submodel search with criteria (A2); record-type filter (A3); fetch 30, deduplicate to 10 (A4); rerun with a larger budget if weak (A5) | Jev ranks; code filters |
| 4 | Locate the source and extract with repair (B1); measure (B2); drop hits by scale, Technic share and size rules | Code |
| 5 | Render board of the survivors (B3) | Agent looks |
| 6 | Per chosen reference: reuse if the scale matches (B5), otherwise rebuild the technique (B4). Add its parts to the part shortlist and `part-board` (B6) | Agent |
| 7 | Build, validate, render and review as today. Record each reference (model, section, lines, source SHA, what was used) in the design brief | Existing checks |

Jev only ranks descriptions. Code owns filtering, measurement and deduplication. The renders own visual choice. The existing checks own validity.

## 5. Retrospective: the An-225

| Module | What was built | What the improved search would have offered | Effect |
|---|---|---|---|
| Engines (focal supporting feature) | Plain 43121 nacelles | 7893 recipe: 46667 fan + 3942c spinner in the 43121, 44126 curved pylon fairing. Same 4-stud scale | **High** for that module |
| Opening nose visor | Stepped brick rings on 3937/3938 | Nothing relevant (0 R); only generic hinge panels | Very low |
| Ramp | Click-hinge plate deck | 60018 and 5893 hinged-plate ramps as alternative hinge layouts | Low–Medium |
| Main and nose gear | Measured classic axle recipe | 7893 wheel set, 6745 nose wheel; the rest Technic noise | Low |
| Tail fins | 54094 endplates | 6745 / 5892 slope-brick fins: alternatives at other scales, not better at 1:100 | Low |
| Wing | Plate field with measured wedges | Large wing plates (6745, 31039) suit smaller scales; the brick-built wing stands | Low |
| Scene story | Two containers | 3181 tow vehicle, tow bar and ground crew as microscale ideas | Low–Medium |

Overall for the An-225: **Medium.** The most visible gain is the engine detail. The visor, the weakest part of the model, has no reference in the collection.

## 6. What this will not improve

- **Buildability.** Geometric fit, connection legality, clutch, stability and `physical_validity` remain the job of `validate`, contacts, the mesh checks and review. A real LEGO source does not certify an adapted copy.
- **Scale and silhouette.** Converting a technique between scales, and designing proportions, remain the agent's work.
- **Description quality.**
  - Descriptions are AI annotations and can be wrong or vague ("tail", "Name: 4018 - Ship").
  - 1,326 assemblies have no description beyond their name, so semantic search cannot find them.
  - Submodel text rarely names the parent vehicle.
- **Coverage.** Some roles have no example in 1,821 models: an opening cargo nose, large cargo aircraft (2 models).
- **Attribution.** Reused modules keep their authors and licence. The agent must not present them as original design.

## 7. Cost, and the next measurement

**Measured cost.**
- **Jev:** 34 runs, 19,321 calls, 10.2M input tokens, **$0.43**, 318 s in total. A default 500-candidate query is about 256k tokens, 8 s and **$0.011**.
- **Per candidate:** inspect about 1.6 s, extract about 0.6 s, LeoCAD render about 5.5 s.
- **Per model (estimate):** 8 roles + 2 model queries + 2 larger reruns ≈ **$0.24** and about 3 min of Jev time (a 3,000-candidate run takes about 47 s). Vetting and rendering 10 candidates per role adds about 10 min of local time.

**Next measurement, before building any tooling.**
- Label about 12 roles × top 10, using renders, for four variants:
  1. ranked FTS;
  2. plain Jev;
  3. Jev with criteria;
  4. Jev with criteria plus A3/A4 filters.
- Compare relevant and distinct designs at 10, and time to a chosen reference.
- Keep A7 (context in the ranked text) only if it wins that comparison.
- Then check the claimed model-level effect: generate one vehicle and one street scene with and without B3/B4/B6, and compare blind renders.
