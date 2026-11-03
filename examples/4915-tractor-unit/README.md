# Mini construction truck cab

A narrow windscreen, shaped roof, grille and small wheel assemblies convey construction-vehicle character at a compact scale.

Source: `4915-1_Flat-Bed.mpd` / `4915 - Mini Construction - Cab.ldr`. Scale: microscale.

The cab body is only two studs wide with tyres extending beyond it. Use its actual dimensions instead of assuming minifigure seating, and build the rear body around the exposed chassis.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "4915-tractor-unit",
    "title": "Mini construction truck cab",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:mini-truck-cab"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rename complete compact four-wheel tractor unit with rear hitch; geometry extends beyond cab. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "microscale",
    "subjects": [
      "truck cabs"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/4915-tractor-unit/preview.mpd",
    "plan": "examples/4915-tractor-unit/scene.plan.json",
    "preview": "examples/4915-tractor-unit/renders/home.png",
    "visual_review": "examples/4915-tractor-unit/card.json",
    "model_sha256": "09e92741746184e39e46701bdc468676cf73361860b6e2259fac857e4912bab6",
    "audit_pointer": "/items/11",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```