# Example status

`check` verdicts for the curated examples (51 of 54 pass; 3 official models show gaps in check). Regenerate with `.venv/bin/python scripts/example_status.py`.

A failing example still shows ideas (shapes, palettes, layouts), but its construction has the listed defects. Do not copy its coordinates. Prefer the [recipes](../docs/reference/README.md), which always pass. Examples that failed are moved to the [archive](archive/README.md). GAP marks an official LEGO model whose remaining problems are parts or joints `check` cannot judge yet, not construction defects.

| Example | Parts | Check | Problems |
|---|---:|---|---|
| [bridge.mpd](bridge.mpd) | 5 | PASS | clean |
| [building-atlas/details/battlement/battlement.mpd](building-atlas/details/battlement/battlement.mpd) | 25 | PASS | clean |
| [building-atlas/details/bench/bench.mpd](building-atlas/details/bench/bench.mpd) | 6 | PASS | clean |
| [building-atlas/details/clock/clock.mpd](building-atlas/details/clock/clock.mpd) | 2 | PASS | clean |
| [building-atlas/details/display-window/display-window.mpd](building-atlas/details/display-window/display-window.mpd) | 2 | PASS | clean |
| [building-atlas/details/fence/fence.mpd](building-atlas/details/fence/fence.mpd) | 5 | PASS | clean |
| [building-atlas/details/flower-box/flower-box.mpd](building-atlas/details/flower-box/flower-box.mpd) | 13 | PASS | clean |
| [building-atlas/details/glazed-door/glazed-door.mpd](building-atlas/details/glazed-door/glazed-door.mpd) | 2 | PASS | clean |
| [building-atlas/details/lamppost/lamppost.mpd](building-atlas/details/lamppost/lamppost.mpd) | 6 | PASS | clean |
| [building-atlas/details/market-stall/market-stall.mpd](building-atlas/details/market-stall/market-stall.mpd) | 33 | PASS | clean |
| [building-atlas/details/stairs/stairs.mpd](building-atlas/details/stairs/stairs.mpd) | 4 | PASS | clean |
| [building-atlas/details/tree/tree.mpd](building-atlas/details/tree/tree.mpd) | 18 | PASS | clean |
| [building-atlas/details/window/window.mpd](building-atlas/details/window/window.mpd) | 3 | PASS | clean |
| [building-atlas/farmstead/farmstead.mpd](building-atlas/farmstead/farmstead.mpd) | 531 | PASS | clean |
| [building-atlas/frontier/frontier.mpd](building-atlas/frontier/frontier.mpd) | 381 | PASS | clean |
| [building-atlas/gatehouse/gatehouse.mpd](building-atlas/gatehouse/gatehouse.mpd) | 322 | PASS | clean |
| [building-atlas/market-court/market-court.mpd](building-atlas/market-court/market-court.mpd) | 712 | PASS | clean |
| [building-atlas/medieval-village/medieval-village.mpd](building-atlas/medieval-village/medieval-village.mpd) | 857 | PASS | clean |
| [building-atlas/skyline/skyline.mpd](building-atlas/skyline/skyline.mpd) | 441 | PASS | clean |
| [building-atlas/temple/temple.mpd](building-atlas/temple/temple.mpd) | 342 | PASS | clean |
| [building-atlas/treehouse/treehouse.mpd](building-atlas/treehouse/treehouse.mpd) | 339 | PASS | clean |
| [mechanism-atlas/differential/differential.mpd](mechanism-atlas/differential/differential.mpd) | 29 | PASS | clean |
| [mechanism-atlas/driven-turntable/driven-turntable.mpd](mechanism-atlas/driven-turntable/driven-turntable.mpd) | 25 | PASS | clean |
| [mechanism-atlas/gear-reduction/gear-reduction.mpd](mechanism-atlas/gear-reduction/gear-reduction.mpd) | 35 | PASS | clean |
| [mechanism-atlas/piston-crank/piston-crank.mpd](mechanism-atlas/piston-crank/piston-crank.mpd) | 19 | PASS | clean |
| [mechanism-atlas/steering-rack/steering-rack.mpd](mechanism-atlas/steering-rack/steering-rack.mpd) | 10 | PASS | clean |
| [mechanism-atlas/worm-drive/worm-drive.mpd](mechanism-atlas/worm-drive/worm-drive.mpd) | 14 | PASS | clean |
| [reference-atlas/recipes/arcade-bay/arcade-bay.mpd](reference-atlas/recipes/arcade-bay/arcade-bay.mpd) | 15 | PASS | clean |
| [reference-atlas/recipes/street-lantern/street-lantern.mpd](reference-atlas/recipes/street-lantern/street-lantern.mpd) | 11 | PASS | clean |
| [sakura-garden/sakura-garden.mpd](sakura-garden/sakura-garden.mpd) | 2175 | PASS | clean |
| [spaceship-atlas/b-wing/b-wing.mpd](spaceship-atlas/b-wing/b-wing.mpd) | 434 | GAP | 5 floating |
| [spaceship-atlas/canopy-cockpit/canopy-cockpit.mpd](spaceship-atlas/canopy-cockpit/canopy-cockpit.mpd) | 49 | PASS | clean |
| [spaceship-atlas/falcon-greebles/falcon-greebles.mpd](spaceship-atlas/falcon-greebles/falcon-greebles.mpd) | 15 | GAP | 2 badly seated |
| [spaceship-atlas/x-wing-nacelle/x-wing-nacelle.mpd](spaceship-atlas/x-wing-nacelle/x-wing-nacelle.mpd) | 41 | PASS | clean |
| [spaceship-atlas/x-wing-wing/x-wing-wing.mpd](spaceship-atlas/x-wing-wing/x-wing-wing.mpd) | 125 | GAP | 1 floating |
| [spaceship-atlas/y-wing-armour/y-wing-armour.mpd](spaceship-atlas/y-wing-armour/y-wing-armour.mpd) | 31 | PASS | clean |
| [technic-atlas/box-chassis/box-chassis.mpd](technic-atlas/box-chassis/box-chassis.mpd) | 18 | PASS | clean |
| [technic-atlas/frame-tower/frame-tower.mpd](technic-atlas/frame-tower/frame-tower.mpd) | 36 | PASS | clean |
| [technic-atlas/mechanisms/cam-follower-engine/cam-follower-engine.mpd](technic-atlas/mechanisms/cam-follower-engine/cam-follower-engine.mpd) | 55 | PASS | clean |
| [technic-atlas/mechanisms/double-cardan-shaft/double-cardan-shaft.mpd](technic-atlas/mechanisms/double-cardan-shaft/double-cardan-shaft.mpd) | 7 | PASS | clean |
| [technic-atlas/mechanisms/four-bar-lift/four-bar-lift.mpd](technic-atlas/mechanisms/four-bar-lift/four-bar-lift.mpd) | 119 | PASS | clean |
| [technic-atlas/mechanisms/four-cylinder-bank/four-cylinder-bank.mpd](technic-atlas/mechanisms/four-cylinder-bank/four-cylinder-bank.mpd) | 34 | PASS | clean |
| [technic-atlas/mechanisms/four-speed-gearbox/four-speed-gearbox.mpd](technic-atlas/mechanisms/four-speed-gearbox/four-speed-gearbox.mpd) | 66 | PASS | clean |
| [technic-atlas/reinforced-frame/reinforced-frame.mpd](technic-atlas/reinforced-frame/reinforced-frame.mpd) | 13 | PASS | clean |
| [technic-atlas/service-platform/service-platform.mpd](technic-atlas/service-platform/service-platform.mpd) | 55 | PASS | clean |
| [turntable-frame/turntable-frame.mpd](turntable-frame/turntable-frame.mpd) | 32 | PASS | clean |
| [vehicle-atlas/details/cargo-chest/cargo-chest.mpd](vehicle-atlas/details/cargo-chest/cargo-chest.mpd) | 3 | PASS | clean |
| [vehicle-atlas/details/driver-cockpit/driver-cockpit.mpd](vehicle-atlas/details/driver-cockpit/driver-cockpit.mpd) | 4 | PASS | clean |
| [vehicle-atlas/details/jet-engine-pod/jet-engine-pod.mpd](vehicle-atlas/details/jet-engine-pod/jet-engine-pod.mpd) | 2 | PASS | clean |
| [vehicle-atlas/details/navigation-lights/navigation-lights.mpd](vehicle-atlas/details/navigation-lights/navigation-lights.mpd) | 4 | PASS | clean |
| [vehicle-atlas/details/pilot-cockpit/pilot-cockpit.mpd](vehicle-atlas/details/pilot-cockpit/pilot-cockpit.mpd) | 5 | PASS | clean |
| [vehicle-atlas/details/wing-mirror/wing-mirror.mpd](vehicle-atlas/details/wing-mirror/wing-mirror.mpd) | 3 | PASS | clean |
| [vehicle-atlas/harbour-launch/harbour-launch.mpd](vehicle-atlas/harbour-launch/harbour-launch.mpd) | 12 | PASS | clean |
| [vehicle-atlas/touring-motorcycle/touring-motorcycle.mpd](vehicle-atlas/touring-motorcycle/touring-motorcycle.mpd) | 8 | PASS | clean |
