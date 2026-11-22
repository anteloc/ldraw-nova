# Design Technic structures and mechanisms

The [Technic card](../cards/technic.md) covers placing parts by their ports and what the build checks. This guide is about choosing a construction: frames that hold, shafts that turn and mechanisms built the way a mechanical engineer would build them. Everything here is checked in the built pose; nothing is animated.

## Start from the skeleton

Write down the silhouette, the main dimensions in studs, where loads go and where the body attaches. Design the skeleton and the visible body together: a body built first leaves no room for joints. Lay out shaft lines and gear pairs on the stud grid before placing parts; `./ldraw-agent technic gears` gives the distances.

- **Frames.** Join beams with two pins per joint (`join` with two hole pairs), an L-liftarm (`32140`, `32526`) or a triangle. A rectangle of single-pin joints is a parallelogram and folds.
- **Shafts.** Run each axle in round holes of one rigid frame, in two bearings when you can, with a bush (`3713`, `32123a`) or a keyed part against each outer face. An axle in a cross hole of the frame cannot turn.
- **Gears.** Place a pair only at its mesh distance, with both shafts in the same beam or frame and each gear within two studs of a bearing. Back a worm on both sides.
- **Pivots.** A frictionless pin (`3673`, long `32556`) or an axle in round holes. Friction pins (`2780`, `6558`) lock.
- **Modules.** Build a repeated or mirrored assembly once in its own section and `join` it to the frame by its holes.

## Mount the body

- Technic bricks (`3700`, `3701`, `3894`) carry studs on top and holes through their sides: a System body sits on their studs.
- A half pin with a stud (`4274`) in a beam hole gives a single stud for a tile or plate.
- Panels (such as `64782`) and fairings hang on pins and axle-pins: seat the pin in the frame first, then the panel on it.

Keep the skeleton's main lines clear and its palette controlled; reserve real mounts for panels and cladding. Compare all seven views and a thumbnail; fix proportions and unsupported mounts before decoration. A vehicle body clad in System bricks also gets the mandatory [silhouette pass](design-models.md#soften-blocky-vehicle-silhouettes).

## Choose a construction by function

| Intended feature | Pattern and construction lesson | Starting example |
| --- | --- | --- |
| Visible drive route | [Parallel gears](mechanism-patterns/transmissions.md#parallel-gear-trains): keep shaft lines and tooth planes | W16's three crankshafts |
| Drive around a corner | [Bevel train](mechanism-patterns/transmissions.md#bevel-trains-and-winches): support each shaft and retain the drum | Defender winch |
| Slow adjustment | [Worm drive](mechanism-patterns/transmissions.md#worm-driven-adjustment): keep the wheel beside the finite threaded span | Mustang rear adjuster; local worm atlas |
| Split an axle or drivetrain | [Differential](mechanism-patterns/transmissions.md#differentials): distinguish carrier, side gears and spider | Defender front/rear/centre differentials |
| Route drive past obstacles | [Cardan shafts](mechanism-patterns/transmissions.md#cardan-shafts): preserve centres, yokes, crosses and phasing | Defender internal propshafts |
| Select a transmission path | [Driving rings](mechanism-patterns/transmissions.md#selectors-and-driving-rings): loose gears differ from axle-locked gears | Defender four-speed and range/direction boxes |
| Compact visible reciprocation | [Cam followers](mechanism-patterns/engines.md#cam-followers): guide the followers above phased cams | Defender inline-six |
| Recognizable crank engine | [Slider cranks](mechanism-patterns/engines.md#crank-and-connecting-rod-engines): keep rods, crank and guides distinct | Chiron W16 |
| Independent wheel corners | [Wishbones and shocks](mechanism-patterns/suspension-steering.md#suspension-corners): preserve pivot geometry and real mounts | Standalone Defender suspension |
| Steerable front axle | [Rack and links](mechanism-patterns/suspension-steering.md#rack-steering): connect rack, tie rods and knuckles | Defender steering; local rack atlas |
| Raise a platform without tilting it | [Four-bar lift](mechanism-patterns/lifts-and-linkages.md#orientation-preserving-lift): match arms and pivot spacing | Chiron rear wing |
| Indexed control detail | [Paddles and pawls](mechanism-patterns/lifts-and-linkages.md#paddles-pawls-and-indexing): retain hinges, return and detent context | Chiron stepper, with an incomplete drive relation |

These are patterns, not a list of permitted subjects: a car's wing linkage can teach a cargo lift. The starting examples are real-set extracts placed by coordinates; read them for proportions and part choices, then build with ports. The `technic-*` [recipes](../../../examples/recipes/README.md) are small checked plans you can copy.

## Find references in real sets

```sh
./ldraw-agent knowledge search 'rack and pinion steering'
./ldraw-agent search submodels 'steering rack'
./ldraw-agent discover search submodels 'a compact braced chassis frame' --construction technic-structure --engine fts --limit 5
```

`search submodels` reads the official sets' section titles; `discover` ranks and prepares them ([find references](find-references.md)). Inspect a reference's parent: it often supplies what the section lacks (the pinion for a steering rack, the bearings for a gearbox).

## Structure contracts and motion

A section's `structure` contract names joints that must exist and the order in which they are assembled ([Technic reference](../reference/technic.md#name-the-intended-connections)); a `mechanism` contract states what should move. For animation or travel studies, the separate `ldraw-mecha` project is optional; the [mechanisms guide](mechanisms.md) describes its relations.
