# Classical arch and cornice

A moulded arch, grooved masonry and round plates under the cornice create shadow lines in a shallow facade bay.

Source: `10276-1.mpd` / `10276 - bk3-step185.ldr`. Scale: display.

The source is only one stud deep and has two separate pier feet. Tie both piers into the host base and continue the cornice rhythm; use the parameterized arcade recipe for another height.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "classical-arch-bay#source-study",
    "title": "Classical arch and cornice",
    "scope": "hold",
    "kind": "detail",
    "aliases": [
      "reference:classical-arch-bay"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Narrow textured tan arch with round-spacer cornice; merge source with arcade-bay recipe. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "display",
    "subjects": [
      "architectural arches"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/reference-atlas/classical-arch-bay/preview.mpd",
    "plan": "examples/reference-atlas/classical-arch-bay/scene.plan.json",
    "preview": "examples/reference-atlas/classical-arch-bay/renders/home.png",
    "visual_review": "examples/reference-atlas/classical-arch-bay/card.json",
    "model_sha256": "80a3d0e8e7f307f229d98ddad5c67b4b9a2eef68a2c787826fb9606c00ed6c64",
    "audit_pointer": "/items/5",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```