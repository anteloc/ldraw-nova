---
name: ldraw-nova
description: 'Builds LEGO models as LDraw MPD files with the ldraw-nova toolkit (./ldraw-agent): write a JSON plan of named placements, build and check it, review the renders, then finalize and deliver ai-NAME.mpd (named after the model, e.g. ai-ford-mustang.mpd) with timing metrics in seconds and hh:mm:ss and visual evidence. Covers the end-to-end workflow, setup (./ldraw-agent doctor, ./setup.sh), LDraw basics (-Y up, 20 LDU stud, 24 LDU brick, 8 LDU plate, colour 16/24), the mandatory silhouette pass that rounds blocky vehicles with SNOT curves, and the mandatory deliverables (metrics.md, xray mosaics, [AI-GENERATED] title, CC-BY-NC licence, AI keywords). Use when asked to design, build, generate or revise a LEGO or LDraw model in this repository, or before running any ./ldraw-agent command (build, review, knowledge, part, search parts, colours, finalize).'
---

# ldraw-nova

Build LEGO models as LDraw MPD files from JSON plans with `./ldraw-agent`. You choose the subject, the parts and what connects to what; the tool computes positions from the parts' real studs and sockets, checks what you built and renders it. Run every command from the repository root.

## The workflow

1. **Brief and timing.** Start recording stage timings *before* planning (see [review-and-deliver](review-and-deliver/SKILL.md)). Write down the subject, scale, silhouette, required features, palette and delivered poses. Run `./ldraw-agent doctor` once; if it reports missing tools, run `./setup.sh`.
2. **Find a construction** for each role the brief needs, and read the best result:

   ```sh
   ./ldraw-agent knowledge search 'side stud panel'
   ./ldraw-agent knowledge show ID
   ```

   Adapt a lesson's principle to your subject; do not copy a whole example. Look up parts for specific needs, not to design piece by piece. See [find-constructions-and-parts](find-constructions-and-parts/SKILL.md).
3. **Write the plan** in `output/TASK/model.plan.json`, or a `generate.py` that writes it ([write-plans](write-plans/SKILL.md)). Build sideways (SNOT) by default ([snot-construction](snot-construction/SKILL.md)). For a Technic brief (beams, pins, axles, gears or mechanisms) use [technic](technic/SKILL.md) instead. A construction preference stated in the brief overrides this default.
4. **Build and fix:**

   ```sh
   ./ldraw-agent build output/TASK/model.plan.json --output output/TASK/ai-NAME.mpd
   ./ldraw-agent review output/TASK/model.plan.json --outdir output/TASK/review --draft
   ```

   `build` prints a short summary: errors with the placements they concern, warnings grouped by code, and the next step. `ai-NAME.mpd` is named after the model: `ai-` plus lowercase words joined by hyphens, e.g. `ai-ford-mustang.mpd`. A failing build leaves `ai-NAME.draft.mpd`; `review --draft` renders it so you can see the problem. Fix the first error and rebuild ([fix-build-errors](fix-build-errors/SKILL.md)).
5. **Review** with the same command once `build` passes; `--draft` only matters while checks fail. Open the previews, compare them with the brief, and look closely at every placement a warning names.
6. **Soften vehicle silhouettes (mandatory for every vehicle: car, truck, plane, spacecraft, ship…).** Inspect the outline; where the subject is rounded, replace blocky straight-edged bricks with curves mounted by SNOT, then review again. The procedure is in [design-models](design-models/SKILL.md).
7. **Finalize and deliver** only the three mandatory items below ([review-and-deliver](review-and-deliver/SKILL.md)).

Keep all edits in one ordinary JSON plan or in a generator that emits it.

## A complete small example

Save as `output/stack.plan.json`:

```json
{
  "version": 1,
  "author": "Your name",
  "sections": [{
    "name": "stack.ldr",
    "description": "A blue plate on a red brick",
    "steps": [
      [{"id": "base", "ref": "3003.dat", "colour": 4, "at": [0, 0, 0]}],
      [{"id": "top", "ref": "3022.dat", "colour": 1, "on": "base"}]
    ]
  }]
}
```

```sh
./ldraw-agent build output/stack.plan.json
./ldraw-agent review output/stack.plan.json
```

- `build` writes `output/stack.mpd` and prints a summary. A failing build writes `output/stack.draft.mpd` instead and keeps any earlier `stack.mpd`.
- `review` rebuilds the plan and puts checks, a frozen model copy, BOMs and previews in `output/stack-review/`. Rerunning it on an unchanged plan reuses the bundle; a changed plan replaces it. `--output` on `build` and `--outdir` on `review` override the defaults.
- The plate's body is 8 LDU high, so `on` puts its origin at Y=-8; it does not add stud height. For parts outside the curated stacking profiles, and for any sideways part, use a connector seat: `"on": {"to": "base", "face": "-Y", "stud": 0}`.

These filenames are working outputs. For delivery, build with `--output output/TASK/ai-NAME.mpd`, named after the model (e.g. `ai-wanderer.mpd`).

## Iterate with scoped evidence

- Build the smallest uncertain interface first.
- `review PLAN --draft` renders a failing model; `--no-render` runs checks only; `--section NAME` checks a local dependency closure. A section check excludes parent and sibling interactions.
- Repair the first failed prerequisite. After two unsuccessful local corrections, inspect the isolated interface and change the approach or the available space.
- Finish with a whole-model `review` and open its views, including hidden joins and the underside.
- Use named placement IDs. `controls/pump` selects a physical part through its parent placement; repeated IDs expand to `id-0`, `id-1`. References and paths are relative to their declaring plan. A whole module path does not identify one mating part.

## Mandatory model deliverables

For **each model**, in its own `output/TASK/` directory:

- **Metrics:** total generation time and timing for every stage (planning, research, authoring, tooling execution, validation, repair, rendering, visual review, finalization), each duration in seconds and as `hh:mm:ss`, e.g. `4523 s (01:15:23)`. Include agent/model thinking time where telemetry exposes it; mark unavailable measurements explicitly and never invent them.
- **Visual evidence:** every xray board's `xray/<board>/mosaic.png`, plus stills and previews from different perspectives. Open the images before delivery.
- **Generated model:** `ai-NAME.mpd`, named after the model with the `ai-` prefix (`ai-wanderer.mpd`, `ai-ford-mustang.mpd`, `ai-mecha-invader.mpd`); `finalize` refuses other names, including the generic `ai-generated.mpd`. Prefix the root section's `description` (the internal main-model title) with `[AI-GENERATED] ` exactly once. The main model and every AI-generated submodel header need `0 Author:` with every contributing agent/model name and version, `0 !LICENSE CC-BY-NC`, immediately followed by `0 Allows sharing and adapting for noncommercial purposes only, with attribution to the AI that authored the current model.`, and `0 !KEYWORDS AI, AI-generated`. `./ldraw-agent finalize` writes the comment and keywords. Preserve attribution and licences in imported third-party sections.

Plans, generators, logs, manifests, BOMs, check reports and review bundles are internal working files. Do not produce extra exports (`.blend`, `.glb`, videos, source packages, README handoffs) unless the user asks.

## LDraw facts

- -Y is up. A stud is 20 LDU wide; a brick body is 24 LDU tall and a plate body 8.
- Most parts have their origin at the top of the body, centred. `./ldraw-agent part CODE` states where it is and lists the studs and sockets on each face.
- Stack by body height, never by bounding box: bounds include the studs.
- Use proper rotations only; never scale or mirror a part. `orient` and `on` produce rotations for you.
- Colour 16 takes the colour of the placement above it, so an ancestor must set a real colour. Colour 24 is for edges only.
- Never read library `.dat` files; `part`, `search parts` and `dimensions` answer part questions.

## Commands

| Command | Use |
|---|---|
| `knowledge search QUERY`, `knowledge show ID` | find and read construction lessons and guide sections |
| `search parts 'slope 45 2 x 2'` | find part numbers by description |
| `part CODE` | origin, body size, studs and sockets by face |
| `build PLAN` | build and check; `--quiet` prints one line, `--report FILE` saves the complete report |
| `review PLAN --outdir DIR` | build, check, render previews and compare BOMs; `--draft` renders a failing model |
| `colours QUERY` | colour codes by name |
| `finalize MPD` | add the licence comment and AI keywords to generated sections |

Every command and flag: [reference](reference/SKILL.md).

## Setup

`./setup.sh` installs everything project-locally (no shell profile or global install is changed): uv, `bin/ldraw-xray`, `bin/jev-rerank`, `bin/ldraw-annotator`, `bin/lsynth` and its Python integration, the model selector viewer, the official LDraw library in `data/ldraw/`, and `.venv/`. LeoCAD (rendering) and Poppler (`pdftotext`) are machine prerequisites. It supports macOS and Linux (arm64/x86_64, including WSL) and needs `curl`, `tar`, `unzip` and network access. On headless Linux provide a display such as Xvfb; on WSL use WSLg. A failed prerequisite stops setup: fix it and rerun.

Set these in the shell that launches agents (setup prints them with absolute paths):

```sh
export LDRAW_DIR="$PWD/data/ldraw"
export LDRAWDIR="$LDRAW_DIR"
export LDRAW_XRAY_CACHE="$PWD/.cache/ldraw-xray"
export LDRAW_ANNOTATOR_DB="$PWD/data/ldraw-info.db"
# Set LEOCAD if the renderer is not on PATH or in /Applications/LeoCAD.app:
# export LEOCAD=/absolute/path/to/LeoCAD
# Optional semantic search credentials (never commit or print their values):
# export TYPESAFE_API_KEY=...
```

- Do not add all of `bin/` to PATH. Invoke tools as `bin/ldraw-xray`, `bin/jev-rerank`, `bin/ldraw-annotator`, `bin/lsynth`. Nova resolves external tools from its own `bin/` first, then PATH.
- Library precedence: `--library`, `LDRAW_DIR`, `LDRAWDIR`, then `data/ldraw`. Nova uses `data/offLibShadow` connector shadows automatically; xray needs `--shadow data/offLibShadow` to use the same ones.
- `TYPESAFE_API_KEY` is only for Jev semantic search; local `knowledge search` and `discover search --engine fts` work without it.
- `./ldraw-agent export-parts-descriptions` creates the optional `data/parts-descriptions-full.tsv` for regex part search.
- `./model-selector.sh` (default `http://127.0.0.1:8770/`) browses annotated reference models in 3D.

## Which subskill

| Task | Subskill |
|---|---|
| Decide what the model looks like; subject-specific advice (aircraft, spacecraft, vehicles, buildings, animals); the mandatory vehicle silhouette pass | [design-models](design-models/SKILL.md) |
| Find a construction lesson, a part number or a part's studs | [find-constructions-and-parts](find-constructions-and-parts/SKILL.md) |
| Write or edit the plan, place parts, split into modules | [write-plans](write-plans/SKILL.md) |
| Sideways surfaces (the default) | [snot-construction](snot-construction/SKILL.md) |
| Beams, pins, axles, gears, mechanisms | [technic](technic/SKILL.md) |
| Hoses, cables, chains, treads | [flexible-parts](flexible-parts/SKILL.md) |
| A build failed or warned | [fix-build-errors](fix-build-errors/SKILL.md) |
| Look at renders, xray, finalize and hand over | [review-and-deliver](review-and-deliver/SKILL.md) |
| Exact commands, flags, output contracts, LDraw format | [reference](reference/SKILL.md) |

## Subskills

Read the one that matches your task:

- [write-plans](write-plans/SKILL.md): Writes model.plan.json (or a generate.py that emits it): sections, steps and placements with id, ref, colour and one position mode (at, on, on {to, face, stud, socket}, under, join, attach), plus orient, yaw, roll, repeat, mirror, offset_studs, includes, module anchors and contracts. Includes the construction recipes (small checked plans for every placement mode) and how to split large models into modules with their own origins. Use when authoring or editing a plan, choosing how to position a part, stacking bricks and plates, repeating or mirroring structure, or organising a model into submodel sections.
- [snot-construction](snot-construction/SKILL.md): Builds sideways (SNOT, studs not on top), the default construction for new models: choose a support with side studs (87087, 30414, 52107, 67329, 99780, 4070, brackets, clips), seat parts and whole upright-built panel modules on its studs with on {to, face, stud, socket, socket_at, roll}, hang parts underneath with under, round off blocky edges with curved parts on side studs (naming the socket of curved slopes), and cover exposed side studs. Includes the SNOT interface table of 43 parts with stud faces and indices, and the parrot head worked reference. Use when a surface must face outward, when building hull or body skins, or when fixing appearance.exposed_side_studs.
- [technic](technic/SKILL.md): Builds Technic models (beams, liftarms, pins, axles, gears, wheels) by naming ports: frame first, then shafts, gears and links, wheels, cladding. Covers technic parts, technic gears, part ports (hole-N, grip-N, shaft), on {to, hole, pin, side}, join {to, holes, side, pins}, the technic.* build checks, mechanism contracts and good mechanical practice. Use when a brief involves beams, pins, axles, gears, chassis or any mechanism; this replaces the SNOT default for Technic briefs.
- [flexible-parts](flexible-parts/SKILL.md): Builds and repairs mounted flexible parts with LSynth: hoses, pneumatic tubes, cables, bands, chains and treads, routed between named rigid fittings or wrapped around mounted wheels. Covers flex guide TYPE, inline flex placements in plan steps, route kinds, flex diagnostics and local repairs, generated flexible assets, and worked references (flex basics, pneumatic press with three hoses, retained chain drive, workshop machine). Use when a model needs a hose, cable, chain, belt or tread, or when fixing a flex.* diagnostic.
- [design-models](design-models/SKILL.md): Designs recognizable, varied models from a brief: silhouette and defining parts first, dedicated parts over substitutes, build from the inside out, then revise from the renders. Covers architecture, vehicles, spacecraft, animals, objects and interiors, with subject-specific subskills, plus the mandatory silhouette pass for every vehicle: inspect the outline (ldraw-xray render and mosaic, stud map) and round blocky straight-edged bricks with SNOT curves (curved-top bricks on brackets, triple-curved wedges, curved slopes on side studs, inverted curves) where the subject is rounded. Use when planning what a model should look like and how its masses, palette and modules are laid out, before writing the plan.
- [find-constructions-and-parts](find-constructions-and-parts/SKILL.md): Research before and during planning: find construction lessons with knowledge search and knowledge show, browse reviewed real-set examples (examples --family, --details), inspect a reference's evidence and adapt its principle, and answer specific part questions (search parts, part CODE, dimensions, SQL, regex, lexical and semantic ranking, categories) without reading library .dat files. Use when choosing how to build a role in the brief, looking up a part number or its studs, sockets and size, or checking whether a part exists.
- [fix-build-errors](fix-build-errors/SKILL.md): Reads and acts on build, review and validate diagnostics: checks_passed, errors with their placement paths, warnings by code, next. Lists the fix for each code (plan.schema, plan.authoring, assembly.body_overlap, assembly.duplicate, assembly.floating_group, assembly.became_floating, appearance.deep_overlap, appearance.exposed_side_studs, appearance.glass_obstructed, part.alias_or_internal, technic.*, coverage.*) and what validation does and does not cover. Use when a build fails or prints warnings, or when deciding whether a geometry report proves anything.
- [review-and-deliver](review-and-deliver/SKILL.md): Reviews a built model visually and delivers it: review PLAN --outdir (BOM, previews, --views, --draft), opening and comparing images with the brief, the mandatory before/after silhouette boards for vehicles, rendering modules alone or in place with bin/ldraw-xray (boards, stud maps, cutaways, mosaic.png), then the delivery rules: metrics.md timing for every stage in seconds and hh:mm:ss, visual evidence, ai-NAME.mpd named after the model (ai- prefix, e.g. ai-ford-mustang.mpd) with [AI-GENERATED] title, Author, CC-BY-NC licence and keywords via finalize, and final review of the delivered bytes. Use after a build passes, when inspecting a warning in the render, and before handing a model to the user.
- [reference](reference/SKILL.md): Reference for the ldraw-nova command line and file formats: every ./ldraw-agent command and option, CLI output and artifact contracts, LDraw line records, transforms, colours and MPD structure, and connector evidence and snapping. Use when looking up an exact command, flag, exit code, output file or LDraw format detail.

## Source docs

Verbatim copies, for details not covered above:

- [AGENTS.md](references/AGENTS.md)
- [docs/agent/guides/build-model.md](references/docs-agent-guides-build-model.md)
- [docs/setup.md](references/docs-setup.md)
