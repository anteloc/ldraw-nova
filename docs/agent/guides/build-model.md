# Build and revise a model

Start with a brief: subject, scale, silhouette, required features, palette and delivered poses. Use [knowledge search](../reference/cli.md#retrieve-construction-knowledge) to find the relevant construction role. Inspect actual parts and preserve the selected lesson's limits. Keep edits in one ordinary JSON plan or a generator that emits that plan.

Use named placement IDs for new work. `controls/pump` selects a physical part through its parent placement; repeated IDs expand to `id-0`, `id-1`. References and paths are relative to their declaring plan. Put required joints on the section and flex routes beside their actual rigid fittings; see [Technic contracts](../reference/technic.md) and [flex fields](../reference/flex.md). A whole module path does not identify one mating part.

## A complete small example

Save this as `output/stack.plan.json`:

```json
{
  "version": 1,
  "author": "Your name",
  "sections": [{
    "name": "stack.ldr",
    "description": "A blue plate on a red brick",
    "steps": [
      [{"id": "base", "ref": "3003.dat", "colour": 4, "at": [0, 0, 0]}],
      [{"id": "top", "ref": "3022.dat", "colour": 1, "on": "base"}]
    ]
  }]
}
```

```sh
./ldraw-agent review output/stack.plan.json
```

`build` writes `output/stack.mpd`. `review` puts checks, a frozen model copy, BOMs and previews in `output/stack-review/`. You can also run `review output/stack.plan.json` directly. Open the previews before accepting the construction. For a rebuild, add `--force`; explicit `--output` on `build` and `--outdir` on `review` override the defaults.

The upper plate's body is 8 LDU high, so `on` puts its origin at Y=-8. It does not add stud height. A different upper part requires its own body height; bounding-box height is not a stacking height.

## Iterate with scoped evidence

Build the smallest uncertain interface first. Run `./ldraw-agent review output/model.plan.json --no-render` while editing; use `--section NAME` for a local dependency closure. Repair the first failed prerequisite. After two unsuccessful local corrections, inspect the isolated interface and change the approach or available space.

Finish with a whole-model `review` and open its views, including hidden joins and the underside. A section check excludes parent and sibling interactions. Keep the final model, editable source, source-bound reports, BOM comparison and image observations together. See [review models](review-models.md).

The [plan reference](../reference/plans.md) owns exact fields, includes, anchors, repetition and Python APIs. Use [compose modules](compose-modules.md) for assemblies, [place parts](place-parts.md) for frames and connections, and [design models](design-models.md) for subject-specific decisions.

