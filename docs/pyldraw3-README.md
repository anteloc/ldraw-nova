# pyldraw3

[![PyPI](https://img.shields.io/pypi/v/pyldraw3.svg)](https://pypi.org/project/pyldraw3/)
[![Lint and Test](https://github.com/hbmartin/pyldraw3/actions/workflows/lint-test.yml/badge.svg)](https://github.com/hbmartin/pyldraw3/actions/workflows/lint-test.yml)
[![Codecov](https://codecov.io/gh/hbmartin/pyldraw3/branch/main/graph/badge.svg)](https://codecov.io/gh/hbmartin/pyldraw3)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Formatter: Ruff](https://img.shields.io/badge/formatter-ruff-46a0d9.svg)](https://github.com/astral-sh/ruff)

A modern Python package for creating and manipulating LDraw format files - the standard for CAD applications that create LEGO models. It is a drop-in replacement for the unmaintained `pyldraw` library.

> ### 🖥️ [pyldraw3-tui](https://github.com/hbmartin/pyldraw3-tui)
>
> Prefer an interactive interface? **[pyldraw3-tui](https://github.com/hbmartin/pyldraw3-tui)** is a companion terminal UI — built on [Textual](https://textual.textualize.io/) and pyldraw3 — for browsing the LDraw parts catalog and inspecting `.ldr`/`.mpd` model files without writing code: look up part codes, explore categories and minifig sections, inspect part metadata with colour swatches and sub-part trees, and open models to view pieces, statistics, and bill-of-materials data (read-only, it never modifies your files).

## Features

- 🧱 **Complete LDraw Support**: Full compatibility with the LDraw standard format
- 🐍 **Pythonic API**: Import LEGO parts directly as Python modules
- 📦 **Dynamic Library Generation**: Automatically generate Python modules from LDraw libraries
- 🧭 **Building Instructions**: Typed STEP/ROTSTEP, LPub3D semantics, validation, manifests, and MPD/LDR snapshots
- 🔎 **Reliable Inspection**: Tolerant loading, structured diagnostics, exact geometry, provenance, and one-pass analysis
- 🔗 **LDCad/Studio Connectivity**: Typed metadata coverage, strict contacts, stable IDs, and occurrence multigraphs
- 📜 **Comprehensive Guide**: Jump into the quick start below, or read the [published documentation](https://hbmartin.github.io/pyldraw3/)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Setup](#setup)
  - [Examples](#examples)
  - [Basic Usage](#basic-usage)
  - [Reading and Writing Model Files](#reading-and-writing-model-files)
  - [Reliable Loading and Inspection](#reliable-loading-and-inspection)
  - [Building Instructions](#building-instructions)
  - [Part Geometry Queries](#part-geometry-queries)
  - [IDE Autocompletion and Type Checking](#ide-autocompletion-and-type-checking)
- [Requirements](#requirements)
- [Agent Skill](#agent-skill)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
  - [Development Commands](#development-commands)
  - [Documentation Site](#documentation-site)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [Key Classes](#key-classes)
- [Contributing](#contributing)
- [License](#license)
- [Trademarks](#trademarks)
- [Credits](#credits)


## Quick Start

### Installation

```bash
uv add pyldraw3
```

### Setup

Activate your virtual environment and set up the LDraw library - this will download the LDraw library and create the parts classes:

```bash
source .venv/bin/activate
ldraw download --yes
ldraw generate --yes
```

By default `ldraw download` fetches the `complete` LDraw release (~80 MB, everything LDraw publishes). To pin a specific dated release instead - useful for reproducible builds or a smaller download - pass `--version`, e.g. `ldraw download --version 2018-02 --yes`. Each downloaded release is cached separately, and `ldraw generate` builds `ldraw.library.*` from whichever release is currently configured (see [Configuration](#configuration)).

### Examples

Check the `examples/` directory for sample scripts demonstrating various features:

```bash
# Run an example
python examples/figures.py > my_model.ldr
```

Each example writes LDraw text to stdout; see the [Examples documentation](https://hbmartin.github.io/pyldraw3/examples/) for a description of what every script demonstrates.

### Basic Usage

This package allows users to create LDraw scene descriptions using `Piece`s which are `Part`s that have a specific position and orientation. `Piece.to_ldraw()` and `Group.to_ldraw()` produce LDraw file content; `str(piece)` and `str(group)` delegate to those serializers:

```python
from ldraw.library.colours import Light_Grey
from ldraw.library.parts.bricks import Brick1X2WithClassicSpaceLogoPattern
from ldraw.pieces import Group, Piece
from ldraw.geometry import Vector, Identity

# Create a simple model
model = Group()
Piece(
    Light_Grey,
    Vector(-10, -32, -90),
    Identity(),
    Brick1X2WithClassicSpaceLogoPattern,
    model,
)

with open("my_model.ldr", "w") as ldr_file:
    print(model, file=ldr_file)
```

`ldraw.library.*` is generated by `ldraw generate` and gives you every part as an importable, autocompletable Python name (as used above). If you'd rather look a part up by its catalog description or LDraw code at runtime - for example when the part name isn't known until your program runs - load the parts catalog directly instead:

```python
from pathlib import Path

from ldraw.config import Config
from ldraw.parts import Parts

config = Config.load()
parts = Parts(Path(config.ldraw_library_path) / "ldraw" / "parts.lst")
cowboy_hat = parts.get_entry_by_description("Minifig Hat Cowboy").code  # -> "3629"
head = parts.get_entry_by_description("Minifig Head with Solid Stud").code  # -> "3626a"
brick1x1 = parts.get_entry_by_description("Brick  1 x  1").code  # -> "3005"
```

Both `cowboy_hat` and `Brick1X2WithClassicSpaceLogoPattern` are just LDraw part code strings, so either style can be passed as the `part` argument to `Piece`.

For new code, `Piece.place` offers a keyword-first constructor with sensible defaults (main colour, origin position, identity rotation):

```python
from ldraw import Piece

piece = Piece.place("3005", colour=4)  # red 1x1 brick at the origin
```

The core construction types are all importable from the top-level package:
`Model`, `Piece`, `Group`, `Person`, `Colour`, `Vector`, `Matrix`,
`Identity`, `Parts`, and the read/validate/BOM helpers. Deep imports
(`from ldraw.pieces import Piece`) keep working.

### Building Models Programmatically

`Model` bridges piece construction and file I/O — build, query, and save:

```python
from ldraw import Group, Model, Person, Piece, Vector

model = Model.from_pieces(
    [Piece.place("3001", colour=4)],
    name="scene.ldr",
    description="A scene",
    author="you",
)

# Figures flow in through their group
group = Group()
figure = Person(position=Vector(0, -48, 0), group=group)
figure.head(colour=14)
figure.torso(colour=4)
model.add_group(group)

# Submodels: registers the section and returns the referencing piece
wheels = Model.from_pieces([Piece.place("3005", colour=0)], name="wheels.ldr")
model.add_submodel(wheels, position=Vector(0, -24, 0))

model.find_pieces(colour=4)  # query by part and/or colour
list(model.iter_pieces())  # leaf pieces, submodels expanded
model.bill_of_materials()  # counted (part, colour) rows
model.save("scene.ldr")
```

### Reading and Writing Model Files

`read_model` parses whole `.ldr` and `.mpd` files - including MPD `0 FILE` /
`0 NOFILE` sections - into a `Model` you can inspect, modify, and save:

```python
from ldraw import read_model

model = read_model("my_model.ldr")
print(model.description, model.author)

for piece in model.pieces:
    print(piece.part, piece.position)

# MPD documents: the first 0 FILE section is the root model,
# later sections are submodels resolvable from their type-1 references.
for ref in model.pieces:
    if (submodel := model.submodel_for(ref)) is not None:
        print(f"{ref.reference} -> {len(submodel.pieces)} pieces")

model.save("my_model_out.ldr")
```

Every parsed object (`Piece`, `Line`, `Triangle`, `Quadrilateral`,
`OptionalLine`, `Comment`, `MetaCommand`) has a `to_ldraw()` method, so
parsed content round-trips back to LDraw text - subfile reference casing
included, byte for byte. Parse errors report the file and 1-based line
number. `ldraw validate` exposes the same checks on the command line.

Building steps are first-class: `model.add_step()` appends a `0 STEP`
marker and `model.steps` returns the pieces grouped step by step. Header
lines are managed through `model.set_header(description=..., name=...,
author=..., ldraw_org=..., license=...)`.

### Reliable Loading and Inspection

For user-facing tools, `load_model()` reads, parses, and validates once. A
malformed line becomes a stable, structured diagnostic while valid content
around it remains available in a partial model:

```python
from ldraw import DiagnosticCode, load_model, prepare_catalog

parts = prepare_catalog().parts
result = load_model("model.mpd", parts=parts)
for diagnostic in result.diagnostics:
    print(diagnostic.code, diagnostic.section, diagnostic.line_number)
    if diagnostic.code is DiagnosticCode.MODEL_UNKNOWN_PART:
        print(f"  unknown part: {diagnostic.offending_value}")

if result.model is not None:
    analysis = result.analyze(parts)
    print(analysis.summary.occurrence_count, analysis.bom)
```

Use `prepare_catalog()` for one cancellable setup operation, public
`PartsCatalog.search()` for consistent multi-field search, and
`parts.inspect_part(code)` / `inspect_model(model, parts)` for metadata,
exact geometry, root-to-leaf occurrence provenance, and explicit failures.
First-run clients can call `discover_libraries()`, `inspect_library()`, and
`plan_download()` before changing anything. Preview rendering remains
optional: `render_capabilities()` reports whether LDView or LeoCAD is present.
The same report-oriented workflows are available from the CLI:

```bash
ldraw parts geometry 3001 --format json
ldraw inspect model.mpd --format json -o inspection.json
ldraw render model.mpd --view front --view top --backend auto
```

Inspection retains valid occurrences from partially malformed input and
includes structured diagnostics in JSON. It exits non-zero when those
diagnostics contain errors; geometry warnings remain reportable successes.

### Building Instructions

Version 1.4 adds a semantic instruction layer without changing raw
`Model.objects`, `Comment`, `MetaCommand`, or the legacy `Model.steps` view.
Each reachable MPD model keeps its own section-local step sequence:

```python
from ldraw import InstructionBuilder, Model, Piece, RotationMode, Vector

submodel = Model.from_pieces(
    [Piece.place("3001", colour=16)],
    name="module.ldr",
)
InstructionBuilder(submodel).step()

model = Model(name="main.ldr")
builder = InstructionBuilder(model)
model.add_submodel(submodel, colour=4, position=Vector(20, 0, 0))
builder.note("Source page 17")
builder.rotation_step(0, 90, 0, mode=RotationMode.ADDITIVE)

document = model.instruction_document()
for section in document.sections:
    for step in section.steps:
        print(section.name, step.number, len(step.added_occurrences()))

model.save("instructions.mpd")
```

The parser recognizes standard `STEP`, MLCad `ROTSTEP`, the supported
structural/camera subset of modern and legacy LPub3D commands, and namespaced
`!PYLDRAW` notes, highlights, and 3D arrows. Unsupported LPub3D directives
remain attached to their original raw objects and round-trip losslessly.

The instruction CLI inspects and validates structure, exports deterministic
JSON, and creates cumulative MPD plus flattened LDR snapshots. It intentionally
does not render PDF, image, HTML, or page layout:

```bash
ldraw instructions inspect instructions.mpd --parts
ldraw instructions validate instructions.mpd --strict --max-parts 25
ldraw instructions export instructions.mpd -o instructions.json
ldraw instructions snapshots instructions.mpd --out snapshots
```

### Part Geometry Queries

`Parts` can answer placement questions directly from the library's part
files, resolving subfile references recursively:

```python
from ldraw import Parts

parts = Parts.get("~/ldraw/parts.lst")

box = parts.bounding_box("3001")  # axis-aligned, in LDU
print(box.min, box.max, box.size)  # origin sits on the stud plane; +Y is down

print(parts.stud_positions("3001"))  # centres of the 8 top studs

for stud in parts.studs("3062b"):  # every stud primitive, tubes included
    print(stud.name, stud.description, stud.position, stud.is_top_stud)

for connection in parts.connections("32000"):
    print(connection.kind, connection.role, connection.position, connection.axis)
```

`parts.geometry(code)` expands drawable points exactly and returns bounds,
studs, typed physical connections, and completeness diagnostics together.
Connection features cover studs/receptacles, bars/clips, pins/holes,
Technic axles/axle holes, hinge fingers, and tyre/rim seats. Profiles retain
diameter, axial span, cross-section, friction/sliding freedom, hinge detents,
source, confidence, and occupancy rather than reducing every connection to a
point. `bounding_box()`
remains as the compact compatibility helper. Stud queries expand stud group
primitives down to individual `stud*` references; `is_top_stud` distinguishes
upward connectors from underside tubes. Use
`ldraw parts geometry CODE [--format table|json]` for the same query without
writing Python.

Primitive-based inference is deliberately conservative. Projects that have
LDCad shadow metadata can layer it on without making it a required dependency:

```python
parts.add_connection_shadow("~/ldcad/shadow")  # directory, .zip, or .csl
parts.add_studio_metadata("studio-connectivity.json")

report = parts.connection_metadata("32000")
print(report.coverage, report.source_count, report.diagnostics)
```

`SNAP_CYL`, `SNAP_CLP`, `SNAP_FGR`, `SNAP_GEN`, `SNAP_INCL`, and
`SNAP_CLEAR` are supported; direct feature/clear commands embedded in custom
part files are consumed as inline metadata too. `Parts.set_connection_overrides()`
provides the final, authoritative layer for custom parts. Adding or clearing
either source invalidates derived geometry automatically.

Connection precedence is heuristics, primitives/official shortcuts, inline
LDCad, registered shadow sources, registered Studio sources, then explicit
overrides. Replacement is by stable feature ID; different IDs remain separate
even when colocated. Coverage is `complete` for clean authoritative metadata
(including an explicit clear-to-empty result), `partial` for recovered or
primitive/heuristic-only evidence, and `none` only when no metadata or
connector primitive exists.

Official complete wheel/tyre shortcuts provide evidence-backed pairing via
`parts.tyre_rim_compatibility`, `compatible_tyres(rim_code)`, and
`compatible_rims(tyre_code)`. Connections inherited by an already assembled
wheel-and-tyre shortcut are marked occupied.

`inspect_model(model, parts)` transforms connection frames into world space.
Use `inspection.connection_contacts()` to find interfaces already mated and
`inspection.snap_candidates(moving, fixed=...)` to obtain ranked rigid
placements. Round interfaces preserve free roll; Technic axle profiles enforce
their quarter-turn cross alignment. Snap deltas are always proper rotations,
so a part placed with a mirroring matrix is never reflected.
`inspection.connection_graphs()` returns confirmed and optimistic immutable
multigraphs over zero-based occurrence indices. Strict stud contacts require
opposing receptacle evidence plus an oriented entry-face and penetration check;
overlapping surfaces alone are not connections.

### IDE Autocompletion and Type Checking

The package ships a `py.typed` marker, so the hand-written API is typed for
mypy/pyright out of the box. For the *generated* `ldraw.library.*` modules,
run:

```bash
ldraw stubs
```

from your project root. This writes an `ldraw-stubs/` PEP 561 stub package
that Pylance/pyright discover automatically (for mypy, ensure the project
root is on `mypy_path`). Regenerate the stubs after switching library
versions with `ldraw download`/`ldraw generate`, and add `ldraw-stubs/` to
your `.gitignore`. Use `--out PATH` to write the stubs somewhere else.
Stub discovery from a project root is standard PEP 561 behavior but can vary
by tool version - the stubs mirror the generated modules exactly, so pointing
your checker's stub path at them always works.

## Requirements

- Python 3.12+

## Agent Skill

The `lego-model-builder` skill turns natural-language model descriptions into
reusable pyldraw3 programs, verified LDraw files, preview images, and parts
lists.

**[Download lego-model-builder.zip](https://hbmartin.github.io/pyldraw3/downloads/lego-model-builder.zip)**

See the
**[beginner-friendly installation and usage guide](https://hbmartin.github.io/pyldraw3/lego-model-builder/)**
for ChatGPT and Claude desktop setup, example prompts, expected files, and
troubleshooting. The guide also includes a command-line installation option
for technical users.

## Configuration

`ldraw download` and `ldraw generate` write their settings to a YAML config file in an OS-appropriate config directory (via [`platformdirs`](https://pypi.org/project/platformdirs/)). Run `ldraw config` to see the current values:

```bash
$ ldraw config
generated_path: /Users/you/Library/Application Support/pyldraw3/generated
ldraw_library_path: /Users/you/Library/Caches/pyldraw3/2018-02
```

- `ldraw_library_path` - the downloaded LDraw release currently in use (switch releases by re-running `ldraw download --version ...`)
- `generated_path` - where `ldraw generate` writes the `ldraw.library.*` package that you `import`

## CLI Reference

The published docs include a standalone [CLI reference](https://hbmartin.github.io/pyldraw3/cli/).

```
usage: ldraw [-h] command ...

Manage LDraw libraries and create, inspect, validate, and render LDraw models.

positional arguments:
  command
    download  Download and unpack an LDraw parts library release.
    generate  Generate the ldraw.library modules from the downloaded library.
    parts     Query the parts catalog.
    validate  Validate an LDraw file (.ldr, .mpd, or .dat).
    bom       Print a bill of materials for an LDraw model file.
    inspect   Inspect exact world bounds, provenance, contacts, and gaps.
    render    Render a deterministic set of standard preview views.
    stubs     Write a type-stub package for ldraw.library into your project.
    instructions
              Inspect, validate, and export renderer-neutral instructions.
    config    Print the current configuration.
    version   Print the installed pyldraw3 version.

options:
  -h, --help  show this help message and exit
```

- `ldraw download [--version VERSION] [--yes]` - download and unpack an LDraw release (default version: `complete`)
- `ldraw generate [--yes] [--force]` - (re)generate `ldraw.library.*` from the currently configured release; `--force` regenerates even if already up to date
- `ldraw parts search TERM [--limit N]` - search the catalog by description or code substring (exit code 1 when nothing matches)
- `ldraw parts info CODE` - show a part's description, category, file path, and the generated-library import to use
- `ldraw parts geometry CODE [--format table|json]` - report exact expanded bounds, studs/connectors, and completeness diagnostics
- `ldraw validate FILE [--strict]` - lint a file: malformed lines, unknown parts and colour codes are errors; suspect matrices, legacy dithered colours, and unknown meta-commands are warnings (`--strict` makes warnings fail; exit code 1 on errors)
- `ldraw bom FILE [--format table|csv|json] [-o OUT]` - print a bill of materials counted by part and colour, submodels expanded
- `ldraw inspect FILE [--format table|json] [--gap-threshold LDU] [--chronological] [--ldcad-shadow PATH] [--studio-metadata PATH] [-o OUT]` - report exact occurrence geometry, provenance, typed contacts/graphs, structured diagnostics, and nearest AABB gaps
- `ldraw render FILE [--view front|isometric|top] [--backend auto|ldview|leocad] [--output-dir DIR] [--overwrite]` - render a safely staged named view set through the optional preview backends
- `ldraw stubs [--out PATH]` - write an `ldraw-stubs/` PEP 561 stub package for IDE autocompletion
- `ldraw instructions inspect|validate|export|snapshots ...` - inspect semantic steps, validate instruction structure, export JSON, or write cumulative MPD/LDR snapshot bundles (requires a configured parts catalog)
- `ldraw config` - print the current configuration as YAML
- `ldraw version` - print the installed `pyldraw3` version

Run `ldraw <command> --help` for a command's full option list.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and packaging.

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/hbmartin/pyldraw3.git
cd pyldraw3

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Download and set up LDraw library (fetches the latest complete release;
# pass --version 2018-02 to pin a dated release for reproducible builds)
uv run ldraw download --yes
uv run ldraw generate --yes
```

### Development Commands

```bash
# Run tests
uv run pytest                 # All tests
uv run pytest --cov=ldraw     # With coverage (97% regression gate)
uv run pytest --integration   # Integration tests only

# Code formatting and linting
uv run ruff format .         # Format code
uv run ruff check            # Lint code
uv run ruff check --fix      # Fix linting issues

# Build package
uv build
```

### Documentation Site

The documentation site is built with [Zensical](https://zensical.org/) from
the Markdown sources in `docs/`. The API reference is expanded from
`ldraw.__all__` at build time and rendered from type annotations and docstrings
via `mkdocstrings-python`.

```bash
uv sync --group docs
uv run zensical serve
uv run zensical build --clean --strict
```

GitHub Pages must be configured to publish from GitHub Actions. If Pages is
still configured to publish from a branch, GitHub will keep serving that branch
instead of the Zensical workflow artifact.

## Architecture

### Core Components

- **CLI Interface** (`ldraw/cli.py`): Command-line interface with catalog, validation, inspection, rendering, BOM, instruction, generation, and configuration commands
- **Instruction Semantics** (`ldraw/instructions.py`): Sectioned STEP/ROTSTEP and LPub3D interpretation, authoring, inventory, and validation
- **Instruction Artifacts** (`ldraw/instruction_artifacts.py`): Deterministic JSON manifests and cumulative MPD/LDR snapshots
- **Dynamic Library Generation** (`ldraw/generation/`): Converts LDraw libraries to Python modules (with `.pyi` stubs)
- **Import System** (`ldraw/imports.py`): Custom meta path hook for dynamic imports

### Key Classes

- `Model` (`ldraw/model.py`) - Reads and writes whole `.ldr`/`.mpd` model files
- `InstructionDocument` / `InstructionBuilder` - Read and author renderer-neutral building instructions
- `Parts` - Manages parts catalog and loading
- `Piece` - Represents individual LEGO pieces in models  
- `Person` (`ldraw/figure.py`) - High-level minifigure construction
- Geometry classes - Matrix operations and 3D mathematics

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for the fork/branch/PR workflow.

## License

This project is licensed under the GNU General Public License v3.0 or later - see the [license (COPYING)](COPYING) file for details.

```
pyldraw, a Python package for creating LDraw format files.
Copyright (C) 2008 David Boddie <david@boddie.org.uk>
Some parts Copyright (C) 2021 Matthieu Berthomé <matthieu@mmea.fr>
Some parts Copyright (C) 2025 Harold Martin <harold.martin@gmail.com>
```

## Trademarks

LDraw is a trademark of the Estate of James Jessiman. LEGO is a registered trademark of the LEGO Group.

## Credits

- **Original Author**: [David Boddie](mailto:david@boddie.org.uk)
- **Previous Maintainer**: [Matthieu Berthomé](mailto:matthieu@mmea.fr)
- **Current Maintainer**: [Harold Martin](mailto:harold.martin@gmail.com)

This repository was extracted from the original Mercurial repository and modernized for current Python practices.
