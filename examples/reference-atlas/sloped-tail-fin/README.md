# Sloped tail fin with beacon

A sequence of slopes, a thin contrasting base and a transparent tip make a small fin recognizable from a distance.

Source: `6745-1_Harrier-Jet.mpd` / `6745 - Vertical Tail.ldr`. Scale: unknown.

Use the six-stud long, narrow source profile as a scale reference. Side studs protrude beyond the nominal one-stud thickness; align the base to the fuselage and retain clearance.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "sloped-tail-fin",
    "title": "Sloped tail fin with beacon",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:sloped-tail-fin"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Thin black fin, yellow plate and translucent-red top; parent role agrees. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "unknown",
    "subjects": [
      "aircraft tails"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/sloped-tail-fin/preview.mpd",
    "plan": "examples/reference-atlas/sloped-tail-fin/scene.plan.json",
    "preview": "examples/reference-atlas/sloped-tail-fin/renders/home.png",
    "visual_review": "examples/reference-atlas/sloped-tail-fin/card.json",
    "model_sha256": "0a37e3ab2145cadeeed59a3eb687ca6bf227d1a4ab66424241dc8b4b6523c030",
    "audit_pointer": "/items/18",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```