# Plan basics

Minimal tutorials for MPD hierarchy, transforms, colour inheritance, procedural generation and connector snapping. These are syntax/API demonstrations, not aesthetic templates. Run `review` on the plan and open its images. The Python example writes its editable plan and checked model under `output/`.

```ldraw-knowledge
[
  {
    "id": "plan-basics#bridge-tutorial",
    "title": "Bridge tutorial",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "standalone:bridge-tutorial"
    ],
    "families": [
      "tutorial"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Minimal yellow deck on red and blue pillars. Retain only MPD hierarchy, transforms, steps and colour-inheritance tutorial; exclude aesthetic bridge recommendations. Two-part pillar inherits colour 16, shown red and blue in actual parent. Isolated renderer yellow is a display default, not source colour error.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "model": "examples/plan-basics/bridge.mpd",
    "model_sha256": "7f9a0a9e808d8b6e6dcf3ddff1ac24b007d0e2b74f4bfc577642b1f6be252138",
    "plan": "examples/plan-basics/bridge.plan.json",
    "audit_pointer": "/items/6",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": []
  },
  {
    "id": "plan-basics#python-api",
    "title": "Python api",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "standalone:python-api"
    ],
    "families": [
      "tutorial"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Four alternating blue/red 2x2 bricks form a short tower, matching procedural loop and on-previous-brick placement. Retain as API tutorial, excluded from aesthetic model recommendations.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "generator": "examples/plan-basics/python_api.py",
    "audit_pointer": "/items/7",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": []
  },
  {
    "id": "plan-basics#shadow-snap",
    "title": "Shadow snap",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "standalone:shadow-snap"
    ],
    "families": [
      "tutorial"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "A yellow 2x2 brick on an inherited-blue plate is centered on a red 2x4 brick. Retain minimal connector-snapping tutorial. Two-part cap contains plate plus yellow brick; plate inherits blue in parent. Parent view confirms nested snapping and colour inheritance.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "plan": "examples/plan-basics/shadow-snap.plan.json",
    "audit_pointer": "/items/8",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": []
  }
]
```
