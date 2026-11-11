# Review, repair and record the final model

For individual-part inspection, first obtain filenames from [part-information sources](part-information.md),
then render those specific references with existing tools and open the images.
Do not read raw library `.dat` contents. Review validates the documented
construction being adapted; part-search results alone cannot establish it.

Run `./ldraw-agent review MODEL.plan.json` or `review MODEL.mpd`. It combines source and geometry checks, declared structural/flex checks, BOM, views and renderer BOM comparison against frozen bytes. Read [diagnostic coverage](../reference/validation.md) and [artifact/exit meanings](../reference/cli.md#review-a-model). `--no-render` is for intermediate checks; skipped stages are not passing evidence.

Repair the first failed prerequisite, then recheck the affected interface and final whole assembly. A local section excludes parent and sibling interactions. Unsupported geometry is different from invalid LDraw. Choose contact scope deliberately and record skipped coverage; fixed supports and moving joints require different contracts.

## Inspect with ldraw-xray

Use `bin/ldraw-xray` from local setup (PATH fallback only if absent). Before use, read the [xray workflow](xray.md) and [environment setup](../../setup.md). Run `bin/ldraw-xray doctor` and consult its current help. Its library, shadow and renderer environment must be checked explicitly; Nova's defaults do not configure a separately invoked CLI.

```sh
bin/ldraw-xray sections data/models-annotated/42075-1.mpd
bin/ldraw-xray board overview data/models-annotated/42075-1.mpd \
  --section '42075 - rearaxle.ldr' --output output/inspect/rear-axle
```

Open `mosaic.png`, then full-size panels for small joins. Check the isolated selection and its actual parent placement, including every distinct parent where reused. Read the manifest's source hash, transforms, cameras and layers. Use source steps for construction order, cutaway or x-ray for obscured internals, stud maps for orientation, and explicit connection evidence for mating interfaces. Parent transforms can stand up a locally flat assembly.

Choose panels to answer a specific uncertainty. Avoid duplicate final-step and completed-model views. Reuse images only when source hashes and selection evidence match. Keep the native recipe/manifest instead of inventing a rendering framework. For moving parts, choose valid poses for the actual range and maintain a fixed camera; a generic 0/45/90 sweep can show impossible poses.

Synthetic axes, highlight colours, ghosting and overlay groups are visualization aids. Contact/overlap overlays reflect the tool's coverage and are not material-collision, clutch, load or motion proofs. State observed geometry separately from inferred operation.

## Read source steps when construction is unclear

`manual prepare FILE --section NAME --outdir DIR` makes attributed source steps and per-step parts. `mechanism prepare` adds operation notes. Use `--overview` for final views and source metadata, and `--no-render` to prepare data with visual/BOM evidence pending. Neither substitutes for opened images.

A final source group without a trailing STEP is still a real step. Empty groups are omitted from pages while source numbers remain. Children are subassembly callouts; embedded DAT parts remain physical leaves. A one-group source has no invented build sequence. The global `ldraw-render-steps.sh` is also available; read its installed help before selecting a section and useful step range.

## Record scoped conclusions

Open the whole model from useful sides, the underside and any hidden joins. Compare the brief at thumbnail size and check every retained selection in isolation and parent context. Record image paths, source identity, specific findings, corrections and unresolved limits in the package README or linked evidence. A JSON report cannot establish visual review.

Use `manual review DIR --images IMAGE ... --note TEXT` for existing prepared-manual evidence. Its export checks bind the reviewed artifacts by hash and require source checks and matching BOM; unchanged failures remain failures. Do not duplicate a full manual render set when native xray evidence already answers a curation question. Changing geometry requires fresh affected checks and images; changing descriptions alone does not.

Deliver editable source and exact final model, validation, BOM comparison, images and scoped observations. Physical validity remains unproven outside the documented checks.

