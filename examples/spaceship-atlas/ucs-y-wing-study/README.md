# Ucs y wing study

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "75181-y-wing",
    "title": "UCS Y-wing: proportions and engine detailing",
    "scope": "inspiration",
    "kind": "assembly",
    "aliases": [
      "spaceship:ucs-y-wing-study"
    ],
    "families": [
      "spaceship"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "Whole ship has a narrow detailed spine, long twin nacelles and rear strut cages, white/yellow forward shell and black display stand. Inspiration only; 37 recorded overlaps remain. Tapered canopy is not a bubble enclosure. Flat tiled hull cheek with shaped underside sits beside forward cockpit; preserve model-local orientation.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-audit.json",
    "subjects": [
      "starfighter"
    ],
    "model": "examples/spaceship-atlas/ucs-y-wing-study/source.mpd",
    "plan": "examples/spaceship-atlas/ucs-y-wing-study/scene.plan.json",
    "preview": "examples/spaceship-atlas/ucs-y-wing-study/renders/home.png",
    "manual": "examples/spaceship-atlas/ucs-y-wing-study/index.html",
    "study_notes": "examples/spaceship-atlas/ucs-y-wing-study/study-notes.json",
    "visual_review": "examples/spaceship-atlas/ucs-y-wing-study/visual-review.json",
    "model_sha256": "9672ecdab2a3ebc10b6234eed450c5723e5f6f9207ca23d29919aa92452fbe42",
    "audit_pointer": "/items/7",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-findings.md",
    "techniques": []
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### UCS Y-wing: proportions and engine detailing

| Source section | Opened-image observation |
|---|---|
| `study-4de7854b1628-00-10134---main.ldr` | Whole ship has a narrow detailed spine, long twin nacelles and rear strut cages, white/yellow forward shell and black display stand. Inspiration only; 37 recorded overlaps remain. Tapered canopy is not a bubble enclosure. |
| `study-4de7854b1628-01-10134---subModel-1.ldr` | Flat tiled hull cheek with shaped underside sits beside forward cockpit; preserve model-local orientation. |
| `study-4de7854b1628-02-10134---subModel-2.ldr` | Small bracket/plate mounting block with round element sits toward aft central machinery; no strength inference. |
| `study-4de7854b1628-03-10134---subModel-3.ldr` | Two Technic bricks with pins carry round cylinder and minifig-head shaped detail on central spine. Do not claim a working swivel or sensor from the decorative shape. |
| `study-4de7854b1628-04-10134---subModel-4.ldr` | Three-part rail presents four sideways studs; two parent instances sit in aft central machinery. |
| `study-4de7854b1628-05-10134---subModel-5.ldr` | Two headlight bricks carry handled tile; parent repeats this handle detail on opposite sides of spine. |
| `study-4de7854b1628-06-10134---subModel-6.ldr` | Headlight brick plus clip tile; four instances around central spine. Retain as dependency with no new connectivity certification. |
| `study-4de7854b1628-07-10134---subModel-7.ldr` | Two-piece wing-shaped plate and printed round grille detail, repeated on aft central spine; not a complete wing assembly. |
| `study-4de7854b1628-09-10134---subModel-R5-D4.ldr` | Patterned white/red astromech body, rounded head and two legs; seated behind cockpit in the main body. Preserve source identity rather than using it as a generic mechanism. |
| `study-4de7854b1628-10-10134---subModel-8.ldr` | Detailed rectangular outrigger between central fuselage and one engine, with copper-coloured hoses, pins and side-stud faces. Source description incorrectly calls this a rear engine nacelle. |
| `study-4de7854b1628-11-10134---subModel-9.ldr` | Opposite outrigger with similar hose/grille detailing and different handed layout. Source description incorrectly calls this a rear engine nacelle. |
| `study-4de7854b1628-12-10134---subModel-10.ldr` | Main rectangular engine body with long surface hoses, side panels and conical rear nozzle; two instances in whole ship. Correct generic hull/strut and sensor-mast wording. |
| `study-4de7854b1628-13-10134---subModel-11.ldr` | Short transverse axle through paired Technic bricks with bushes; four placements on engine body provide lateral attachment features. |
| `study-4de7854b1628-14-10134---subModel-12.ldr` | Conical engine nozzle and surrounding clips/arms mounted at rear of engine body. Source description falsely calls it a dorsal rotating sensor/weapon turret. |
| `study-4de7854b1628-15-10134---subModel-13.ldr` | Long thin engine-side surface strip with lance-shaped pipe and grille tiles, repeated on opposite engine-body faces. Not an upright antenna mast array. |
| `study-4de7854b1628-16-10134---subModel-14.ldr` | Thin vented strip with underside pins and central handled detail, placed on outer engine sides; scope label to nacelle trim. |
| `study-4de7854b1628-17-10134---subModel-15.ldr` | Long open rear engine cage: four ribbed struts terminate in a round wheel-like end ring. Two instances extend aft from nacelles. Source incorrectly calls it engine front/cowling. |
| `study-4de7854b1628-18-10134---subModel-16.ldr` | Paired transverse axle/angle-connector brace located at the cage end ring. Static geometry does not establish moving linkage behavior. |
| `study-4de7854b1628-19-10134---subModel-17.ldr` | Axle and paired angle connectors with bushes, nested as one crosspiece of end-ring brace. |
| `study-4de7854b1628-20-10134---subModel-18.ldr` | Long ribbed strut assembled along an axle line; four copies form the cage. Clarify rear cage strut rather than armour/hose run. |
| `study-4de7854b1628-21-10134---subModel-20.ldr` | Rounded white forward nacelle housing with yellow stripe, internal core and four decorative side struts; two instances at forward engine ends. |
| `study-4de7854b1628-22-10134---subModel-19.ldr` | Substantial box-shaped core inside forward nacelle housing, with pin interfaces, side studs, handles and hinged faces. Not merely a hinged access panel. |
| `study-4de7854b1628-23-10134---subModel-21.ldr` | Two-rod decorative side strut with mechanical-figure pieces at one end; four copies wrap forward nacelle housing. No functional actuator claim. |
| `study-4de7854b1628-24-10134---subModel-22.ldr` | White/yellow forward hull and tapered tinted cockpit canopy, side cheek strips, nose projections and raised dorsal twin cannon. Retain as part of inspiration package pending repairs. |
| `study-4de7854b1628-25-10134---subModel-23.ldr` | Slim curved/sloped white/yellow cheek rail, repeated along both cockpit sides with local frame transformed into parent. |
| `study-4de7854b1628-26-10134---subModel-24.ldr` | Small plate-and-locking-hinge construction at rear edge of canopy; describe canopy mounting/hinge support rather than a barrel. |
| `study-4de7854b1628-27-10134---subModel-25.ldr` | Paired bar-and-cone cannon detail on roof behind canopy. Source calls it twin nose cannon/antenna, but parent proves dorsal position. |
| `study-4de7854b1628-28-10134---subModel-26.ldr` | Complete black display stand with crossed feet, tall Technic upright, diagonal brace and angled blank tiled plaque. Stability remains unproven. |
| `study-4de7854b1628-29-10134---subModel-27.ldr` | Tall Technic-brick upright placed vertically in stand; top pins form model-support region. |
| `study-4de7854b1628-30-10134---subModel-28.ldr` | Bent liftarm brace connects low portion of upright to stand base; static bracing, no demonstrated mechanism. |
| `study-4de7854b1628-31-10134---subModel-29.ldr` | Paired short angled liftarms and axle form nested top joint of stand brace. |
| `study-4de7854b1628-32-10134---subModel-30.ldr` | Small hinged plates appear twice at plaque location on stand base. Correct metadata claiming these directly hold the model: they support the plaque. |
| `study-4de7854b1628-33-10134---subModel-31.ldr` | Broad black tiled plaque panel on front of stand. No printed information is present in this source; label blank plaque surface. |
