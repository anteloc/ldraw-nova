# Local setup

Run `./setup.sh` from this checkout, including flex synthesis by default.
This follows ldraw-mecha's project-local uv tool layout and
version pins. It installs the tools and library below; LeoCAD and Poppler
remain machine prerequisites. No shell profile or global tool install is changed.

| Component | Version | Location |
| --- | --- | --- |
| uv | 0.9.3 | `bin/uv`, `bin/uvx` |
| ldraw-xray | 0.5.0 | `bin/ldraw-xray` |
| jev-rerank | 0.5.0 | `bin/jev-rerank` |
| ldraw-annotator-nova | 0.5.0 | `bin/ldraw-annotator` |
| lsynth-nova | 0.5.0 | `bin/lsynth` and the Python integration in `.venv/` |
| Model selector viewer | ldraworg-library `a38efc7` | `bin/ldbi-viewer/` |
| Official LDraw library | current `complete.zip` | `data/ldraw/` |
| Nova and test dependencies | `uv.lock` | `.venv/` |

Tool environments live in `bin/uv-tools/`, downloaded Python in `bin/python/`,
and uv's cache in `.cache/uv/`. All are ignored by Git. Only `bin/.gitkeep` is
tracked in `bin/`. The supplied `data/ldraw-info.db` and annotated sources remain
project data; setup does not replace them or download another database.

Setup supports macOS and Linux on arm64/x86_64, including Linux inside WSL.
It needs `curl`, `tar`, `unzip` and network access to the pinned GitHub releases
and the official LDraw library. uv provisions Python 3.12 when needed. Install
Poppler (`pdftotext`) for the specification checks and LeoCAD for rendering.
On headless Linux, provide a display such as Xvfb; on WSL, use WSLg.

Setup reinstalls the four tools from uv's cache, reuses matching uv and an
existing complete library, syncs Nova with `--locked`, then runs Nova doctor,
index, a PDF extraction check, xray doctor, and the model selector index. A failed prerequisite stops
setup; fix it and rerun. Inspect xray's `renders` and `errors` fields before
rendering. To refresh the library, move `data/ldraw` aside and rerun. Extraction
is staged under `.cache` before publication; incomplete existing libraries are
reported rather than overwritten. The upstream `complete.zip` is not pinned,
so a fresh download may contain newer parts.

## Environment and tool discovery

Setup prints exports using the checkout's absolute path. Set them in the shell
that launches your agents; restart the terminal/editor as needed. From the root:

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

Do not add all of `bin/` to PATH: its uv should not shadow your own. Invoke tools
as `bin/ldraw-xray`, `bin/jev-rerank`, `bin/ldraw-annotator` and `bin/lsynth`. Nova resolves
external tools from its own `bin/` first, then PATH. LeoCAD uses `LEOCAD` first,
then `bin/LeoCAD.app/Contents/MacOS/LeoCAD`, `bin/leocad/AppRun`, `bin/leocad`,
PATH and finally `/Applications/LeoCAD.app/Contents/MacOS/LeoCAD`.

Nova's library precedence is `--library`, `LDRAW_DIR`, `LDRAWDIR`, then the
checkout's `data/ldraw` when present. Empty variables are unset. External CLIs
need the exports above or their own explicit flags; Nova's defaults do not set
the parent shell's environment. `LDRAW_SHADOW` can select optional connector
shadows; Nova automatically uses its supplied `data/offLibShadow`, while xray
needs `--shadow data/offLibShadow` to inspect with those same shadows.

Jev requires `TYPESAFE_API_KEY`; local knowledge search and explicit
`discover search --engine fts` work without it. Annotator uses its selected
provider's credentials, independently of Jev. See the [annotation guide](agent/guides/annotate-models.md).
Neither installation nor verification makes paid model calls.

Change tool versions in `scripts/setup-tools.sh`. The selector viewer pin is
in `scripts/setup-viewer.sh`; a changed pin or missing core assets triggers a
fresh download, staged before replacing the installed viewer. For xray and LSynth also update
`pyproject.toml` and regenerate `uv.lock`, keeping the CLI and Nova environment
on the same version. To remove installed files, remove `bin/` contents except
`.gitkeep`, `.venv`, `data/ldraw`, `.cache/uv` and `.cache/ldraw-xray`. Preserve
other project data and any evidence you need.

## Verify changes to setup

The full test suite exercises flexible models; standard setup includes the engine. Select this checkout's library explicitly if your shell has
exports from another project:

```sh
./setup.sh
LDRAW_DIR="$PWD/data/ldraw" .venv/bin/python -m pytest -q
```

Focused setup tests use temporary tool stubs and archives, with no network or
provider calls:

```sh
.venv/bin/python -m pytest tests/test_setup.py tests/test_resources.py tests/test_discovery.py -q
```

LSynth needs no API key or additional environment variable. Its standalone CLI
bundles its configuration and synthesis parts; see `bin/lsynth --help` and
`bin/lsynth --list`. For custom standalone definitions, use `-c FILE` or
`LSYNTH_CONFIG`. `--install-parts` explicitly copies support parts into a library;
setup does not modify the official library this way. Nova
uses the same pinned wheel in `.venv` for Python imports and synthesis. For
direct environment syncing, retain it with
`bin/uv sync --locked --extra test`. LSynth is a required Python dependency
and is retained by ordinary environment syncing.


## Model selector

Setup includes Mecha's model selector, adapted to Nova's construction-reference
workflow. Launch it from the project root:

```sh
./model-selector.sh
# Alternate port, without opening a browser:
./model-selector.sh --port 9000 --no-open
```

The default address is `http://127.0.0.1:8770/`. Search annotated models, sort by
part count, inspect them in 3D, download MPDs, and copy a prompt with the local
model path. See [the selector guide](../model-selector/README.md).

The Python server and pages are tracked in `model-selector/`; downloaded
ldbi/three.js assets and their licence live in ignored `bin/ldbi-viewer/`.
The generated catalog lives in ignored `output/model-selector/` and is rebuilt
by setup and each server start. No Bun, Node, GLB converter, account, or API key
is needed. Library precedence matches Nova (`--library`, `LDRAW_DIR`, `LDRAWDIR`,
then `data/ldraw`); annotated models always come from this repository.

## Optional description snapshot for regex search

Run `./ldraw-agent export-parts-descriptions` to create the Git-ignored
`data/parts-descriptions-full.tsv` if absent. It is a complete UTF-8 snapshot of
`PARTS_DESCRIPTIONS`, not another authoritative source. Existing exports remain
untouched unless `--force` is supplied; refresh after updating the DB.
[Part-information methods](agent/guides/part-information.md) cover regex, SQL,
FTS, Jev, categories and dimensions. Informational part commands require no
installed LDraw library; explicit geometry inspection and model building do.
