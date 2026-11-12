# Working in ldraw-nova

This repository provides LDraw model generation, part/reference discovery,
geometry checks, rendering and a curated construction knowledge base. Use the
existing `ldraw-agent` tooling and ordinary JSON plans; Python generators can
emit the same plans. Run commands below from the repository root.

## Construction first; part information for specific questions

Follow **brief → retrieve construction guidance and examples → adapt their
principles → build → inspect → repair → deliver**. Existing documentation,
lessons, recipes and examples establish how to build. Part retrieval supports
specific needs such as a variant, substitute, dimension, accessory or attachment;
do not design an entire model by searching piece by piece or reinvent supported
constructions with ad-hoc generators or geometry reconstruction.

**NEVER directly read, search or independently parse library `.dat` contents**
under `data/ldraw/parts/`, `data/ldraw/p/`, or equivalent external library roots
for part descriptions, structure or geometry. Raw headers often contain
`~Moved to...` pointers; corrected database descriptions avoid manual alias
navigation. Equal descriptions for different filenames are intentional.

**Use informational sources and existing tools instead.** Choose SQL/literal
search, FTS/BM25, Jev ranking, regex over the generated description TSV,
categories or cached dimensions to answer the particular question. These are
complementary options, not a mandatory sequence. See the
[part-information guide](docs/agent/guides/part-information.md) for sources,
commands, limits and the create-if-missing TSV export. Keep results bounded.

Before visually inspecting parts, obtain their exact filenames from these
sources, then render those identified parts and open the images. Existing
`part`, `connectors`, measurement, rendering and validation tools may internally
read geometry; consume their reports rather than parsing raw definitions.
A search hit or cached dimension does not prove fit or a construction method.

## Generate a model

Keep each new model, editable sources and evidence in `output/<task>/`. Choose
dimensions, palette and construction details from the user's brief; resolve
ordinary design choices yourself. Retrieve construction guidance and examples
before adapting their principles to the brief.

Default to **SNOT (Studs Not On Top)** construction for new models. Read the
[SNOT guide](docs/agent/guides/snot.md) and retrieve relevant SNOT connections
before planning the core and visible surfaces. Use inspected side-stud bricks,
brackets or other mating interfaces to support sideways assemblies. Combine
conventional studs-up System, Technic or flexible techniques where the brief,
structure or function needs them. An explicit user construction preference
overrides this default.

1. Establish the subject, silhouette, scale, required features and poses. Run
   `./ldraw-agent doctor`. If setup is needed, run `./setup.sh` (includes LSynth
   for flexible parts). Setup installs project-local tools, Python and the
   official LDraw library.
   Poppler and LeoCAD are prerequisites; see [local setup](docs/setup.md) and the
   [setup and CLI contracts](docs/agent/reference/cli.md#setup).
2. Search for the construction roles the brief needs, then read the returned
   source sections, parent requirements and limits:

   ```sh
   ./ldraw-agent knowledge search 'mounted pneumatic hoses'
   ./ldraw-agent examples 'steering rack'
   ./ldraw-agent knowledge show technic:retained-chain-drive
   ```

   Search works locally without Jev or a network connection. Default results
   include current guidance and admitted construction/tutorial lessons.
   Inspiration, diagnostic, research, archive and hold scopes require explicit
   selection; finding a source does not approve its reuse or export. When no
   suitable lesson exists, use [source discovery](docs/agent/guides/find-references.md).
   For new spacecraft, define silhouette and scale before exporting a reference.
   Compare construction lessons from different source models; see the
   [spacecraft comparison workflow](docs/agent/guides/design-models.md#compare-construction-sources-before-selecting-one).
   The SNOT default does not select a default ship or silhouette.
3. Author a [JSON plan](docs/agent/reference/plans.md) with named placements.
   Keep repairs in the plan or generator. Inspect real part origins and mating
   interfaces with `part` and `connectors`; names and bounding boxes do not prove
   fit. Build supports and attachments before skins or flexible routes. Use SNOT
   as the default construction style, with other techniques as needed; adapt lessons without
   copying an example's whole silhouette by default.
4. Build and review your plan (using `output/my-model/` as an example):

   ```sh
   ./ldraw-agent build output/my-model/model.plan.json --output output/my-model/model.mpd
   ./ldraw-agent review output/my-model/model.plan.json --outdir output/my-model/review --views home front back top bottom
   ```

   Read the reports and open the images. Repair the first failed prerequisite;
   if repeated corrections fail, isolate the interface and reconsider its
   construction. `--no-render` and `--section` support intermediate work; finish
   with a whole-model review. Use `--force` for intentional reruns. Keep authored
   notes outside the generated review directory, which is replaced as a bundle.
5. Deliver the editable plan/generator and dependencies, final MPD, validation
   and review reports, matching BOMs, previews, and a short README with replay
   commands, images actually inspected and unresolved limits. Evidence must
   match the delivered model revision. Report incomplete checks explicitly.

## Read guidance for the task at hand

| Task | Guidance |
|---|---|
| Plan fields, repetition, includes or Python authoring | [Plan reference](docs/agent/reference/plans.md), [build workflow](docs/agent/guides/build-model.md) |
| Subject proportions and construction choices | [Design models](docs/agent/guides/design-models.md) |
| Targeted part questions and search-method selection | [Part information](docs/agent/guides/part-information.md) |
| Part frames, mounting and submodel composition | [Place parts](docs/agent/guides/place-parts.md), [compose modules](docs/agent/guides/compose-modules.md) |
| Sideways construction | [SNOT](docs/agent/guides/snot.md) |
| Aircraft of any style: airliner, jet, prop plane, biplane, floatplane | [Aircraft](docs/agent/guides/aircraft.md) |
| Structural frames, joints and moving assemblies | [Technic](docs/agent/guides/technic.md), [mechanisms](docs/agent/guides/mechanisms.md) |
| Hoses, cables, bands, chains or treads | [Flex authoring](docs/agent/guides/flex.md), [flex contracts](docs/agent/reference/flex.md) |
| Browsing annotated models in the local 3D selector | [Model selector](model-selector/README.md) (`./model-selector.sh`) |
| Annotating unstructured reference models | [Annotator workflow](docs/agent/guides/annotate-models.md) |
| X-ray, parent context, stud maps and inspection boards | [Xray workflow](docs/agent/guides/xray.md) |
| Visual inspection, failures and evidence coverage | [Review models](docs/agent/guides/review-models.md), [validation](docs/agent/reference/validation.md) |

LDraw uses negative Y as up, a 20 LDU stud pitch, and 24/8 LDU brick/plate body
heights. Stack using body height, not bounding-box height. Use proper rotations;
do not stretch or reflect rigid parts. Colour 16 needs an explicit ancestor;
colour 24 is for edges.

## Visual review and evidence

Visually inspect every retained or improved model and submodel, both isolated
and in its actual parent placement. Open rendered images; text and JSON alone
are insufficient. Use **`bin/ldraw-xray`** for submodel/parent inspection
(or a PATH installation if the local tool is absent). Before using it, read
the [xray workflow](docs/agent/guides/xray.md), configure the environment from
[local setup](docs/setup.md), then run `bin/ldraw-xray doctor`.
For annotation, read the [annotator workflow](docs/agent/guides/annotate-models.md)
and use `bin/ldraw-annotator` with the supplied database read-only.
Reuse existing images only when their source hashes and selections match;
render new views for changed geometry or unresolved questions.

Record skipped coverage. Automatic contacts stop above 500 placements; inspect
modules or request `--contacts all` when needed. A section review excludes
parent/sibling interactions. BOM agreement, connectivity, rendered poses and
material clearance are distinct evidence; none alone proves strength or motion.
Mount flex endpoints first, synthesize early and inspect the actual output.
Example bend limits are not universal material limits.

## Change the tooling or knowledge base

For code changes, work in `ldraw_tools/` and use the related tests in `tests/`.
Run affected tests with `.venv/bin/python -m pytest tests/test_<area>.py -q`;
use `.venv/bin/python -m pytest -q` for broad changes. `./setup.sh` installs test
dependencies; standard setup includes LSynth for flex tests. Keep CLI help and the relevant
`docs/agent/` contract aligned with behavior. Model generation is validated by
its own review artifacts, not by rerunning the entire software test suite.

For KB changes, package READMEs own `ldraw-knowledge` registrations. Edit those
owners and regenerate compatibility catalogs using each atlas README's command.
Keep scopes, aliases, source attribution and source/BOM/visual freshness gates.
New or changed geometry needs matching visual evidence before admission.
`docs/reports/` contains historical findings; `data/` and `lsynth-examples/`
contain source research, not automatically admitted construction lessons.
Preserve the planning baseline in `docs/plans/knowledge-base-overhaul/snapshot/`;
record subsequent decisions in the implementation record instead.
