# Goal: Create Tooling and Resources for Generative LDraw Modelling

From the **LDraw language specification**, located at `docs/ldraw-specs.pdf`, create the required python tooling and resources like e.g. **agentic** reference docs, required for an agent to **generate geometrically, sintactically and semantically correct LDraw models**, expressed as `.mpd` source files.

At the end, rewrite the `./instructions.md`, in order to become a **high-quality prompt** for other agents, even low-end ones, to be instructed into how to generate **new LDraw models** by means of the mentioned **tooling and reference docs**.

## Resources

- `./docs/ldraw-specs.pdf` (MANDATORY): the **full LDraw language specification**.
- `data/models-annotated/`: annotated Official Model Repository (OMR) models, in `.mpd` format.
- `data/ldraw-info.db`: searchable part, model and submodel descriptions.
- `data/categories/`: descriptive part and colour catalog.
- `data/offLibShadow/`: connector metadata.
- `LDRAW_DIR`, falling back to `LDRAWDIR` when unset or empty: official LDraw parts library; `.dat` parts are under its `parts/` directory.

## Tooling

You are free to **install** any required **python packages** and **extra tooling** in order to fulfill this task: **DO NOT** reinvent the wheel!

Currently available tooling:

- `leocad`: a CLI tool for several operations to be performed on a model or part, like e.g. get its BOM or render an image for the model. Run `leocad --help` for options.
    * `leocad -l "${LDRAW_DIR:-$LDRAWDIR}" -csv parts-bom.csv <model-or-part.ext>`: provides a parts BOM for the given model or part.
    * `leocad -l "${LDRAW_DIR:-$LDRAWDIR}" -i rendered-model.png --viewpoint home <model-or-part.ext>`: renders the given viewpoint for the model or part.
    * Use the other options at your discretion.
- `jev-rerank`: globally available semantic search CLI. Query `data/ldraw-info.db`; check service availability and use the [FTS fallback](../docs/agent/reference-discovery.md#check-jev-availability-before-searching) when unavailable.
- `mpd2glb.sh`: globally available semantic GLB converter. The repository's `./prepare-glb.sh` wraps it to export `.mpd`, `.dat` or `.ldr` sources with part descriptions.
- `ldraw-render-steps.sh`: globally available step renderer. Read its help with no arguments. Use consecutive images from different views to study reference constructions, inspect unfinished submodels, detect defects and improve their design. See the [build-page workflow](../docs/agent/build-manuals.md).
