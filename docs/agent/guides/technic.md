# Build supports, retained shafts and body mounts

Design the skeleton, load direction, body and mounts together. Use fixed-structure contracts for static frames; use joint scope for declared mounts in a delivered mechanism pose. These checks do not verify motion. For requested motion, follow [mechanisms](mechanisms.md).

Search current knowledge by the required role. A catalog entry is a discovery candidate, not a reviewed seating or motion profile. Exact registry and contract semantics belong in the [Technic reference](../reference/technic.md).

## Start from the structure and its mounting points

Record the silhouette, support/load direction, dimensions, palette and body attachment locations. Design the skeleton and visible body together; filling the body first can leave inaccessible joints.

```sh
./ldraw-agent technic list
./ldraw-agent technic parts 64179
./ldraw-agent technic parts 2780
./ldraw-agent examples --family technic
./ldraw-agent technic plan box-chassis --output output/chassis.plan.json
./ldraw-agent review output/chassis.plan.json \
  --views home front back right left top bottom
```

`technic plan` exports an assembly plan and a sibling `.structure.json` contract, linked by the section's `structure` property. `build` and `review` run that contract automatically. Review puts the results in `validation.json` under `structure`, with a frozen contract copy. Open the previews. Use `review PLAN --no-render --force` for intermediate checks after edits; finish with rendered review.

Use `--force` to replace an exported plan and contract. `--colour` and `--accent` change the palette; `--levels 1|2|3` changes the tower. [technic_recipes.py](../../../ldraw_tools/technic_recipes.py) exposes placements and mounting pairs for adaptation. Existing plans can add `"structure": "frame.structure.json"` to the relevant section. Standalone `technic check MODEL --contract CONTRACT` remains available for MPDs, selected sections and old plans.

## Seat the joints before closing the frame

```sh
./ldraw-agent connectors output/chassis.mpd --occurrence 0
./ldraw-agent snap output/chassis.mpd --moving 1 --fixed 0 --limit 5
```

Reviewed mechanical port IDs begin with `technic:`. `connectors`, `snap` and geometry inspection use them for supported geometry. `part` still exposes raw library metadata for comparison. Existing stud interfaces remain available; the half pin also supplies its missing System stud interface.

Snapping aligns a grip with its receiving bore, considers axial positions and preserves keyed orientation. Read `collision.status`, `interface_errors`, truncation and remaining review items. Blocked candidates cannot be applied. `--allow-occupied` cannot permit overlapping occupation of a reviewed hole or shaft span. Distinct axle intervals remain available for other members and bushes.

Normal `validate --geometry` and `inspect` report invalid seating, incomplete grips and conflicting occupation when contacts are computed. Large models still need module checks or explicit `--contacts all`; the normal automatic limit is 500 placements. General material intersections need the ordinary geometry checks and visual inspection too.

Insert pins into a supported member before bringing the closing member onto their exposed ends. Add shaft spacers and supports before installing the final retainer. Check both escape directions of a retaining stack. A correct final pose does not prove that the parts can be inserted with every surrounding member already present.

## Find structural references and finish the appearance

Start with local knowledge search. If broader raw-source discovery is needed, use offline FTS; Jev is optional after its [availability check](../reference/cli.md#check-jev-availability-before-searching):

```sh
./ldraw-agent discover search submodels 'a compact braced chassis frame' \
  --construction technic-structure --engine fts --limit 5
```

When unavailable, use `--engine fts`, the local catalogs and examples. Identify offline keyword ranking explicitly. The construction filter considers the selected description and actual BOM, excludes obvious mechanism contents, and allows static sections from mechanism-bearing parents. It does not prove every axle in a “chassis” is structural. Inspect parent support, mounting interfaces and build order; preserve attribution and extraction manifests.

The [submodel atlas](../../../examples/submodel-atlas/README.md) shows reviewed Technic sections whose parents supply what the section lacks: the pinion for a steering rack (01) and the tilt of a differential axle (02). It also shows a System lamp cluster on a Technic mount (04).

Keep the skeleton's main lines clear, control its palette and reserve real mounts for panels or System cladding. Expose structure where it explains the subject; organize connector clutter elsewhere. Compare all seven views and a thumbnail. Fix proportions and unsupported mounts before adding decoration. Deliver the MPD, plan/generator, contract, checks, BOM comparison and visual review of the final revision.

## Choose a construction by function

| Intended feature | Pattern and construction lesson | Starting example |
| --- | --- | --- |
| Visible drive route | [Parallel gears](mechanism-patterns/transmissions.md#parallel-gear-trains): preserve shaft lines and tooth planes | W16's three crankshafts |
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

These are patterns, not a list of permitted subjects. A car's wing linkage can
teach a cargo lift; its engine can teach a pumping station. The new context still
needs its own mounting structure, dimensions and review.

