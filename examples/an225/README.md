# An-225: System airframe in a loading pose

Long six-engine cargo airframe with swept flat plate wing, twin fins, repeated landing bogies and raised nose/loading ramp. Cockpit section is glazing and hinge support; hold section is floor/threshold trim. Cargo blocks are solid placeholders; dorsal posts are a mounting motif.

## Reproduce and adapt

Run from the repository root. Write a new plan/output so the reviewed source stays available:

```sh
.venv/bin/python examples/an225/generate.py --plan output/an225.plan.json
./ldraw-agent review output/an225.plan.json
```

Keep the original source credit in the plan and MPD. Read the [design brief](design-brief.md) for local frames, actual interfaces and palette roles. Adapt the interface or module that serves the new brief; the whole silhouette is not a template. Geometry changes require new checks and isolated/parent review of the affected sections.

## Evidence and limits

1,011 placements; one optimistic versus 417 confirmed groups. Flat wing, stepped belly/nose, blunt tail, no cockpit interior, normal non-kneeling stance and ramp toe 6 LDU above ground. Recorded mesh checks retain eight hinge intersections and their explanations. No load, friction, retraction, steering, strength or continuous travel claim.

The [visual audit](evidence/visual-audit.json) records opened isolated sections and their actual parents. [Relocation records](evidence/relocation.json) map unchanged images, native recipes/manifests and reports to this package by SHA-256. Internal paths in those historical artifacts identify their original locations. The [original visual notes](history/visual-review.md) preserve revisions and coverage; exploratory outputs remain outside the package. No new physical acceptance is implied by promotion.

## Section entry points

These are addressable sections of one package. Repeated colours and logical groups do not become separate recommended models.

| Source section | Audited role |
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

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "an225",
    "title": "An-225: System airframe in a loading pose",
    "scope": "construction",
    "kind": "assembly",
    "subjects": [
      "vehicle",
      "aircraft"
    ],
    "techniques": [
      "system"
    ],
    "families": [
      "vehicle"
    ],
    "aliases": [
      "replacement:an225"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "Long six-engine cargo airframe with swept flat plate wing, twin fins, repeated landing bogies and raised nose/loading ramp. Cockpit section is glazing and hinge support; hold section is floor/threshold trim. Cargo blocks are solid placeholders; dorsal posts are a mounting motif.",
    "limits": "1,011 placements; one optimistic versus 417 confirmed groups. Flat wing, stepped belly/nose, blunt tail, no cockpit interior, normal non-kneeling stance and ramp toe 6 LDU above ground. Recorded mesh checks retain eight hinge intersections and their explanations. No load, friction, retraction, steering, strength or continuous travel claim.",
    "model": "examples/an225/an225-mriya.mpd",
    "model_sha256": "a454e81b53c115d874fc5d4dadd6a378564cee5f623111416f7f142f77b20c7a",
    "plan": "examples/an225/an225-mriya.plan.json",
    "generator": "examples/an225/generate.py",
    "visual_review": "examples/an225/evidence/visual-audit.json",
    "audit": "examples/an225/evidence/visual-audit.json"
  }
]
```

The original `evidence/aircraft.vehicle.json` preserves the old courier-part rejection. Current general aircraft checks no longer require that recipe; see `evidence/aircraft-current.json` after the promotion check. Main-bogie road checks are scoped to that bogie, not the complete aircraft. Hinge and mesh helpers remain beside the generator; their exact original inputs are under `evidence/tests/` and `evidence/checks/`.
