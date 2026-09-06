# Goal: Create Tooling and Resources for Generative LDraw Modelling

From the **LDraw language specification**, located at `docs/ldraw-specs.pdf`, create the required python tooling and resources like e.g. **agentic** reference docs, required for an agent to **generate geometrically, sintactically and semantically correct LDraw models**, expressed as `.mpd` source files.

At the end, rewrite the `./instructions.md`, in order to become a **high-quality prompt** for other agents, even low-end ones, to be instructed into how to generate **new LDraw models** by means of the mentioned **tooling and reference docs**.

## Resources

- `./docs/ldraw-specs.pdf` (MANDATORY): the **full LDraw language specification**.
- `../ldraw-lib/models-annotated/`: annotated Official Model Repository (OMR) models, in `.mpd` format.
- `../ldraw-lib/ldraw/`: official LDraw library.
- `../ldraw-lib/ldraw/parts/`: library parts, in `.dat` format.

## Tooling

You are free to **install** any required **python packages** and **extra tooling** in order to fulfill this task: **DO NOT** reinvent the wheel!

Currently available tooling:

- `leocad`: a CLI tool for several operations to be performed on a model or part, like e.g. get its BOM or render an image for the model. Run `leocad --help` for options.
    * `leocad -l ../ldraw-lib/ldraw -csv parts-bom.csv <model-or-part.ext>`: provides a parts BOM for the given model or part, see `./106-1-bom-example.csv`
    * `leocad -l ../ldraw-lib/ldraw -i rendered-model.png --viewpoint home <model-or-part.ext>`: renders the given viewpoint for the model or part, see `./106-1-rendered-example.png`
    * Use the other options at your discretion.
- `./prepare-glb.sh`: Convert a `.mpd`, `.dat` or `.ldr` model or part file to a `.glb` model with **semantic annotations**. Use it if in need of **deeply inspecting**, via **Blender MCP**, any model or part.
