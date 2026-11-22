---
name: find-constructions-and-parts
description: 'Research before and during planning: find construction lessons with knowledge search and knowledge show, browse reviewed real-set examples (examples --family, --details), inspect a reference''s evidence and adapt its principle, and answer specific part questions (search parts, part CODE, dimensions, SQL, regex, lexical and semantic ranking, categories) without reading library .dat files. Use when choosing how to build a role in the brief, looking up a part number or its studs, sockets and size, or checking whether a part exists.'
---

# Find constructions and parts

Research before and during planning: find the construction lesson for each role in the brief, inspect a reference's evidence before reusing it, and answer specific part questions (number, variant, size, studs) without reading library files. **Construction knowledge comes first**: brief → retrieve guidance and examples → adapt their principles → build → inspect → repair → deliver. Part search answers specific questions inside that loop; it is not a way to design piece by piece.

**Never read, search or parse library `.dat` contents** (`data/ldraw/parts/`, `data/ldraw/p/`, or any external library), never follow `~Moved to...` chains by hand, and never reconstruct geometry from raw coordinates. Use the tools below and their reports.

## 1. Find a construction lesson

```sh
./ldraw-agent knowledge search 'sideways glazing attachment' --limit 5
./ldraw-agent knowledge show ID
./ldraw-agent examples 'retained chain' --family flex
./ldraw-agent knowledge search 'spacecraft silhouette' --scope inspiration
```

- Retrieve a few role-specific lessons, open their documentation and model source paths, and compare interfaces, scale and limits.
- Default search covers current guides, construction lessons and tutorials. Inspiration, diagnostics, holds, archives and research need an explicit `--scope`.
- **No match is useful information**: do not silently fill the list from a weaker source. Record the unresolved question and use raw discovery below.
- `--family spaceship` interleaves source models by default; compare principles against the brief ([spacecraft](../design-models/spacecraft/SKILL.md)).
- Families include `recipe`, `snot`, `submodel`, `vehicle`, `spaceship`, `aircraft`, `technic`, `mechanism`, `flex`. `examples --family F --details [QUERY]` lists detail packages.

## 2. Answer a specific part question

| Question | Source and method |
|---|---|
| Known filename or literal description fragments | `search parts`: SQL over `PARTS_DESCRIPTIONS` |
| Filename family or a text pattern | `rg` against the full TSV snapshot |
| Keywords with lexical relevance ranking | `discover search parts --engine fts`: FTS5/BM25 index |
| Purpose, appearance or semantic relevance | `discover search parts --engine jev`, or standalone `jev-rerank` |
| Minifigure body parts or accessories | `catalog parts --category minifig` or an exact subgroup |
| Candidate dimensions and local extents | `dimensions PART...`; optional size filters on `search parts` |
| Attachment details after identifying a part | `part`, `connectors`, `snap`, and visual inspection |
| How to build a structure | construction guides, `knowledge`, examples and recipes |

The methods have no mandatory order; combine them and keep results bounded. A relevance score, category label or cached dimension does not establish fit, strength or availability.

### SQL lookup: `search parts`

```sh
./ldraw-agent search parts 3023 --field part --match exact
./ldraw-agent search parts 'brick 2 x 4' --limit 8
./ldraw-agent search parts 'Minifig Shield%' --field description --match like --limit 8
./ldraw-agent search parts 'shield' --limit 8 --offset 8
./ldraw-agent search parts 'slope' --dimensions --min-size 20 8 20 --max-size 80 48 80 --limit 8
./ldraw-agent dimensions 3001.dat 3023 3659
```

| Option | Meaning |
|---|---|
| `--field part\|description\|both` | fields searched (default both) |
| `--match terms` | default: every whitespace-separated literal term must appear |
| `--match exact` | whole-field match; part codes with or without `.dat` |
| `--match like` | SQLite `%` and `_` wildcards |
| `--limit`, `--offset` | positive limit, nonnegative offset |
| `--dimensions`, `--min-size`, `--max-size` | size filters (X Y Z, LDU) |

Matching is ASCII case-insensitive; exact filenames rank first, then shorter descriptions. Distinct filenames with equal descriptions are kept (that does not prove interchangeability). Dimensions are positive local-axis extents that may include studs and decoration: not body heights or connection planes.

### Inspect the part you chose

```sh
./ldraw-agent part 3001            # origin, body box, full bounds, studs and sockets by face
./ldraw-agent part 32140 3648b     # several parts; Technic parts list technic_ports
./ldraw-agent part 3001 --full     # every connector record, provenance, completeness
./ldraw-agent part-board 4079 3829c01 --outdir output/fittings   # render candidates, then open the images
```

### Regex over the full snapshot

```sh
./ldraw-agent export-parts-descriptions
rg -i -m 20 -- 'minifig.*(shield|helmet)' data/parts-descriptions-full.tsv
rg -m 20 -- '^3001[^[:space:]]*' data/parts-descriptions-full.tsv
./ldraw-agent export-parts-descriptions --force   # refresh after the DB changes
```

A Git-ignored UTF-8 TSV snapshot of every `PARTS_DESCRIPTIONS` row (`part`, `description`). Use SQL when field-aware matching matters. Never dump the whole table into context.

### Lexical and semantic ranking

```sh
./ldraw-agent discover search parts 'jet engine housing' --engine fts --limit 6
./ldraw-agent discover search parts 'a heraldic shield for a castle' --engine jev --limit 6
bin/jev-rerank --db data/ldraw-info.db \
  --table-field PARTS_DESCRIPTIONS.description --top 6 \
  --query 'a heraldic shield for a castle' --show --json
```

FTS is offline token-OR with BM25 ordering. Jev needs `TYPESAFE_API_KEY`; check availability first (see [cli-contracts](../reference/cli-contracts/SKILL.md)). There is no silent engine switch. Describe one part role per query. Part discovery filters to System by default: use `--construction all` or a Technic scope deliberately.

### Categories and other sources

```sh
./ldraw-agent catalog categories
./ldraw-agent catalog parts 'shield' --category minifig --limit 8
./ldraw-agent catalog parts --category minifig.accessories --limit 8
./ldraw-agent technic catalog 'worm' --limit 8
```

Categories are fallible hints (prefixes include subgroups). `--include-unavailable` adds legacy/internal hints; `catalog parts --measure` and `technic catalog --connectors` inspect installed geometry. Read-only SQL is allowed for supplemental tables:

```sh
sqlite3 -readonly -header -column data/ldraw-info.db \
  "SELECT alias, keywords FROM PART_KEYWORDS WHERE keywords LIKE '%Castle%' LIMIT 8;"
sqlite3 -readonly -header -column data/ldraw-info.db \
  "SELECT code, color, value FROM COLORS WHERE color LIKE '%Blue%' LIMIT 8;"
```

| Source | Content and limits |
|---|---|
| `PARTS_DESCRIPTIONS` | Corrected part descriptions; equal descriptions do not prove interchangeability |
| `PARTS_DESCRIPTIONS_FTS`, `PARTS_DESCRIPTIONS_JEV` | Lexical index; semantic view |
| `PART_BBOXES` | Cached local bounds and completeness, not live measurements |
| `data/categories/dimensions.py` | Extra estimates, rounded stud/plate extents |
| `PART_KEYWORDS`, `PART_CATEGORIES`, `CATEGORIES` | Partial vocabulary and category assignments |
| `PART_INFOS` | Supplemental alias/name fields; not proof of canonical replacement |
| `COLORS` | Colour codes and names; not proof a part was made in a colour (`./ldraw-agent colours QUERY`) |
| `PARTS_BRICKLINK_CAT`, `PARTS_REBRICKABLE_CAT` | Currently empty |

## 3. Broader raw-source discovery

When curated knowledge lacks a role, search parts, models or submodels offline. Whole models inform proportions, submodels reveal construction, parts supply shapes. These raw results are **not admitted examples**.

```sh
./ldraw-agent discover index
./ldraw-agent discover search submodels 'rack steering' --construction all --engine fts --limit 5
./ldraw-agent discover search parts 'jet engine housing' --engine fts --limit 6
./ldraw-agent search submodels 'steering' --limit 5
```

Choose the construction filter deliberately (raw discovery defaults to System); do not infer a technique from the subject.

### Compare actual images and dimensions

```sh
./ldraw-agent discover catalog output/lamps.json --outdir output/lamp-references --jobs 2
./ldraw-agent discover show submodel-2bd03fab63ff8deee3a007d0
./ldraw-agent discover prepare submodel-2bd03fab63ff8deee3a007d0 \
  --outdir output/lamp-references --contacts all \
  --views home front back right left top bottom
```

Open the catalog's `index.html` and the views. Images are framed independently in source-local orientation: compare listed dimensions and parent transforms, not apparent size. Each card holds `source.mpd` (dependency-closed, attributed extraction), `preview.mpd`, `extraction.json` (hashes, renames, recorded repairs), `card.json` (BOM, fittings, bounds, parent placements, diagnostics, contacts, review status) and `renders/`. `--contacts none` is the economical default; request `all` on a selected assembly before reuse.

### Record a decision, then reuse, adapt or rebuild

```sh
./ldraw-agent discover review submodel-2bd03fab63ff8deee3a007d0 \
  --catalog output/lamp-references --decision adapt --viewed-views home front right top \
  --note 'The globe and tall moulded post suit this pavement; reserve the post base and check its connection to the scene.'
./ldraw-agent discover example submodel-2bd03fab63ff8deee3a007d0 \
  --catalog output/lamp-references --output output/my-lamp-example \
  --title 'Globe street lamp' --scale minifigure \
  --lesson 'Use a dedicated post and globe to keep a narrow street fitting legible.' \
  --placement-notes 'Preserve source orientation and measure the exposed base; reserve the complete globe envelope above the pavement.'
```

- Decisions: `reuse`, `adapt`, `technique`, `reject`. List only views actually opened. Changed artifacts invalidate the review.
- `discover example` exports an editable plan (via `assets`) once checks pass, BOMs match and a reuse/adapt review exists. Its `source_origin` anchor is not a connector; author attachment frames only after inspecting real surfaces.
- If the reference is the wrong scale or invalid, rebuild its technique with real parts and your interfaces. `discover recipe` lists rebuilt recipes, e.g. `discover recipe arcade-bay --height 5 --colour 19 --accent 28 --output output/tall-arch.plan.json`.
- In process notes, name the precedent, modules studied, what was copied or rebuilt and what each contributes.

## Read references critically

- **Prefer the actual assembly over its label.** Expand the physical inventory and read the source before assigning roles: the W16 "V8" label, double-bevel gears on parallel axes and a cam-driven engine are counterexamples. Embedded DATs with numeric descriptions may be important gears.
- **Keep selection, frame and occurrence identity together.** Record model hash, exact `FILE` section, occurrence paths, composed transforms and colours. Mecha paths like `84/16` are not Nova `--occurrence` indices: get current indices with `inspect`/`connectors` on the same selection. Extracting a section changes its frame.
- **A visible support may be an incomplete interface.** List fixed supports, moving members, inputs/outputs and omitted neighbours (a rack without its pinion, a gearbox without bearings). Coaxial proximity is not rigid coupling, torque transfer or retention.
- **Missing evidence is a reason to inspect.** A disconnected-looking drivetrain may be rounded rotations, embedded parts, shadow gaps or skipped contacts. Record unresolved couplings rather than inventing connectors. Never silently normalize real scale/shear or introduce reflections.
- **Keep observation and qualification together:** what was measured, what the source checked, what was inferred, and what changes in this model.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/find-references.md](references/docs-agent-guides-find-references.md)
- [docs/agent/guides/part-information.md](references/docs-agent-guides-part-information.md)
