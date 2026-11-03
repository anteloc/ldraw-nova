# Two-track loading ramp

Two wheel tracks, hinge fingers and a small grille communicate a functional loading surface while keeping the centre open.

Source: `5893-1_Truck.mpd` / `5893 - Truck ramp.ldr`. Scale: minifigure.

Measure the mating hinge in the host truck and match its finger spacing. Check both deployed and folded clearance; the source image shows only its stored local pose.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "truck-loading-ramp",
    "title": "Two-track loading ramp",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:truck-loading-ramp"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Paired wheel tracks and bar ends; parent shows upright stowed ramp behind truck. No checked-motion claim. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "vehicle loading"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/truck-loading-ramp/preview.mpd",
    "plan": "examples/truck-loading-ramp/scene.plan.json",
    "preview": "examples/truck-loading-ramp/renders/home.png",
    "visual_review": "examples/truck-loading-ramp/card.json",
    "model_sha256": "d3f1ae8be73072129c2dd42b033e7cbd9b1179caca06f1e948066b99dbdb65a7",
    "audit_pointer": "/items/24",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```