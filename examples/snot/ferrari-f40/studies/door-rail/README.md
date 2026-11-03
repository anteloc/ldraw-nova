# Door rail

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "ferrari-f40#door-rail",
    "title": "Door rail",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "f40:door-rail"
    ],
    "families": [
      "snot"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "A thin visible trim rail can also carry a repeated sideways stud field behind it. Two source stages combine a 6636 tile, two small spacers/caps and three 44728 brackets into a six-piece rail. The brackets expose a common perpendicular stud face. Their parent door supplies the remaining panel and hinge stack; the rail alone is not a complete opening door. subModel-34.ldr declares this child at [0,-88,0], in source step 7. The complete car's corresponding door is added in main source step 43. Its saved door is a separate callout, not a declared child of main.ldr. Transfer the repeated-bracket pattern to door trim or another narrow fascia. Keep the original spacing until actual sockets on the new panel have been inspected, then check the combined assembly.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/f40-audit.json",
    "model": "examples/snot/ferrari-f40/studies/door-rail/source.mpd",
    "plan": "examples/snot/ferrari-f40/studies/door-rail/scene.plan.json",
    "model_sha256": "a8abb51ee60bb3079919ebbf2ca25824c902357b24f42b334ab28125f24586bb",
    "audit_pointer": "/items/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/f40-findings.md",
    "techniques": [
      "snot"
    ],
    "subjects": []
  }
]
```