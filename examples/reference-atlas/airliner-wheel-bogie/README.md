# Airliner wheel bogie

Small wheel carriers and a compact upright mounting pair create aircraft landing gear with a clear silhouette.

Source: `7893-1.mpd` / `7893 - wheels.ldr`. Scale: minifigure.

This System aircraft fitting contains a few Technic connector pieces. Match the upper mounting interface and tyre ground plane to the host aircraft; this is not a retracting mechanism recipe. Connection analysis leaves 5 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "airliner-wheel-bogie",
    "title": "Airliner wheel bogie",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:airliner-wheel-bogie"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Four-wheel, two-axle bogie and short upright mount with two parent placements. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "aircraft landing gear"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/airliner-wheel-bogie/preview.mpd",
    "plan": "examples/reference-atlas/airliner-wheel-bogie/scene.plan.json",
    "preview": "examples/reference-atlas/airliner-wheel-bogie/renders/home.png",
    "visual_review": "examples/reference-atlas/airliner-wheel-bogie/card.json",
    "model_sha256": "623fcc3cfab937710d54ad22223d8f715b7124a37e9dc6427414187e75e82e0e",
    "audit_pointer": "/items/2",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```