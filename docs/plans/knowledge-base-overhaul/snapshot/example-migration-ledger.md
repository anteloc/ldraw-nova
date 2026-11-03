# Example package migration ledger

Planning only, 2026-11-03. This maps all **187 visually audited candidate entries** to concrete package destinations, preserving their existing qualifications. It adds no visual acceptance. [Machine-readable ledger](example-migration-ledger.json) includes every catalog alias, current primary-source hash comparison and tracked-file routing inventory.

Repeated colour variants, child models and visibility cutaways can share one package. The actual LDraw FILE names and provenance remain intact; a package rename does not rename its geometry. `lesson_anchor` identifies a README lesson, not an invented model section. Construction destinations remain conditional on the linked corrections and check scopes.

## Per-candidate decisions

### submodel

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `01-8081-front-axle`<br/>`examples/submodel-atlas/01-8081-front-axle` | `examples/8081-front-axle` | **construction** — retain scoped lesson; package and correct. Front suspension arms, shock and steering links are visible; parent frame supplies the pinion. Keep lesson and parent dependency together; no claim of complete steering mechanism in isolated axle. |
| `02-42075-rear-axle`<br/>`examples/submodel-atlas/02-42075-rear-axle` | `examples/42075-differential-axle` | **inspiration** — retain scoped lesson; package and correct. Differential, U-joint input, half-shafts and leaning shock match source lesson and mounted rear location. Keep repair/source-study status because known raw shock geometry errors are not disproved by clean rendering. |
| `03-42050-v8-engine`<br/>`examples/submodel-atlas/03-42050-v8-engine` | `examples/42050-v8-engine` | **construction** — retain scoped lesson; package and correct. Two cylinder banks and hidden crank are visible in step and transparent views; source role at drag-racer front matches. Static illustration does not establish working motion. |
| `04-42078-headlight`<br/>`examples/submodel-atlas/04-42078-headlight` | `examples/42078-headlight-cluster` | **inspiration** — retain scoped lesson; package and correct. Two-colour lens cluster and offset mount match truck bumper position. Retain repair candidate; the previously reported tiny overlap cannot be decided from pixels. |
| `05-10269-headlight-nacelle`<br/>`examples/submodel-atlas/05-10269-headlight-nacelle` | `examples/10269-primary-drive-cover` | **construction** — retain scoped lesson; package and correct. Actual parent shows primary-drive cover with shift lever, not front headlight. Four sideways headlight bricks carry the circular panel. Correct semantic package name; catalog lesson already corrected. |
| `06-10283-shuttle-framework`<br/>`examples/submodel-atlas/06-10283-shuttle-framework` | `examples/10283-oms-pod` | **construction** — retain scoped lesson; package and correct. Actual part is a rear OMS pod with curved hinged white shell on side-stud core; not whole shuttle framework. Good core-to-skin lesson. Nested child inspection still required. |
| `07-75060-cockpit-base`<br/>`examples/submodel-atlas/07-75060-cockpit-base` | `examples/75060-pivoting-cockpit` | **construction** — retain scoped lesson; package and correct. Pilot pod, fixed Technic bearing bricks and marked axis are visually consistent. Posed copy demonstrates intended relative transform, not dome clearance or passive self-leveling. Additional three-pose board opened: bearings fixed across 0/45/90 degrees. Synthetic pose does not establish full-parent clearance. |
| `08-7784-bat-hull`<br/>`examples/submodel-atlas/08-7784-bat-hull` | `examples/7784-bat-grille` | **construction** — retain scoped lesson; package and correct. Thin bat silhouette mounts at nose via backside pin connector and is tilted in vehicle. Rename as grille; useful flat-build-to-parent transform lesson. |
| `10-10182-roof-tower`<br/>`examples/submodel-atlas/10-10182-roof-tower` | `examples/10182-roof-tower` | **construction** — retain scoped lesson; package and correct. Parrots within four arches, four hinge bases and pitched repeated roof panels match claimed corner tower. Visible seams are not a measured closure or fit check. |
| `s01-10298-vespa-front`<br/>`examples/submodel-atlas/s01-10298-vespa-front` | `examples/10298-vespa-leg-shield` | **construction** — retain scoped lesson; package and correct. Studs-forward column and tiled skin visibly become tilted leg shield on scooter. Keep scoped panel lesson; stud-map uses diagnostic colours. |
| `s02-21307-caterham-nose`<br/>`examples/submodel-atlas/s02-21307-caterham-nose` | `examples/21307-engine-exhaust` | **construction** — retain scoped lesson; package and correct. Four revolvers create a static exhaust/manifold texture on the engine under the bonnet, not car nose. Parent and construction steps support current corrected lesson. |
| `s03-21319-central-perk-wall`<br/>`examples/submodel-atlas/s03-21319-central-perk-wall` | `examples/21319-patterned-floor` | **construction** — retain scoped lesson; package and correct. Edge-on bricks/plates form floor mosaic, not wall. Side studs provide connections visible during construction; orientation map supports plate-edge texture lesson. |
| `s04-21309-saturn-module`<br/>`examples/submodel-atlas/s04-21309-saturn-module` | `examples/21309-radial-hub` | **construction** — retain scoped lesson; package and correct. Eight spoke panels connect around central clip hub in parent cross-section. Isolated exported hub is not the complete eight-panel assembly; keep sibling/parent dependency explicit. |
| `s05-41627-yoda`<br/>`examples/submodel-atlas/s05-41627-yoda` | `examples/41627-yoda` | **construction** — retain scoped lesson; package and correct. Figure and side-stud core support flat panels turned onto head/body. Nested panels must be reviewed individually; source composite includes separate Luke context only. |
| `s06-10278-door-column`<br/>`examples/submodel-atlas/s06-10278-door-column` | `examples/10278-vine-column` | **construction** — retain scoped lesson; package and correct. Sideways stone-texture column and projecting bars support the vine lesson; parent location beside doorway matches. Review leaf child separately. |
| `s07-10272-rooftop-box`<br/>`examples/submodel-atlas/s07-10272-rooftop-box` | `examples/10272-glazed-wall` | **construction** — retain scoped lesson; package and correct. Windscreen panes form a stand wall; local studs-down frame becomes sideways after parent placement. Retain corrected semantic name and explicitly unverified attachment. |
| `s08-10267-christmas-tree`<br/>`examples/submodel-atlas/s08-10267-christmas-tree` | `examples/10267-christmas-tree` | **construction** — retain scoped lesson; package and correct. Four-sided foliage on stud core visible, but title/lesson/board incorrectly say four identical faces. Source has two different face children, repeated twice each (11 vs 12 parts); guide reuse instruction to repeat one face loses this distinction. Require description correction. |
| `s09-10258-bus-roof`<br/>`examples/submodel-atlas/s09-10258-bus-roof` | `examples/10258-rounded-roof` | **construction** — retain scoped lesson; package and correct. Brackets carry sideways curved bricks along both long edges. Roof is visibly rounded and placed atop bus deck; useful body-edge lesson. |
| `s10-21046-empire-corner`<br/>`examples/submodel-atlas/s10-21046-empire-corner` | `examples/21046-recessed-entrance` | **construction** — retain scoped lesson; package and correct. Module is front entrance with recessed glazed doorway in rib facade. Side-stud core and cross-oriented fin children fit corrected lesson, not an unspecified corner. |
| `s11-10226-radial-engine`<br/>`examples/submodel-atlas/s11-10226-radial-engine` | `examples/10226-striped-rudder` | **construction** — retain scoped lesson; package and correct. Striped vertical tail rudder and handle-bearing column are visible in actual parent. No radial engine. Rename semantic package; retain source coordinate and hinge limits. |
| `s13-40412-buckbeak-body`<br/>`examples/submodel-atlas/s13-40412-buckbeak-body` | `examples/40412-buckbeak-head` | **construction** — retain scoped lesson; package and correct. Large face/head on side-stud box with hidden pink core; source parent disproves body-and-wings label. Keep head shaping lesson and inspect core/face children. |
| `s14-21303-walle-eye`<br/>`examples/submodel-atlas/s14-21303-walle-eye` | `examples/21303-walle-eye` | **inspiration** — retain scoped lesson; package and correct. Housing, rounded eye contour and ribbed-hose decoration match scene. Retain source/inspiration or repair classification; visually plausible hoses do not resolve 49 nonrigid diagnostics. |
| `s15-10183-underbody`<br/>`examples/submodel-atlas/s15-10183-underbody` | `examples/10183-inverted-underbody` | **inspiration** — retain scoped lesson; package and correct. Curved bricks genuinely inverted under central locomotive body. Retain repair/inspiration classification for four nonrigid transforms; parent view locates assembly but does not prove attachment. |
| `s16-30050-shuttle-fuselage`<br/>`examples/submodel-atlas/s16-30050-shuttle-fuselage` | `examples/30050-micro-shuttle` | **construction** — retain scoped lesson; package and correct. Whole micro shuttle has two upright clipped wings and angled nose. Current lesson matches but source/build-page step numbering differs due to ROTSTEP; preserve explicit mapping. |
| `s17-10294-titanic-hull`<br/>`examples/submodel-atlas/s17-10294-titanic-hull` | `examples/10294-hull-panels#s17-10294-titanic-hull` | **construction** — retain scoped lesson; package and correct. Red tiled hull panel lies flat in its local frame and becomes lower bow side in parent; curved bilge edge visible. No evidence here of measured attachment to neighbouring sections. |
| `s17b-10294-titanic-hull-cabins`<br/>`examples/submodel-atlas/s17b-10294-titanic-hull-cabins` | `examples/10294-hull-panels#s17b-10294-titanic-hull-cabins` | **construction** — retain scoped lesson; package and correct. Paired open studs form portholes in port hull wall; child units use a counter-rotation. Lesson supported; inspect nested ring-bearing units separately. |
| `s18-75276-tie-mount`<br/>`examples/submodel-atlas/s18-75276-tie-mount` | `examples/75276-mouth-grille` | **construction** — retain scoped lesson; package and correct. Actual parent locates mouth vent under Stormtrooper face, not TIE mount. Offset plates and car mudguard support centring/sculpted-arch lesson. |
| `s19-31031-chameleon`<br/>`examples/submodel-atlas/s19-31031-chameleon` | `examples/31031-chameleon` | **construction** — retain scoped lesson; package and correct. Full animal with sideways flank stripes, hinged limbs and bulged eyes matches current corrected lesson. Root board does not individually expose all ten children. |
| `s20-21325-blacksmith`<br/>`examples/submodel-atlas/s20-21325-blacksmith` | `examples/21325-tree-trunk` | **construction** — retain scoped lesson; package and correct. Trunk lies horizontally in its own build frame and stands upright beside blacksmith building; brown dinosaur-tail pieces make roots. Tree-branch children require individual review. |
| `s22-10030-isd-tower`<br/>`examples/submodel-atlas/s22-10030-isd-tower` | `examples/10030-micro-tantive` | **construction** — retain scoped lesson; package and correct. Tiny Tantive IV adjacent to Star Destroyer; sideways fuselage and radial engine pieces, not command tower. Keep microscale shape/orientation lesson under corrected name. |

Per-section observations, parents and limits: [submodel findings](submodel-findings.md).

### reference

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `aircraft-undercarriage`<br/>`examples/reference-atlas/aircraft-undercarriage` | `examples/aircraft-undercarriage` | **construction** — retain scoped lesson; package and correct. Keep wheel-strut geometry in one source pose; retractable is not demonstrated. Preserve parent mounts; no checked travel claim. |
| `airliner-engine`<br/>`examples/reference-atlas/airliner-engine` | `examples/airliner-engine` | **construction** — retain scoped lesson; package and correct. Keep fan housing and long thin pylon; four parent placements clarify attachment. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `airliner-wheel-bogie`<br/>`examples/reference-atlas/airliner-wheel-bogie` | `examples/airliner-wheel-bogie` | **construction** — retain scoped lesson; package and correct. Keep four-wheel, two-axle bogie and short upright mount with two parent placements. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `arched-clip-panel`<br/>`examples/reference-atlas/arched-clip-panel` | `examples/arched-clip-panel` | **construction** — retain scoped lesson; package and correct. Keep arched opening, Technic holes and paired clips as roof-panel detail. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `classic-truck-cab`<br/>`examples/reference-atlas/classic-truck-cab` | `examples/6594-tractor-unit` | **construction** — retain scoped lesson; package and correct. Rename to complete compact tractor unit: white cab, red stripe, green grille, four-wheel chassis and rear turntable. Not just a cab. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `classical-arch-bay`<br/>`examples/reference-atlas/classical-arch-bay` | `examples/classical-arch-bay#source-study` | **construction** — retain scoped lesson; package and correct. Keep narrow textured tan arch with round-spacer cornice; merge source with arcade-bay recipe. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `dormer-balcony`<br/>`examples/reference-atlas/dormer-balcony` | `examples/dormer-balcony` | **construction** — retain scoped lesson; package and correct. Keep sloped blue dormer/window bay, turquoise wall and black ornamental railing with brown top. Correct turquoise-railing description. |
| `faceted-ship-bow`<br/>`examples/reference-atlas/faceted-ship-bow` | `examples/faceted-ship-bow` | **construction** — retain scoped lesson; package and correct. Keep faceted red/blue bow. Include parent orientation: isolated view appears upright. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `fire-escape-railing`<br/>`examples/reference-atlas/fire-escape-railing` | `examples/fire-escape-railing` | **construction** — retain scoped lesson; package and correct. Keep platform/rail detail with long support plate and bar/clip railing; not a complete stair flight. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `hinged-wing`<br/>`examples/reference-atlas/hinged-wing` | `examples/hinged-wing` | **construction** — retain scoped lesson; package and correct. Keep tapered wing with actual bar/clip root: 60478 handle plates, not hinge fingers. No validated sweep claim. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `layered-tree`<br/>`examples/reference-atlas/layered-tree` | `examples/layered-tree` | **construction** — retain scoped lesson; package and correct. Keep round brown trunk, three foliage layers and base as landscaping lesson. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `mini-truck-cab`<br/>`examples/reference-atlas/mini-truck-cab` | `examples/4915-tractor-unit` | **construction** — retain scoped lesson; package and correct. Rename complete compact four-wheel tractor unit with rear hitch; geometry extends beyond cab. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `moulded-staircase`<br/>`examples/reference-atlas/moulded-staircase` | `examples/moulded-staircase` | **construction** — retain scoped lesson; package and correct. Keep moulded stairs and landing with actual floor opening shown in parent. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `ornamental-lamp`<br/>`examples/reference-atlas/ornamental-lamp` | `examples/ornamental-lamp` | **construction** — retain scoped lesson; package and correct. Keep white base, grey post, clear cup/yellow bulb and green/red decoration alongside post. Decoration is not on top. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `park-bench`<br/>`examples/reference-atlas/park-bench` | `examples/park-bench` | **construction** — retain scoped lesson; package and correct. Keep dark-blue seat/back and white feet as small furniture lesson. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `rail-bogie`<br/>`examples/reference-atlas/rail-bogie` | `examples/rail-bogie` | **construction** — retain scoped lesson; package and correct. Keep two-axle bogie, central pivot, buffers and coupling. Correct single-axle source/card descriptions: two single-axle parts form one bogie. |
| `rounded-cockpit-shell`<br/>`examples/reference-atlas/rounded-cockpit-shell` | `examples/10212-rounded-side-covers` | **construction** — retain scoped lesson; package and correct. Rename paired rounded body-side covers. Non-ghost parent view places these around the wing mechanism beside the body; cockpit/nose identity is incorrect. Curved-skin reuse elsewhere must be described as adaptation. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `shuttered-window`<br/>`examples/reference-atlas/shuttered-window` | `examples/shuttered-window` | **construction** — retain scoped lesson; package and correct. Keep brown frame, grey shutters and blue open frames; avoid calling open frames glass panes. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `sloped-tail-fin`<br/>`examples/reference-atlas/sloped-tail-fin` | `examples/sloped-tail-fin` | **construction** — retain scoped lesson; package and correct. Keep thin black fin, yellow plate and translucent-red top; parent role agrees. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `small-ornamental-tree`<br/>`examples/reference-atlas/small-ornamental-tree` | `examples/small-ornamental-tree` | **construction** — retain scoped lesson; package and correct. Keep cone/round trunk and large leaf blades as a distinct small tree construction. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `spacecraft-hatch`<br/>`examples/reference-atlas/spacecraft-hatch` | `examples/spacecraft-hatch` | **construction** — retain scoped lesson; package and correct. Keep blue hinged rear hatch with nozzle/fin. Inherited colour differs between preview and parent. One pose does not certify travel. |
| `spacecraft-wheel-module`<br/>`examples/reference-atlas/spacecraft-wheel-module` | `examples/5980-buggy-chassis` | **construction** — retain scoped lesson; package and correct. Rename small vehicle chassis/wheel module. Whole-source view shows separate wheeled buggy in multi-object scene, not spacecraft landing gear. Remove deployed-landing-clearance guidance. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `swivel-armchair`<br/>`examples/reference-atlas/swivel-armchair` | `examples/swivel-armchair` | **construction** — retain scoped lesson; package and correct. Keep compact black chair and turntable mount. Static-pose scope only; swivel clearance not verified. |
| `timbered-wall`<br/>`examples/reference-atlas/timbered-wall` | `examples/timbered-wall` | **construction** — retain scoped lesson; package and correct. Keep printed corner panels, window and arched roof supports as facade detail. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `truck-loading-ramp`<br/>`examples/reference-atlas/truck-loading-ramp` | `examples/truck-loading-ramp` | **construction** — retain scoped lesson; package and correct. Keep paired wheel tracks and bar ends; parent shows upright stowed ramp behind truck. No checked-motion claim. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `warehouse-forklift`<br/>`examples/reference-atlas/warehouse-forklift` | `examples/warehouse-forklift` | **construction** — retain scoped lesson; package and correct. Keep complete minifigure forklift: mast, forks, seat, levers, wheels. Isolated inherited colour may differ from source parent. No validated working-lift claim. |
| `winter-lamp`<br/>`examples/reference-atlas/winter-lamp` | `examples/winter-lamp` | **construction** — retain scoped lesson; package and correct. Keep thin black post, yellow light, inverted shade and green wreath/red accent. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export. |
| `arcade-bay`<br/>`examples/reference-atlas/recipes/arcade-bay` | `examples/classical-arch-bay#adjustable-recipe` | **construction** — retain scoped lesson; package and correct. Fresh home view shows narrow tan arch, tall piers, round spacers and cornice. Keep adjustable-height recipe beside classical-arch-bay source; articulated means architectural detail, not motion. |
| `street-lantern`<br/>`examples/reference-atlas/recipes/street-lantern` | `examples/street-lantern` | **construction** — retain scoped lesson; package and correct. Fresh home view shows narrow round-brick post, open collar, translucent yellow lamp, inverted dish cap and square foot. Keep adjustable-height recipe. |

Per-section observations, parents and limits: [reference findings](reference-findings.md).

### mechanical

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `differential`<br/>`examples/mechanism-atlas/differential` | `examples/differential` | **construction** — retain scoped lesson; package and correct. Keep as differential-plus-axle-frame study. Open carrier, output sides, drive gear and surrounding beam supports are visible; source-parent view shows integration between wheel corners. Static images do not prove differential operation. |
| `driven-turntable`<br/>`examples/mechanism-atlas/driven-turntable` | `examples/driven-turntable` | **construction** — retain scoped lesson; package and correct. Keep paired turntable halves, pin-equipped rotating attachment, drive gear and open base frame as one mounting study. Parent vehicle supplies external drive and attached load. Source pose only. |
| `gear-reduction`<br/>`examples/mechanism-atlas/gear-reduction` | `examples/gear-reduction` | **construction** — retain scoped lesson; package and correct. Rename canonical key to gear-and-axle-module to match guide. Red elevated clutch gear and exposed axles depend on surrounding parent transmission. Do not offer as standalone reduction gearbox or infer a complete ratio from this extract. |
| `piston-crank`<br/>`examples/mechanism-atlas/piston-crank` | `examples/piston-crank` | **construction** — retain scoped lesson; package and correct. Keep single-cylinder display engine: exposed lower crank, rod and geared shaft agree with guide; upper piston is enclosed by the embedded cylinder part. Parent kart provides chassis and drivetrain. No motion or clearance proof. |
| `steering-rack`<br/>`examples/mechanism-atlas/steering-rack` | `examples/steering-rack` | **construction** — retain scoped lesson; package and correct. Keep rack carriage with beam carrier and steering connections. Driving pinion is absent from the extract and supplied by parent tractor. Search result must state this dependency. |
| `worm-drive`<br/>`examples/mechanism-atlas/worm-drive` | `examples/worm-drive` | **construction** — retain scoped lesson; package and correct. Keep worm shaft, small driven gear and layered supports. Parent supplies winding assembly; isolated module has no drum/cable and no demonstrated self-locking/load capacity. |
| `cam-follower-engine`<br/>`examples/technic-atlas/mechanisms/cam-follower-engine` | `examples/cam-follower-engine` | **construction** — retain scoped lesson; package and correct. Keep root plus both child constructions together. Six axle followers sit above phased liftarm cams; one follower is raised. Label children guided-follower-block and camshaft-with-support-links, replacing generic piston-engine descriptions. Retained source geometry does not prove gravity return or full-cycle contact. |
| `double-cardan-shaft`<br/>`examples/technic-atlas/mechanisms/double-cardan-shaft` | `examples/double-cardan-shaft` | **construction** — retain scoped lesson; package and correct. Keep as unsupported paired-joint shaft study, not ready-to-mount drive module. Seven-piece extract shows two universal joints and intermediate axle but no bearings, adjoining axles or retention. Preserve phase and measured positioning frame; add supports during adaptation. |
| `four-bar-lift`<br/>`examples/technic-atlas/mechanisms/four-bar-lift` | `examples/four-bar-lift` | **construction** — retain scoped lesson; package and correct. Keep as partial wing-lift linkage study. Broad wing panel, paired uprights, links and partial surrounding frame are visible. Guide assumes fixed upper pivot and omits full actuator. Do not retrieve as a self-supporting service lift. |
| `four-cylinder-bank`<br/>`examples/technic-atlas/mechanisms/four-cylinder-bank` | `examples/four-cylinder-bank` | **construction** — retain scoped lesson; package and correct. Keep four-cylinder core with alternating piston heights, shared crankshaft and end drive gear. No freestanding support frame. Parent central drive and other banks are required for the source engine role. |
| `four-speed-gearbox`<br/>`examples/technic-atlas/mechanisms/four-speed-gearbox` | `examples/four-speed-gearbox` | **construction** — retain scoped lesson; package and correct. Keep four-speed transmission core plus auxiliary shaft/support child. Driving rings, selector elements and compact gear trains are visible; the child forms one side of its support/shaft arrangement. External selector controls and surrounding driveline are omitted. No ratio or full-cycle validation added. |
| `independent-suspension`<br/>`examples/technic-atlas/mechanisms/independent-suspension` | `examples/paired-suspension-axles` | **construction** — retain scoped lesson; package and correct. Keep as paired front/rear suspension studies requiring integration. Whole view visibly contains two separated axle assemblies, four wheel corners, wishbones and shocks; it is not a connected chassis. Explicitly state missing central chassis, guide-link holders and Cardan boundary supports in retrieval excerpt. |

Per-section observations, parents and limits: [mechanical findings](mechanical-findings.md).

### structural

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `workshop-machine`<br/>`examples/workshop/workshop` | `examples/workshop-machine` | **construction** — retain scoped lesson; package and correct. Keep as complete static integration starter. Two box trestles support bonded workbench; retained hand-cranked chain module sits under portal-mounted extended cylinder; separate pump/valve pads and three fitted hoses are visible. All ten children/routes reviewed alone and in parent, including chain inside its bearing frame. Calling it a conveyor describes intent; cargo transport, actuator travel and hose slack across travel remain untested. |
| `mounted-frame-named`<br/>`examples/workshop/mounted-frame` | `examples/mounted-service-frame` | **construction** — retain scoped lesson; package and correct. Keep named-plan version as canonical service-platform starter. Technic box frame, System deck, trim and upper cover match original service-platform geometry; consolidate duplicate catalog entry. |
| `retained-chain-drive`<br/>`examples/workshop/chain-drive` | `examples/retained-chain-drive` | **construction** — retain scoped lesson; package and correct. Keep supported static chain-loop starter: side rails and bearing caps, shaft spacers/stops, hand crank and complete synthesized loop are visible. Preserve wheel spacing and mounting grid. No running tension, wear or cargo-transport test. |
| `reinforced-frame`<br/>`examples/technic-atlas/reinforced-frame` | `examples/reinforced-frame` | **construction** — retain scoped lesson; package and correct. Keep small pin-and-frame lesson: four yellow crossmembers span moulded frame with two-point attachment. Home and underside agree with description. No load-capacity claim. |
| `box-chassis`<br/>`examples/technic-atlas/box-chassis` | `examples/box-chassis` | **construction** — retain scoped lesson; package and correct. Keep compact box-frame/trestle lesson with paired long upper rails. Same role visible as the two workshop supports. Retain geometry/structural check scope and expose usable stud-ended mounts. |
| `frame-tower`<br/>`examples/technic-atlas/frame-tower` | `examples/frame-tower` | **construction** — retain scoped lesson; package and correct. Keep stacked frame tower: rectangular rings, opposed vertical frames and side connectors clearly express repeated bracing. No load rating. |
| `service-platform`<br/>`examples/technic-atlas/service-platform` | `examples/mounted-service-frame` | **construction** — merge identical geometry; named plan is canonical. Merge into named mounted-frame package. Source bytes match its MPD exactly; same bodywork-on-Technic lesson should have one authored description and one search result. |

Per-section observations, parents and limits: [structural findings](structural-findings.md).

### vehicle

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `touring-motorcycle`<br/>`examples/vehicle-atlas/touring-motorcycle` | `examples/touring-motorcycle` | **construction** — retain scoped lesson; package and correct. Keep narrowly as purpose-made motorcycle-part composition: moulded frame/fairing, spoked wheels and rear luggage tray. Good recognizable silhouette, but not a general brick-built vehicle or steering-mechanism lesson. |
| `harbour-launch`<br/>`examples/vehicle-atlas/harbour-launch` | `examples/harbour-launch` | **construction** — retain scoped lesson; package and correct. Keep narrowly as moulded-hull open launch with helm, windscreen, lights and lifebuoy. No propulsion mechanism or complex hull-building lesson. Light crossbar reviewed separately and mounted across windscreen. |
| `courier-jet`<br/>`examples/vehicle-atlas/courier-jet` | `examples/courier-jet` | **construction** — retain scoped lesson; package and correct. Keep narrowly as compact aircraft assembled from matched nose/glazing, body panels, wings, tail and underwing engines. Large purpose-made elements dominate the shape; exclude as universal aircraft default. No landing gear is present. Repeated engine child reviewed in both wing placements. Fresh see-through home/top views confirm the enclosed seat, controls and instrument panel; no missing-cockpit defect. |
| `driver-cockpit`<br/>`examples/vehicle-atlas/details/driver-cockpit` | `examples/vehicle-fittings#driver-cockpit` | **construction** — retain scoped lesson; package and correct. Keep small seat/steering-stand/dashboard layout on two-by-six floor. Explicitly reserve seat-back and canopy space. This is an interior fitting, not a complete vehicle starter. |
| `pilot-cockpit`<br/>`examples/vehicle-atlas/details/pilot-cockpit` | `examples/vehicle-fittings#pilot-cockpit` | **construction** — retain scoped lesson; package and correct. Keep small seat/control-stick/instrument-slope layout on two-by-eight floor. Stick in one upright pose; cockpit envelope and canopy must be provided by parent. |
| `wing-mirror`<br/>`examples/vehicle-atlas/details/wing-mirror` | `examples/vehicle-fittings#wing-mirror` | **construction** — retain scoped lesson; package and correct. Keep tiny headlight-brick side-stud tile lesson as fitting snippet. Show mounting orientation and outward-facing mirrored use; no standalone assembly package required if grouped with fittings. |
| `cargo-chest`<br/>`examples/vehicle-atlas/details/cargo-chest` | `examples/vehicle-fittings#cargo-chest` | **construction** — retain scoped lesson; package and correct. Keep purpose-made open crate and supporting pallet as fitting snippet. Odd-width placement lattice must be stated; no detailed brick-built cargo-body lesson. |
| `navigation-lights`<br/>`examples/vehicle-atlas/details/navigation-lights` | `examples/vehicle-fittings#navigation-lights` | **construction** — retain scoped lesson; package and correct. Keep red/green round lights on short plate crossbar as fitting snippet. Source launch shows use across windscreen. Preserve documented forward direction and colour sides. |
| `jet-engine-pod`<br/>`examples/vehicle-atlas/details/jet-engine-pod` | `examples/vehicle-fittings#jet-engine-pod` | **construction** — retain scoped lesson; package and correct. Keep purpose-made engine housing/internal core fitting, with top stud attachment. Source courier jet supplies underside wing sockets. Preserve intake direction and clearance below wing; this is not a brick-built turbine construction. |

Per-section observations, parents and limits: [vehicle findings](vehicle-findings.md).

### building

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `cottage`<br/>`examples/building-atlas/cottage` | `examples/cottage` | **construction** — improve cottage and nested weak tree/bench before promotion. Keep one basic upright shell/roof/site-composition lesson, with scope explicitly unfurnished and introductory. Shell, five windows, closed door, roof/dormer and supported porch read correctly. Sparse tree and blocky bench remain replacement candidates; their nested uses must be updated too. Roof has a continuous underside plate deck; do not imply a usable dormer room or interior access through it. |
| `conservatory`<br/>`examples/building-atlas/conservatory` | `examples/glasshouse-walls` | **construction** — extract reviewed wall shell and its dependency closure; retire whole-scene recommendation. Revise selection: retain glazed wall-shell construction with full-height fixed glazing and framed door; do not recommend the whole scene or current glass-roof assembly. Fresh views show thick multi-course transparent roof largely obscuring sparse repeated flower boxes. This conflicts with the advertised planting-as-interior-focus lesson. Existing visual review already acknowledges roof opacity. Preserve original whole source only as provenance/regression fixture where required. |
| `skyline`<br/>`examples/building-atlas/skyline` | `examples/microscale-skyline` | **construction** — retain scoped lesson; consolidate fitting variants. Keep microscale massing lesson: stepped tan tower, glazed slab tower and low pavilion on shared plinth. Correct three-tower wording to two towers and a pavilion. No minifigure-scale elements; one flat source section. |
| `porch`<br/>`examples/building-atlas/details/porch` | `examples/building-fittings#porch` | **construction** — retain scoped lesson; consolidate fitting variants. Keep supported four-post porch with separate floor and tiled canopy, demonstrated at cottage entrance. Preserve doorway/approach width and supporting stud surfaces. |
| `flower-box`<br/>`examples/building-atlas/details/flower-box` | `examples/building-fittings#flower-box` | **construction** — retain scoped lesson; consolidate fitting variants. Keep small fitting snippet: four flowers on round stems behind simple planter frontage. Not a broad botanical/landscaping example; colour variants are parameters, not separate lessons. |
| `stairs`<br/>`examples/building-atlas/details/stairs` | `examples/building-fittings#stairs` | **construction** — retain scoped lesson; consolidate fitting variants. Keep compact plate-built steps with three one-plate rises and supported landing. Reserve exact landing height and approach. |
| `fence`<br/>`examples/building-atlas/details/fence` | `examples/building-fittings#fence` | **construction** — retain scoped lesson; consolidate fitting variants. Keep simple two-post rail as fitting snippet, not a rich fence design template. Cottage shows the corresponding white variant at site boundary. |
| `beacon`<br/>`examples/building-atlas/details/beacon` | `examples/building-fittings#beacon` | **construction** — retain scoped lesson; consolidate fitting variants. Keep simple translucent cylindrical light on square foot as fitting snippet. Functional industrial lighting means visual role, not an operating light. |
| `chimney`<br/>`examples/building-atlas/details/chimney` | `examples/building-fittings#chimney` | **construction** — retain scoped lesson; consolidate fitting variants. Keep banded round stack on square plinth as fitting snippet. Avoid general industrial-building style claims. |
| `window`<br/>`examples/building-atlas/details/window` | `examples/building-fittings#window` | **construction** — retain scoped lesson; consolidate fitting variants. Keep frame/pane fitting with required opening dimensions, demonstrated in cottage shell. Preserve source parts and fit limitations. |
| `glazed-door`<br/>`examples/building-atlas/details/glazed-door` | `examples/building-fittings#glazed-door` | **construction** — retain scoped lesson; consolidate fitting variants. Keep frame/door fitting in closed pose; compatible green variant shown in conservatory shell. No checked door swing. |
| `display-window`<br/>`examples/building-atlas/details/display-window` | `examples/building-fittings#display-window` | **construction** — retain scoped lesson; consolidate fitting variants. Keep full-height fixed frame/glazing fitting; share one authored recipe with wall-shell lesson and parameterize colour. |
| `solar-array`<br/>`examples/building-atlas/details/solar-array` | `examples/building-fittings#solar-array` | **construction** — retain scoped lesson; consolidate fitting variants. Keep horizontal printed-panel rack with real supports as small static equipment lesson. No articulated tilt/tracking claim. |
| `clock`<br/>`examples/building-atlas/details/clock` | `examples/building-fittings#clock` | **construction** — retain scoped lesson; consolidate fitting variants. Keep printed clock-brick fitting on plate. Two-piece snippet, not separate architectural construction lesson. |
| `battlement`<br/>`examples/building-atlas/details/battlement` | `examples/building-fittings#battlement` | **construction** — retain scoped lesson; consolidate fitting variants. Keep low parapet/merlon pattern on connected rectangular deck. Correct Square tower top to rectangular 8-by-10-stud footprint in source plan, MPD description and generated catalog. |
| `dormer-roof`<br/>`examples/building-atlas/details/dormer-roof` | `examples/cottage#dormer-roof` | **construction** — retain scoped lesson; consolidate fitting variants. Keep as basic supported gable roof with decorative dormer and tiled ridge; link to its cottage use instead of duplicating prose. Underside is a continuous plate deck; do not claim hollow loft or usable upper room. |

Per-section observations, parents and limits: [building findings](building-findings.md).

### snot

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `parrot`<br/>`examples/snot/parrot` | `examples/parrot` | **construction** — retain scoped lesson; package and correct. retain_specific_lessons_with_corrected_routing_and_limits |
| `cat`<br/>`examples/snot/cat` | `examples/cat` | **construction** — retain scoped lesson; package and correct. retain_specific_lessons_with_corrected_routing_and_limits |
| `halcyon`<br/>`examples/snot/halcyon` | `examples/halcyon` | **construction** — retain scoped lesson; package and correct. retain_specific_lessons_with_corrected_routing_and_limits |

Per-section observations, parents and limits: [snot findings](snot-findings.md).

### f40

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `body-mount`<br/>`examples/snot/ferrari-f40/studies/body-mount` | `examples/ferrari-f40#body-mount` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_narrow_study_not_checked_whole_car |
| `door-rail`<br/>`examples/snot/ferrari-f40/studies/door-rail` | `examples/ferrari-f40#door-rail` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_narrow_study_not_checked_whole_car |
| `fascia-core`<br/>`examples/snot/ferrari-f40/studies/fascia-core` | `examples/ferrari-f40#fascia-core` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_narrow_study_not_checked_whole_car |
| `rear-lamp`<br/>`examples/snot/ferrari-f40/studies/rear-lamp` | `examples/ferrari-f40#rear-lamp` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_narrow_study_not_checked_whole_car |
| `window-louver`<br/>`examples/snot/ferrari-f40/studies/window-louver` | `examples/ferrari-f40#window-louver` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_narrow_study_not_checked_whole_car |

Per-section observations, parents and limits: [f40 findings](f40-findings.md).

### bwing6208

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `airframe`<br/>`examples/snot/b-wing-6208/studies/airframe` | `examples/b-wing-6208#airframe` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `center`<br/>`examples/snot/b-wing-6208/studies/center` | `examples/b-wing-6208#center` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `cockpit`<br/>`examples/snot/b-wing-6208/studies/cockpit` | `examples/b-wing-6208#cockpit` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `cockpit-arm`<br/>`examples/snot/b-wing-6208/studies/cockpit-arm` | `examples/b-wing-6208#cockpit-arm` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `exhaust`<br/>`examples/snot/b-wing-6208/studies/exhaust` | `examples/b-wing-6208#exhaust` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `front`<br/>`examples/snot/b-wing-6208/studies/front` | `examples/b-wing-6208#front` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `front-core`<br/>`examples/snot/b-wing-6208/studies/front-core` | `examples/b-wing-6208#front-core` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_visibility_cutaway |
| `front-fins`<br/>`examples/snot/b-wing-6208/studies/front-fins` | `examples/b-wing-6208#front-fins` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_visibility_cutaway |
| `side-shell`<br/>`examples/snot/b-wing-6208/studies/side-shell` | `examples/b-wing-6208#side-shell` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `wing-1`<br/>`examples/snot/b-wing-6208/studies/wing-1` | `examples/b-wing-6208#wing-1` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `wing-2`<br/>`examples/snot/b-wing-6208/studies/wing-2` | `examples/b-wing-6208#wing-2` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `wing-3`<br/>`examples/snot/b-wing-6208/studies/wing-3` | `examples/b-wing-6208#wing-3` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |
| `wing-root`<br/>`examples/snot/b-wing-6208/studies/wing-root` | `examples/b-wing-6208#wing-root` | **construction** — retain study within parent package; distinguish child, callout and cutaway. retain_scoped_construction_lesson |

Per-section observations, parents and limits: [bwing6208 findings](bwing6208-findings.md).

### spaceship

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `b-wing`<br/>`examples/spaceship-atlas/b-wing` | `examples/75050-b-wing` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `canopy-cockpit`<br/>`examples/spaceship-atlas/canopy-cockpit` | `examples/canopy-cockpit` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `falcon-greebles`<br/>`examples/spaceship-atlas/falcon-greebles` | `examples/falcon-greebles` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `x-wing-nacelle`<br/>`examples/spaceship-atlas/x-wing-nacelle` | `examples/x-wing-nacelle` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `x-wing-wing`<br/>`examples/spaceship-atlas/x-wing-wing` | `examples/x-wing-wing` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `y-wing-armour`<br/>`examples/spaceship-atlas/y-wing-armour` | `examples/y-wing-armour` | **construction** — retain scoped lesson; package and correct. retain_scoped_construction_study_with_metadata_corrections |
| `star-destroyer-study`<br/>`examples/spaceship-atlas/star-destroyer-study` | `examples/10030-star-destroyer` | **inspiration** — retain scoped lesson; package and correct. retain_opt_in_inspiration_only |
| `ucs-y-wing-study`<br/>`examples/spaceship-atlas/ucs-y-wing-study` | `examples/75181-y-wing` | **inspiration** — retain scoped lesson; package and correct. retain_opt_in_inspiration_only |

Per-section observations, parents and limits: [spaceship findings](spaceship-findings.md).

### standalone

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `copper-lane`<br/>`examples/modular-street` | `examples/copper-lane` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `copper-bean`<br/>`examples/copper-bean` | `examples/copper-bean` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `sakura-garden`<br/>`examples/sakura-garden` | `examples/sakura-garden` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `cathedral-window`<br/>`examples/cathedral/window-fit.mpd` | `examples/cathedral-glazing#cathedral-window` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `cathedral-rose`<br/>`examples/cathedral/rose-fit.mpd` | `examples/cathedral-glazing#cathedral-rose` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `gear-drive`<br/>`examples/technic-studies/gear-drive` | `examples/gear-drive` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `bridge-tutorial`<br/>`examples/bridge.plan.json` | `examples/plan-basics#bridge-tutorial` | **tutorial** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `python-api`<br/>`examples/python_api.py` | `examples/plan-basics#python-api` | **tutorial** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `shadow-snap`<br/>`examples/shadow-snap.plan.json` | `examples/plan-basics#shadow-snap` | **tutorial** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |

Per-section observations, parents and limits: [standalone findings](standalone-findings.md).

### remaining-standalone

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `atlas-root`<br/>`examples/atlas-crane` | `examples/archive/atlas-crane-2026-11-03` | **hold** — hold whole source; extract only named selected sections. Hold whole model outside default construction retrieval; source context only for three selected lessons. No recommendation of unreviewed children. |
| `atlas-frame`<br/>`examples/atlas-crane` | `examples/atlas-crane-studies#atlas-frame` | **construction** — hold whole source; extract only named selected sections. Improve into one scoped frame-composition lesson; document mounting interfaces and source check limits before admission. |
| `atlas-outrigger`<br/>`examples/atlas-crane` | `examples/atlas-crane-studies#atlas-outrigger` | **construction** — hold whole source; extract only named selected sections. Improve as static outrigger construction study; do not call it a verified telescoping or load-bearing mechanism. |
| `atlas-boom`<br/>`examples/atlas-crane` | `examples/atlas-crane-studies#atlas-boom` | **construction** — hold whole source; extract only named selected sections. Improve as boom and 3:4:5 diagonal-layout study; extension, pivot, rope continuity and load capacity remain unverified. Truss is direct geometry within this section, not a separate authored submodel. |
| `turntable`<br/>`examples/turntable-frame` | `tests/fixtures/turntable-seating` | **diagnostic** — retain known-failure fixture. Keep only as diagnostic/manual-reconstruction fixture; substitute joiner and four invalid-seating findings must remain visible. Exclude construction recommendations until resolved. |

Per-section observations, parents and limits: [remaining-standalone findings](remaining-standalone-findings.md).

### lsynth-legacy

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `BRICK_ARC`<br/>`lsynth-examples/BRICK_ARC-Constraints.dat` | `lsynth-examples#BRICK_ARC` | **research** — retain raw source/synthesis and provenance; exclude default. Four coloured curled fingers emerge from a stepped cylindrical wrist. Treat as silhouette demonstration; no articulated or legal-brick-joint claim. Installed engine reflection failure remains blocking for derived construction. |
| `ELECTRIC_CABLE`<br/>`lsynth-examples/ELECTRIC_CABLE-Constraints.ldr` | `lsynth-examples#ELECTRIC_CABLE` | **research** — retain raw source/synthesis and provenance; exclude default. Tall girder workshop lamp with side arm, broad dish shade and coiled lead. Distill mounting and cable-entry lesson, preserving lead-family roll and access. |
| `ELECTRIC_NXT_CABLE`<br/>`lsynth-examples/ELECTRIC_NXT_CABLE-Constraints.ldr` | `lsynth-examples#ELECTRIC_NXT_CABLE` | **research** — retain raw source/synthesis and provenance; exclude default. Controller surrounded by sensors and two motors, coloured cables and slack loops. x933c01 plug geometry is missing; no complete connector-fit lesson until resolved. |
| `ELECTRIC_POWER_FUNCTION_CABLE`<br/>`lsynth-examples/ELECTRIC_POWER_FUNCTION_CABLE-Constraints.ldr` | `lsynth-examples#ELECTRIC_POWER_FUNCTION_CABLE` | **research** — retain raw source/synthesis and provenance; exclude default. Battery box, receivers and four separate motors form a component bench. Useful for plug/control/output access; lacks a shared mounting chassis. |
| `ELECTRIC_POWER_FUNCTION_CABLE_HALF`<br/>`lsynth-examples/ELECTRIC_POWER_FUNCTION_CABLE_HALF-Constraints.ldr` | `lsynth-examples#ELECTRIC_POWER_FUNCTION_CABLE_HALF` | **research** — retain raw source/synthesis and provenance; exclude default. Plug connects through middle junction to two small lamp heads. Distill explicit branching at actual hardware; two separate routes cannot substitute for missing junction. |
| `ELECTRIC_RCX_CABLE`<br/>`lsynth-examples/ELECTRIC_RCX_CABLE-Constraints.ldr` | `lsynth-examples#ELECTRIC_RCX_CABLE` | **research** — retain raw source/synthesis and provenance; exclude default. RCX controller with peripheral sensors/motors on a bench. Keep as legacy interface reference, not default current-part palette. |
| `FIBER_OPTICS_CABLE`<br/>`lsynth-examples/FIBER_OPTICS_CABLE-Constraints.ldr` | `lsynth-examples#FIBER_OPTICS_CABLE` | **research** — retain raw source/synthesis and provenance; exclude default. Four-cylinder V engine with curved optical fan-out, separate distributor assembly and loose guide samples. Front view confirms two cylinder banks; preserve distinction between inlined distributor geometry and assembly BOM. |
| `FIBER_OPTICS_CABLE_WIDE`<br/>`lsynth-examples/FIBER_OPTICS_CABLE_WIDE-Constraints.ldr` | `lsynth-examples#FIBER_OPTICS_CABLE_WIDE` | **research** — retain raw source/synthesis and provenance; exclude default. Two broad guides around compact mirrored cross-block/lever frame. Missing 4173497 parent prevents identifying a complete device or certifying its mounts. |
| `HOSE_FLEXIBLE_12L`<br/>`lsynth-examples/HOSE_FLEXIBLE_12L-Constraints.ldr` | `lsynth-examples#HOSE_FLEXIBLE_12L` | **research** — retain raw source/synthesis and provenance; exclude default. Three-wheel rover with clear bubble canopy, Technic wheel supports and System body. Missing 3020a remains explicit; retain as mixed-construction composition candidate, not a ready hose-generation recipe. |
| `HOSE_FLEXIBLE_19L`<br/>`lsynth-examples/HOSE_FLEXIBLE_19L-Constraints.ldr` | `lsynth-examples#HOSE_FLEXIBLE_19L` | **research** — retain raw source/synthesis and provenance; exclude default. Raised cylindrical equipment turret and separate curved barrier/straight samples. Missing 57539a and 57539b leave some hose geometry absent; no complete hose path acceptance. |
| `HOSE_FLEXIBLE_8.5L`<br/>`lsynth-examples/HOSE_FLEXIBLE_8.5L-Constraints.ldr` | `lsynth-examples#HOSE_FLEXIBLE_8.5L` | **research** — retain raw source/synthesis and provenance; exclude default. Pipe mounting board with upright loop, broad arch and straight samples. Distill end fitting orientations and coherent single route; whole board is a comparison fixture. |
| `MINIFIG_CHAIN_16L`<br/>`lsynth-examples/MINIFIG_CHAIN_16L-Constraints.ldr` | `lsynth-examples#MINIFIG_CHAIN_16L` | **research** — retain raw source/synthesis and provenance; exclude default. Many coloured chain poses on square board, with visible eye/end fittings. Useful end-link vocabulary; gravity, tautness and legal spans not established. |
| `RUBBER_BAND`<br/>`lsynth-examples/RUBBER_BAND-Constraints.ldr` | `lsynth-examples#RUBBER_BAND` | **research** — retain raw source/synthesis and provenance; exclude default. Triangular, crossed and two-wheel/micromotor arrangements. Preserve known tangent warnings and visibly questionable routes; prefer mounted tested starter for generation. |
| `RUBBER_BELT`<br/>`lsynth-examples/RUBBER_BELT-Constraints.ldr` | `lsynth-examples#RUBBER_BELT` | **research** — retain raw source/synthesis and provenance; exclude default. Two-wheel and multi-wheel flat belt wraps. Rim/pulley family compatibility and tangent warnings need per-route repair; do not copy arbitrary wheels. |
| `STRING_HOSE`<br/>`lsynth-examples/STRING_HOSE-Constraints.ldr` | `lsynth-examples#STRING_HOSE` | **research** — retain raw source/synthesis and provenance; exclude default. Wound shafts, large reel and two suspended hook arrangements. Drums and hook blocks are identifiable but bearing frame/anchors are incomplete. Do not infer winding dynamics or tension. |
| `STRING_xxL`<br/>`lsynth-examples/STRING_xxL-Constraints.ldr` | `lsynth-examples#STRING_xxL` | **research** — retain raw source/synthesis and provenance; exclude default. Measuring-board strings include straight and curved spans with ends. Only first three of six source studies are represented by supplied synthesis; later STRING_BAND blocks have no visual approval here. |
| `TECHNIC_AXLE_FLEXIBLE`<br/>`lsynth-examples/TECHNIC_AXLE_FLEXIBLE-Constraints.ldr` | `lsynth-examples#TECHNIC_AXLE_FLEXIBLE` | **research** — retain raw source/synthesis and provenance; exclude default. Swept open frame with angular upper rails and curved blue/yellow lower edges. Distill joiner/angle-connector interfaces and envelope; not a verified rotating transmission. |
| `TECHNIC_CHAIN_LINK`<br/>`lsynth-examples/TECHNIC_CHAIN_LINK-Constraints.ldr` | `lsynth-examples#TECHNIC_CHAIN_LINK` | **research** — retain raw source/synthesis and provenance; exclude default. Supported long small-link chain route plus gear-pair, triangular and single-wheel comparisons. Preserve tangent-warning scope and distinguish support rail from unsupported wrap samples. |
| `TECHNIC_CHAIN_LINK_WITH_TWO_STUDS`<br/>`lsynth-examples/TECHNIC_CHAIN_LINK_WITH_TWO_STUDS-Constraints.ldr` | `lsynth-examples#TECHNIC_CHAIN_LINK_WITH_TWO_STUDS` | **research** — retain raw source/synthesis and provenance; exclude default. Studded rigid-link loops around coarse-toothed wheels; potential conveyor-flight vocabulary. Retain exact wheel/link family, closure and support checks as prerequisites. |
| `TECHNIC_CHAIN_TREAD`<br/>`lsynth-examples/TECHNIC_CHAIN_TREAD-Constraints.ldr` | `lsynth-examples#TECHNIC_CHAIN_TREAD` | **research** — retain raw source/synthesis and provenance; exclude default. Two separate hinged-tread sizes on carrier blocks. Distill compatible wheel/link and axle support layout; they are not a single vehicle or interchangeable track family. |
| `TECHNIC_CHAIN_TREAD_38`<br/>`lsynth-examples/TECHNIC_CHAIN_TREAD_38-Constraints.ldr` | `lsynth-examples#TECHNIC_CHAIN_TREAD_38` | **research** — retain raw source/synthesis and provenance; exclude default. Long beam carrier with four large middle wheels, small end wheels and spring detail. Repeated route-wheel records must not create duplicate physical wheels. |
| `TECHNIC_FLEX-SYSTEM`<br/>`lsynth-examples/TECHNIC_FLEX-SYSTEM-Constraints.ldr` | `lsynth-examples#TECHNIC_FLEX-SYSTEM` | **research** — retain raw source/synthesis and provenance; exclude default. Tall frame has crossed inner cables, broad outer sleeve and lower clip/lever samples. Distinguish cable ends, fixed sleeve supports and pivots; no demonstrated actuation. |
| `TECHNIC_PNEUMATIC_HOSE`<br/>`lsynth-examples/TECHNIC_PNEUMATIC_HOSE-Constraints.ldr` | `lsynth-examples#TECHNIC_PNEUMATIC_HOSE` | **research** — retain raw source/synthesis and provenance; exclude default. Pump, lever valve and two-port cylinder with three working-layout hoses plus loose material samples. Prefer modern mounted press lesson; preserve hardware-before-routing principle. |
| `TECHNIC_RIBBED_HOSE`<br/>`lsynth-examples/TECHNIC_RIBBED_HOSE-Constraints.ldr` | `lsynth-examples#TECHNIC_RIBBED_HOSE` | **research** — retain raw source/synthesis and provenance; exclude default. Broad arch, low return and straight ribbed spans seated on support bricks. Distill correct supports and broad curvature; touching segments do not establish a joint. |
| `TECHNIC_TREAD`<br/>`lsynth-examples/TECHNIC_TREAD-Constraints.ldr` | `lsynth-examples#TECHNIC_TREAD` | **research** — retain raw source/synthesis and provenance; exclude default. Three continuous rubber-track carriers; supplemental view reveals all nine wheels omitted by hidden synthesis controls. One owner per physical wheel, separate from route constraints. |
| `TECHNIC_TREAD_CRAWLER`<br/>`lsynth-examples/TECHNIC_TREAD_CRAWLER-Constraints.ldr` | `lsynth-examples#TECHNIC_TREAD_CRAWLER` | **research** — retain raw source/synthesis and provenance; exclude default. Vintage low, stepped and upright crawler layouts plus isolated wheel wraps. Dedicated cylindrical-axle wheel/bearing family; tangent warnings and support gaps remain. |

Per-section observations, parents and limits: [lsynth-legacy findings](lsynth-legacy-findings.md).

### constraint-lab

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `straight`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#straight` | **diagnostic** — retain executable fixture and expected failure classification. Straight cylindrical route with enlarged sleeves at each end; no bend. |
| `corner-6`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#corner-6` | **diagnostic** — retain executable fixture and expected failure classification. Tight L-shaped route with visibly abrupt inner bend; preserve expected failure. |
| `corner-24`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#corner-24` | **diagnostic** — retain executable fixture and expected failure classification. Rounded right-angle route with straight end approaches; accepted narrowly above fixture minimum. |
| `corner-32`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#corner-32` | **diagnostic** — retain executable fixture and expected failure classification. Broader rounded corner in existing home view; sampled radius differs from nominal helper radius. |
| `corner-48`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#corner-48` | **diagnostic** — retain executable fixture and expected failure classification. Broad smooth corner with long end approaches; greatest sampled radius among corner baselines. |
| `corner-32-midpoint`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#corner-32-midpoint` | **diagnostic** — retain executable fixture and expected failure classification. Extra midpoint produces a more angular, tighter two-stage bend than baseline 32; preserve as counterexample to more markers being better. |
| `bundle`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#bundle` | **diagnostic** — retain executable fixture and expected failure classification. Two distinct parallel red corners, both individually visible with separate sleeves and a gap; same-frame comparison fixture, no supporting hardware. |
| `return`<br/>`examples/flex/constraint-lab` | `tests/fixtures/flex-constraints#return` | **diagnostic** — retain executable fixture and expected failure classification. U-shaped return with deliberate broad loop and separate ends; reversal has real routing space, not an instantaneous tangent flip. |

Per-section observations, parents and limits: [constraint-lab findings](constraint-lab-findings.md).

### mounted-flex

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `press`<br/>`examples/flex/pneumatic-press` | `examples/pneumatic-press` | **construction** — retain scoped lesson; package and correct. Use named.plan.json and named-review evidence as canonical. Preserve original-source compatibility/evidence separately. Correct C-frame to portal frame; keep three distinct hoses, actual fitting interfaces and static-only scope. |
| `hose`<br/>`examples/flex/hose.ldr` | `examples/flex-basics#hose` | **tutorial** — retain scoped lesson; package and correct. Red S-shaped hose with two sleeves, no mounted hardware; syntax, synthesis and BOM smoke only. |
| `band`<br/>`examples/flex/band.ldr` | `examples/flex-basics#band` | **tutorial** — retain scoped lesson; package and correct. Continuous red loop around two grey pulleys; no bearing frame or shaft retention. |
| `chain`<br/>`examples/flex/chain.ldr` | `examples/flex-basics#chain` | **tutorial** — retain scoped lesson; package and correct. Yellow discrete links around two grey gears; no bearings/supports. Prefer retained-chain-drive for mounted construction. |

Per-section observations, parents and limits: [mounted-flex findings](mounted-flex-findings.md).

### replacement

| Current candidate / owner | Proposed destination | Scope and action |
|---|---|---|
| `boombox`<br/>`output/boombox` | `examples/boombox` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `an225`<br/>`output/an225-mriya` | `examples/an225-mriya` | **construction** — retain scoped lesson; package and correct. Apply the linked per-section findings and preserve all existing check limitations. |
| `titan`<br/>`output/titan` | `output/titan` | **hold** — retain research in place; no submodel admission. Tracked yellow excavator with boxy house, glazed cab, articulated-looking arm and exposed hose loops; root only reviewed. No child admitted. |

Per-section observations, parents and limits: [replacement findings](replacement-findings.md).

## Existing catalog entries not admitted

Preserve their source for compatibility/history; remove their default recommendation and replacement fallback. These are not newly visually accepted. Re-selection would require the same visual/evidence gate.

| Legacy alias | Source | Proposed archive destination |
|---|---|---|
| `building:market-court` | `examples/building-atlas/market-court` | `examples/archive/building/market-court` |
| `building:museum` | `examples/building-atlas/museum` | `examples/archive/building/museum` |
| `building:fire-station` | `examples/building-atlas/fire-station` | `examples/archive/building/fire-station` |
| `building:school` | `examples/building-atlas/school` | `examples/archive/building/school` |
| `building:clinic` | `examples/building-atlas/clinic` | `examples/archive/building/clinic` |
| `building:workshop` | `examples/building-atlas/workshop` | `examples/archive/building/workshop` |
| `building:railway-station` | `examples/building-atlas/railway-station` | `examples/archive/building/railway-station` |
| `building:farmstead` | `examples/building-atlas/farmstead` | `examples/archive/building/farmstead` |
| `building:gatehouse` | `examples/building-atlas/gatehouse` | `examples/archive/building/gatehouse` |
| `building:medieval-village` | `examples/building-atlas/medieval-village` | `examples/archive/building/medieval-village` |
| `building:temple` | `examples/building-atlas/temple` | `examples/archive/building/temple` |
| `building:treehouse` | `examples/building-atlas/treehouse` | `examples/archive/building/treehouse` |
| `building:lighthouse` | `examples/building-atlas/lighthouse` | `examples/archive/building/lighthouse` |
| `building:winter-lodge` | `examples/building-atlas/winter-lodge` | `examples/archive/building/winter-lodge` |
| `building:wizard-tower` | `examples/building-atlas/wizard-tower` | `examples/archive/building/wizard-tower` |
| `building:moon-base` | `examples/building-atlas/moon-base` | `examples/archive/building/moon-base` |
| `building:frontier` | `examples/building-atlas/frontier` | `examples/archive/building/frontier` |
| `building:desert-sanctuary` | `examples/building-atlas/desert-sanctuary` | `examples/archive/building/desert-sanctuary` |
| `building:bench` | `examples/building-atlas/details/bench` | `examples/archive/building/bench` |
| `building:tree` | `examples/building-atlas/details/tree` | `examples/archive/building/tree` |
| `building:lamppost` | `examples/building-atlas/details/lamppost` | `examples/archive/building/lamppost` |
| `building:fountain` | `examples/building-atlas/details/fountain` | `examples/archive/building/fountain` |
| `building:market-stall` | `examples/building-atlas/details/market-stall` | `examples/archive/building/market-stall` |
| `vehicle:grand-tourer` | `examples/vehicle-atlas/grand-tourer` | `examples/archive/vehicle/grand-tourer` |
| `vehicle:delivery-van` | `examples/vehicle-atlas/delivery-van` | `examples/archive/vehicle/delivery-van` |
| `vehicle:pickup` | `examples/vehicle-atlas/pickup` | `examples/archive/vehicle/pickup` |
| `vehicle:tipper-truck` | `examples/vehicle-atlas/tipper-truck` | `examples/archive/vehicle/tipper-truck` |

## Other retained research and holds

| Source | Destination | Decision |
|---|---|---|
| `examples/stadium` | `examples/archive/stadium` | Reconcile authoritative plan/generator and delivered model before any admission. |
| `output/goliath` | `output/goliath` | Unfinished circuit/integration; process only, no model admission. |
| `output/jaguar-e-type` | `output/jaguar-e-type` | Reconcile source-specific reconstruction, attribution/restriction and completion before selection. |
| `examples/construction-studies` | `docs/reports/construction-studies` | Preserve analysis/source evidence; deduplicate Copper Lane lessons against its one example package. |
| `examples/archive` | `examples/archive` | Keep archive excluded; no automatic resurrection or deletion. |
| `examples/technic-studies` | `docs/reports/technic-studies` | Keep transferred historical source notes/images; gear-drive is the separately admitted child package. |
| `examples/snot/ferrari-f40` | `examples/ferrari-f40` | Preserve attributed source and selected-study evidence; unselected callouts and whole car remain source context, not admitted lessons. |
| `examples/snot/b-wing-6208` | `examples/b-wing-6208` | Keep parent source, route dependency and study metadata; no automatic admission of other set objects. |
| `examples/cathedral` | `examples/archive/cathedral` | Retain whole scene and history outside default; move only the two reviewed glazing fittings and their plan/evidence companions. |
| `lsynth-examples` | `lsynth-examples` | Retain synthesis companions, credits and previews with the raw corpus. |
| `examples/bridge.mpd` | `examples/plan-basics` | Move the reviewed MPD with bridge.plan.json; keep its section names. |
| `examples/cathedral/window-fit.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/window-fit.mpd` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/window-fit.plan.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/window-fit.stdout.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/rose-fit.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/rose-fit.mpd` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/rose-fit.plan.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/cathedral/rose-fit.stdout.json` | `examples/cathedral-glazing` | Keep fitting plan, source and exact check report together; not whole-cathedral acceptance. |
| `examples/submodel-atlas/recipes/01-8081-front-axle.json` | `examples/8081-front-axle` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/02-42075-rear-axle.json` | `examples/42075-differential-axle` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/03-42050-v8-engine.json` | `examples/42050-v8-engine` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/04-42078-headlight.json` | `examples/42078-headlight-cluster` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/05-10269-headlight-nacelle.json` | `examples/10269-primary-drive-cover` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/06-10283-shuttle-framework.json` | `examples/10283-oms-pod` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/07-75060-cockpit-base.json` | `examples/75060-pivoting-cockpit` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/08-7784-bat-hull.json` | `examples/7784-bat-grille` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/10-10182-roof-tower.json` | `examples/10182-roof-tower` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s01-10298-vespa-front.json` | `examples/10298-vespa-leg-shield` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s02-21307-caterham-nose.json` | `examples/21307-engine-exhaust` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s03-21319-central-perk-wall.json` | `examples/21319-patterned-floor` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s04-21309-saturn-module.json` | `examples/21309-radial-hub` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s05-41627-yoda.json` | `examples/41627-yoda` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s06-10278-door-column.json` | `examples/10278-vine-column` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s07-10272-rooftop-box.json` | `examples/10272-glazed-wall` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s08-10267-christmas-tree.json` | `examples/10267-christmas-tree` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s09-10258-bus-roof.json` | `examples/10258-rounded-roof` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s10-21046-empire-corner.json` | `examples/21046-recessed-entrance` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s11-10226-radial-engine.json` | `examples/10226-striped-rudder` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s13-40412-buckbeak-body.json` | `examples/40412-buckbeak-head` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s14-21303-walle-eye.json` | `examples/21303-walle-eye` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s15-10183-underbody.json` | `examples/10183-inverted-underbody` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s16-30050-shuttle-fuselage.json` | `examples/30050-micro-shuttle` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s17-10294-titanic-hull.json` | `examples/10294-hull-panels` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s17b-10294-titanic-hull-cabins.json` | `examples/10294-hull-panels` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s18-75276-tie-mount.json` | `examples/75276-mouth-grille` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s19-31031-chameleon.json` | `examples/31031-chameleon` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s20-21325-blacksmith.json` | `examples/21325-tree-trunk` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |
| `examples/submodel-atlas/recipes/s22-10030-isd-tower.json` | `examples/10030-micro-tantive` | Relocate native xray recipe with selected package; repair relative paths explicitly, preserve original evidence manifest. |

## File ownership and shared infrastructure

The JSON inventories **5089 tracked files** under examples and lsynth-examples. Files with an owner travel with that package, subject to selective extraction and metadata consolidation; shared files remain at their existing location until their consumers are reconciled. No automatic recursive copy or deletion is authorized by this inventory.

Parent source packages such as F40/B-wing retain their provenance and dependencies as a unit; only selected lessons enter search. The whole F40 source is not admitted by five reviewed studies. Atlas source travels as held provenance while only three named construction studies are extracted. The conservatory roof/whole scene is excluded even though its glazing selection is useful. Old test fixtures may retain their original paths until tests are migrated.

Grouped fitting packages retain independent source files below their lesson IDs; do not concatenate unrelated snippets into an artificial model. Keep one README with scoped sections and generate index entries for those sections. Distinct imported source assemblies can keep distinct packages even when their subject names overlap.

Shared atlas catalog/gallery generators, selections/manifests, reproduction helpers and root READMEs are infrastructure, not newly accepted examples. Replace authored catalog summaries with generated views of package metadata. Keep shared runtime geometry helpers in ldraw_tools; move or retire only the atlas orchestration layer after its consumers migrate.

See [catalog and export compatibility plan](catalog-export-migration.md) for aliases, generator/export contracts, evidence relocation and acceptance checks.
