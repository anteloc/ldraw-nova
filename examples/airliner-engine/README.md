# Airliner engine and pylon

A dedicated cylindrical engine casing, turbine face and exhaust create a convincing nacelle with a thin brick-built pylon.

Source: `7893-1.mpd` / `7893 - engine.ldr`. Scale: minifigure.

Reserve the four-stud engine diameter and eleven-stud source length. Match the pylon top studs to the wing and check fan and exhaust clearances before repeating the module. Connection analysis leaves 7 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "airliner-engine",
    "title": "Airliner engine and pylon",
    "scope": "archive",
    "kind": "assembly",
    "aliases": [
      "reference:airliner-engine",
      "aircraft:airliner-engine-retired"
    ],
    "families": [
      "reference",
      "aircraft"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Retired on 2026-11-10: superseded by `7893-jet-nacelle`, extracted from the current corpus with build pages, a board and a review. Fan housing and long thin pylon; four parent placements clarify attachment. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "aircraft engines"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/airliner-engine/preview.mpd",
    "plan": "examples/airliner-engine/scene.plan.json",
    "preview": "examples/airliner-engine/renders/home.png",
    "visual_review": "examples/airliner-engine/card.json",
    "model_sha256": "72c4462e668332a6c6a540c04c31ec796b68b0f71646eda652c9fb373c290f05",
    "audit_pointer": "/items/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```