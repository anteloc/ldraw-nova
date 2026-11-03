# Faceted research-ship bow

Side-stud bricks and small slopes shape a compact ship bow in multiple directions without scaling any physical part.

Source: `31045-1.mpd` / `31045 - Ship front.ldr`. Scale: microscale.

The source axes do not present the bow as a complete horizontal hull. Consult the parent placement matrix before orienting it, and continue its red, dark blue and grey bands into the adjoining hull. Connection analysis leaves 3 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "faceted-ship-bow",
    "title": "Faceted research-ship bow",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:faceted-ship-bow"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Faceted red/blue bow. Include parent orientation: isolated view appears upright. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "microscale",
    "subjects": [
      "boat hulls"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/faceted-ship-bow/preview.mpd",
    "plan": "examples/reference-atlas/faceted-ship-bow/scene.plan.json",
    "preview": "examples/reference-atlas/faceted-ship-bow/renders/home.png",
    "visual_review": "examples/reference-atlas/faceted-ship-bow/card.json",
    "model_sha256": "6d7bdea4d0b5efb5eea91b669b33d8596894e7d14c8c5f8def11c3b46b2e17a7",
    "audit_pointer": "/items/7",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```