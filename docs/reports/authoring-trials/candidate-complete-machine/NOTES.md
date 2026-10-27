# Complete-machine candidate authoring record

Requested silhouette: compact rectangular braced workbench, exposed hand-cranked
chain conveyor and overhead pneumatic stop. The supported 120 LDU shaft spacing,
10L drive / 8L idler shafts and extended cylinder's 116 LDU mounting-eye separation
are preserved. Bench footprint is 320 × 320 LDU; crank and hose extents are measured
by the final review. Negative Y is up.

Palette: dark blue (272) System guard/bodywork, orange (25) safety courses and
tiles, neutral grey structural hardware and deck; black/red/blue pneumatic hoses.
The added side rails are mounted to actual bench studs with required joint checks.
The original front guard and all its top tiles also gain attachment checks.

Precedent: `examples/workshop/workshop/model.plan.json`, via the existing
`ldraw_tools.workshop.workshop_plan` recipe. Source author attribution is retained.
No reference-model extraction was used. The ordinary JSON plan is self-contained;
`generate.py` reproduces it using the existing toolkit. Internal mechanical dimensions and hose
limits are preserved; visible bodywork is recoloured and side safety rails added.

Environment: `doctor` passed. Jev prerequisites exist and the bounded uncached
`brick` availability query succeeded with one live API call. No external advice
or agent repair was used.

## Repair log

- Initial authoring: recoloured bodywork, added both safety rails and their tile
  attachment checks. No review correction yet.

## Timing

First clock observation: 2026-10-27 11:00:37 UTC, following initial instructions and
brief reads. That pre-clock interval was not measured. A conservative 11:00:00 UTC
origin is used for the 90-minute budget. Substantive commands are timed by `run.py`
in `commands.jsonl`. Reading, editing, image-opening and reasoning time is not
individually instrumented and will be identified separately in the result.

## Limits

The delivery is one extended static pose. It does not verify dynamic pneumatic
control, cylinder travel, changing hose slack, pressure, chain tension, material
strength, physical transport, commercial part/colour availability, or stock hose
length. LSynth chain links do not have complete connector metadata; tooth
engagement and closure require contextual image inspection. Geometric checks are
not a certification of general collision freedom or physical buildability.

## Review and repair cycle 1

The first whole-model review returned exit 0 and matching 170-placement BOMs.
Home/front/back/top/bottom images were opened. Four scoped chain images were
also opened. All original required joints and actual hose checks passed.
However, investigation of the disconnected-evidence warning using the existing
`inspect --detail full --contacts all` tool revealed a separate 33-placement
rigid conveyor group. The `3036` base's stud rows and the two `3008` lower rails
were offset by 10 LDU in Z. The initial source and evidence are retained in
`revision-1.plan.json`, `revision-1-review`, `revision-1-chain-review`, and
`revision-1-inspection.json`.

Correction: move every rigid conveyor placement except its mounted base by
+10 LDU in Z; the chain follows its actual wheel placements. Shaft spacing,
shaft lengths, supports, retaining stacks and crank relationships are unchanged.
Add two required joints with eight studs each between the base and lower rails.
This is counted as one failed manual review → source-correction cycle despite
the first CLI review's selected checks returning success.

## Infrastructure pause

The platform usage interruption is estimated from the last completed command,
2026-10-27T11:04:16.594110+00:00, through the first resumed clock observation,
2026-10-27T16:44:44+00:00. Both pause boundaries are labeled estimated; this
interval is excluded from active time. The initial 11:00:00 budget origin remains
a conservative estimate preceding the first measured clock observation.

## Final evidence, revision 2

The final whole-model review passes validation, all declared structural scopes,
rendering and BOM comparison. Python and LeoCAD each count 170 physical placements,
with no BOM differences. Full contact analysis ran: no contact skip. The final
optimistic graph has one connected 143-part rigid group, 24 individually posed
chain links and three hoses. Thus the repaired base mounting eliminates the
extra rigid conveyor group; the remaining disconnected-evidence warning is
accounted for by flexible-part metadata coverage.

Required joint counts: workshop 61, fixed box-chassis 24, chain-drive 27. The two
main shafts and handle axle retain their axial-stop checks and insertion STEPs.
The overall final bounds are X -160..160, Y -260..176, Z -160..204.5 LDU.

The actual synthesized hose measurements are:

| Route | Sampled minimum radius (LDU) | Required (LDU) |
| --- | ---: | ---: |
| supply | 20.115343 | 15 |
| raise | 19.817444 | 15 |
| lower | 21.805396 | 15 |

All three preserve tube radius 5 LDU and minimum pair separation 10 LDU. Pair
separations are 12.529964 (supply/raise), 12.529434 (supply/lower), and 11.200237
(raise/lower) LDU. Nonlocal self-separation checks pass. These are the existing
tool's finite sampled geometry results, not manufactured hose lengths.

Fresh final images actually opened:

- `final-review/previews/home.png`: complete machine, mounted blue guard rails,
  orange accents, mounted controls, exposed cylinder and sleeve locations.
- `final-review/previews/front.png`: extended cylinder, stop head and separate
  red/blue routes; both braced trestles visible under the bench.
- `final-review/previews/back.png`: rear access, cylinder pins and crank clearance.
- `final-review/previews/bottom.png`: two supporting frames, underside rails and
  the bench mounting layout; no separate floating rigid frame is visible.
- `final-review/previews/top.png`: deck arrangement, free rear handle access,
  pump-to-valve supply passage and routed red/blue hose corridor.
- `chain-review/previews/home.png`: continuous posed chain over both gears,
  spacer stacks, bearings and external stops; the corrected lower rails sit
  on real base studs. No visible link break in this view.
- `chain-review/previews/top.png`: parallel supported shafts, equal wheel plane,
  contiguous retention stacks and exposed crank handle. This visual check does
  not measure chain closure or simulate tooth engagement through rotation.

The six hose obstacle-bound candidates are the endpoint pump, valve or cylinder
regions. I inspected their sleeves and adjacent routes in the final home/front/
back/top views; they appear seated at the intended nozzles, with no visible
intermediate hose penetration. Broad bounds include the fitting bodies' empty
space. Other general overlap candidates include intended stud, pin, gear and
chain interfaces; arbitrary material intersection is not certified.

The inherited `3023.dat` valve pad is a library alias. `part 3023` was inspected:
it resolves to `3023b`, has complete geometry and connector metadata, and the
actual two-stud valve/base connections pass. The alias is intentionally preserved
in the source/BOM, with this warning documented. The unreviewed-Technic warning
covers the 24 chain links and valve structural taxonomy; the actual valve stud
mount and named hose endpoints are checked separately. Shaft-bearing rotation
warnings are intended for this static mechanism.

Repair count: **1** failed manual review → source correction; no failed CLI
review exit. Interventions or outside expert repairs: **0**. No requested feature
was omitted. No toolkit, shipped source, dependency or validator was modified.

## Reproduce

Run from this snapshot's repository root:

```sh
.venv/bin/python output/trials/complete-machine/run.py .venv/bin/python output/trials/complete-machine/generate.py
.venv/bin/python output/trials/complete-machine/run.py ./ldraw-agent review output/trials/complete-machine/machine.plan.json --outdir output/trials/complete-machine/final-review --force --views home front back top bottom --contacts all --detail full --limit 1000
.venv/bin/python output/trials/complete-machine/run.py ./ldraw-agent review output/trials/complete-machine/machine.plan.json --section chain-drive.ldr --outdir output/trials/complete-machine/chain-review --force --views home top --contacts all
```

Open the fresh images after a rebuild. The editable MPD is
`final-review/model.mpd`; it embeds the synthesized hose geometry and chain and
can be opened without running LSynth. The frozen plan, contracts, original route
constraints, generated assets and manifests are in the same review bundle.
