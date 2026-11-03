# Timbered wall and projecting arches

Patterned timber panels, a shutter and paired arches create strong architectural identity in a small wall section.

Source: `6067-1.mpd` / `6067 - Side Wall.ldr`. Scale: minifigure.

The arches project well beyond the upright wall. Preserve their roof-support relationship, inspect the source base, and adapt the red palette deliberately to the new building.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "timbered-wall",
    "title": "Timbered wall and projecting arches",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:timbered-wall"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Printed corner panels, window and arched roof supports as facade detail. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "walls"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/timbered-wall/preview.mpd",
    "plan": "examples/timbered-wall/scene.plan.json",
    "preview": "examples/timbered-wall/renders/home.png",
    "visual_review": "examples/timbered-wall/card.json",
    "model_sha256": "be1f5daf6ba16a417cb42e2c90fc4899f800c248f6a4e838e41c5df0221e6bc8",
    "audit_pointer": "/items/23",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```