# Construction recipes

Small plans that place parts by their real interfaces (`on`, `under` and Technic seats) instead of hand-written coordinates and matrices. Each builds and reviews cleanly; copy the placements and change parts, colours and studs.

| Recipe | Plan | Preview |
|---|---|---|
| Cover a side-stud course with a tile | [side-stud-cover.plan.json](side-stud-cover.plan.json) | ![Cover a side-stud course with a tile](side-stud-cover.png) |
| Headlight brick with a round lens | [headlight-lamp.plan.json](headlight-lamp.plan.json) | ![Headlight brick with a round lens](headlight-lamp.png) |
| Upward bracket carrying a front grille | [bracket-grille.plan.json](bracket-grille.plan.json) | ![Upward bracket carrying a front grille](bracket-grille.png) |
| One panel module seated on both sides of a core | [side-panels.plan.json](side-panels.plan.json) | ![One panel module seated on both sides of a core](side-panels.png) |
| Window frame and glass between brick columns | [window-wall.plan.json](window-wall.plan.json) | ![Window frame and glass between brick columns](window-wall.png) |
| Rigid Technic chassis: rails pinned to an open frame at two holes each | [technic-pin-frame.plan.json](technic-pin-frame.plan.json) | ![Rigid Technic chassis: rails pinned to an open frame at two holes each](technic-pin-frame.png) |
| Braced 8:24 gear pair: two shafts in two beams, bushed both sides | [technic-gear-pair.plan.json](technic-gear-pair.plan.json) | ![Braced 8:24 gear pair: two shafts in two beams, bushed both sides](technic-gear-pair.png) |
| Rack-and-pinion steering: kingpin hubs, L-liftarm arms and a 1 x 7 rack | [technic-rack-steering.plan.json](technic-rack-steering.plan.json) | ![Rack-and-pinion steering: kingpin hubs, L-liftarm arms and a 1 x 7 rack](technic-rack-steering.png) |
| Wheel on an axle carried by two pinned beams | [technic-wheel-axle.plan.json](technic-wheel-axle.plan.json) | ![Wheel on an axle carried by two pinned beams](technic-wheel-axle.png) |
| Drive turned 90 degrees by two 12-tooth double bevels in an open frame | [technic-bevel-corner.plan.json](technic-bevel-corner.plan.json) | ![Drive turned 90 degrees by two 12-tooth double bevels in an open frame](technic-bevel-corner.png) |
| Worm driving a 24-tooth gear between two open frames | [technic-worm-drive.plan.json](technic-worm-drive.plan.json) | ![Worm driving a 24-tooth gear between two open frames](technic-worm-drive.png) |
| Swing arm on a frictionless pin, sprung by a 6.5L shock absorber | [technic-suspension-arm.plan.json](technic-suspension-arm.plan.json) | ![Swing arm on a frictionless pin, sprung by a 6.5L shock absorber](technic-suspension-arm.png) |
| Lever raised by a pneumatic cylinder to a rigid mount | [technic-cylinder-lever.plan.json](technic-cylinder-lever.plan.json) | ![Lever raised by a pneumatic cylinder to a rigid mount](technic-cylinder-lever.png) |
| Inverted slope hung under a plate | [inverted-nose.plan.json](inverted-nose.plan.json) | ![Inverted slope hung under a plate](inverted-nose.png) |
| Jumper plate centring a detail between studs | [jumper-centre.plan.json](jumper-centre.plan.json) | ![Jumper plate centring a detail between studs](jumper-centre.png) |
| Row of slopes placed by stud index | [roof-slope-row.plan.json](roof-slope-row.plan.json) | ![Row of slopes placed by stud index](roof-slope-row.png) |

Rebuild and review one:

```sh
./ldraw-agent review examples/recipes/side-stud-cover.plan.json --outdir output/recipes/side-stud-cover
```

Evidence: each recipe passed `review` with matching Python and LeoCAD BOMs, and its preview (the PNG beside the plan) was opened and checked on 2026-11-15. The eight Technic recipes (2026-11-17) also passed every Technic build check and, where they declare one, their mechanism contract. The MPD beside each plan is the reviewed model.

```ldraw-knowledge
[
 {
  "id": "recipe-side-stud-cover",
  "title": "Cover a side-stud course with a tile",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:side-stud-cover"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "A 1 x 4 brick with studs on its side carries a 1 x 4 tile on all four side studs: on {to: core, face: -Z}. The default quarter turn covers the most studs, so no roll is needed. Plates above and below lock the course into a wall or hull. Parts: 30414, 2431, 3710.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/side-stud-cover.plan.json",
  "model": "examples/recipes/side-stud-cover.mpd",
  "model_sha256": "80668e3c1d55047b15de4a6bf1c39f17791be02f7fd7600451ad89c114252fcc",
  "preview": "examples/recipes/side-stud-cover.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "side stud course",
   "smooth sideways surface",
   "hull skin"
  ]
 },
 {
  "id": "recipe-headlight-lamp",
  "title": "Headlight brick with a round lens",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:headlight-lamp"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "A headlight brick (4070) carries a round 1 x 1 tile on its recessed side stud: on {to: lamp, face: -Z}. The stud sits 4 LDU inside the face, so the tile stands 4 LDU proud. Use for lamps, portholes and gauges. Parts: 4070, 98138.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/headlight-lamp.plan.json",
  "model": "examples/recipes/headlight-lamp.mpd",
  "model_sha256": "f52aefc7f2cd14dfd01d37ed3e0de72a2f6ce976c8a42f73fa97c29e04517b53",
  "preview": "examples/recipes/headlight-lamp.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "lamp",
   "headlight",
   "porthole",
   "gauge"
  ]
 },
 {
  "id": "recipe-bracket-grille",
  "title": "Upward bracket carrying a front grille",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:bracket-grille"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "A 1 x 2 - 1 x 2 up bracket (99780) on the front studs of a plate turns two studs forward; a grille tile sits on them: on {to: bracket, face: -Z}. Pick the plate stud with stud: N, counting in the order part lists them. Parts: 99780, 2412b, 3020.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/bracket-grille.plan.json",
  "model": "examples/recipes/bracket-grille.mpd",
  "model_sha256": "74bc2a8b36027ac4a0d503d9fb80f7463854a05c1830953eb26f92a64f5540c3",
  "preview": "examples/recipes/bracket-grille.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "vehicle grille",
   "front fascia",
   "control panel"
  ]
 },
 {
  "id": "recipe-side-panels",
  "title": "One panel module seated on both sides of a core",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:side-panels"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "A panel section built upright (plate under tile) is seated on the -Z and +Z side studs of a 52107 brick with on {to: core, face: F, socket_at: [-10, 8, 0], roll: 0}. The same module serves both sides: no matrices and no mirrored copy. Parts: 52107, 3023b, 3069b.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/side-panels.plan.json",
  "model": "examples/recipes/side-panels.mpd",
  "model_sha256": "d59d655316bcbf0f45c678b4b717a4d5f6c95c1878dd6babeab749e811f0b80b",
  "preview": "examples/recipes/side-panels.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "door panel",
   "side skin",
   "symmetric panels",
   "module"
  ]
 },
 {
  "id": "recipe-window-wall",
  "title": "Window frame and glass between brick columns",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:window-wall"
  ],
  "families": [
   "recipe",
   "building"
  ],
  "lesson": "A 1 x 2 x 2 window frame stands on a sill plate between 1 x 1 brick columns; its glass shares the frame origin (48 LDU above the sill top). A lintel plate seated on the frame studs (socket 1) ties frame and columns together. Parts: 60592, 60601, 3005, 3710.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/window-wall.plan.json",
  "model": "examples/recipes/window-wall.mpd",
  "model_sha256": "8064020bedc45eb2e196e6d884bc745c164f9898fd73da23e0029b2b2c802471",
  "preview": "examples/recipes/window-wall.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "building window",
   "wall opening",
   "facade"
  ]
 },
 {
  "id": "recipe-inverted-nose",
  "title": "Inverted slope hung under a plate",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:inverted-nose"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "An inverted 45 degree slope hangs under a 2 x 2 plate by its four top studs: under {to: deck}. A tile on top finishes the nose. Use for vehicle noses, chins, wing roots and overhangs built downward. Parts: 3660b, 3022, 3068b.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/inverted-nose.plan.json",
  "model": "examples/recipes/inverted-nose.mpd",
  "model_sha256": "ad38120cc1defbdbe29d4358896bf421bacc527bc77eae00826f7059d5ab1c25",
  "preview": "examples/recipes/inverted-nose.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "vehicle nose",
   "chin",
   "overhang",
   "inverted slope"
  ]
 },
 {
  "id": "recipe-jumper-centre",
  "title": "Jumper plate centring a detail between studs",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:jumper-centre"
  ],
  "families": [
   "recipe",
   "snot"
  ],
  "lesson": "A 1 x 2 jumper plate on two studs offers one stud on the centre line, half a stud off the grid; a round tile on it is centred on the brick. Use for centred lamps, emblems and antennas on even-width parts. Parts: 3794b, 3004, 98138.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/jumper-centre.plan.json",
  "model": "examples/recipes/jumper-centre.mpd",
  "model_sha256": "0e1b1528d410198516886a0da6dcd0267519f43644d1db265729910566844f51",
  "preview": "examples/recipes/jumper-centre.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "half stud offset",
   "centred detail",
   "jumper"
  ]
 },
 {
  "id": "recipe-roof-slope-row",
  "title": "Row of slopes placed by stud index",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:roof-slope-row"
  ],
  "families": [
   "recipe",
   "building"
  ],
  "lesson": "Four 2 x 2 slopes sit on a 2 x 8 plate with on {to: plate, stud: 0, 4, 8, 12}. The tool resolves the slope origin offset and turn from the sockets, so no coordinates are written by hand. Parts: 3039, 3034.",
  "limits": "Small checked recipe: review passed with matching BOMs and its preview was inspected. It does not certify clutch or strength.",
  "plan": "examples/recipes/roof-slope-row.plan.json",
  "model": "examples/recipes/roof-slope-row.mpd",
  "model_sha256": "37f6f741aae36deeaa3c029ac4f80bb218df2d7d35da42a906d4ff8f4c0ecf76",
  "preview": "examples/recipes/roof-slope-row.png",
  "techniques": [
   "connector seat",
   "snot"
  ],
  "subjects": [
   "roof",
   "slope row",
   "bonnet",
   "wedge surface"
  ]
 },
 {
  "id": "recipe-technic-pin-frame",
  "title": "Rigid Technic chassis: rails pinned to an open frame at two holes each",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-pin-frame"
  ],
  "families": [
   "recipe",
   "technic"
  ],
  "lesson": "join lays one part on another by matching holes and inserts the pins: {\"join\": {\"to\": \"frame\", \"holes\": {\"hole-0\": \"hole-0\", \"hole-6\": \"hole-6\"}, \"side\": \"-Y\"}} pins a 7-long beam (32524) to a 5 x 7 open frame (64179) at two holes. Two spaced pins make a joint rigid; one pin is a hinge, and a rectangle of single-pin joints folds. Parts: 64179, 32524, 2780.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-pin-frame.plan.json",
  "model": "examples/recipes/technic-pin-frame.mpd",
  "model_sha256": "660d3c3e746939835e0f5638503681966c6f73ead0a11c64d7565c75564ba167",
  "preview": "examples/recipes/technic-pin-frame.png",
  "techniques": [
   "join",
   "two-pin joint",
   "technic"
  ],
  "subjects": [
   "technic chassis frame",
   "technic frame",
   "chassis",
   "beam frame",
   "pin joint",
   "rigid joint",
   "liftarm pin joint"
  ]
 },
 {
  "id": "recipe-technic-gear-pair",
  "title": "Braced 8:24 gear pair: two shafts in two beams, bushed both sides",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-gear-pair"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "8 + 24 teeth mesh 1.25 x (8 + 24) = 40 LDU apart, so the shafts go in holes two apart (hole-1, hole-3). Each shaft runs in two beams; the second beam sits on the shafts with on {to: input, hole: hole-1, pin: shaft, next_to: input-gear, side: +X} plus orient, and a bush outside each beam stops the shafts sliding. The mechanism contract checks that the input turns the output. Parts: 32524, 32073, 3647, 3648b, 3713.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-gear-pair.plan.json",
  "model": "examples/recipes/technic-gear-pair.mpd",
  "model_sha256": "a78ade93596a846fad839e326458f948271c45ea473a75c617a0e93d3d068ea6",
  "preview": "examples/recipes/technic-gear-pair.png",
  "techniques": [
   "technic seat",
   "next_to",
   "mechanism contract"
  ],
  "subjects": [
   "gear train",
   "gear pair",
   "spur gears",
   "gear ratio",
   "transmission",
   "gearbox",
   "reduction"
  ]
 },
 {
  "id": "recipe-technic-rack-steering",
  "title": "Rack-and-pinion steering: kingpin hubs, L-liftarm arms and a 1 x 7 rack",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-rack-steering"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "Kingpins are 4-long axles turning in the open frame's front corner holes; on each sit a cross block hub (6536, its round hole carries an axle-pin wheel stub), a bush and an L-liftarm steering arm (32140, flip on the left one). The 1 x 7 rack (87761) is pinned to both arms' short ends: a parallelogram. A 12-tooth pinion (32270) on a shaft through both frame ends meshes 20 LDU above the rack; turn the knob at the back, or add a bevel corner to bring it up. Contract: input pinion-shaft moves rack and both hubs, 1 degree of freedom.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-rack-steering.plan.json",
  "model": "examples/recipes/technic-rack-steering.mpd",
  "model_sha256": "80b7aae758d24cfa07672ba1378f51aa76958baf642a836a8cfdb45fda6aa799",
  "preview": "examples/recipes/technic-rack-steering.png",
  "techniques": [
   "technic seat",
   "join",
   "flip",
   "mechanism contract"
  ],
  "subjects": [
   "rack and pinion steering",
   "steering",
   "front axle",
   "kingpin",
   "steering rack",
   "pinion",
   "tie rod"
  ]
 },
 {
  "id": "recipe-technic-wheel-axle",
  "title": "Wheel on an axle carried by two pinned beams",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-wheel-axle"
  ],
  "families": [
   "recipe",
   "technic",
   "vehicle"
  ],
  "lesson": "Two beams on edge pinned side by side (join with two hole pairs) make a two-stud-deep bearing. A 5-long axle runs through both, a bush stops it inside, a half bush spaces the rim (56145) clear and the tyre (55976) goes on with snap: {\"snap\": {\"to\": \"rim\"}}. Parts: 32524, 32073, 3713, 32123a, 56145, 55976.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-wheel-axle.plan.json",
  "model": "examples/recipes/technic-wheel-axle.mpd",
  "model_sha256": "119e41182f201292a510eeb909763ee2c35b8923baf33382ea128556fab7341f",
  "preview": "examples/recipes/technic-wheel-axle.png",
  "techniques": [
   "technic seat",
   "join",
   "snap",
   "next_to"
  ],
  "subjects": [
   "wheel hub axle",
   "wheel",
   "axle bearing",
   "tyre",
   "rim",
   "wheel mount"
  ]
 },
 {
  "id": "recipe-technic-bevel-corner",
  "title": "Drive turned 90 degrees by two 12-tooth double bevels in an open frame",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-bevel-corner"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "Two 12-tooth double bevels (32270) mesh with each centre 20 LDU from where the shafts cross. The shafts enter the open frame (64179) through a side hole and an end hole, reach 10 LDU short of the crossing, and the gears sit on their inner ends with slide; a bush outside the frame retains each shaft. Each gear is within two studs of its bearing. Parts: 64179, 3705, 32270, 3713.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-bevel-corner.plan.json",
  "model": "examples/recipes/technic-bevel-corner.mpd",
  "model_sha256": "e9b21c19d714dfa5a99c83efcb9e791f0c0041bdf7f56aa4072fe98526b3e1e4",
  "preview": "examples/recipes/technic-bevel-corner.png",
  "techniques": [
   "technic seat",
   "slide",
   "mechanism contract"
  ],
  "subjects": [
   "bevel gears",
   "right angle drive",
   "drive around a corner",
   "perpendicular gears",
   "double bevel"
  ]
 },
 {
  "id": "recipe-technic-worm-drive",
  "title": "Worm driving a 24-tooth gear between two open frames",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-worm-drive"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "A worm (4716) meshes a gear whose axis passes 10 + its pitch radius away: 40 LDU for 24 teeth (3648b). Two open frames (64179) stacked two studs apart on spacer beams carry the gear shaft along X and the worm shaft along Z; long friction pins (6558) go through frame, spacer and frame. Bushes back the worm on both sides against its thrust. Parts: 64179, 32524, 6558, 3706, 3707, 3648b, 4716, 3713, 32123a.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-worm-drive.plan.json",
  "model": "examples/recipes/technic-worm-drive.mpd",
  "model_sha256": "ea3a5241923eab8d0a0e6e6819f89b37b185b188ad7d8ad0aca353382c631602",
  "preview": "examples/recipes/technic-worm-drive.png",
  "techniques": [
   "technic seat",
   "join",
   "long pins",
   "mechanism contract"
  ],
  "subjects": [
   "worm gear",
   "worm drive",
   "worm",
   "slow reduction",
   "self locking"
  ]
 },
 {
  "id": "recipe-technic-suspension-arm",
  "title": "Swing arm on a frictionless pin, sprung by a 6.5L shock absorber",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-suspension-arm"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "The arm pivots on one frictionless pin (join pins: 3673.dat). The 6.5L shock (76537) has eyes 110 LDU apart, which never lands on the stud grid, so the arm turns to the angle the triangle needs: with the mount 80 and the arm hole 100 from the pivot, the law of cosines gives 74.41 degrees; the shock's own roll is then read off the build. The contract counts one degree of freedom: the shock slides as the arm swings. Parts: 32524, 32523, 76537, 3673, 2780.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-suspension-arm.plan.json",
  "model": "examples/recipes/technic-suspension-arm.mpd",
  "model_sha256": "c793fdf20933cf729b83521efbd416dd822861e783ffa49ee8c62a96ad7a5df3",
  "preview": "examples/recipes/technic-suspension-arm.png",
  "techniques": [
   "join",
   "frictionless pin",
   "mechanism contract"
  ],
  "subjects": [
   "suspension shock absorber",
   "suspension",
   "swing arm",
   "shock absorber",
   "pivot",
   "liftarm pin joint",
   "hinge"
  ]
 },
 {
  "id": "recipe-technic-cylinder-lever",
  "title": "Lever raised by a pneumatic cylinder to a rigid mount",
  "scope": "construction",
  "kind": "recipe",
  "aliases": [
   "recipe:technic-cylinder-lever"
  ],
  "families": [
   "recipe",
   "technic",
   "mechanism"
  ],
  "lesson": "A pneumatic cylinder (74981-f2, extended, eyes 116 LDU apart) pins to a lever and to a mount with frictionless pins; the lever pivots on one frictionless pin. The lever angle follows from the triangle: mount 80 and lever hole 100 from the pivot give 79.40 degrees. The contract checks the cylinder moves the lever (1 degree of freedom). Hoses go on afterwards: see the flex guide. Parts: 32524, 32523, 74981-f2, 3673, 2780.",
  "limits": "Small checked recipe: build passed every Technic check and its mechanism contract, review passed with matching BOMs, and the preview was inspected on 2026-11-17. It shows the built pose; it does not simulate motion or certify strength.",
  "plan": "examples/recipes/technic-cylinder-lever.plan.json",
  "model": "examples/recipes/technic-cylinder-lever.mpd",
  "model_sha256": "f4d22cbfc72e2c251b25c7e62b1599f3d9454e99aa794860bebbe8d2bda34121",
  "preview": "examples/recipes/technic-cylinder-lever.png",
  "techniques": [
   "join",
   "frictionless pin",
   "mechanism contract"
  ],
  "subjects": [
   "pneumatic cylinder mount",
   "linear actuator",
   "cylinder lift arm",
   "lever",
   "pneumatic lift",
   "actuator mount"
  ]
 }
]
```
