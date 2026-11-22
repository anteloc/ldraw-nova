# Build and revise a model

Start timing before the brief: subject, scale, silhouette, required features, palette and delivered poses. Track every stage using the [delivery requirements](../cards/review.md#deliver). Use [knowledge search](../reference/cli.md#retrieve-construction-knowledge) to find the relevant construction role. Inspect actual parts and preserve the selected lesson's limits. Keep edits in one ordinary JSON plan or a generator that emits that plan.

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
./ldraw-agent build output/stack.plan.json
./ldraw-agent review output/stack.plan.json
```

`build` writes `output/stack.mpd` and prints a summary; a failing build writes `output/stack.draft.mpd` instead and keeps any earlier `stack.mpd`. `review` rebuilds the plan and puts checks, a frozen model copy, BOMs and previews in `output/stack-review/`. Open the previews before accepting the construction. Rerunning `review` on an unchanged plan reuses its bundle; a changed plan replaces it. Explicit `--output` on `build` and `--outdir` on `review` override the defaults.

The upper plate's body is 8 LDU high, so `on` puts its origin at Y=-8. It does not add stud height. For parts outside the curated stacking profiles, and for any sideways part, use a connector seat: `"on": {"to": "base", "face": "-Y", "stud": 0}` (see the [SNOT card](../cards/snot.md)).

## Iterate with scoped evidence

Build the smallest uncertain interface first. Run `./ldraw-agent review output/model.plan.json --draft` while editing to see a failing model, or `--no-render` for checks only; use `--section NAME` for a local dependency closure. The [checks card](../cards/checks.md) says what each diagnostic asks you to change. Repair the first failed prerequisite. After two unsuccessful local corrections, inspect the isolated interface and change the approach or available space.

Finish with a whole-model `review` and open its views, including hidden joins and the underside. A section check excludes parent and sibling interactions. Keep editable source, source-bound reports, BOM comparison and image observations internally. For user delivery, build with `--output output/TASK/ai-NAME.mpd` (named after the model, e.g. `ai-ford-mustang.mpd`), finalize the required metadata, and deliver only the model, timing metrics and visual evidence specified in the [review card](../cards/review.md#deliver). The example filenames above describe working outputs, not the final handoff name. See [review models](review-models.md).

The [plan reference](../reference/plans.md) owns exact fields, includes, anchors, repetition and Python APIs. Use [compose modules](compose-modules.md) for assemblies, [place parts](place-parts.md) for frames and connections, and [design models](design-models.md) for subject-specific decisions.

