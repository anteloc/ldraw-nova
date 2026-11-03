# Small LSynth examples

Start with the [constraint authoring and repair guide](../../docs/agent/guides/flex.md).
The [executable constraint lab](constraint-lab/README.md) teaches bends, return
loops and bundles by measuring actual synthesis, including a failing tight bend.

These editable examples exercise three different physical boundaries. Install with `./setup.sh --with-lsynth`, then run from the repository root:

```sh
./ldraw-agent flex build examples/flex/hose.ldr --output output/flex/hose.mpd
./ldraw-agent flex build examples/flex/band.ldr --output output/flex/band.mpd
./ldraw-agent flex build examples/flex/chain.ldr --output output/flex/chain.mpd
./ldraw-agent review output/flex/hose.mpd --contacts none --views home top
./ldraw-agent review output/flex/band.mpd --contacts none --views home top
./ldraw-agent review output/flex/chain.mpd --contacts none --views home top
```

`flex build` checks both the constraints and the actual generated asset. Use `--force` to replace generated outputs after editing; unchanged synthesis is reused, with checks rerun. Open the previews before reusing the geometry. For complete models, [declare constraint sources in plan assets](../../docs/agent/reference/flex.md#generated-flexible-assets) and run `review PLAN` once. The pneumatic press below demonstrates that path.

| Source | Construction lesson | Expected physical count |
|---|---|---:|
| [hose.ldr](hose.ldr) | Three path markers with tangents along +X; many segments form one hose | 1 |
| [band.ldr](band.ldr) | Two pulleys guide one continuous band; wheels remain real parts | 3 |
| [chain.ldr](chain.ldr) | Two gears guide separate rigid chain links | 26: 24 links + 2 gears |
| [pneumatic-press/](pneumatic-press/README.md) | A complete model: hoses seated on real pneumatic nozzles, with tested bend radius and clearance | 41: 38 rigid + 3 hoses |

These are geometry studies without supporting frames. The hose has visible segment shading; the band has straight runs and curved wraps; the chain displays individual links. They do not establish stock lengths, tension or legal mechanical engagement. The band intentionally uses the legacy `4185.dat` identity listed by LSynth's radius definitions; current library alias warnings need no guessed substitution. Empty legacy `0 !` comments in LS11 also produce harmless unknown-meta warnings.

For creating paths, importing assets into plans, provenance and check limitations, read the [flexible-parts guide](../../docs/agent/reference/flex.md).

## Knowledge registration

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
    "model": "examples/flex/hose.ldr",
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
    "model": "examples/flex/band.ldr",
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
    "model": "examples/flex/chain.ldr",
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