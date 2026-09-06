# LDraw generation tools

Generate MPD assemblies using real LDraw parts, inspect their geometry and connections, and check the result with Python and LeoCAD.

Start an agent with [instructions.md](instructions.md). Read the [tool reference](docs/agent/tooling.md), [LDraw rules](docs/agent/ldraw-reference.md), and [geometry guide](docs/agent/geometry.md). The mandatory source is [docs/ldraw-specs.pdf](docs/ldraw-specs.pdf); the [source map](docs/agent/specification-map.md) links rules to its pages.

Requires Python 3.12+, Poppler's `pdftotext`, and the supplied LDraw library. LeoCAD is required for visual review. `mpd2glb.sh` is optional for Blender inspection. The setup uses a project virtual environment and caches; it does not change the official library or global application settings.

```sh
./setup.sh
./ldraw-agent build examples/bridge.plan.json --output output/bridge.mpd --report output/bridge.build.json
./ldraw-agent validate output/bridge.mpd --geometry --strict
./check-model.sh output/bridge.mpd
./ldraw-agent render output/bridge.mpd --outdir output/bridge-review
.venv/bin/python -m pytest -q
```

Open the PNGs for visual review. The checked source is also included as [examples/bridge.mpd](examples/bridge.mpd). The example intentionally demonstrates nested submodels, inherited colours, rotation, steps, and stud stacking with only five parts. Use `--force` to regenerate an existing example. For reproducible transitive dependencies, use `uv sync --locked --extra test`; `uv.lock` is included. `setup.sh` uses it when `uv` is installed, with pip as a fallback. On macOS, install Poppler with `brew install poppler` if needed.

Defaults resolve relative to this repository: `../ldraw-lib/ldraw` and `../ldraw-lib/models-annotated`. Override with `LDRAW_DIR`, `MODELS_DIR`, or the CLI's `--library` / `--models` options before the command.

The implementation reuses [pyldraw3](https://github.com/hbmartin/pyldraw3) for parsing, writing, geometry expansion, BOMs, and connector inference; NumPy for matrix/geometry checks; JSON Schema for generation plans; the existing SQLite model index for retrieval; Poppler for the supplied PDF; and LeoCAD for renders. Local validation fills gaps needed by the documented assembly workflow. These are checks and review evidence, not a proof of physical buildability. See the explicit [coverage and repair guide](docs/agent/validation.md).
