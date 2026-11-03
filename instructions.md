# Build and review an LDraw model

Deliver editable source, an MPD, scoped checks, matching BOMs and previews you
have opened. Keep new work in `output/`. Use one loop: **brief → retrieve → edit
plan → review → inspect images → repair**.

## Find what this brief needs

Run `./ldraw-agent doctor`. Use `./setup.sh` if necessary, with `--with-lsynth`
for flexible parts. Write down the requested silhouette, scale, dimensions,
palette and working features before choosing a construction.

```sh
./ldraw-agent knowledge search 'mounted pneumatic hoses'
./ldraw-agent examples 'steering rack'
./ldraw-agent knowledge show technic:retained-chain-drive
```

Search is local and works without Jev or network access. Default results include
current guidance and selected construction/tutorial lessons. Read the returned
source, parent requirements, evidence and limits. A matching example is a scoped
lesson, not an instruction to copy its whole silhouette. Choose System, SNOT,
Technic or a combination to suit the brief. No building or spaceship template is
universal. Inspiration, diagnostics and held work require an explicit scope and
do not silently fill empty searches. See [knowledge retrieval](docs/agent/reference/cli.md).

Use [source discovery](docs/agent/guides/find-references.md) when the curated KB
has no suitable construction; inspect the actual source and its parent before
reuse. Look up real parts and interfaces with `part`, `connectors` and the
catalog tools. Metadata names and bounding boxes do not establish fit.

## Author and assemble

Use an ordinary [JSON plan](docs/agent/reference/plans.md); Python can generate the same
format for repetition or calculations. Use named placements and
[joint/route authoring](docs/agent/guides/build-model.md). Keep geometry fixes in the
editable plan or generator. Use the existing builder/parser and LSynth engine.

Negative Y is up. Stud pitch is 20 LDU; brick and plate bodies are 24 and 8 LDU.
Stack using the upper part's body height, not bounding-box height. Inspect actual
origins. Use proper rotations; do not stretch or reflect rigid physical parts.
Colour 16 needs an explicit ancestor; colour 24 belongs to edges.

Build supports and real mating interfaces before skins or flexible routes.
Preserve bearings, axial stops, insertion order, fitting sleeves and passages.
Keep fixed-frame rigidity contracts separate from moving assemblies. A static
pose does not demonstrate motion. For [flex](docs/agent/guides/flex.md),
mount fittings/wheels first, route from their measured frames, synthesize early
and inspect actual output. Example bend limits are not universal material limits.

## Review and deliver

```sh
./ldraw-agent review output/model.plan.json --views home front back top bottom
```

Read `review.json` and `validation.json`, then open the images. Fix the first
failed prerequisite. Intermediate `--no-render` and `--section` reviews exclude
some delivery evidence; finish with whole-model checks and fresh final images.
After two unsuccessful corrections, isolate the problem and reconsider space or
interfaces while preserving the requested features and checks.

Use global `ldraw-xray` for isolated sections and actual parent context. Follow
its mandatory `../ldraw-xray/README.md` and `../ldraw-xray/AGENTS.md`. Reuse
source-matched images for unchanged geometry; add views to resolve uncertainty.
Every retained or improved model/submodel needs visual inspection, not just a
JSON description. Source-step pages reveal authored assembly stages; posed or
cutaway views do not prove build order or travel.

Keep explicit skipped coverage: contacts skip automatically above 500 placements;
select modules or request `--contacts all` when needed. Contact groups, BOM
agreement and successful rendering each establish different things. None proves
strength, complete material clearance, stock hose length or unrestricted motion.

Deliver source, model, validation/review reports, manifests, BOMs, final previews
and notes naming images opened, repairs and unresolved limits. Use `--force` for
intentional review reruns. See [validation](docs/agent/reference/validation.md) and
[CLI contracts](docs/agent/reference/cli.md) for diagnostic meanings and exact options.
