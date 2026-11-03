# Moulded staircase and landing

A dedicated staircase provides thin risers and an open underside with far fewer parts than stacked solid bricks.

Source: `10182-1.mpd` / `10182 - First floor - Staircase.ldr`. Scale: minifigure.

Reserve four studs across the stair and a twelve-stud source depth including the narrow upper landing. Match the actual landing height to the floor; add handrails where the brief needs them.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "moulded-staircase",
    "title": "Moulded staircase and landing",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:moulded-staircase"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Moulded stairs and landing with actual floor opening shown in parent. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "stairs"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/moulded-staircase/preview.mpd",
    "plan": "examples/moulded-staircase/scene.plan.json",
    "preview": "examples/moulded-staircase/renders/home.png",
    "visual_review": "examples/moulded-staircase/card.json",
    "model_sha256": "50217ba7bb0f7dffccc7b6bb8fea92c79a0f8e94127d9e16a46731ea56eb9eb7",
    "audit_pointer": "/items/12",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```