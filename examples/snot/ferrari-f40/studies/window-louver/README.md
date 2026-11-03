# Window louver

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "ferrari-f40#window-louver",
    "title": "Window louver",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "f40:window-louver"
    ],
    "families": [
      "snot"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Make one small louver module, then place repeats on explicit stepped mounting planes. Three source stages combine a 3666 rail, two 30413 translucent panels and two 87087 side-stud bricks. The module contains five parts. The side-stud bricks turn the panel faces perpendicular to the rail. The surrounding clamshell supplies the repeated mounts; the local origin is not an automatically verified connector. subModel-52.ldr places three copies in step 15 at [-90,-75,7], [-130,-83,7] and [-170,-91,7], using its declared rotations. Their origins advance 40 LDU longitudinally and 8 LDU vertically in that parent frame. Transfer the repeated-module approach to vents, glazing or grille blades. The 40-by-8 progression belongs to this assembly, not to every louver design. Preserve joint seating and inspect clearance after changing the pitch.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/f40-audit.json",
    "model": "examples/snot/ferrari-f40/studies/window-louver/source.mpd",
    "plan": "examples/snot/ferrari-f40/studies/window-louver/scene.plan.json",
    "model_sha256": "9b485812d2bbd91ea7c1f0b7e8453a7af81e0c46f72e14ef4165b062163d9a9a",
    "audit_pointer": "/items/4",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/f40-findings.md",
    "techniques": [
      "snot"
    ],
    "subjects": []
  }
]
```