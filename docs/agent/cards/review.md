# Review card

```sh
./ldraw-agent review output/TASK/model.plan.json --outdir output/TASK/review
```

`review` rebuilds the plan and runs every check. It writes the BOM, renders previews (home, top and front; choose others with `--views home front back left right top bottom`) and compares the renderer's BOM with the model's. Rerunning on an unchanged plan reuses the bundle, and a changed plan replaces it; `--force` recomputes anyway. Files you add to the bundle stop the review, so keep notes outside it.

## Look at the model

1. Open the previews and compare silhouette, proportions and colours with the brief, at thumbnail size and full size.
2. Look closely at every placement a warning names. To render one module alone, or in its parent:

   ```sh
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --view home -o output/TASK/xray/NAME
   bin/ldraw-xray render output/TASK/review/model.mpd --section NAME.ldr --parent model.ldr --highlight section --ghost --view home -o output/TASK/xray/NAME-in-place
   ```

   The [xray guide](../guides/xray.md) has more views, including stud maps and cutaways.
3. Fix what you see in the plan, then review again.

Checks cannot tell whether a model looks right; the images can. Neither checks nor images prove clutch, strength or motion.

## Deliver

In `output/TASK/`: the plan or generator, `model.mpd`, the `review/` bundle and a README of at most 40 lines covering:

- what was built and the main construction techniques;
- the commands that rebuild and review it;
- the images you opened;
- the limits you know about: warnings left on purpose and checks that were skipped.
