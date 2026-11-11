# Answer a specific part question

**Construction knowledge comes first.** Follow the documented workflow:
brief → retrieve guidance and examples → adapt their construction principles →
build → inspect → repair → deliver. Use existing lessons, recipes and tools for
supported constructions, including the SNOT default. Adapt principles to the
subject rather than copying an example's whole silhouette.

Use the sources below when that construction raises a specific question: identify
a referenced part, compare variants or dimensions, choose a substitute, find an
accessory, or investigate an attachment. Do not assemble an entire design by
searching piece by piece or replace documented techniques with ad-hoc generators.
If guidance is insufficient, follow [reference discovery](find-references.md)
and record the unresolved construction question.

**Never directly read, search, or independently parse library `.dat` contents**
for descriptions, structure or geometry. This includes `data/ldraw/parts/`,
`data/ldraw/p/`, and the equivalent directories in externally configured libraries.
Do not follow `~Moved to...` chains manually or reconstruct geometry from raw
coordinates. Database descriptions resolve those pointers for ordinary parts;
duplicate descriptions for distinct filenames are intentional. Querying compact
metadata avoids thousands of file reads and keeps mesh definitions out of context.

For visual inspection, first obtain exact filenames from informational sources,
then let the rendering tools resolve those specific files under `parts/` or `p/`.
Open the rendered images. Existing measurement, connection, rendering, build and
validation tools may internally read geometry; agents should use their reports.

## Choose the method for the question

There is no mandatory order among these methods. Combine them when useful and
keep results bounded. A high relevance score, category label or cached dimension
does not establish fit, strength, physical-part status or manufacturing availability.

| Question | Source and method |
|---|---|
| Known filename or literal description fragments | `search parts`: SQL over `PARTS_DESCRIPTIONS` |
| Filename family or a text pattern | `rg` against the full TSV snapshot |
| Keywords with lexical relevance ranking | `discover search parts --engine fts`: existing FTS5/BM25 index |
| Purpose, appearance or semantic relevance | `discover search parts --engine jev`, or standalone `jev-rerank` |
| Minifigure body parts or accessories | `catalog parts --category minifig` or an exact subgroup |
| Candidate dimensions and local extents | `dimensions PART...`; optional size filters on `search parts` |
| Attachment details after identifying a part | Existing `part`, `connectors`, `snap`, and visual-inspection tools |
| How to build a structure | Construction guides, `knowledge`, examples and recipes; broader annotated references when needed |

### SQL and exact/literal lookup

```sh
./ldraw-agent search parts 3023 --field part --match exact
./ldraw-agent search parts 'brick 2 x 4' --limit 8
./ldraw-agent search parts 'Minifig Shield%' --field description --match like --limit 8
./ldraw-agent search parts 'shield' --limit 8 --offset 8
./ldraw-agent search parts 'slope' --dimensions --min-size 20 8 20 --max-size 80 48 80 --limit 8
./ldraw-agent dimensions 3001.dat 3023 3659
```

`--field part|description|both` defaults to both fields. `--match terms` (default)
requires every whitespace-separated literal term in either selected field.
`exact` compares whole fields, accepting part codes with or without `.dat`;
`like` uses SQLite `%` and `_` wildcards. Matching follows SQLite's ASCII
case-insensitive text behavior. Literal mode treats wildcard characters literally.
Exact filenames rank first; remaining ties use description length then filename.
`--offset` is nonnegative and `--limit` is positive. Results retain distinct
filenames with equal descriptions and report total counts, truncation and provenance.
No installed-library check occurs during search.

Dimension lookup returns DB bounding-box evidence and category estimates
separately. Filtering prefers complete, finite `PART_BBOXES` dimensions, then
available category estimates; missing sizes are excluded only for size filters.
Bounds are positive minimum/maximum X/Y/Z extents in local-axis LDU, not rotated
fit tests. Returned sizes may include studs and decoration; they are not body
heights or connection planes. The report identifies the selected source.

### Regex over the full snapshot

```sh
./ldraw-agent export-parts-descriptions
rg -i -m 20 -- 'minifig.*(shield|helmet)' data/parts-descriptions-full.tsv
rg -m 20 -- '^3001[^[:space:]]*' data/parts-descriptions-full.tsv
# Refresh deliberately after the source database changes:
./ldraw-agent export-parts-descriptions --force
```

The export contains **every** `PARTS_DESCRIPTIONS` row, ordered by filename,
with `part` and `description` column headers. It is UTF-8 TSV with standard CSV-style
quoting for tabs, newlines and quotes. The supplied ordinary descriptions occupy
one line each; future embedded newlines may make regex matches span only part of
a record. Use SQL when field-aware matching matters.

The file is Git-ignored because it duplicates the DB. An explicit file argument
lets `rg` search it anyway. Export creates it if missing and preserves it otherwise;
`--force` atomically replaces it. It is a snapshot, not an automatically refreshed
index. Never dump the whole table into the agent's context.

### Lexical and semantic ranking

```sh
./ldraw-agent discover search parts 'jet engine housing' --engine fts --limit 6
./ldraw-agent discover search parts 'a heraldic shield for a castle' --engine jev --limit 6
bin/jev-rerank --db data/ldraw-info.db \
  --table-field PARTS_DESCRIPTIONS.description --top 6 \
  --query 'a heraldic shield for a castle' --show --json
```

Use the [Jev availability check](../reference/cli.md#check-jev-availability-before-searching).
FTS is an explicit offline option; there is no silent engine switch. FTS uses token
OR with built-in BM25 ordering; literal SQL search has different substring/AND
semantics. Jev reranks a bounded candidate set; preserve its scores and coverage.
Describe one needed part role, not an instruction to generate a whole model's BOM.

Part discovery uses database-only candidate classification and stable IDs. Default
construction filtering remains System; use `--construction all` or an appropriate
Technic scope deliberately. Metadata classification is not physical validation.
`discover show part-ID` reports metadata with installed availability and physical
accounting unknown. Explicit `part` inspection supplies geometry evidence later.

### Categories and additional information

```sh
./ldraw-agent catalog categories
./ldraw-agent catalog parts 'shield' --category minifig --limit 8
./ldraw-agent catalog parts --category minifig.accessories --limit 8
./ldraw-agent technic catalog 'worm' --limit 8
```

Category prefixes include their subgroups. Minifigure groups are useful for body
parts and accessories; general category files contain misclassifications. Treat
all categories as hints, never as authoritative labels or complete coverage.
Metadata catalog results leave availability unknown. `--include-unavailable`
also includes legacy/internal hints; it does not check installation.
`catalog parts --measure` and `technic catalog --connectors` explicitly inspect
installed geometry/interfaces. Connector inspection first narrows candidates by
query/family/model; alias resolution stays within the tooling.

| Source | Content and limits |
|---|---|
| `PARTS_DESCRIPTIONS` | Corrected ordinary part descriptions. Equal descriptions do not prove interchangeability. Two current `models/` rows still point to LDR models. |
| `PARTS_DESCRIPTIONS_FTS` | Existing lexical index; required for part FTS searches. |
| `PARTS_DESCRIPTIONS_JEV` | Filename/description view used by existing semantic workflows. |
| `PART_BBOXES` | Cached local bounds, center, dimensions and completeness; not live measurements. |
| `data/categories/dimensions.py` | Additional estimates, including rounded stud/plate extents; some references are absent. |
| `PART_KEYWORDS` | Partial supplemental vocabulary, themes, set and part references. |
| `PART_CATEGORIES`, `CATEGORIES` | Partial category assignments and vocabulary. |
| `data/categories/parts/minifig/` | Body-part and accessory symbols. |
| Other `data/categories/parts/*.py` | Fallible category hints; use the catalog tool rather than parsing these files yourself. |
| `PART_INFOS` | Supplemental alias/name/description fields; not proof of canonical replacement and not a substitute for corrected descriptions. |
| `COLORS` | Colour codes/names/values; not evidence that a part was manufactured in a colour. |
| `PARTS_BRICKLINK_CAT`, `PARTS_REBRICKABLE_CAT` | Currently empty; unavailable as mapping sources. |
| Annotated models, model/submodel DB descriptions and curated examples | Contextual part usage and construction; use the existing reference workflow and evidence gates. |
| `data/offLibShadow/` and curated interface metadata | Access through existing connector/inspection tools, not ad-hoc geometry calculations. |

Supplemental SQL queries can be used directly, bounded and read-only:

```sh
sqlite3 -readonly -header -column data/ldraw-info.db \
  "SELECT alias, keywords FROM PART_KEYWORDS WHERE keywords LIKE '%Castle%' LIMIT 8;"
sqlite3 -readonly -header -column data/ldraw-info.db \
  "SELECT alias, categories FROM PART_CATEGORIES WHERE categories LIKE '%Minifig%' LIMIT 8;"
sqlite3 -readonly -header -column data/ldraw-info.db \
  "SELECT code, color, value FROM COLORS WHERE color LIKE '%Blue%' LIMIT 8;"
```

The supplied DB and category files remain read-only. Category/dimension parsing
uses the existing safe literal reader with a disposable SQLite cache; source
path, size/mtime and cache-format changes invalidate it. Missing or invalid
sources produce explicit errors or missing-value evidence. Choose another
available informational source when appropriate; never fall back to `.dat`
scanning. Use exact filenames for targeted rendering and existing inspection
commands, then return to the documented construction and review workflow.
