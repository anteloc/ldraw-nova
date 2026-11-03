# Park bench with shaped back

Dedicated shaped back elements and a mostly tiled seat create a recognizable bench with a low part count.

Source: `10261-1.mpd` / `10261 - bench.ldr`. Scale: minifigure.

Reserve eight studs of width and the backrest overhang beyond the two-stud seat. Attach the two white feet to the pavement and keep the seat studs accessible if adding figures.

The `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.

[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).

Run `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "park-bench",
    "title": "Park bench with shaped back",
    "scope": "hold",
    "kind": "assembly",
    "aliases": [
      "reference:park-bench"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Dark-blue seat/back and white feet as small furniture lesson. Origin hash differs from current corpus; preserve frozen artifacts and reconcile provenance before reusable export.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "seating"
    ],
    "export_blocker": "Existing discover export rejects stale origin identity; reconcile provenance before enabling export. Frozen artifact agreement does not waive this gate.",
    "model": "examples/park-bench/preview.mpd",
    "plan": "examples/park-bench/scene.plan.json",
    "preview": "examples/park-bench/renders/home.png",
    "visual_review": "examples/park-bench/card.json",
    "model_sha256": "0cb89243cbcca6f3c7835947af6aa0cf26ab55aa3c8cff72f94f66fae0d2ce7f",
    "audit_pointer": "/items/14",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```