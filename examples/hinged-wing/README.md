# Tapered wing with hinge root

Wedge plates establish a taper while hinge fingers, a grille and a small light give the wing a clear root and tip.

Source: `6745-1_Harrier-Jet.mpd` / `6745 - Wing LH.ldr`. Scale: unknown.

The source is the left wing. Inspect the matching right assembly rather than assuming reflection preserves connectors; reserve the root hinge sweep and approximately 12.8-stud span.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "hinged-wing",
    "title": "Tapered wing with hinge root",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:hinged-wing",
      "aircraft:hinged-wing"
    ],
    "families": [
      "reference",
      "aircraft"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Tapered wing with actual bar/clip root: 60478 handle plates, not hinge fingers. No validated sweep claim. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "unknown",
    "subjects": [
      "aircraft wings"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/hinged-wing/preview.mpd",
    "plan": "examples/hinged-wing/scene.plan.json",
    "preview": "examples/hinged-wing/renders/home.png",
    "visual_review": "examples/hinged-wing/card.json",
    "model_sha256": "a2112d85b7808db8f2dcd0c8c5cbf4d5e84018af256732a2229ed1ba1b8e2ffd",
    "audit_pointer": "/items/9",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```