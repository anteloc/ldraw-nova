# Replacement candidate findings

Planning decisions only. Three candidates / 25 sections visually reviewed: boombox six, An-225 eighteen, Titan root only. Goliath and Jaguar are triaged without visual admission. [Evidence and hashes](replacement-audit.json); [native boards](next-native/audit.json).

## Boombox: retain and package as a scoped example

`output/boombox/boombox.mpd` is a recognizable portable stereo. Promote its editable generator, plan, MPD, provenance and scoped evidence into one semantic example package during implementation. It provides a non-building SNOT panel/shell lesson, not a universal composition template. Document local panel coordinates, installed orientation, attachment interfaces and adaptation limits.

Existing design evidence explains the 26×6 case, 24×12 fascia, 40 LDU side-stud spacing (five plates / two stud pitches), and rear bracket courses. Preserve these measured interfaces rather than an instruction to copy the whole model. Existing checks cover 392 placements, 44 part types and 68 part/colour combinations. One optimistic group versus 185 confirmed groups is not full physical certification. Preserve the recessed speaker-socket/upper-spacer explanation, heuristic contact limits, handle attachment limits and unchecked colour availability.

| Section | Visual description and correction |
|---|---|
| `boombox.ldr` | Recognizable portable stereo: two large round speakers, central cassette/control strip, carry handle and aerial. Retain as scoped SNOT panel-and-shell exemplar, not universal model template. |
| `boombox-fascia.ldr` | Front panel composed flat in local coordinates and mounted vertically facing outward; two speaker bays, cassette tile, meters, orange tuner strip, controls and azure printed display. |
| `boombox-rear.ldr` | Flat rear panel with central dark battery-door motif, vents and white label. Actual back view confirms placement; no opening door or hinge shown. |
| `boombox-speaker.ldr` | Raised square bezel around round inverted dish and central cap, used twice in fascia. Preserve recessed socket/upper spacer evidence and do not rely on checker lower-spacer pairing. |
| `boombox-tweeter.ldr` | Small round brick and printed grille tile form tweeter; two upper fascia instances. |
| `boombox-knob.ldr` | Flat printed dial tile on round brick/collar stack; two centre fascia instances. Not a domed knob. |

## An-225: retain as System airframe and loading-pose study

`output/an225-mriya/an225-mriya.mpd` reads as a long six-engine cargo aircraft with swept wing and twin-fin tail. Its 18 sections provide useful modular organization without requiring the courier-jet parts prescribed by the current aircraft checker. Promote one package with generator, plan, source, brief, provenance and bounded validation evidence. Submodels become addressable sections in that package; colour variants and logical part groups do not become independent lessons.

Correct broad names in searchable descriptions as below. Keep documented simplifications prominent: flat wing, stepped belly/nose, blunt tail, no cockpit interior, normal rather than kneeling stance, and ramp toe 6 LDU above ground. Hinge orientation and the 22.5° ramp detent are useful exact-interface evidence; they do not establish friction, travel under load or build strength.

| Section | Visual description and correction |
|---|---|
| `an225-mriya.ldr` | Recognizable long six-engine high-wing cargo aircraft with twin-fin tail and raised nose/loading ramp. Retain as scoped System airframe and loading-pose study; stepped nose/belly and flat wing remain explicit simplifications. |
| `an225-keel.ldr` | Long layered plate keel with widened centre and gear mounting strips. Parent locates it beneath fuselage; visual bonding is not a strength rating. |
| `an225-fuselage.ldr` | Long hollow-sided fuselage shell with curved roof edges, blue/yellow stripe and open forward loading end; wing and tail mounting areas interrupt the roof finish. |
| `an225-sponsons.ldr` | Two separate long rounded-top side fairings around main gear. Logical pair in one section, not one independently connected module. |
| `an225-aft.ldr` | Stepped curved belly pieces and blunt tail closure, located beneath aft fuselage. Section is an incremental shell group, not a complete standalone rear fuselage. |
| `an225-cockpit.ldr` | Upper front glazing, roof strip and visor hinge bases. No seats, controls or complete cockpit interior; describe as glazing and hinge support. |
| `an225-hold.ldr` | Tiled floor strip, yellow threshold and ramp hinge bases. Describe as hold floor/threshold trim; enclosing walls belong to fuselage. |
| `an225-container-orange.ldr` | Solid orange brick cargo placeholder inside forward hold, not a hollow container with opening doors. |
| `an225-container-green.ldr` | Solid sand-green brick cargo placeholder farther aft in hold; same lesson as orange variant, no second search result. |
| `an225-main-gear.ldr` | Seven classic two-wheel axles joined by a longitudinal top beam; two mirrored-position parent instances make main landing gear. No retraction or steering demonstrated. |
| `axle-classic.ldr` | Classic System wheel holder, two rims and tyres; repeated seven times in main bogie and once per nose-leg section. Both actual immediate parents reviewed. |
| `an225-nose-leg.ldr` | Single two-wheel axle with stacked upper mounting plates, used twice beneath forward fuselage. Not a complete road vehicle or kneeling mechanism. |
| `an225-wing.ldr` | One complete swept, flat plate-built wing spanning both sides, with tiled central fields and studded wedge margins. No anhedral or load test. |
| `an225-engine.ldr` | Purpose-made jet nacelle with plate pylon and tile, repeated six times below wing. Composition lesson, not a brick-built engine mechanism. |
| `an225-tail.ldr` | Complete horizontal stabiliser and paired purpose-made vertical fins, with blue/yellow caps. No separate moving rudders/elevators shown. |
| `an225-details.ldr` | Four separated round mounting posts on dorsal fuselage; logical detail group for Buran mounting motif, not a connected assembly or supplied payload. |
| `an225-visor.ldr` | Stepped layered brick nose shell, placed raised ahead of cockpit. Preserve actual hinge orientation and static pose; do not claim tested opening travel or friction. |
| `an225-ramp.ldr` | Tiled flat ramp with yellow side borders and click-hinge tops, installed lowered at nose. Recorded toe remains 6 LDU above ground; not a flush or load-tested ramp. |

Existing reports cover 1,011 physical placements, matching Python/LeoCAD BOMs, 7,662 contacts with one optimistic versus 417 confirmed groups, and mesh analysis of 1,256 candidate pairs. Preserve the eight hinge intersections and their recorded explanations. `--strict` without geometry passing is not `--geometry --strict` passing: the latter still fails coverage. Main-bogie road checks do not classify the whole aircraft as a road vehicle. Aircraft family-part errors reflect hardcoded courier-jet requirements; use this as a checker regression case and retain the failure details until that policy is corrected. No new numeric checks were run here.

## Titan: hold; root triage only

`output/titan/titan.mpd` visually depicts a tracked excavator with a boxy yellow house, glazed cab, arm and exposed hoses. Its current root and preview hashes match the existing review. Do not admit the complete model or any unreviewed child as a working multi-pose reference.

All six saved pose reports still contain issues: c-reach-a 4, c-reach-b 3, reach 6, c-travel-a 1, c-travel-b 1, travel 6. The travel report records minimum route separation 6.1 and route-specific clearance/bend issues. Those diagnostics require interpretation and repair; they are not by themselves new material-intersection proofs. Hold pending consistent fixed-stock route lengths across poses, resolution of report issues, and review of every selected child and actual parent. Keep process/repair history outside default construction retrieval.

## Goliath and Jaguar: no visual admission

- `output/goliath`: process-only research. Notes describe a staged skeleton and unfinished hose-circuit work. Distill any general workflow lessons into guides only after checking applicability; do not advertise completed geometry.
- `output/jaguar-e-type`: hold the source-specific reconstruction. Preserve attribution and the source-stated commercial-use restriction. Reconcile source/provenance and completion before any model admission; this audit makes no legal determination or visual quality approval.

## Resulting retrieval policy

Default construction search may return the boombox and An-225 only after package corrections, with technique, intended use and limitations in the result. It must not fall back to Titan, Goliath or Jaguar when those searches have no match. Explicit research search can expose them with their hold reasons.
