# Recipes

Each recipe is one short page with a picture, a connection diagram and a complete generator that passes `check`. Copy the closest recipe into `output/NAME/generate.py`, change it toward your subject, and run it. CI runs every recipe, so the code always works.

| I want to build | Start from | It teaches |
|---|---|---|
| A house, shop, station, any walled building | [Small house](small-house.md) | `wall()` with door and window openings, hinged door, gable roof with ridge |
| A car, van, cart, anything on small wheels | [Small car](small-car.md) | Wheel holders, rims and tyres by `mate`, wheel arches clearing tyres |
| A Technic chassis, crane base, machine frame | [Technic frame](technic-frame.md) | Pinned beams, `along=`, closing a loop with `pin(between=...)` |
| A winch, turntable drive, gearbox, any drive | [Gear train](gear-train.md) | Axles as bearings, gear spacing, `slide`/`toward`, bushes |
| A spaceship, aircraft, anything with wings | [Starfighter](starfighter.md) | Bridging wings to a hull, canopy, side studs (SNOT) |

| Technique | Where |
|---|---|
| Stack bricks and plates without coordinates | [kit](../agent/kit.md): `place(cell=, level=, turn=)` and `part.top` |
| Connect a pin, axle, stud, hinge, clip or wheel | [kit](../agent/kit.md): `mate(port, to=part.port(name))`; port names from `./ldraw-agent ports PART` |
| Walls with openings | [Small house](small-house.md) |
| Floors from several plates | `fill()`, then bridge every seam with one part across it ([kit](../agent/kit.md)) |
| Sideways building (SNOT) | [Starfighter](starfighter.md): bricks with side studs |
| Modules and how they connect | Sections in the [kit](../agent/kit.md); draw the connection diagram in your brief and run `check --intended` |
| Find the right part | `./ldraw-agent search parts 'words'`, `catalog parts`, [reference discovery](../agent/reference-discovery.md) |
| Shape, colour and detail | [Visual design](../agent/visual-design.md) |

Recipes are deliberately small. Combine them: a fire station is the house walls plus a garage-door opening; a truck is the car with a longer spine and a cargo box built with `wall()`. When a user selects one of your finished models as good, turn it into a new recipe with the [curation guide](curation.md).
