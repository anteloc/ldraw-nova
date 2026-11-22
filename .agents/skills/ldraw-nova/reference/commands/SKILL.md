---
name: commands
description: 'Every ./ldraw-agent command with its options, generated from the argument parser: core commands (flex, review, examples, knowledge, technic, vehicle, doctor, search, dimensions, part, colours, finalize, build, validate, render) and specialist commands (discover, spaceship, manual, mechanism, catalog, design, part-board, index, spec, sections, study, extract, matrix, profiles, inspect, bom, compare-bom, snap, connectors, cad-check, glb). Use when looking up a command''s exact flags or global options such as --library and --shadow.'
---

# Command reference

Every `./ldraw-agent` command and its options, generated from the argument parser. `./ldraw-agent COMMAND --help` prints the same text; output contracts, artifacts and exit codes are in [cli-contracts](../cli-contracts/SKILL.md). This summary lists the options that matter most; the verbatim copy below has every flag.

**Global options go before the command:** `--library` (parts library root; default `LDRAW_DIR`, then `LDRAWDIR`, then `data/ldraw`), `--shadow` (LDCad directory/zip/csl; repeatable; replaces `LDRAW_SHADOW` or `./data/offLibShadow`), `--no-shadow`.

## Shared options

Many commands that read a model accept the same selection and geometry options:

| Option | Default | Meaning |
|---|---|---|
| `--section NAME` | — | only this FILE block and its dependency closure; indices become section-local |
| `--colour CODE` | — | explicit inherited colour for a selected subassembly (needs `--section` on `review`) |
| `--detail {summary,full}` | summary (`inspect`: full) | report detail |
| `--contacts {auto,all,none}` | auto | auto computes contacts for at most 500 physical placements |
| `--limit N` | 200 | instance/contact/pair/component rows shown (does not limit checks) |
| `--offset N` | — | first physical occurrence to display |
| `--max-instances N` | 100000 | physical expansion budget |
| `--full` | — | print the complete report instead of the summary |
| `--quiet` | — | one line: verdict, counts, first error |
| `--report FILE` | — | save the complete JSON report |
| `--timeout S` | 90 | per external command |

## Core commands

| Command | Purpose | Key arguments and options |
|---|---|---|
| `build PLAN` | Build a validated MPD from a JSON plan | `--output` (default `NAME.mpd` beside the plan), `--report`, `--force` (replace an existing MPD after successful validation), shared geometry options, `--quiet` |
| `review FILE` | Build if needed, check geometry, render and compare BOMs in one folder | `FILE` is a plan or MPD/LDR; `--outdir` (default `SOURCE-review`), `--force`, `--no-render`, `--draft`, `--views` (default home top front), `--section`, `--colour`, shared options |
| `validate FILE` | Check an MPD's source and, with `--geometry`, its assembly geometry | `--profile {assembly,syntax}` (default assembly), `--geometry`, `--strict` (warnings fail), shared options |
| `render FILE` | Render review views and export a LeoCAD BOM | `--outdir` (required), `--views` (default home top front), `--timeout`, `--section`, `--colour` |
| `finalize MODEL` | Add the licence comment and AI keywords to a built MPD and check delivery metadata, including the `ai-<model-name>.mpd` filename | in place unless `--output` |
| `part CODE...` | Origin, body, studs/sockets by face and Technic ports of one or more parts | `--full` (every connector record), `--limit` (default 30, with `--full`) |
| `search KIND QUERY` | Search part descriptions or annotated models | `KIND {parts,models,submodels}`, `--limit` (10), `--offset`, parts only: `--field {part,description,both}`, `--match {terms,exact,like}`, `--dimensions`, `--min-size X Y Z`, `--max-size X Y Z` |
| `dimensions REFS...` | Cached dimensions for identified parts, without geometry loading | — |
| `colours [QUERY]` | Look up codes in the installed `LDConfig.ldr` | — |
| `knowledge search QUERY` | Rank lessons and guide sections | `--limit` (5), `--scope {default,construction,tutorial,inspiration,diagnostic,research,archive,hold,all,guidance}`, `--family`, `--subject`, `--technique`, `--diversify {source,none}`, `--full` |
| `knowledge show ID` | Read a lesson (ID or qualified alias) or a guide section (`path#anchor`) | `--family`, `--full` |
| `examples [QUERY]` | Find curated examples across families | `--limit` (5), `--scale {minifigure,microscale}`, `--details`, `--family`, `--diversify`, `--scope`, `--full` |
| `doctor` | Show dependencies and source paths | — |

### `flex`

| Subcommand | Purpose | Key options |
|---|---|---|
| `flex types` | List synthesis types, products and constraint parts | — |
| `flex guide TYPE` | Family-specific authoring, inspection and repair guidance | — |
| `flex hose` | Author visible constraints from two outward-facing endpoints | `--start`, `--start-direction`, `--end`, `--end-direction`, `--output` (all required); `--lead`, `--via` (repeatable), `--up`, `--type` (default `TECHNIC_PNEUMATIC_HOSE_BEVELED`), `--colour` (4), `--force` |
| `flex check FILE` | Diagnose constraints and optionally their synthesized asset | `--asset`, `--block N`, `--min-radius`, `--max-turn`, `--tube-radius`, `--min-separation`, `--length`, `--length-tolerance` (1), `--obstacles`, `--obstacle-section`, `--report` |
| `flex build FILE` | Check constraints, synthesize and measure an MPD asset | `--output` (default `SOURCE.mpd`), `--namespace`, `--force`, `--timeout` (90), `--no-cache`, `--report`, plus the `flex check` limits |

### `technic`

| Subcommand | Purpose | Key options |
|---|---|---|
| `technic parts [CODE]` | Parts with ports: one in full, or the most used by role or words | `--role {member,connector,shaft,retainer,gear,wheel,equipment,bridge}`, `--query`, `--top` (40) |
| `technic gears [TEETH...]` | Tooth counts, pitch radii and mesh centre distances | — |
| `technic trace FILE` | Rigid groups, turning joints and gear meshes; checks mechanism contracts | `--section` |
| `technic check FILE` | Seated joints, restraints, required mounts and assembly order | `--contract`, `--report`, `--max-instances` (500), `--section`, `--colour` |
| `technic catalog [QUERY]` | Inventory mechanism parts, aliases, availability and review gaps | `--family {actuator,bearing,belt,cable,cam,chain,clutch,coupling,differential,electric,gear,hinge,hose,link,motor,pneumatic,propeller,rack,shaft,spring,structure,tread,turntable,wheel,worm}`, `--model`, `--connectors`, `--limit` (20), `--output`, `--force` |
| `technic list` | List editable structural recipes | — |
| `technic plan NAME` | Export a structural plan and required-joint contract | `--levels` (2), `--colour` (71), `--accent` (14), `--output` (required), `--force` |

### `vehicle`

| Subcommand | Purpose | Key options |
|---|---|---|
| `vehicle list` | Editable vehicle starting points | — |
| `vehicle wheels [NAME]` | Measured, matched wheel packs | — |
| `vehicle details [NAME]` | List or export dedicated fitting recipes | `--palette` (heritage-racing), `--output`, `--force` |
| `vehicle plan NAME` | Export an editable vehicle plan and its design brief | `--palette`, `--output` (required), `--force` |
| `vehicle check FILE` | Review supported vehicle interfaces in a family profile | `--profile {road,motorcycle,watercraft,aircraft}` (road), `--recipe {touring-motorcycle,harbour-launch,courier-jet}`, `--ground-y`, `--report`, `--limit` (100), `--section`, `--colour` |

## Specialist commands

Hidden from `--help`; their guides say when to use them.

| Command | Purpose | Key arguments and options |
|---|---|---|
| `discover index` | Build a local typed index from the Jev fields and source headers | `--refresh` |
| `discover search KIND QUERY` | Rank eligible references, inspect contents, diversify the shortlist | `KIND {parts,models,submodels}`, `--engine {jev,fts}` (jev), `--limit` (10), `--pool` (60), `--candidates` (500; 0 = all), `--all-families`, `--construction {system,all,technic-structure,mechanism}`, `--min-parts` (2), `--max-parts`, `--max-technic-share` (0.5), `--parent-cap` (2), `--yes`, `--no`, `--report` |
| `discover show ID` | Resolve a stable identity; dependencies and BOM | — |
| `discover parts RESULTS` | Suggest actual parts from constructions in a saved search report | `--limit` (20) |
| `discover prepare ID` | Extract, measure and render one reference card | `--outdir` (required), `--views` (home front right top), `--colour` (7), `--contacts {none,auto,all}` (none), `--refresh` |
| `discover catalog MANIFEST` | Resumable visual catalog from a manifest or saved search | `--outdir` (required), `--views`, `--contacts`, `--refresh`, `--jobs {1,2,3,4}` |
| `discover review ID` | Record the agent's visual review after opening the images | `--catalog`, `--decision {reuse,adapt,technique,reject}`, `--note`, `--viewed-views` (all required) |
| `discover example ID` | Export a reviewed reference as an editable example | `--catalog`, `--output`, `--title`, `--lesson`, `--placement-notes` (required), `--scale {minifigure,microscale,display,unknown}`, `--force` |
| `discover recipe [NAME]` | List or export parameterized construction recipes | `--height`, `--colour`, `--accent`, `--output`, `--force` |
| `spaceship list` / `details` | Compare construction lessons / cockpit, wing, engine and hull lessons across sources | `--limit` (8), `--diversify {source,none}` (source) |
| `spaceship brief ARCHETYPE` | Define spacecraft intent before selecting construction | `{starfighter,freighter,capital-ship}`, `--output`, `--force` |
| `spaceship export NAME` | Export an explicitly selected construction | `--outdir` (required), `--force` |
| `manual prepare FILE` | Extract a source assembly and make attributed step manuals | `--section`, `--outdir` (required), `--title`, `--notes`, `--overview`, `--views` (home back), `--colour` (7), `--no-render`, `--normalize-rotations`, `--repair-bfc-comments`, `--force`, `--max-instances` (2000) |
| `manual review DIRECTORY` | Record the build pages and final preview actually opened | `--images`, `--note` (required) |
| `manual export REFERENCE` | Copy a visually reviewed study and placement plan | `--outdir` (required), `--force` |
| `mechanism list` / `prepare` / `review` / `export` | Same as `manual`, for curated mechanism studies (`prepare --operation` notes; `export` accepts a curated key) | as `manual` |
| `catalog KIND [QUERY]` | Category metadata: `{categories,parts,colours}` | `--category`, `--limit` (12), `--max-size`, `--include-unavailable`, `--measure` |
| `design KIND [NAME]` | `{palettes,details}` | `--palette` (botanical-bookshop), `--output`, `--force` |
| `part-board REFS...` | Render 1–12 candidate parts to an offline board | `--outdir` (required), `--colour` (19), `--timeout` |
| `export-parts-descriptions` | Write the full description TSV snapshot | `--force` |
| `index` | Refresh the installed library index for geometry tools | — |
| `profiles` | List the curated upright stacking profiles used by `on: "ID"` | — |
| `spec [QUERY]` | Search the bundled LDraw specification | `--page`, `--limit` (8) |
| `sections FILE` | List sections with source lines, or print one | `--section` |
| `study FILE` | Inventory hierarchy, counts, reuse and diagnostics | `--report`, `--max-instances`, `--detail`, `--limit` (30) |
| `extract FILE` | Copy an attributed dependency closure | `--section`, `--namespace`, `--output` (required), `--repair-bfc-comments`, `--normalize-rotations`, `--force` |
| `matrix AXIS DEGREES` | `AXIS {x,y,z}` | — |
| `inspect FILE` | Geometry, contacts and occurrence indices (syntax profile) | shared options (`--detail` default full) |
| `bom FILE` | Python physical parts list | `--report`, `--section`, `--colour` |
| `compare-bom FILE` | Exact comparison with a LeoCAD BOM | `--csv` (required), `--report`, `--section`, `--colour` |
| `connectors FILE` | Connector features of one occurrence | `--occurrence` (required), `--limit` (50), `--offset`, `--section`, `--colour` |
| `snap FILE` | Search connector candidates to move an occurrence | `--moving` (required), `--fixed`, `--limit` (5), `--moving-depth`, `--moving-feature`, `--fixed-feature`, `--max-candidates` (100), `--allow-occupied`, `--output`, `--candidate`, `--force` |
| `cad-check FILE` | LeoCAD import/export smoke test | `--timeout`, `--section`, `--colour` |
| `glb FILE` | Semantic GLB export (only on explicit request) | `--output` (required), `--timeout` (180) |

Usage of these: [find-constructions-and-parts](../../find-constructions-and-parts/SKILL.md) (`discover`, `catalog`, `search`), [connectors-and-snapping](../connectors-and-snapping/SKILL.md) (`connectors`, `snap`), [review-and-deliver](../../review-and-deliver/SKILL.md) (`manual`, `finalize`).

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/reference/commands.md](references/docs-agent-reference-commands.md)
