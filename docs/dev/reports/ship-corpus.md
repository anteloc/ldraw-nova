# Official ship corpus: `check` calibration

2026-10-09. `scripts/official_corpus.py --family spaceship` checks the main craft of 43 official LEGO ship sets: Classic Space, Futuron, Blacktron, M:Tron, Space Police, Ice Planet, Spyrius and Star Wars minifig-scale and mini sets. Official models are well built, so each failure is a gap in `check`, a genuinely loose accessory, or an error in the LDraw file. Full results: [ship-corpus.json](ship-corpus.json).

## Result

| | Before | After |
|---|---:|---:|
| Crafts with no floating, colliding or badly seated parts | 9 of 43 | 19 of 43 |
| Crafts with badly seated parts | 13 | 0 |
| Spaceship-atlas extracts passing | 0 of 5 | 2 of 5 (canopy cockpit, Y-wing armour) |
| Technic-atlas four-speed gearbox | FAIL | PASS |

## What changed in `check`

| Gap | Fix |
|---|---|
| Classic finger hinges (4275b/4276b, 2452, 4504) floated or collided at any angle | pyldraw3 replaces the authored fingers of hinge primitives (h1, h2, clh*) with a guess along the wrong axis. The part cache now carries the primitives' authored data into the part |
| Inverted slopes (4287, 42023) reported "badly seated" by 4 to 5 LDU | On partial-coverage parts, guessed ports of a kind the part already authors are dropped; other guessed sockets are cut to the body |
| Hinge halves with no usable finger data, roller doors in grooved bricks, spring shooters | New interlocking families (`hinge`, `groove`, `shooter`): overlapping members connect and their overlaps are reviews |
| Minifigures and their accessories counted as floating construction | Groups made only of figure and flexible parts are reported as loose figures, not failures |
| 2 LDU fits at grille tiles, fences and clips counted as collisions | Overlaps up to 2 LDU between shaped parts are reviews; two plain bricks or plates overlapping stay errors |
| Spring-shooter generic fittings 1.1 LDU apart | Generic interfaces mate within 2 LDU |
| Embedded part copies titled only by number ("35188") | They take the library part's description, so a gear copy is recognised as a gear |

Regression tests: `tests/test_check.py` (hinge plates at 30°, inverted-slope ports, loose figures, official tight fit, embedded gear copy).

## What remains

| Cause | Sets |
|---|---|
| 9V electric plates and battery boxes, magnets: no port data | 6781, 6862, 6891 |
| Parts placed at half-stud offsets (round plates, antennas, rounded caps) | 20019, 7140, B-wing extract, X-wing wing extract |
| Single loose parts and small groups | 918, 6811, 6830, 6832, 6835, 6877, 6879, 6897, 6939, 30050, 30051 |
| Classic control-stick hinge (4592/4593) | 6894, Falcon greebles extract |
| Collisions in a rotated sub-assembly | 8031, 7667, 6973 |
| Large mixed groups (Technic, cargo, jail modules) | 6886, 7667, 75033, 6923, 20021 |

The three atlas extracts that still fail are labelled GAP in `examples/STATUS.md`: problems `check` cannot judge yet, not construction defects.

## Construction signatures

`--signatures` also writes `ldraw_tools/data/family-signatures.json`: per family, the 25th/50th/75th and 10th/50th/90th percentiles of plain bricks, plates, wedges, slopes, tiles, brackets, hinges, round parts, sideways and angled parts. `check --family` and `Model(..., family=)` compare a model with them.
