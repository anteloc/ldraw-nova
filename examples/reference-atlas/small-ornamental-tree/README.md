# Small ornamental tree

Stacked brown cones and differently angled foliage produce a tapered trunk and a compact organic crown.

Source: `40782-1.mpd` / `40782 - TreeMedium`. Scale: unknown.

Treat this as a narrow ornamental plant or a small tree at the chosen scene scale. Add a ground attachment; the source does not include a landscape base. Connection analysis leaves 7 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "small-ornamental-tree",
    "title": "Small ornamental tree",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:small-ornamental-tree"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Cone/round trunk and large leaf blades as a distinct small tree construction. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "unknown",
    "subjects": [
      "foliage"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/small-ornamental-tree/preview.mpd",
    "plan": "examples/reference-atlas/small-ornamental-tree/scene.plan.json",
    "preview": "examples/reference-atlas/small-ornamental-tree/renders/home.png",
    "visual_review": "examples/reference-atlas/small-ornamental-tree/card.json",
    "model_sha256": "2d6dcd2dcf40d7417af74ad19d82211865a848f44ebc167363a3b76ba50e6f27",
    "audit_pointer": "/items/19",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```