# Spaceships: shape, structure and detail

These are studies of **large official ships**: use them for proportions and detail ideas, not as starting points. To build a ship, start from a [spaceship recipe](../../docs/reference/README.md) and the [spaceship guide](../../docs/agent/spaceships.md), which list the parts and joints these ships are made of. The [interactive gallery](index.html) links the images, sources and construction notes.

| Whole-ship study | Preview | Parts | Use |
| --- | --- | ---: | --- |
| [B-wing starfighter](b-wing/GUIDE.md) | [![B-wing](b-wing/renders/home.png)](b-wing/index.html) | 434 | Study: wing, engine and cockpit construction |
| [UCS Y-wing](ucs-y-wing-study/GUIDE.md) | [![UCS Y-wing](ucs-y-wing-study/renders/home.png)](ucs-y-wing-study/index.html) | 1,493 | Inspiration: twin engines, exposed machinery and narrow spine |
| [Imperial Star Destroyer](star-destroyer-study/GUIDE.md) | [![Star Destroyer](star-destroyer-study/renders/home.png)](star-destroyer-study/index.html) | 1,335 | Inspiration: wedge hull, recessed edges and layered superstructure |

The Y-wing and Star Destroyer retain source errors and **cannot be exported as checked constructions**. Their guides explain how to study their useful forms. The B-wing carries three recorded corrections to rounded positions in a copied wing stack; its original library file is unchanged.

## Reusable constructions

| Construction | Parts | Study format | What to learn |
| --- | ---: | --- | --- |
| [UCS X-wing lower port wing](x-wing-wing/GUIDE.md) | 125 | Four completed views and source section data | Thin plate layers, a mounted nacelle and long tip detail |
| [UCS X-wing nacelle](x-wing-nacelle/GUIDE.md) | 41 | One source group, two views | Concentric cylinders, a long core and transverse mounts |
| [Enclosed canopy cockpit](canopy-cockpit/GUIDE.md) | 49 | Root and three child sections, two views each | Real octagonal canopy halves, hinge interfaces, rear glazing and pilot |
| [UCS Y-wing armour panel](y-wing-armour/GUIDE.md) | 31 | Seven steps, two views each | Layered support, clean sloping edges, vents and a central detail strip |
| [Millennium Falcon service cluster](falcon-greebles/GUIDE.md) | 15 | Three steps, two views each | Small moulded fittings arranged as a contained machinery bay |

All five constructions match their rendered BOMs; [STATUS](../STATUS.md) gives their current `check` verdicts (PASS, or GAP where a joint is not yet judged). The cockpit retains legacy part aliases and its pilot; inspect those before substituting newer parts. A source with a single STEP group supplies one construction state, not an invented sequence of insertions.

All **50 images were opened**: 30 step views and 20 final/overview views. All eight Python/LeoCAD BOM comparisons match. The [visual review](visual-review.md) records what was inspected and learned.

## Start a spacecraft

Copy the closest [recipe](../../docs/reference/README.md) and build with the kit; run `./ldraw-agent check MODEL.mpd --family spaceship` to compare how it is built with official ships. `./ldraw-agent spaceship brief starfighter` lists the part roles and recipes for a starfighter, freighter or capital ship.

`spaceship export` still copies a study's source and placement plan, but these are hundreds of parts placed by raw matrices: expect to study them, not to adapt them. Some show **GAP** in [STATUS](../STATUS.md): joints `check` cannot judge yet, not defects.

## Add more examples

Follow the [build-manual and atlas workflow](../../docs/agent/build-manuals.md). It explains how to preserve exact source identities, turn source steps into pages, study parent interfaces, review the images and select useful new entries for any atlas.

[selections.json](selections.json) pins these eight sources and their discovery evidence. [generate.py](generate.py) recreates them:

```sh
.venv/bin/python examples/spaceship-atlas/generate.py
.venv/bin/python examples/spaceship-atlas/generate.py --name y-wing-armour
```

Regeneration checks source hashes and clears the affected visual reviews. Reopen the new images before recording review again. `--no-render` leaves rendered evidence pending. Original authors and licences are retained; these are attributed source studies and adaptations, not newly claimed original spacecraft designs.
