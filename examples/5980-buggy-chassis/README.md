# Spacecraft wheel module

Wheel-pin plates, a tall bracket and small exhaust and grille fittings give a compact wheeled module a mechanical identity.

Source: `5980-1.mpd` / `5980 - 5980-4-a.ldr`. Scale: unknown.

The original parent calls this landing gear; its isolated appearance also suggests rover ideas. Preserve the hinge and bracket interfaces and test deployed clearance in the parent before reuse. Connection analysis leaves 7 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "5980-buggy-chassis",
    "title": "Spacecraft wheel module",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:spacecraft-wheel-module"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rename small vehicle chassis/wheel module. Whole-source view shows separate wheeled buggy in multi-object scene, not spacecraft landing gear. Remove deployed-landing-clearance guidance. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "unknown",
    "subjects": [
      "spacecraft landing gear"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/5980-buggy-chassis/preview.mpd",
    "plan": "examples/5980-buggy-chassis/scene.plan.json",
    "preview": "examples/5980-buggy-chassis/renders/home.png",
    "visual_review": "examples/5980-buggy-chassis/card.json",
    "model_sha256": "54ba749780582886136a049f2003f11e95767dda1b4c354dd38b5e672063e0b5",
    "audit_pointer": "/items/21",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```