# Ornamental globe lamp

An inverted transparent globe and a sideways foliage sprig give a street fitting a distinctive silhouette.

Source: `3316-1.mpd` / `3316 - Lamppost.ldr`. Scale: minifigure.

Reserve the round four-stud base and the asymmetric foliage envelope. Check the bar, globe and sprig interfaces when adapting its height. Connection analysis leaves 9 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "ornamental-lamp",
    "title": "Ornamental globe lamp",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:ornamental-lamp"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "White base, grey post, clear cup/yellow bulb and green/red decoration alongside post. Decoration is not on top. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "street lighting"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/ornamental-lamp/preview.mpd",
    "plan": "examples/reference-atlas/ornamental-lamp/scene.plan.json",
    "preview": "examples/reference-atlas/ornamental-lamp/renders/home.png",
    "visual_review": "examples/reference-atlas/ornamental-lamp/card.json",
    "model_sha256": "1118d481587469c19c5ff021f0a43d314939e6abf220299588f4e8475c933af3",
    "audit_pointer": "/items/13",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```