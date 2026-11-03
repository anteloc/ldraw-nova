# Winter lamp with wreath

A dish shade, transparent round light and green life ring create a readable seasonal lamp with seven parts.

Source: `31038-1_Winter.mpd` / `31038 - Lamp.ldr`. Scale: minifigure.

The thin post has no pavement footing. Design its support before installation, and keep the wreath clear of pedestrians and nearby walls. Connection analysis leaves 3 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "winter-lamp",
    "title": "Winter lamp with wreath",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:winter-lamp"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Thin black post, yellow light, inverted shade and green wreath/red accent. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "street lighting"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/winter-lamp/preview.mpd",
    "plan": "examples/reference-atlas/winter-lamp/scene.plan.json",
    "preview": "examples/reference-atlas/winter-lamp/renders/home.png",
    "visual_review": "examples/reference-atlas/winter-lamp/card.json",
    "model_sha256": "7530276aed3c513a231ddc7a8bbd9dcc42de132438a1ceaffc6b7f94af96ac8e",
    "audit_pointer": "/items/26",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```