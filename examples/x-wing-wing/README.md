# X wing wing

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "x-wing-wing",
    "title": "X-wing lower port wing with engine and tip cannon",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "spaceship:x-wing-wing"
    ],
    "families": [
      "spaceship"
    ],
    "legacy_groups": [
      "details"
    ],
    "lesson": "Thin plate wing, nacelle-1, projecting tip cannon and root trim form this local construction. The engine and laser cannon are separate roles. Preserve parent mounting context; the whole X-wing is not a single dish.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-audit.json",
    "subjects": [
      "wing"
    ],
    "model": "examples/x-wing-wing/source.mpd",
    "plan": "examples/x-wing-wing/scene.plan.json",
    "generator": "examples/x-wing-wing/generate.py",
    "preview": "examples/x-wing-wing/renders/home.png",
    "manual": "examples/x-wing-wing/index.html",
    "study_notes": "examples/x-wing-wing/study-notes.json",
    "visual_review": "examples/x-wing-wing/visual-review.json",
    "model_sha256": "09d0daa26aeba02e8a68d1bb35151f63bc20e78ff95de58bd6adc35d3dd80cc0",
    "audit_pointer": "/items/4",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-findings.md",
    "techniques": []
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### X-wing lower port wing with engine and tip cannon

| Source section | Opened-image observation |
|---|---|
| `study-7f62aaf2edbb-00-7191---bottom-port-wing.ldr` | Thin wedge plate wing with root nacelle and long tip cannon; actual parent is whole X-wing airframe, contradicting metadata calling it a single dish. |
| `study-7f62aaf2edbb-01-7191---blaster.ldr` | Long axial tip cannon with cylinder base, gear/ribbed region and projecting bar; parent view establishes tip position. |
| `study-7f62aaf2edbb-02-7191---nacelle-1.ldr` | Nacelle-1 engine with round red inlet core, cylindrical body and slender exhaust; distinguish engine from separate tip laser and from nacelle-2 mount variant. |
| `study-7f62aaf2edbb-03-7191---wing-step13-2.ldr` | Small root trim/support strip of plates, grilles and a perpendicular mount; inspected at inner wing near nacelle. |
