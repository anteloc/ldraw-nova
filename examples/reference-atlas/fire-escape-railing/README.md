# Fire-escape railing insert

Bars and articulated small elements produce thin open ironwork that reads more delicately than stacked wall bricks.

Source: `10185-1.mpd` / `10185 - Second Floor - Fire Escape.ldr`. Scale: minifigure.

This is a railing insert and support strip from a larger fire escape, not a complete stair. Preserve the angled bar connections and locate the strip in its floor or balcony context.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "fire-escape-railing",
    "title": "Fire-escape railing insert",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:fire-escape-railing"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Platform/rail detail with long support plate and bar/clip railing; not a complete stair flight. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "exterior railings"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/fire-escape-railing/preview.mpd",
    "plan": "examples/reference-atlas/fire-escape-railing/scene.plan.json",
    "preview": "examples/reference-atlas/fire-escape-railing/renders/home.png",
    "visual_review": "examples/reference-atlas/fire-escape-railing/card.json",
    "model_sha256": "487d1277cda48235d99e4e7b1b45882d7c03c9402b0c66de79c04d4ce5e5658d",
    "audit_pointer": "/items/8",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```