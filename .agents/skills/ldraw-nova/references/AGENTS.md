# Working in ldraw-nova

Build LEGO models as LDraw MPD files from JSON plans with `./ldraw-agent`. You choose the subject, the parts and what connects to what; the tool computes positions from the parts' real studs and sockets and checks what you built. Run commands from the repository root.

## Build a model

1. **Brief and timing.** Start recording stage timings before planning (see [delivery requirements](docs/agent/cards/review.md#deliver)). Write down the subject, scale, silhouette, required features and palette. Run `./ldraw-agent doctor` once; if it reports missing tools, run `./setup.sh`.
2. **Find a construction** for each role the brief needs, and read the best result:

   ```sh
   ./ldraw-agent knowledge search 'side stud panel'
   ./ldraw-agent knowledge show ID
   ```

   Adapt a lesson's principle to your subject; do not copy a whole example. Look up parts for specific needs, not to design piece by piece.
3. **Write the plan** in `output/TASK/model.plan.json`, or a `generate.py` that writes it. Read the [plan card](docs/agent/cards/plan.md). Build sideways (SNOT) by default: read the [SNOT card](docs/agent/cards/snot.md). For a Technic brief (beams, pins, axles, gears or mechanisms) read the [Technic card](docs/agent/cards/technic.md) instead. A construction preference stated in the brief overrides this default.
4. **Build and fix:**

   ```sh
   ./ldraw-agent build output/TASK/model.plan.json --output output/TASK/ai-NAME.mpd
   ./ldraw-agent review output/TASK/model.plan.json --outdir output/TASK/review --draft
   ```

   `build` prints a short summary: errors with the placements they concern, warnings grouped by code, and the next step. `ai-NAME.mpd` names the model after its subject: `ai-` plus lowercase words joined by hyphens, e.g. `ai-ford-mustang.mpd`. A failing build leaves `ai-NAME.draft.mpd`; `review --draft` renders it so you can see the problem. Read the [checks card](docs/agent/cards/checks.md) to act on a diagnostic. Fix the first error and rebuild.
5. **Review** with the same command once `build` passes; `--draft` only matters while checks fail. Open the previews and compare them with the brief, and look closely at every placement a warning names. The [review card](docs/agent/cards/review.md) explains how.
6. **Soften vehicle silhouettes (mandatory for every vehicle: car, truck, plane, spacecraft, ship…).** Inspect the outline; where the subject is rounded, replace blocky straight-edged bricks with curves mounted by SNOT: [silhouette pass](docs/agent/guides/design-models.md#soften-blocky-vehicle-silhouettes).
7. **Finalize and deliver** only the three mandatory items below for each model. Follow the [review card](docs/agent/cards/review.md#deliver) to finalize metadata, check the exact delivered bytes and link every required artifact.

## Mandatory model deliverables

- **Metrics:** total generation time and timing for every stage, including planning, research, authoring, tooling execution, validation, repair, rendering, visual review and finalization. Give every duration in seconds and as `hh:mm:ss`, e.g. `4523 s (01:15:23)`. Include agent/model thinking time where telemetry exposes it; explicitly mark unavailable measurements and never invent them.
- **Visual evidence:** every xray board's `xray/<board>/mosaic.png`, plus stills and previews from different perspectives. Open the images before delivery.
- **Generated model:** `ai-NAME.mpd`, named after the model with the `ai-` prefix (`ai-wanderer.mpd`, `ai-ford-mustang.mpd`, `ai-mecha-invader.mpd`); `finalize` refuses other names. Prefix the internal main-model title (the root section's `description`) with `[AI-GENERATED] ` exactly once. In the main model and every AI-generated submodel's header, include `0 Author:` with the name and version of every contributing agent/model, `0 !LICENSE CC-BY-NC`, immediately followed by `0 Allows sharing and adapting for noncommercial purposes only, with attribution to the AI that authored the current model.`, and `0 !KEYWORDS AI, AI-generated`. Preserve attribution and licences in imported third-party sections.

Plans, generators, logs, manifests, BOMs, check reports and review bundles are internal working files, not additional user deliverables. Do not produce extra exports or deliverables unless the user requests them: no `.blend`, `.glb`, videos, source packages or README handoffs by default. Each model gets its own directory.

## LDraw facts

- -Y is up. A stud is 20 LDU wide; a brick body is 24 LDU tall and a plate body 8.
- Most parts have their origin at the top of the body, centred. `./ldraw-agent part CODE` states where it is and lists the studs and sockets on each face.
- Stack by body height, never by bounding box: bounds include the studs.
- Use proper rotations only; never scale or mirror a part. `orient` and `on` produce rotations for you.
- Colour 16 takes the colour of the placement above it, so an ancestor must set a real colour. Colour 24 is for edges only.

## Commands

| Command | Use |
|---|---|
| `knowledge search QUERY`, `knowledge show ID` | find and read construction lessons and guide sections |
| `search parts 'slope 45 2 x 2'` | find part numbers by description |
| `part CODE` | origin, body size, studs and sockets by face |
| `build PLAN` | build and check; `--quiet` prints one line, `--report FILE` saves the complete report |
| `review PLAN --outdir DIR` | build, check, render previews and compare BOMs; `--draft` renders a failing model |
| `colours QUERY` | colour codes by name |

Never read library `.dat` files; `part`, `search parts` and `dimensions` answer part questions.

## Guides for specific subjects

Use these only when the brief needs them:

| Subject | Guide |
|---|---|
| Vehicles, spacecraft, buildings, animals | [Design models](docs/agent/guides/design-models.md) |
| Aircraft | [Aircraft](docs/agent/guides/aircraft.md) |
| Technic frames and mechanisms | [Technic card](docs/agent/cards/technic.md), then [Technic guide](docs/agent/guides/technic.md) for construction patterns |
| Hoses, cables, chains and treads | [Flex authoring](docs/agent/guides/flex.md) |
| Large models in modules | [Compose modules](docs/agent/guides/compose-modules.md) |
| Parts by role or appearance | [Part information](docs/agent/guides/part-information.md) |
| Learning from real sets | [Find references](docs/agent/guides/find-references.md), [xray](docs/agent/guides/xray.md) |
| Every plan field and command | [Plans](docs/agent/reference/plans.md), [commands](docs/agent/reference/commands.md), [CLI contracts](docs/agent/reference/cli.md), [SNOT interfaces](docs/agent/reference/snot-interfaces.md) |

## Changing the toolkit or knowledge base

See [docs/maintainers](docs/maintainers/README.md). Changes are judged by the [benchmark](bench/README.md) of what agents build, not by passing tests alone.
