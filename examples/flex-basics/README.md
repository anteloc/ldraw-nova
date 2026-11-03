# Flexible-part basics

Three constraint tutorials: one posed hose, one band with two physical wheels, and separate rigid chain links with two gears. They teach synthesis and BOM ownership; they have no supporting frames and establish no stock length, tension or moving engagement.

```sh
./ldraw-agent flex build examples/flex-basics/hose.ldr --output output/hose.mpd
./ldraw-agent review output/hose.mpd --contacts none
```

Use the [mounted-flex guide](../../docs/agent/guides/flex.md) for real fittings, support and route checks. Preserve the original constraint files; already-synthesized output cannot reconstruct them.

```ldraw-knowledge
[
  {
    "id": "flex-basics#hose",
    "title": "Hose",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "mounted-flex:hose"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Red S-shaped hose with two sleeves, no mounted hardware; syntax, synthesis and BOM smoke only.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-audit.json",
    "model": "examples/flex-basics/hose.ldr",
    "model_sha256": "159b54f8933f010c44e65ae09ca349da27276cbe4a3f424905caba70694772e6",
    "audit_pointer": "/minimal_examples/0",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-findings.md",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-basics#band",
    "title": "Band",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "mounted-flex:band"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Continuous red loop around two grey pulleys; no bearing frame or shaft retention.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-audit.json",
    "model": "examples/flex-basics/band.ldr",
    "model_sha256": "9728eda4a8d212ab7c208cc8377a5a3d2795e27a334bd55cd24f3541298ad49d",
    "audit_pointer": "/minimal_examples/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-findings.md",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-basics#chain",
    "title": "Chain",
    "scope": "tutorial",
    "kind": "tutorial",
    "aliases": [
      "mounted-flex:chain"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Yellow discrete links around two grey gears; no bearings/supports. Prefer retained-chain-drive for mounted construction.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-audit.json",
    "model": "examples/flex-basics/chain.ldr",
    "model_sha256": "ee3406f83ea3ae6378fe39e8ca56e5be2821b99984481cefa7f6cac9660c30f3",
    "audit_pointer": "/minimal_examples/2",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/mounted-flex-findings.md",
    "techniques": [
      "flex"
    ],
    "subjects": []
  }
]
```
