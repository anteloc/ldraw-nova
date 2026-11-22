---
name: vehicles
description: 'Builds System vehicles (cars, trucks, vans, buses, boats, motorcycles) with SNOT bodywork: master layout (X across, -Z forward, Y=0 at the road), wheels first, scale and stance decisions, dedicated fittings (vehicle list, vehicle wheels, vehicle details, vehicle plan), inside-out build order, the mandatory silhouette pass that rounds blocky edges with SNOT curves, render-driven revision, plus the Ferrari F40 reference with five small body studies. Use when the subject is a car, truck, boat, motorcycle or other System vehicle (for a Technic chassis see the technic skill).'
---

# Vehicles

Build System road vehicles (cars, vans, trucks, buses), boats and motorcycles with SNOT bodywork: a master layout from the wheels outward, dedicated fittings, an inside-out build order and a render-driven revision, plus the Ferrari F40 reference. Shared principles are in [design-models](../SKILL.md). A Technic chassis with steering and suspension belongs to [technic](../../technic/SKILL.md) and [suspension-steering](../../technic/suspension-steering/SKILL.md).

## Start with a silhouette and the defining parts

Record era, purpose, character and viewing scale. Choose an arrangement (low bonnet/cabin/deck, cab-forward commercial body, separate cab/load bed…) and describe what distinguishes this vehicle from a generic wheeled box.

**Road vehicle frame:** X across, -Z forward, negative Y up, **Y=0 at the road**. Keep one master layout of tyre centres, axle stations, track, wheelbase, front/rear overhangs, body width, sill height, glazing base, roof height and cabin/bed boundaries. **Choose wheels before the chassis and bodywork**: the tyre envelope constrains everything around it. Boats use the interior hull floor as Y=0 (not the waterline); motorcycles use the measured frame axle spacing and tyre envelope.

| Decision | What to establish |
|---|---|
| Scale | Four-wide compact, six-wide town/display, eight-wide detailed, or a deliberate alternative; whether a real figure must fit |
| Stance | Track relative to body width, tyre diameter, ground clearance, wheelbase and overhang balance |
| Major masses | Bonnet length, windscreen rake, cabin position and height, rear deck or cargo volume |
| Surface language | A few related curves/slopes; deliberate transitions through nose, shoulders and tail |
| Identity | One strong front light/grille treatment and two supporting features |
| Palette | Body, roof, trim, chassis, metal, glass, head/tail lamps; keep broad surfaces quiet |

Use length/width, wheelbase/length and roof-height/length as comparisons to your subject, not pass/fail ratios: a bus, sports car and van should not share proportions. Decide early whether a cabin is display glazing or must hold seats, controls, a driver, headroom and access.

```sh
./ldraw-agent vehicle list
./ldraw-agent vehicle wheels
./ldraw-agent vehicle details
./ldraw-agent examples --family vehicle --details
./ldraw-agent design palettes heritage-racing
./ldraw-agent examples --family vehicle
./ldraw-agent vehicle plan grand-tourer --output output/tourer.plan.json
```

`vehicle plan` exports an ordinary version-1 plan plus `tourer.plan.brief.json`: an editable starting point, not a substitute for designing the requested vehicle. It does not scale parts or promise colour availability; change the brief and plan together. Older road recipes are retired from default retrieval.

## Choose dedicated parts before building substitutes

Compare whole vehicles for silhouette, then query one cab, bogie, wing, engine or hull role at a time ([find-constructions-and-parts](../../find-constructions-and-parts/SKILL.md)). `discover parts SAVED_SEARCH.json` exposes the fittings used in matched constructions. Use real seats, steering wheels, windscreens, mudguards, motorcycle frames, boat hulls, engine housings, printed instruments and cargo containers where they suit; reserve their envelopes and build the structure to their interfaces. Brick-built alternatives are fine when a dedicated part does not fit; state why in the brief.

```sh
./ldraw-agent vehicle details driver-cockpit --output output/cockpit.plan.json
./ldraw-agent vehicle details cargo-chest --palette desert-utility --output output/load.plan.json
./ldraw-agent examples cockpit --family vehicle --details
./ldraw-agent part-board 4079 3829c01 3039p34 30150 --outdir output/vehicle-fittings
./ldraw-agent search parts 'boat hull' --limit 8
```

| Recipe | Real fittings | Assembly contract |
|---|---|---|
| `driver-cockpit` | 4079 seat, 3829c01 steering stand/wheel, 3069bp25 printed dashboard | 2×6 floor; base underside Y=0; seat back extends past its floor |
| `pilot-cockpit` | 4079 seat, 4592/4593 control stick, 3039p34 instruments | 2×8 floor; upright static stick, front -Z |
| `wing-mirror` | 4070 side-stud mount and 3070b mirror tile | Recessed stud at Z=-6; tile face Z=-14, whole fitting yawed outward |
| `cargo-chest` | 30150 moulded open chest with handles | 3×4 pallet; half-stud centre offset on an even-width deck; replace tiles under it |
| `navigation-lights` | Paired transparent red/green round lamps | Four-stud crossbar, port -X/red, starboard +X/green |
| `jet-engine-pod` | 4868b engine shell and 4869 core | Common native origin; mount stud body plane Y=0, body hangs to Y=46 |

These export plans with explicit anchors; `ldraw_tools.vehicle_details.detail_module()` composes them into Python modules (cockpit palettes use the `wood` role for upholstery). A displayed seat does not prove minifigure fit: check cushion, back, knees, reach, headroom and roof access together. Remove conflicting tiles/core parts before inserting fittings; render roof-off when the shell hides them.

Real-set vehicle details in the submodel atlas (`./ldraw-agent examples --family submodel --details vehicle`): S01 studs-forward tiled leg shield, S09 rounded roof edges on brackets, 05 sideways round drive cover, 08 grille built flat and stood on a pin mount, S02 sideways exhaust manifold, S15 upside-down train belly and 04 Technic-mounted lamp cluster (S15 and 04 need `--scope inspiration`).

## Build from the inside out

1. Test one axle with both wheels: rim orientation, retention, tyre seating. Rotate the opposite side with a proper matrix, never a reflection.
2. Join the axle stations with a bonded narrow spine. Cross plates bridge seams outside the tyre space; no full-width floor through the wheels.
3. Reserve both wheel wells. Add real fenders or supported brick-built arches. A hollow fender's AABB is not its internal clearance.
4. Establish a continuous shoulder/sill line and coherent bonnet-to-cabin transitions. Slopes shape it, with measured sockets and real support.
5. Fit glazing and any interior before closing the roof. Avoid a tall plate stack masquerading as a sports-car cabin; treat windscreen rake, roof width and overhang as one composition.
6. Add supported front/rear fascias and restrained details: paired headlights, red tail lamps, grille, bumpers, mirrors, handles, exhaust or cargo fittings. Every sideways tile needs a real side-stud interface ([snot-construction](../../snot-construction/SKILL.md)).
7. Cap selected broad surfaces with long tiles or curves. Leave studs only where they support something or add deliberate character.
8. **Mandatory:** inspect the silhouette and round off the blocky edges (bonnet and roof edges, nose and tail, arches, fenders; bow, stern and bilge for boats; tank and fairings for motorcycles) with SNOT curves where the subject is rounded. Follow the silhouette pass in [design-models](../SKILL.md); the London bus roof (`10258-rounded-roof`: curved-top bricks on brackets) and the F40 studies are the vehicle lessons to start from.

Expose chassis, axles, body, cab and front/rear fascias as separate sections ([write-plans](../../write-plans/SKILL.md)). Python helpers use X/Z in studs and height in LDU through the `Module`/builder API. New body families author their own modules around measured wheel interfaces; do not stretch existing plans.

## Ferrari F40: SNOT bodywork reference

`examples/ferrari-f40/` labels all 74 sections of the supplied `10248 Ferrari F40.ldr`. Search its gallery (`index.html`) for `door`, `louver`, `bracket`, `engine`. The complete car (`main.ldr`, 1,156 direct parts, 83 steps) references none of the other 73 sections: those are saved construction callouts, and they differ from the flattened car (e.g. the body-mount callout uses a `60897` clip where main step 13 uses `4085c`). The complete car keeps **25 body-overlap errors** (up to ~2.504 LDU): use it as whole-car inspiration only.

Five checked small studies (each passes source/geometry checks and BOM comparison, one optimistic group):

| Study | Parts / stages | Lesson | Source section |
|---|---:|---|---|
| `studies/body-mount` | 5 / 4 | Combine bracket, side-stud and clip interfaces in one compact mount | `subModel-6.ldr` |
| `studies/door-rail` | 6 / 2 | Repeat brackets behind a thin visible trim strip | `subModel-35.ldr` |
| `studies/rear-lamp` | 8 / 4 | Put a lamp and grille on perpendicular faces | `subModel-53.ldr` |
| `studies/window-louver` | 5 / 3 | Repeat a small glazing module on stepped mounting planes (40 LDU longitudinal, 8 LDU vertical progression in this source) | `subModel-57.ldr` |
| `studies/fascia-core` | 6 / 3 | Separate sideways panel mounts from structural support | `subModel-63.ldr` |

```sh
./ldraw-agent build examples/ferrari-f40/studies/rear-lamp/scene.plan.json \
  --output output/ferrari-rear-lamp.mpd
./ldraw-agent inspect output/ferrari-rear-lamp.mpd --contacts all
```

Import a study's attributed `source.mpd` as a plan asset, or include its placement plan. Its `source_origin` anchor is a coordinate frame, not a verified connector: inspect the receiving parts and review the combined assembly. Read each study's `GUIDE.md` for interfaces and reuse limits. Use the checked study extractions, not the annotated complete MPD (which keeps 14 rounded non-rigid matrices).

## Open renders and revise

Review front three-quarter, true side, front, rear, top and underside; view the cab/bed separately if the roof hides it. Drive a concrete revision with:

- Does the silhouette read as this vehicle at thumbnail size? Does the stance suit its purpose, wheels neither lost nor comically exposed?
- Is the side profile coherent from bonnet through glazing and roof to tail? Are overhangs, arches and ground clearance convincing together?
- Are front and rear designed, with readable lamps, grille and bumper depth?
- Do roof thickness, glazing, interior and body width agree at this scale?
- Are long surfaces cleanly seamed with an organized palette? Remove random stripes, excess studs, oversized roof lips, unrelated trim.
- Are tyres clear of arches, sills and underbody, and paired wheels aligned? Inspect both sides.
- Does the outline still read as stacked boxes where the subject is rounded? Complete the silhouette pass ([design-models](../SKILL.md)) with before/after boards.
- Boats: hull/helm proportions, deck access, hull-side clearance, floor vs waterline. Motorcycles: frame/fairing fit, wheel alignment, handlebars, saddle, luggage clearance.

Record image paths, findings and revisions; regenerate checks, BOM and renders from the final plan. Keep `physical_validity: not_proven` and state untested rolling freedom, strength, driver fit and part/colour availability.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/guides/design-models.md](references/docs-agent-guides-design-models.md)
- [examples/ferrari-f40/README.md](references/examples-ferrari-f40-README.md)
