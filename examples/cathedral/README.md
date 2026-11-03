# Cathedral

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "cathedral-glazing#cathedral-window",
    "title": "Cathedral window",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "standalone:cathedral-window"
    ],
    "families": [
      "building"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Isolated fit fixture contains one repeated pointed-arch bay. Two rectangular glazed windows sit below a large OPEN upper arch; do not describe fully glazed Gothic window. White paired arches, side posts and upper fill surround two tan framed printed panes; actual fixture and four cathedral wall contexts checked. Consolidate as one six-stud bay lesson.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "model": "examples/cathedral/window-fit.mpd",
    "generator": "examples/cathedral/generate.py",
    "model_sha256": "87aea3982e72c1b33b669e9a74d85b1498b42397e0ed1c982eb8c39c0cce33e4",
    "audit_pointer": "/items/3",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": [
      "architecture"
    ]
  },
  {
    "id": "cathedral-glazing#cathedral-rose",
    "title": "Cathedral rose",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "standalone:cathedral-rose"
    ],
    "families": [
      "building"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rose motif plus rear side-stud support brick; supports a narrow mounting lesson, not a whole cathedral endorsement. Transparent blue round backing, white radial dish and transparent amber centre tile; appears above west-front entrance. Decorative applied motif, not a demonstrated through-wall opening.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "model": "examples/cathedral/rose-fit.mpd",
    "generator": "examples/cathedral/generate.py",
    "model_sha256": "8fe6406dca7263bc3ab5c4d308d730fb1c565a6e8f7b023c494bf7752f32b7ce",
    "audit_pointer": "/items/4",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": [
      "architecture"
    ]
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### Cathedral window

| Source section | Opened-image observation |
|---|---|
| `cathedral-window-fit.ldr` | Isolated fit fixture contains one repeated pointed-arch bay. Two rectangular glazed windows sit below a large OPEN upper arch; do not describe fully glazed Gothic window. |
| `cathedral-window-fit-bay.ldr` | White paired arches, side posts and upper fill surround two tan framed printed panes; actual fixture and four cathedral wall contexts checked. Consolidate as one six-stud bay lesson. |

### Cathedral rose

| Source section | Opened-image observation |
|---|---|
| `cathedral-rose-fit.ldr` | Rose motif plus rear side-stud support brick; supports a narrow mounting lesson, not a whole cathedral endorsement. |
| `cathedral-rose.ldr` | Transparent blue round backing, white radial dish and transparent amber centre tile; appears above west-front entrance. Decorative applied motif, not a demonstrated through-wall opening. |
