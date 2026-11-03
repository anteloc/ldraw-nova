# B wing

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "75050-b-wing",
    "title": "75050 B-wing airframe study",
    "scope": "construction",
    "kind": "assembly",
    "aliases": [
      "spaceship:b-wing"
    ],
    "families": [
      "spaceship"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "The root places one detailed airframe section containing the offset cockpit, three unequal wings and four-nozzle cluster. It does not contain separate wing/fuselage/engine submodels. Retain the three recorded position corrections and source provenance; articulation is untested.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-audit.json",
    "subjects": [
      "starfighter"
    ],
    "model": "examples/75050-b-wing/source.mpd",
    "plan": "examples/75050-b-wing/scene.plan.json",
    "generator": "examples/75050-b-wing/generate.py",
    "preview": "examples/75050-b-wing/renders/home.png",
    "manual": "examples/75050-b-wing/index.html",
    "study_notes": "examples/75050-b-wing/study-notes.json",
    "visual_review": "examples/75050-b-wing/visual-review.json",
    "model_sha256": "91c67fdbea95b99d3067586b8b3c80d103be79417ec62d185833d1b4f148fae5",
    "audit_pointer": "/items/0",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-findings.md",
    "techniques": []
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### 75050 B-wing airframe study

| Source section | Opened-image observation |
|---|---|
| `study-773704369559-00-75050---Main.ldr` | Whole 75050 ship: offset cockpit, three unequal wings, four-nozzle cluster; retained in supplied static pose. |
| `study-773704369559-01-75050---B-Wing.ldr` | Single detailed airframe section contains the ship geometry. Root merely places it; metadata must not invent separately stored wing, fuselage and engine submodels. |
