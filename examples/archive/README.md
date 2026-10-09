# Archived examples

These models fail `check`: parts float free of the model, or parts collide. **Do not copy their construction.** They stay here for their history and their ideas (layouts, palettes, subjects), and they are left out of `ldraw-agent examples`, the atlas catalogs and `examples/STATUS.md`.

Start new work from the [recipes](../../docs/reference/README.md). The last column names the recipe planned to replace each one ([roadmap](../../docs/dev/recipe-roadmap.md)).

| Example | Parts | `check` | Planned replacement |
|---|---:|---|---|
| [atlas-crane](atlas-crane/atlas-crane.mpd) | 1082 | 891 floating, 21 collisions (the boom has no pins) | M6 crane |
| [cathedral](cathedral/cathedral.mpd) | 5394 | 139 floating | L2 gothic arches |
| [copper-bean](copper-bean/copper-bean.mpd) | 1022 | 18 floating | B2 shopfront |
| [modular-street](modular-street/copper-lane.mpd) (Copper Lane) | 1655 | 1 floating, 2 collisions | B3 modular building floor |
| [building-atlas/clinic](building-atlas/clinic/clinic.mpd) | 426 | 10 floating | B3 modular building floor |
| [building-atlas/conservatory](building-atlas/conservatory/conservatory.mpd) | 437 | 2 floating | B9 glasshouse |
| [building-atlas/cottage](building-atlas/cottage/cottage.mpd) | 442 | 2 collisions | B1 small house |
| [building-atlas/desert-sanctuary](building-atlas/desert-sanctuary/desert-sanctuary.mpd) | 260 | 4 floating | B7 civic portico |
| [building-atlas/fire-station](building-atlas/fire-station/fire-station.mpd) | 462 | 3 floating | B8 garage |
| [building-atlas/lighthouse](building-atlas/lighthouse/lighthouse.mpd) | 368 | 4 floating | B4 lighthouse / tower |
| [building-atlas/moon-base](building-atlas/moon-base/moon-base.mpd) | 487 | 5 floating | — |
| [building-atlas/museum](building-atlas/museum/museum.mpd) | 376 | 15 floating | B7 civic portico |
| [building-atlas/railway-station](building-atlas/railway-station/railway-station.mpd) | 504 | 10 floating | B7 civic portico, B6 porch and canopy |
| [building-atlas/school](building-atlas/school/school.mpd) | 530 | 2 floating | B3 modular building floor |
| [building-atlas/winter-lodge](building-atlas/winter-lodge/winter-lodge.mpd) | 489 | 2 collisions | B5 hip roof and dormer |
| [building-atlas/wizard-tower](building-atlas/wizard-tower/wizard-tower.mpd) | 459 | 1 floating | B4 lighthouse / tower |
| [building-atlas/workshop](building-atlas/workshop/workshop.mpd) | 475 | 16 floating | B8 garage |
| [building-atlas/details/beacon](building-atlas/details/beacon/beacon.mpd) | 4 | 1 floating | T2 side-mounted details |
| [building-atlas/details/chimney](building-atlas/details/chimney/chimney.mpd) | 12 | 1 floating | T8 round tower |
| [building-atlas/details/dormer-roof](building-atlas/details/dormer-roof/dormer-roof.mpd) | 213 | 2 collisions | B5 hip roof and dormer |
| [building-atlas/details/fountain](building-atlas/details/fountain/fountain.mpd) | 27 | 2 floating | T8 round tower, T10 tree and garden |
| [building-atlas/details/porch](building-atlas/details/porch/porch.mpd) | 36 | 18 floating (two roof halves, no bridge) | B6 porch and canopy |
| [building-atlas/details/solar-array](building-atlas/details/solar-array/solar-array.mpd) | 14 | 7 floating (panels not bridged) | T3 hinged panel |
| [vehicle-atlas/courier-jet](vehicle-atlas/courier-jet/courier-jet.mpd) | 46 | 1 collision | V3 aircraft |
| [vehicle-atlas/delivery-van](vehicle-atlas/delivery-van/delivery-van.mpd) | 122 | 4 collisions | V2 pickup / van |
| [vehicle-atlas/grand-tourer](vehicle-atlas/grand-tourer/grand-tourer.mpd) | 97 | 4 collisions | V4 sports car |
| [vehicle-atlas/pickup](vehicle-atlas/pickup/pickup.mpd) | 129 | 6 collisions | V2 pickup / van |
| [vehicle-atlas/tipper-truck](vehicle-atlas/tipper-truck/tipper-truck.mpd) | 113 | 4 collisions | V2 pickup / van |
| [technic-atlas/mechanisms/independent-suspension](technic-atlas/mechanisms/independent-suspension/independent-suspension.mpd) | 259 | 189 floating, 8 collisions (boundary holders omitted from the extract) | M5 suspension |

## The generators behind them

Two legacy generators still produce models like these. Prefer the kit and recipes:
- `ldraw_tools.architecture`: `porch`, `beacon`, `utility_stack` (the chimney), `fountain`, `solar_array`;
- `./ldraw-agent vehicle plan` with the grand-tourer, delivery-van, pickup, tipper-truck and courier-jet profiles. It warns when used.

## Bring one back

1. Fix the construction until `./ldraw-agent check MODEL.mpd` passes.
2. `git mv` the folder back to its old path.
3. Remove its key from the `ARCHIVED` set in that atlas's `generate.py`, and restore its catalog entry.
4. Run `.venv/bin/python scripts/example_status.py`.
