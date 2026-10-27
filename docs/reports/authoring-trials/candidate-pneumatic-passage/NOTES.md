# Pneumatic passage trial

Completed adaptation of the mounted pneumatic press starter. The silhouette remains a tall yellow/grey press on a square grey bench, with a standing hand pump at the left, valve at the front, extended cylinder in the frame, black supply hose and red/blue cylinder hoses. The yellow guard with black cap sits beside the supply passage. Bounds are 320 × 244 × 320 LDU (X/Y/Z), including studs; the bench is 16 × 16 studs.

## Reproduction

From the repository snapshot root:

```sh
.venv/bin/python output/trials/pneumatic-passage/run.py .venv/bin/python output/trials/pneumatic-passage/generate.py
.venv/bin/python output/trials/pneumatic-passage/run.py ./ldraw-agent review output/trials/pneumatic-passage/model.plan.json --outdir output/trials/pneumatic-passage/review --views home front back right left top bottom --contacts all --detail full --limit 300 --force
```

`starter.plan.json` preserves the supplied source and attribution. `generate.py` makes the final editable JSON plan. `review/model.mpd` embeds all parts and synthesized hose geometry. The review folder contains frozen source, LSynth constraints, manifests, checks, both BOMs, comparison and previews.

## Fitting changes and mounting

- Pump: starter origin `[-120,-14,-20]` becomes `[-100,-14,-20]`, a 20 LDU / one-stud move in +X. Starter rotation `[[0,0,-1],[0,1,0],[1,0,0]]` becomes identity: +90 degrees around +Y. Its nozzle now faces -Z. The original four-stud mounting requirement remains and passes.
- Valve: starter origin `[40,-56,-110]` becomes `[40,-56,-150]`, a 40 LDU / two-stud move toward the front (-Z). Rotation is unchanged. Its two-stud deck mounting requirement remains and passes.
- Cylinder: the supported `74981-f2` extended pose and 116 LDU eye spacing are unchanged. Both mounting pins retain their beam/cylinder/head connections.
- Guard: yellow `3004` brick at `[-40,-24,-130]`, black current `3023b` cap at `[-40,-32,-130]`. Both new two-stud joints are declared and pass. The guard remains in the final model and BOM.

## Checks and measurements

Final whole-model review passes validation, rendering, and BOM comparison: 43 Python and 43 LeoCAD physical placements, no differences. All eight required joints pass. All three hoses retain minimum sampled radius 15 LDU, round tube radius 5 LDU and minimum separation 10 LDU. Measured minimum radii are 20.686 / 22.621 / 21.780 LDU for supply / line-up / line-down. Pair separations are 12.530 / 12.518 / 16.357 LDU for supply–up / supply–down / up–down.

One failed review-to-source repair cycle was required: the initial supply curve had a 10.288 LDU bend. The passage was enlarged by moving the valve farther forward and giving the supply a deeper midpoint. The subsequent review passed. After a successful review, the cap's obsolete 3023 alias was replaced with its current target 3023b; this was warning cleanup, not another failed review cycle. No check was relaxed. See `repair-log.md` and the numbered command logs.

## Images actually opened

Final-revision `home`, `top`, `front`, `right`, `back`, `left`, and `bottom` PNGs were opened with the image-view tool after the final review. Exact paths, UTC opening times and measured image-tool durations are in `images-opened.json`. Earlier-revision openings are kept separately and are not used as final evidence.

- Home and top show the black hose turning behind the guard with a visible free passage; the guard is attached to deck studs. The red/blue routes remain to the right of the press body.
- Home, front, right and left show the pump sleeve and all three valve sleeves seated on the fittings. The straight departures are visible before the curves. The side views distinguish the three vertically separated valve connections.
- Front, home, right and back show the red base sleeve and blue rod-side sleeve on the cylinder. Both cylinder eyes remain pinned to the beam/head.
- Back and side views show the accessible pin ends and the press-head/anvil separation in this static pose. Pump and valve bases meet the deck; there are no visibly floating rigid pieces.
- Bottom shows the bonded lower deck seam and plate undersides. It does not expose the hidden top-side stud sockets; their engagement is supported by the required-joint checks and the other views.

## All conservative candidates reviewed

The detailed geometry report has 64 untruncated overlap candidates. Forty-two have detected intended connections: bonded deck plates, column courses, frame cap/top, anvil/head layers, pump/valve/guard stud mounts, and cylinder pin/eye/beam/head joints. The contextual views show their intended seating rather than unrelated body intersections.

The remaining 22 pairs were reviewed explicitly:

- Six hose-to-fitting pairs: supply/pump, supply/valve, red/cylinder, red/valve, blue/cylinder, blue/valve. These are also all six sampled `flex.obstacle_bounds` warnings. The visible overlaps are the intended nozzle sleeves; straight departures clear the fitting bodies.
- Supply/guard and supply/guard-cap: whole-route bounding boxes include empty interior space. Top and home show the actual black tube behind the guard, without touching it. The sampled tube-envelope check does not flag either guard part.
- Three hose/hose bounding pairs: their large boxes overlap, while the actual sampled routes pass the unchanged 10 LDU pair-separation check and appear separated in home/top/side views.
- Nine hose/press-work-area pairs: blue/anvil-a; red and blue against each of anvil-b, anvil-plate, anvil-face and die. Home/top/right show the actual red and blue curves outside the anvil and die, despite the enclosing boxes crossing that work area. None is a sampled tube obstacle candidate.
- Cylinder/beam and cylinder/head: bounding depth is about 0.000255 LDU at the adjoining eye faces. Front/back/right show the intended pin-mounted eye interfaces. The four named pin joints pass; no visible unrelated body penetration is apparent.

## Remaining coverage limits

Checks and visual inspection do not prove physical strength, pressure-circuit operation, stock/manufactured hose lengths, elasticity, full motion clearance or general collision freedom. The valve is not in the reviewed Technic structural-interface registry, although its named two-stud mount passes generic connection checks. Generated hoses lack connector metadata, so connection analysis reports one rigid assembly plus three hose components. No automated connector-before-closure constraints were supplied by this starter; insertion access was inspected visually at the exposed front/back pin ends, without swept-path analysis. The cylinder is delivered in one extended static pose.

Jev prerequisites and one bounded uncached authentication query succeeded (one API call). No semantic reference search was needed beyond the prescribed starter and inspected parts.

## Time accounting

The trial started at 2026-10-27T05:54:28Z. A platform usage interruption paused work after the last completed wrapped command, estimated at 05:59:57.694174Z, until the first resumption clock reading at 10:56:40Z. That estimated pause is recorded in `infrastructure-pause.json` and excluded from active elapsed time. Substantive CLI/generator command durations come from `commands.jsonl`. Image-tool durations were measured separately around tool calls. File reads, note writing, tool-dispatch overhead and reasoning were not individually timed; they remain included in active elapsed time and are not fabricated as command time.
