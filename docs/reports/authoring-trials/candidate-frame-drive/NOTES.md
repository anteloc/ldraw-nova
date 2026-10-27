# Frame-drive candidate trial

Started 2026-10-27T05:58:16Z; deadline 2026-10-27T06:28:16Z.

Intent: a compact industrial service platform, grey structural frame and deck,
yellow braces/bearings/crank, black axles and retaining bushes, white rear housing.
The drive is longitudinal over the front deck, with its handle projecting from the
right side. Preserve wheel spacing (120 LDU), paired bearings and all axial stops.

Source: the mounted-frame and retained chain-drive workshop JSON plans, copied
unchanged into source-inputs for provenance. The workshop machine puts its drive
at [0,-8,40] without rotation; this assembly puts it at [10,-106,-70], rotated 90°
about Y, directly atop the service platform front deck. Twelve decorative tiles
were removed to expose its stud mounting surface. The rear housing stays.

All original named joints and insertion contracts remain. Frame STEP 2's four
independent pins and drive STEP 4's four independent bearings are reversed within
their original STEP. Each connector still precedes the dependent assembly STEP.
A named whole-assembly joint checks deck-front to drive/base, and twelve new
joints check the drive support stacks. The frame rigidity contract remains;
moving drive assemblies retain their original joints scope.

Availability: doctor passed with installed parts, LeoCAD and LSynth. Jev live
availability query succeeded with 1 API call; source selection used the explicit
supplied workshop starters. No discovery ranking was needed.

Initial visual study: opened mounted-frame home and chain-drive top previews.
The former shows the eight mounted deck supports over the rectangular braced
core; the latter exposes paired bearings, wheel spacing and axial retaining stack.

Repair log: no failed review/source-correction cycles yet.

Timing: substantive CLI/generator commands run through run.py into commands.jsonl.
Initial reads, source-file writing, image tools and reasoning are not individually
wrapper-timed; they count in total elapsed wall time and are not fabricated.

Infrastructure interruption: estimated 2026-10-27T06:00:19.387419Z to 2026-10-27T10:56:33Z (17,773.612581 s), excluded from active budget per resumed instructions. Boundary is estimated from last completed timed command to resumption clock read. Prior active elapsed: 123.387419 s. Original absolute deadline superseded by active-time budget.

Repair cycle 1: first whole-model review failed two newly declared base-to-lower-rail joints. Part 3036 has stud rows at local z=+/-10,+/-30,+/-50, while source rails sit at +/-40. Shifted only the drive base to [0,0,10] and compensated the assembly placement to [0,-106,-70]. Base now seats on both rails while remaining exactly over frame/deck-front. All wheel, axle, bearing, spacer and stop coordinates remain unchanged. Checks retained. Failure evidence: review-01-failed.json.

Final review: whole-model review passed validation, BOM export, seven-view LeoCAD
rendering and BOM comparison. Both BOMs count 101 physical placements, including
24 chain links. All 40 frame joints, 37 drive joints (25 retained plus 12 added),
and the root deck/base joint pass. The frame retains 20 insertion constraints and
the drive retains 3; all original retained-axle requirements remain active.

Final images opened: review/previews/home.png, front.png, back.png, right.png,
left.png, top.png and bottom.png. Home shows the longitudinal drive mounted above
the front deck and the crank extending outside the right support. Top exposes both
paired bearings and contiguous gear-spacer/bush stacks. Front/back show the centered
chain, accessible crank and vertical clearance above the deck and rear housing.
Right/left expose the two support courses and chain runs. Bottom exposes the open
box frame, both supporting rails and plate underside in the assembled context.
No obvious new body intersection or open chain gap was seen in these views.
The static pose is inspected; continuous operation is not certified.

The full existing `inspect` report (inspection.json) was requested because summary
review intentionally omits the overlap rows. It has 221 contacts and 142 bounds
candidates. The front deck/base interface has 48 stud contacts; each corrected
base/lower-rail interface has eight. All non-chain drive parts and the frame belong
to the same optimistic connection component. The 28 singleton components are the
24 chain links and four round roof beacons. The beacon part lookup finds a female
interface at local [0,8,0], exactly at the roof stud plane when placed; it is
classified as a pin hole rather than a stud socket in the available metadata.
The beacons are visually seated on the four corner studs. This is recorded as a
connection-evidence coverage gap, without changing metadata or checks.

Bounds candidates include normal stud engagement, pins through frame holes,
shafts through bearings/bushes/gears, chain-tooth engagement and neighboring links.
These were reviewed against the seven assembled views; no complete material
intersection or dynamic-collision proof is claimed. The chain interface registry
is unreviewed, closure/engagement is visual only, and the checker does not certify
tension, strength, manufactured chain fit or motion. Top-level stud mounting can be
pressed down from above; automated insertion-path simulation is unavailable.

Repair count: one failed review followed by one source correction, then passing
review. An auxiliary report-printing command also exited 1 because it assumed
`structure` was a list; it made no source change and is not a model repair cycle.
No intervention, toolkit modification, dependency change or external expert repair.

Final measured bounds: X -99.5..154.5, Y -217..70, Z -152.562575..170 LDU;
size approximately 254 x 287 x 322.563 LDU. Source changes and exact STEP reorder
lists are in source-changes.json. Final drive pose is [0,-106,-70] with +90° Y
rotation; the local base offset [0,0,10] preserves its world position over the deck.

Reproduce from this snapshot root:

```sh
.venv/bin/python output/trials/frame-drive/run.py .venv/bin/python output/trials/frame-drive/generate.py
.venv/bin/python output/trials/frame-drive/run.py ./ldraw-agent review output/trials/frame-drive/model.plan.json --outdir output/trials/frame-drive/review --views home front back right left top bottom --contacts all --force
```

`model.plan.json` is also a complete editable source without needing the generator;
`review/model.mpd` embeds the chain geometry and opens without LSynth.
