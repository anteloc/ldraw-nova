# SNOT recipes

Small plans that place sideways parts with connector seats (`on: {to, face, stud, socket}`) instead of hand-written matrices. Each builds and reviews cleanly; copy the placements and change parts, colours and studs.

| Recipe | Plan | Preview |
|---|---|---|
| Cover a side-stud course with a tile | [side-stud-cover.plan.json](side-stud-cover.plan.json) | ![Cover a side-stud course with a tile](side-stud-cover.png) |
| Headlight brick with a round lens | [headlight-lamp.plan.json](headlight-lamp.plan.json) | ![Headlight brick with a round lens](headlight-lamp.png) |
| Upward bracket carrying a front grille | [bracket-grille.plan.json](bracket-grille.plan.json) | ![Upward bracket carrying a front grille](bracket-grille.png) |
| One panel module seated on both sides of a core | [side-panels.plan.json](side-panels.plan.json) | ![One panel module seated on both sides of a core](side-panels.png) |
| Window frame and glass between brick columns | [window-wall.plan.json](window-wall.plan.json) | ![Window frame and glass between brick columns](window-wall.png) |

Rebuild and review one:

```sh
./ldraw-agent review examples/snot-recipes/side-stud-cover.plan.json --outdir output/recipes/side-stud-cover
```

Evidence: each recipe passed `review` with matching Python and LeoCAD BOMs, and its home view (the PNG beside the plan) was opened and checked on 2026-11-15. The MPD beside each plan is the reviewed model.

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
  "limits": "Small checked recipe: review passed with matching BOMs and the home view was inspected. It does not certify clutch or strength.",
  "plan": "examples/snot-recipes/side-stud-cover.plan.json",
  "model": "examples/snot-recipes/side-stud-cover.mpd",
  "model_sha256": "80668e3c1d55047b15de4a6bf1c39f17791be02f7fd7600451ad89c114252fcc",
  "preview": "examples/snot-recipes/side-stud-cover.png",
  "techniques": [
   "snot",
   "connector seat"
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
  "limits": "Small checked recipe: review passed with matching BOMs and the home view was inspected. It does not certify clutch or strength.",
  "plan": "examples/snot-recipes/headlight-lamp.plan.json",
  "model": "examples/snot-recipes/headlight-lamp.mpd",
  "model_sha256": "f52aefc7f2cd14dfd01d37ed3e0de72a2f6ce976c8a42f73fa97c29e04517b53",
  "preview": "examples/snot-recipes/headlight-lamp.png",
  "techniques": [
   "snot",
   "connector seat"
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
  "limits": "Small checked recipe: review passed with matching BOMs and the home view was inspected. It does not certify clutch or strength.",
  "plan": "examples/snot-recipes/bracket-grille.plan.json",
  "model": "examples/snot-recipes/bracket-grille.mpd",
  "model_sha256": "74bc2a8b36027ac4a0d503d9fb80f7463854a05c1830953eb26f92a64f5540c3",
  "preview": "examples/snot-recipes/bracket-grille.png",
  "techniques": [
   "snot",
   "connector seat"
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
  "limits": "Small checked recipe: review passed with matching BOMs and the home view was inspected. It does not certify clutch or strength.",
  "plan": "examples/snot-recipes/side-panels.plan.json",
  "model": "examples/snot-recipes/side-panels.mpd",
  "model_sha256": "d59d655316bcbf0f45c678b4b717a4d5f6c95c1878dd6babeab749e811f0b80b",
  "preview": "examples/snot-recipes/side-panels.png",
  "techniques": [
   "snot",
   "connector seat"
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
   "snot"
  ],
  "lesson": "A 1 x 2 x 2 window frame stands on a sill plate between 1 x 1 brick columns; its glass shares the frame origin (48 LDU above the sill top). A lintel plate seated on the frame studs (socket 1) ties frame and columns together. Parts: 60592, 60601, 3005, 3710.",
  "limits": "Small checked recipe: review passed with matching BOMs and the home view was inspected. It does not certify clutch or strength.",
  "plan": "examples/snot-recipes/window-wall.plan.json",
  "model": "examples/snot-recipes/window-wall.mpd",
  "model_sha256": "8064020bedc45eb2e196e6d884bc745c164f9898fd73da23e0029b2b2c802471",
  "preview": "examples/snot-recipes/window-wall.png",
  "techniques": [
   "snot",
   "connector seat"
  ],
  "subjects": [
   "building window",
   "wall opening",
   "facade"
  ]
 }
]
```
