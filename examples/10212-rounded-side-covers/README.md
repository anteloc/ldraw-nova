# Rounded cockpit shell

Repeated curved roof pieces form a smooth shell while narrow side ledges leave space for a cockpit or nose insert.

Source: `10212-1.mpd` / `10212 - subModel-19.ldr`. Scale: display.

The source shell is six studs wide and open at one end and underneath. Preserve the ledges and rear opening, then build the glazing, floor and host attachments for the new model.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "10212-rounded-side-covers",
    "title": "Rounded cockpit shell",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:rounded-cockpit-shell"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rename paired rounded body-side covers. Non-ghost parent view places these around the wing mechanism beside the body; cockpit/nose identity is incorrect. Curved-skin reuse elsewhere must be described as adaptation. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "display",
    "subjects": [
      "vehicle bodywork"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/10212-rounded-side-covers/preview.mpd",
    "plan": "examples/10212-rounded-side-covers/scene.plan.json",
    "preview": "examples/10212-rounded-side-covers/renders/home.png",
    "visual_review": "examples/10212-rounded-side-covers/card.json",
    "model_sha256": "62831a996f973733dfa03dbf7e6da998442a670ab78fe0a7242224582d6d0f26",
    "audit_pointer": "/items/16",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```