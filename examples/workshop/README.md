# Build a complete workshop assembly

These starters use ordinary JSON plans with named joints and inline flexible
routes. Read the [authoring guide](../../docs/agent/authoring.md), copy a plan to
`output/`, edit it, and run `review`.

| Starter | What it supplies |
|---|---|
| [Mounted frame](mounted-frame/model.plan.json) | The existing braced service platform and eight System deck mounts, with inline named structural intent. Its MPD geometry is unchanged. |
| [Retained chain drive](chain-drive/model.plan.json) | Two bearings per shaft, gear spacers, axial stops, a keyed hand crank and a 24-link chain loop. |
| [Pneumatic station](../flex/pneumatic-press/named.plan.json) | The existing mounted pump, valve and extended cylinder, three hoses, named nozzle endpoints and automatic mount checks. |
| [Workshop machine](workshop/model.plan.json) | Two braced trestles, bonded workbench, hand-cranked conveyor, gantry-mounted pneumatic stop, controls, three hoses and a mounted control guard. |

```sh
.venv/bin/python examples/workshop/generate.py workshop --output output/machine.plan.json
./ldraw-agent review output/machine.plan.json --views home front back top
```

Open the previews. After an edit, rerun with `--force`. For an intermediate
local check, use `review output/machine.plan.json --section chain-drive.ldr
--no-render`. That excludes surrounding parts and needs a final whole-model review.

The generator exports `chain-drive`, `mounted-frame` or `workshop`; `--colour`
and `--accent` set explicit LDraw colours. It refuses an existing source unless
`--force` is supplied. The Python functions in `ldraw_tools.workshop` return the
same dictionaries for composition and ordinary procedural changes.

## Adapt the supported construction

Change colours, equipment arrangement, module placement and mounted bodywork.
Named paths such as `conveyor/drive-axle` survive reordering. Changing actual
fitting poses regenerates their hose endpoints; change only the necessary
waypoints to reserve a clear corridor. Sources and generated files stay separate.

The chain recipe uses `4019.dat` wheels at **120 LDU spacing**, supported on
round `3700.dat` bearings. Its 10L drive shaft and 8L idler use contiguous
spacers and retaining bushes. A 3L thin crank carries a retained handle axle.
The mounting checks cover keyed engagement and the bearings; intended bearing
rotation is reported. Do not stretch links or change the spacing arbitrarily.

The pneumatic stop uses the **extended `74981-f2` pose**, with 116 LDU between
mounting eyes. Its nozzle frames and the pump/valve frames are measured and
fingerprinted. The supplied hose limits are geometric: 15 LDU sampled minimum
bend radius, 5 LDU round tube radius and 10 LDU separation. The raised control pads
and supply passage clear the conveyor base. Moving fittings can require a new
passage; the route helper does not solve obstacles or guarantee a bend radius.

The braced trestles keep fixed-structure contracts. The whole machine uses
`scope: joints` to check the actual mounts without declaring rotating shafts
or the pneumatic mechanism rigid. The same `review` checks every declared scope.

## Evidence and limits

The original press and structural fixtures remain unchanged. The simplified
press retains their rigid transforms and physical inventory; generated flex
section names identify the new inline routes. Tests also deliberately displace
mounts, reorder parts and move nested routes.

Inspect chain closure and tooth engagement, the shaft stops, cylinder eyes,
actual hose sleeves, underside mounts and all flagged obstacle candidates.
LSynth links lack full connector metadata. A bounds candidate at a fitting
does not by itself mean an intersection; other candidates must be investigated.

The delivered machine is one static pose with an intended hand-driven conveyor
and pneumatic stop. No animation, pressure circuit simulation, stock hose
length, tension, strength or physical transport test is claimed. The stop's
travel and hose slack through that travel require additional work if requested.
See the [verification record](../../docs/reports/authoring-simplification.md)
for automated checks, rendered evidence and independent trial results.
