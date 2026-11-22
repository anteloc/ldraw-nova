---
name: reference
description: 'Reference for the ldraw-nova command line and file formats: every ./ldraw-agent command and option, CLI output and artifact contracts, LDraw line records, transforms, colours and MPD structure, and connector evidence and snapping. Use when looking up an exact command, flag, exit code, output file or LDraw format detail.'
---

# Reference

Look up exact details of the ldraw-nova command line and the LDraw format. Task skills tell you what to do; these pages tell you the precise flag, artifact, exit code or format rule when you need it.

| Need | Subskill |
|---|---|
| A command's flags, defaults and global options (`--library`, `--shadow`) | [commands](commands/SKILL.md) |
| What `build`/`review` write, exit codes, scripting, manuals, discovery and the Jev availability check | [cli-contracts](cli-contracts/SKILL.md) |
| Line types, matrices, colours 16/24, MPD blocks, BFC, headers, spec page numbers | [ldraw-format](ldraw-format/SKILL.md) |
| Connector IDs, `connectors` and `snap`, collision result meanings, wheel packs | [connectors-and-snapping](connectors-and-snapping/SKILL.md) |

Exit codes everywhere: **0** selected checks passed, **1** a check failed, **2** input/dependency/execution failure. Read `diagnostics`, `coverage` and `physical_validity` (always `not_proven`), not only the exit code.

Other references live with their tasks: plan fields in [write-plans](../write-plans/SKILL.md), SNOT stud tables in [snot-construction](../snot-construction/SKILL.md), Technic ports and contracts in [ports-and-contracts](../technic/ports-and-contracts/SKILL.md), flex fields in [flexible-parts](../flexible-parts/SKILL.md), diagnostic codes in [fix-build-errors](../fix-build-errors/SKILL.md).

## Subskills

Read the one that matches your task:

- [commands](commands/SKILL.md): Every ./ldraw-agent command with its options, generated from the argument parser: core commands (flex, review, examples, knowledge, technic, vehicle, doctor, search, dimensions, part, colours, finalize, build, validate, render) and specialist commands (discover, spaceship, manual, mechanism, catalog, design, part-board, index, spec, sections, study, extract, matrix, profiles, inspect, bom, compare-bom, snap, connectors, cad-check, glb). Use when looking up a command's exact flags or global options such as --library and --shadow.
- [cli-contracts](cli-contracts/SKILL.md): CLI and output contracts: setup, review artifacts and failure behaviour, construction manuals (manual prepare/export), reviewed real-set submodels, mechanism studies, discovery and inspection, studying and extracting complex references, generating from a plan, individual checks and exports, the automation contract (JSON output, exit codes), knowledge retrieval and registering examples. Use when scripting the toolkit, interpreting a command's output files or exit codes, or using a specialist workflow beyond build and review.
- [ldraw-format](ldraw-format/SKILL.md): LDraw records, transforms and specification sources: line types 0-5 syntax, transform matrices and coordinates, colours, MPD structure (0 FILE, 0 NOFILE), BFC and other metadata, dimensions and origins, and where each rule is in the bundled specification PDF. Use when reading or checking an .ldr or .mpd file by hand or reasoning about rotations, colours or MPD sections.
- [connectors-and-snapping](connectors-and-snapping/SKILL.md): Connector evidence and snapping: LDCad shadow-library connectors loaded through pyldraw3, discovering and previewing connector IDs and occupancy, snap and connectors commands, applying a snap to an MPD copy, interpreting collisions, and measured wheel assemblies. Use when a placement needs a connector that on, under or join do not cover, or when diagnosing why parts do or do not connect.
