# Opening window with shutters

Dedicated window leaves and louvred shutters add depth and a recognizable opening mechanism to a facade.

Source: `6769-1.mpd` / `6769 - North - Window.ldr`. Scale: minifigure.

Use the frame footprint for the wall opening, not the approximately 7.5-stud open-shutter envelope. Reserve front and side sweep and preserve the leaf pivots. Connection analysis leaves 3 optimistic groups; inspect those unresolved interfaces during adaptation.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "shuttered-window",
    "title": "Opening window with shutters",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:shuttered-window"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Brown frame, grey shutters and blue open frames; avoid calling open frames glass panes. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "windows"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/shuttered-window/preview.mpd",
    "plan": "examples/shuttered-window/scene.plan.json",
    "preview": "examples/shuttered-window/renders/home.png",
    "visual_review": "examples/shuttered-window/card.json",
    "model_sha256": "d4a3e23b581fe2b304137c753a72d3dd73313a68d5fe90745fccb3ce834f094b",
    "audit_pointer": "/items/17",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```