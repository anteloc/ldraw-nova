# Classic compact truck tractor

A moulded windscreen, doors, grille, lights and antenna make a compact truck read as a vehicle rather than a box.

Source: `6594-1.mpd` / `6594 - Truck Head.ldr`. Scale: minifigure.

This source includes wheels and rear chassis as well as the cab. Inspect its coupling and wheel envelope before attaching a trailer; retain or replace the branded panel deliberately. Connection analysis leaves 8 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "6594-tractor-unit",
    "title": "Classic compact truck tractor",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:classic-truck-cab"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rename to complete compact tractor unit: white cab, red stripe, green grille, four-wheel chassis and rear turntable. Not just a cab. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "truck cabs"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/6594-tractor-unit/preview.mpd",
    "plan": "examples/6594-tractor-unit/scene.plan.json",
    "preview": "examples/6594-tractor-unit/renders/home.png",
    "visual_review": "examples/6594-tractor-unit/card.json",
    "model_sha256": "931abff5800d56683115749063df2cc97f1ad024ccbe6153d4b0c63d29f6a38e",
    "audit_pointer": "/items/4",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```