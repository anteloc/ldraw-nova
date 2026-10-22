# ldraw-nova

Build LEGO models with an AI agent, ordinary JSON plans and LDraw parts. The tools find parts and reference constructions, generate editable MPDs, check geometry, render previews and compare parts lists. Python generators support larger procedural designs.

[Watch the demonstration](https://youtu.be/YDjjxGqWpgU) · [Project background](docs/background.md)

## Start locally

You need Python 3.12+, an installed LDraw parts library, Poppler (`pdftotext`) and LeoCAD on `PATH`. The repository includes the reference data and connector metadata used by the tools.

```sh
export LDRAW_DIR=/path/to/ldraw
./setup.sh
./ldraw-agent review examples/bridge.plan.json --outdir output/bridge-review
```

Open the PNGs in `output/bridge-review/previews/`. The same folder contains the model, validation report, Python BOM, LeoCAD BOM comparison and a manifest tying artifacts to the model revision. `review --no-render` runs intermediate Python checks when previews are not needed. `./ldraw-agent doctor` reports local dependencies.

## Build your own model

Give an agent your model idea and [instructions.md](instructions.md). The working loop is:

1. Choose a design and inspect the parts or example constructions it needs.
2. Write a [JSON plan](docs/agent/plans.md); use Python when calculations or loops help.
3. Run `review`, open the previews, repair the source and repeat.
4. Deliver the editable MPD, source, checks and reviewed images.

```sh
./ldraw-agent build output/my-model.plan.json
./ldraw-agent review output/my-model.mpd
```

`build` infers `output/my-model.mpd` and writes only after source/geometry checks pass. You can also run `review output/my-model.plan.json` to build and review in one command. Use `--force` for a deliberate rebuild or replacement of a generated review. Keep editable source and visual-review notes outside the generated review directory.

Existing JSON plans, `build --output`, individual check/render commands and shell wrappers remain supported. Successful checks provide evidence, not proof of physical buildability; warnings, skipped checks and required visual inspection stay explicit.

| Need | Read |
|---|---|
| Agent workflow and subject-specific guides | [Instructions](instructions.md) |
| Plan format, placements and Python API | [Plan guide](docs/agent/plans.md) |
| Commands, review options and artifacts | [Tool reference](docs/agent/tooling.md) |
| Geometry checks and limitations | [Validation](docs/agent/validation.md) |
| Flexible hoses, cables, bands, chains and treads | [LSynth guide](docs/agent/flexible-parts.md), [small examples](examples/flex/README.md) |
| Studs Not On Top (SNOT) construction | [SNOT guide](docs/agent/snot.md), [parrot core](examples/snot/parrot/README.md), [cat details and joints](examples/snot/cat/README.md), [Halcyon original interceptor](examples/snot/halcyon/README.md) |
| Spaceships: SNOT by default | [Halcyon default model](examples/snot/halcyon/README.md), [spaceship guide](docs/agent/spaceships.md) |
| Reusable constructions and model examples | [Reference atlas](examples/reference-atlas/README.md), `./ldraw-agent examples --help` |

Semantic reference search uses [jev-rerank](https://github.com/anteloc/jev-rerank) and a TypeSafe API key. It is optional: offline catalogs, examples and `discover search ... --engine fts` remain available. Follow the [availability check](docs/agent/reference-discovery.md#check-jev-availability-before-searching) before using the service.

## Run the web app

The web app and Docker configuration live in the sibling [ldraw-nova-docker](https://github.com/anteloc/ldraw-nova-docker) repository. Install Git and Docker, then clone matching release tags side by side:

```sh
git clone --branch v0.6.0 https://github.com/anteloc/ldraw-nova.git
git clone --branch v0.6.0 https://github.com/anteloc/ldraw-nova-docker.git
cd ldraw-nova-docker
docker compose build
docker compose up -d
```

The first build needs about 5 GB of disk space. Open **http://localhost:8765**, or **https://localhost:8443** for VR on Meta Quest 3 (accept the self-signed certificate). Devices on your network can use the host computer's IP address. The app has no login; run it on a trusted network. Set `TYPESAFE_API_KEY` in the app's Settings for semantic search. Stop it with `docker compose down`.

The web app provides interactive 3D/VR views and conversation history. The local CLI also supports semantic GLB export for Blender through `./prepare-glb.sh --file MODEL.mpd MODEL.glb`, using the installed `mpd2glb.sh` converter. The editable MPD remains the authoritative model.

## Development

```sh
uv sync --locked --extra test
.venv/bin/python -m pytest -q
```

Tests use a miniature library plus the configured official library for integration cases. Integration tests skip explicitly when the official library is unavailable. Current checks do not certify material collision freedom, strength, motion or real part/colour availability. See the [verification records](docs/agent/verification.md) for tested coverage and historical results.

Further work includes model quality across more families, generation cost and speed, instruction-manual reconstruction, and VR handling/performance.

## Acknowledgements

I'd like to thank the following:

- [The LDraw Community](https://www.ldraw.org/)
- [LDView](https://tcobbs.github.io/ldview/)'s Travis Cobbs (@tcobbs), and contributors.
- [LeoCAD](https://github.com/leozide/leocad)'s Leonardo Zide (@leozide), and contributors.
- [LDCad](https://www.melkert.net/LDCad) and Shadow Library, Roland Melkert.
- [ldraw.rs](https://github.com/segfault87/ldraw.rs)'s Park Joon-Kyu (@segfault87), and contributors.
- [pyldraw3](https://github.com/hbmartin/pyldraw3)'s  Harold Martin (@hbmartin), and contributors.

... and thanks to all of the many other LDraw creators!

**NOTE:** For this work, I've used many LDraw models, libraries, tools, docs... from many sources.

There is a lot **amazing people** that generously contributed to this, even for **decades**, by **generously donating their finest work** to the public domain and open source community. 

If you think you should be included on this section, please **drop me an email!**

## Trademarks

**LEGO(R)** is a trademark of the **LEGO Group** of companies which does not sponsor, authorize or endorse this software.
