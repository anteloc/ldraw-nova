# Layered woodland tree

Round trunk courses and rotated foliage layers create a broad canopy with irregular edges.

Source: `4208-1.mpd` / `4208 - tree.ldr`. Scale: minifigure.

The green base is four studs square, but foliage spreads about 11.6 studs. Reserve that canopy envelope and adjust layer angles instead of simply scaling the source. Connection analysis leaves 5 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "layered-tree",
    "title": "Layered woodland tree",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:layered-tree"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Round brown trunk, three foliage layers and base as landscaping lesson. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "foliage"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/layered-tree/preview.mpd",
    "plan": "examples/reference-atlas/layered-tree/scene.plan.json",
    "preview": "examples/reference-atlas/layered-tree/renders/home.png",
    "visual_review": "examples/reference-atlas/layered-tree/card.json",
    "model_sha256": "22c2fd0c5aa1a50be31c92cfd515fe19eda013463ad21bf42e8c02779382dd80",
    "audit_pointer": "/items/10",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```