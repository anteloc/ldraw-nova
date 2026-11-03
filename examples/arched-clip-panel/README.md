# Arched panel with side clips

A small arch, grooved top edge and side clips combine a shaped opening with a useful attachment vocabulary.

Source: `10243-1.mpd` / `10243 - Roof - Notch.ldr`. Scale: minifigure.

This is a narrow roof-notch wall insert, not a complete dormer. Preserve the side-clip clearance and source orientation, and inspect the adjoining roof before attaching a new panel.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "arched-clip-panel",
    "title": "Arched panel with side clips",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:arched-clip-panel"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Arched opening, Technic holes and paired clips as roof-panel detail. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "architectural openings"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/arched-clip-panel/preview.mpd",
    "plan": "examples/arched-clip-panel/scene.plan.json",
    "preview": "examples/arched-clip-panel/renders/home.png",
    "visual_review": "examples/arched-clip-panel/card.json",
    "model_sha256": "979c732006d25e460dad5e5fca5193a3329e040bfb43b2434b4be16f2ceefc6c",
    "audit_pointer": "/items/3",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```